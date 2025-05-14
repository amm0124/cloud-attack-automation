#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2_permission_checker.py - AWS IAM 권한 체크 도구

현재 AWS 자격 증명(Access Key, Secret Key)의 권한을 확인하고 위험한 권한이 있는지 분석합니다.
MITRE ATT&CK: T1526 (Cloud Service Discovery)

경고: 이 도구는 교육 및 보안 테스트 목적으로만 사용해야 합니다.
"""

import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError

# AWS 자격 증명 하드코딩 (실제 환경에서는 보안상 권장되지 않음)
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
AWS_REGION = "ap-northeast-2"


def check_dangerous_permissions():
    """
    현재 액세스 키가 위험한 권한을 가지고 있는지 확인
    """
    print("[*] 현재 보안 인증 정보의 권한 확인 중...")

    dangerous_permissions = {
        "admin_access": False,
        "iam_admin": False,
        "dangerous_policies": [],
        "dangerous_actions": []
    }

    high_risk_actions = [
        "iam:*",
        "iam:CreateUser",
        "iam:CreateAccessKey",
        "iam:AttachUserPolicy",
        "iam:AttachRolePolicy",
        "iam:AttachGroupPolicy",
        "iam:PutUserPolicy",
        "iam:PutRolePolicy",
        "iam:AddUserToGroup",
        "iam:UpdateAssumeRolePolicy",
        "iam:CreatePolicy",
        "iam:CreatePolicyVersion",
        "iam:SetDefaultPolicyVersion",
        "iam:PassRole",
        "sts:AssumeRole",
        "organizations:*",
        "lambda:CreateFunction",
        "lambda:InvokeFunction",
        "cloudformation:CreateStack",
        "ec2:RunInstances",
        "*:*"
    ]

    admin_policies = [
        "AdministratorAccess",
        "arn:aws:iam::aws:policy/AdministratorAccess"
    ]

    iam_admin_policies = [
        "IAMFullAccess",
        "arn:aws:iam::aws:policy/IAMFullAccess"
    ]

    try:
        # AWS 세션 및 클라이언트 초기화
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

        iam_client = session.client('iam')
        sts_client = session.client('sts')

        print("[+] AWS 세션 생성 성공")

        # 현재 보안 인증 정보 확인
        caller_identity = sts_client.get_caller_identity()
        account_id = caller_identity['Account']
        user_arn = caller_identity['Arn']
        user_id = caller_identity['UserId']

        print(f"[+] 현재 자격 증명: {user_arn}")
        print(f"[+] AWS 계정 ID: {account_id}")

        # 1. STS SimulatePrincipalPolicy API를 사용하여 권한 시뮬레이션
        user_name = user_arn.split('/')[-1] if '/' in user_arn and "user" in user_arn else None

        if user_name:
            print(f"[*] 사용자 {user_name}의 권한 시뮬레이션 중...")

            # 관리자 액세스 확인
            admin_simulation = []
            for action in ["*:*", "iam:*"]:
                try:
                    response = iam_client.simulate_principal_policy(
                        PolicySourceArn=user_arn,
                        ActionNames=[action],
                        ResourceArns=["*"]
                    )

                    for result in response['EvaluationResults']:
                        if result['EvalDecision'] == 'allowed':
                            admin_simulation.append({
                                'action': action,
                                'allowed': True,
                                'resource': '*'
                            })
                except ClientError as e:
                    if "AccessDenied" in str(e):
                        print(f"[!] simulate_principal_policy에 대한 권한이 없습니다. 대체 방법으로 진행합니다.")
                    else:
                        print(f"[!] 권한 시뮬레이션 중 오류: {str(e)}")

            if admin_simulation:
                dangerous_permissions["admin_access"] = True
                for sim in admin_simulation:
                    dangerous_permissions["dangerous_actions"].append(sim['action'])

            # 위험한 액션 확인
            for action in high_risk_actions:
                if action not in dangerous_permissions["dangerous_actions"]:
                    try:
                        response = iam_client.simulate_principal_policy(
                            PolicySourceArn=user_arn,
                            ActionNames=[action],
                            ResourceArns=["*"]
                        )

                        for result in response['EvaluationResults']:
                            if result['EvalDecision'] == 'allowed':
                                dangerous_permissions["dangerous_actions"].append(action)
                    except ClientError:
                        pass  # 이미 AccessDenied 오류에 대해 처리했음

        # 2. 현재 사용자의 정책 확인
        if user_name:
            # 첨부된 정책 확인
            attached_policies = iam_client.list_attached_user_policies(UserName=user_name)

            for policy in attached_policies['AttachedPolicies']:
                if policy['PolicyName'] in admin_policies or policy['PolicyArn'] in admin_policies:
                    dangerous_permissions["admin_access"] = True
                    dangerous_permissions["dangerous_policies"].append(policy['PolicyName'])

                if policy['PolicyName'] in iam_admin_policies or policy['PolicyArn'] in iam_admin_policies:
                    dangerous_permissions["iam_admin"] = True
                    dangerous_permissions["dangerous_policies"].append(policy['PolicyName'])

            # 현재 사용자의 그룹 정책 확인
            user_groups = iam_client.list_groups_for_user(UserName=user_name)

            for group in user_groups['Groups']:
                group_policies = iam_client.list_attached_group_policies(GroupName=group['GroupName'])

                for policy in group_policies['AttachedPolicies']:
                    if policy['PolicyName'] in admin_policies or policy['PolicyArn'] in admin_policies:
                        dangerous_permissions["admin_access"] = True
                        dangerous_permissions["dangerous_policies"].append(f"{group['GroupName']}:{policy['PolicyName']}")

                    if policy['PolicyName'] in iam_admin_policies or policy['PolicyArn'] in iam_admin_policies:
                        dangerous_permissions["iam_admin"] = True
                        dangerous_permissions["dangerous_policies"].append(f"{group['GroupName']}:{policy['PolicyName']}")

        # 3. 실제 권한 테스트
        print("[*] 실제 권한 테스트 중...")

        # IAM 사용자 목록 확인 시도
        try:
            iam_client.list_users(MaxItems=1)
            print("[+] IAM 읽기 권한 확인됨: iam:ListUsers")
            dangerous_permissions["dangerous_actions"].append("iam:ListUsers")
        except ClientError as e:
            if "AccessDenied" in str(e):
                print("[!] IAM 읽기 권한 없음: iam:ListUsers")

        # STS 권한 확인
        try:
            sts_client.get_caller_identity()
            print("[+] STS 권한 확인됨: sts:GetCallerIdentity")
            dangerous_permissions["dangerous_actions"].append("sts:GetCallerIdentity")
        except ClientError as e:
            if "AccessDenied" in str(e):
                print("[!] STS 권한 없음: sts:GetCallerIdentity")

        # S3 버킷 목록 확인 시도
        try:
            s3_client = session.client('s3')
            s3_client.list_buckets()
            print("[+] S3 읽기 권한 확인됨: s3:ListAllMyBuckets")
            dangerous_permissions["dangerous_actions"].append("s3:ListAllMyBuckets")
        except ClientError as e:
            if "AccessDenied" in str(e):
                print("[!] S3 읽기 권한 없음: s3:ListAllMyBuckets")

        # EC2 인스턴스 목록 확인 시도
        try:
            ec2_client = session.client('ec2')
            ec2_client.describe_instances(MaxResults=5)
            print("[+] EC2 읽기 권한 확인됨: ec2:DescribeInstances")
            dangerous_permissions["dangerous_actions"].append("ec2:DescribeInstances")
        except ClientError as e:
            if "AccessDenied" in str(e):
                print("[!] EC2 읽기 권한 없음: ec2:DescribeInstances")

        # 람다 함수 목록 확인 시도
        try:
            lambda_client = session.client('lambda')
            lambda_client.list_functions(MaxItems=1)
            print("[+] Lambda 읽기 권한 확인됨: lambda:ListFunctions")
            dangerous_permissions["dangerous_actions"].append("lambda:ListFunctions")
        except ClientError as e:
            if "AccessDenied" in str(e):
                print("[!] Lambda 읽기 권한 없음: lambda:ListFunctions")

        # 권한 결과 요약
        if dangerous_permissions["admin_access"]:
            print("[!] 경고: 이 자격 증명은 관리자 액세스 권한을 가지고 있습니다!")

        if dangerous_permissions["iam_admin"]:
            print("[!] 경고: 이 자격 증명은 IAM 관리자 권한을 가지고 있습니다!")

        if dangerous_permissions["dangerous_policies"]:
            print(f"[!] 위험한 정책 발견: {', '.join(dangerous_permissions['dangerous_policies'])}")

        if dangerous_permissions["dangerous_actions"]:
            print(f"[!] 위험한 액션 권한 발견: {', '.join(set(dangerous_permissions['dangerous_actions']))}")

        if not any([dangerous_permissions["admin_access"],
                    dangerous_permissions["iam_admin"],
                    dangerous_permissions["dangerous_policies"],
                    dangerous_permissions["dangerous_actions"]]):
            print("[+] 이 자격 증명은 특별히 위험한 권한을 가지고 있지 않습니다.")

        # 위험도 점수 계산
        risk_score = 0

        if dangerous_permissions["admin_access"]:
            risk_score += 100
        elif dangerous_permissions["iam_admin"]:
            risk_score += 90

        risk_score += len(dangerous_permissions["dangerous_policies"]) * 10
        risk_score += len(set(dangerous_permissions["dangerous_actions"])) * 5

        risk_score = min(risk_score, 100)  # 최대 100점으로 제한

        dangerous_permissions["risk_score"] = risk_score

        print(f"[+] 보안 위험도 점수: {risk_score}/100")

        # 결과를 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aws_permissions_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(dangerous_permissions, f, default=str, indent=2)

        print(f"[+] 권한 정보가 {filename} 파일에 저장되었습니다.")

        return dangerous_permissions

    except Exception as e:
        print(f"[!] 권한 확인 중 오류 발생: {str(e)}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("      AWS IAM 권한 체크 도구 - 보안 테스트용")
    print("=" * 60)
    print("경고: 이 도구는 교육 및 보안 테스트 목적으로만 사용하세요.")
    print("=" * 60)

    # 자격 증명 사용 전 확인
    print(f"AWS 계정 정보를 사용하여 권한을 확인합니다.")
    print(f"사용할 Access Key: {AWS_ACCESS_KEY[:4]}{'*' * (len(AWS_ACCESS_KEY) - 8)}{AWS_ACCESS_KEY[-4:]}")
    confirm = input("계속하시겠습니까? (y/n): ")

    if confirm.lower() == 'y':
        check_dangerous_permissions()
    else:
        print("작업이 취소되었습니다.")