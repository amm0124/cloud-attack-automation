import boto3

def is_admin_user(iam_client):
    try:
        user = iam_client.get_user()
        user_name = user['User']['UserName']
    except iam_client.exceptions.NoSuchEntityException:
        # IAM 역할로 실행 중일 수도 있음
        print("이 코드는 IAM User가 아닌 Role로 실행되고 있을 수 있습니다.")
        return False

    # 유저에 연결된 정책 확인 (inline + managed)
    attached = iam_client.list_attached_user_policies(UserName=user_name)
    for policy in attached['AttachedPolicies']:
        if policy['PolicyName'] == 'AdministratorAccess':
            return True

    # 인라인 정책도 확인
    inline = iam_client.list_user_policies(UserName=user_name)
    for policy_name in inline['PolicyNames']:
        policy_doc = iam_client.get_user_policy(UserName=user_name, PolicyName=policy_name)
        statements = policy_doc['PolicyDocument']['Statement']
        if isinstance(statements, dict):
            statements = [statements]
        for stmt in statements:
            if stmt.get('Effect') == 'Allow' and stmt.get('Action') == '*' and stmt.get('Resource') == '*':
                return True

    # 그룹에 연결된 정책도 확인
    groups = iam_client.list_groups_for_user(UserName=user_name)
    for group in groups['Groups']:
        group_name = group['GroupName']
        group_policies = iam_client.list_attached_group_policies(GroupName=group_name)
        for policy in group_policies['AttachedPolicies']:
            if policy['PolicyName'] == 'AdministratorAccess':
                return True

    return False


# 세션 및 IAM 클라이언트 생성
session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
    region_name='us-east-1'  # 원하는 리전으로 변경
)
iam = session.client('iam')

# 관리자 권한 여부 확인
if is_admin_user(iam):
    print("✅ 현재 IAM 사용자는 관리자 권한이 있습니다.")
else:
    print("❌ 현재 IAM 사용자는 관리자 권한이 없습니다.")