#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1_iam_info_collector.py - AWS IAM 정보 수집 도구

현재 AWS 자격 증명(Access Key, Secret Key)을 사용하여 모든 IAM 관련 정보를 수집합니다.
MITRE ATT&CK: T1526 (Cloud Service Discovery)

경고: 이 도구는 교육 및 보안 테스트 목적으로만 사용해야 합니다.
"""

import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError

# AWS 자격 증명 하드코딩 (실제 환경에서는 보안상 권장되지 않음)
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""

AWS_REGION = "ap-northeast-2"


def gather_all_iam_info():
    """
    모든 IAM 관련 정보 수집
    """
    print("[*] AWS IAM 정보 수집 중...")
    iam_info = {
        "current_user": {},
        "users": [],
        "groups": [],
        "roles": [],
        "policies": []
    }

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

        # 1. 현재 사용자 정보 수집
        print("[*] 현재 사용자 정보 수집 중...")
        user_name = user_arn.split('/')[-1] if '/' in user_arn else None

        if user_name and "user" in user_arn:
            user_details = iam_client.get_user(UserName=user_name)
            iam_info["current_user"] = user_details['User']

            # 사용자 정책 가져오기
            attached_policies = iam_client.list_attached_user_policies(UserName=user_name)
            iam_info["current_user"]["attached_policies"] = attached_policies["AttachedPolicies"]

            inline_policies = iam_client.list_user_policies(UserName=user_name)
            iam_info["current_user"]["inline_policies"] = inline_policies["PolicyNames"]

            # 사용자 그룹 가져오기
            user_groups = iam_client.list_groups_for_user(UserName=user_name)
            iam_info["current_user"]["groups"] = user_groups["Groups"]

            # 액세스 키 정보 가져오기
            access_keys = iam_client.list_access_keys(UserName=user_name)
            iam_info["current_user"]["access_keys"] = access_keys["AccessKeyMetadata"]

            # MFA 장치 가져오기
            mfa_devices = iam_client.list_mfa_devices(UserName=user_name)
            iam_info["current_user"]["mfa_devices"] = mfa_devices["MFADevices"]

            print(f"[+] 현재 사용자 정보 수집 완료: {user_name}")
        else:
            print("[!] 현재 자격 증명은 IAM 사용자가 아닙니다. 역할 기반 또는 루트 계정 액세스일 수 있습니다.")

        # 2. 모든 사용자 정보 수집
        print("[*] 모든 IAM 사용자 정보 수집 중...")
        users_response = iam_client.list_users()
        for user in users_response['Users']:
            user_info = {
                "UserDetails": user,
                "AttachedPolicies": [],
                "InlinePolicies": [],
                "Groups": [],
                "AccessKeys": [],
                "MFADevices": []
            }

            # 사용자별 정보 수집
            try:
                # 첨부된 정책
                attached_policies = iam_client.list_attached_user_policies(UserName=user['UserName'])
                user_info["AttachedPolicies"] = attached_policies["AttachedPolicies"]

                # 인라인 정책
                inline_policies = iam_client.list_user_policies(UserName=user['UserName'])
                user_info["InlinePolicies"] = inline_policies["PolicyNames"]

                # 그룹
                user_groups = iam_client.list_groups_for_user(UserName=user['UserName'])
                user_info["Groups"] = user_groups["Groups"]

                # 액세스 키
                access_keys = iam_client.list_access_keys(UserName=user['UserName'])
                user_info["AccessKeys"] = access_keys["AccessKeyMetadata"]

                # MFA 장치
                mfa_devices = iam_client.list_mfa_devices(UserName=user['UserName'])
                user_info["MFADevices"] = mfa_devices["MFADevices"]

            except ClientError as e:
                print(f"[!] 사용자 {user['UserName']} 세부 정보 가져오기 오류: {str(e)}")

            iam_info["users"].append(user_info)

        print(f"[+] 총 {len(iam_info['users'])}명의 IAM 사용자 정보 수집 완료")

        # 3. 모든 그룹 정보 수집
        print("[*] IAM 그룹 정보 수집 중...")
        groups_response = iam_client.list_groups()
        for group in groups_response['Groups']:
            group_info = {
                "GroupDetails": group,
                "AttachedPolicies": [],
                "InlinePolicies": []
            }

            # 그룹별 정책 정보 수집
            try:
                # 첨부된 정책
                attached_policies = iam_client.list_attached_group_policies(GroupName=group['GroupName'])
                group_info["AttachedPolicies"] = attached_policies["AttachedPolicies"]

                # 인라인 정책
                inline_policies = iam_client.list_group_policies(GroupName=group['GroupName'])
                group_info["InlinePolicies"] = inline_policies["PolicyNames"]

            except ClientError as e:
                print(f"[!] 그룹 {group['GroupName']} 세부 정보 가져오기 오류: {str(e)}")

            iam_info["groups"].append(group_info)

        print(f"[+] 총 {len(iam_info['groups'])}개의 IAM 그룹 정보 수집 완료")

        # 4. 모든 역할 정보 수집
        print("[*] IAM 역할 정보 수집 중...")
        roles_response = iam_client.list_roles()
        for role in roles_response['Roles']:
            role_info = {
                "RoleDetails": role,
                "AttachedPolicies": [],
                "InlinePolicies": []
            }

            # 역할별 정책 정보 수집
            try:
                # 첨부된 정책
                attached_policies = iam_client.list_attached_role_policies(RoleName=role['RoleName'])
                role_info["AttachedPolicies"] = attached_policies["AttachedPolicies"]

                # 인라인 정책
                inline_policies = iam_client.list_role_policies(RoleName=role['RoleName'])
                role_info["InlinePolicies"] = inline_policies["PolicyNames"]

            except ClientError as e:
                print(f"[!] 역할 {role['RoleName']} 세부 정보 가져오기 오류: {str(e)}")

            iam_info["roles"].append(role_info)

        print(f"[+] 총 {len(iam_info['roles'])}개의 IAM 역할 정보 수집 완료")

        # 5. 모든 정책 정보 수집
        print("[*] IAM 정책 정보 수집 중...")
        policies_response = iam_client.list_policies(Scope='Local')

        for policy in policies_response['Policies']:
            policy_info = {
                "PolicyDetails": policy,
                "PolicyDocument": {}
            }

            # 고객 관리형 정책의 경우 정책 문서 가져오기
            try:
                if not policy['Arn'].startswith('arn:aws:iam::aws:'):
                    policy_version = iam_client.get_policy_version(
                        PolicyArn=policy['Arn'],
                        VersionId=policy['DefaultVersionId']
                    )
                    policy_info["PolicyDocument"] = policy_version['PolicyVersion']['Document']

            except ClientError as e:
                print(f"[!] 정책 {policy['PolicyName']} 세부 정보 가져오기 오류: {str(e)}")

            iam_info["policies"].append(policy_info)

        print(f"[+] 총 {len(iam_info['policies'])}개의 IAM 정책 정보 수집 완료")

        # 결과를 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aws_iam_info_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(iam_info, f, default=str, indent=2)

        print(f"[+] IAM 정보가 {filename} 파일에 저장되었습니다.")

        return iam_info

    except Exception as e:
        print(f"[!] IAM 정보 수집 중 오류 발생: {str(e)}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("       AWS IAM 정보 수집 도구 - 보안 테스트용")
    print("=" * 60)
    print("경고: 이 도구는 교육 및 보안 테스트 목적으로만 사용하세요.")
    print("=" * 60)

    # 자격 증명 사용 전 확인
    print(f"AWS 계정 정보를 사용하여 정보를 수집합니다.")
    print(f"사용할 Access Key: {AWS_ACCESS_KEY[:4]}{'*' * (len(AWS_ACCESS_KEY) - 8)}{AWS_ACCESS_KEY[-4:]}")
    confirm = input("계속하시겠습니까? (y/n): ")

    if confirm.lower() == 'y':
        gather_all_iam_info()
    else:
        print("작업이 취소되었습니다.")