import boto3
import json
from botocore.exceptions import ClientError

# AWS 자격 증명으로 세션 생성
session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key=''
)


def enumerate_permissions():
    # IAM 클라이언트 생성
    iam = session.client('iam')

    print("=== 권한 열거 시작 ===")

    try:
        # 현재 사용자 정보 확인
        current_user = iam.get_user()
        print(f"현재 사용자: {current_user['User']['UserName']}")

        # 사용자의 정책 확인
        user_policies = iam.list_attached_user_policies(
            UserName=current_user['User']['UserName']
        )
        print("\n직접 연결된 정책:")
        for policy in user_policies['AttachedPolicies']:
            print(f"- {policy['PolicyName']}")

            # 정책 상세 내용 확인
            policy_version = iam.get_policy_version(
                PolicyArn=policy['PolicyArn'],
                VersionId=iam.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
            )
            print(json.dumps(policy_version['PolicyVersion']['Document'], indent=4))

        # 사용자 그룹 확인
        user_groups = iam.list_groups_for_user(
            UserName=current_user['User']['UserName']
        )
        print("\n소속 그룹:")
        for group in user_groups['Groups']:
            print(f"- {group['GroupName']}")

            # 그룹에 연결된 정책 확인
            group_policies = iam.list_attached_group_policies(
                GroupName=group['GroupName']
            )
            print(f"  그룹 '{group['GroupName']}'에 연결된 정책:")
            for policy in group_policies['AttachedPolicies']:
                print(f"  - {policy['PolicyName']}")

        # 사용자가 수임할 수 있는 역할 확인 시도
        roles = iam.list_roles()
        print("\n계정 내 역할 목록:")
        for role in roles['Roles']:
            print(f"- {role['RoleName']}")

        # 계정의 모든 사용자 나열
        users = iam.list_users()
        print("\n계정 내 사용자 목록:")
        for user in users['Users']:
            print(f"- {user['UserName']}")

    except ClientError as e:
        print(f"권한 열거 중 오류 발생: {e}")

    print("=== 권한 열거 완료 ===")


# 실행
enumerate_permissions()