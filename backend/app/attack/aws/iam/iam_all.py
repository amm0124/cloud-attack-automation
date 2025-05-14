import boto3

# 자격 증명으로 세션 생성
session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key=''
)
iam = session.client('iam')


# 사용자 정보
def list_users():
    print("🔹 [IAM Users]")
    users = iam.list_users()['Users']
    for user in users:
        name = user['UserName']
        print(f"- User: {name}")

        # 사용자에 연결된 managed policy
        attached = iam.list_attached_user_policies(UserName=name)['AttachedPolicies']
        for pol in attached:
            print(f"  📎 Attached Policy: {pol['PolicyName']}")

        # 인라인 정책
        inlines = iam.list_user_policies(UserName=name)['PolicyNames']
        for p in inlines:
            policy = iam.get_user_policy(UserName=name, PolicyName=p)
            print(f"  📄 Inline Policy: {p} => {policy['PolicyDocument']}")


# 그룹 정보
def list_groups():
    print("\n🔹 [IAM Groups]")
    groups = iam.list_groups()['Groups']
    for group in groups:
        name = group['GroupName']
        print(f"- Group: {name}")

        attached = iam.list_attached_group_policies(GroupName=name)['AttachedPolicies']
        for pol in attached:
            print(f"  📎 Attached Policy: {pol['PolicyName']}")

        inlines = iam.list_group_policies(GroupName=name)['PolicyNames']
        for p in inlines:
            policy = iam.get_group_policy(GroupName=name, PolicyName=p)
            print(f"  📄 Inline Policy: {p} => {policy['PolicyDocument']}")


# 역할 정보
def list_roles():
    print("\n🔹 [IAM Roles]")
    roles = iam.list_roles()['Roles']
    for role in roles:
        name = role['RoleName']
        print(f"- Role: {name}")

        attached = iam.list_attached_role_policies(RoleName=name)['AttachedPolicies']
        for pol in attached:
            print(f"  📎 Attached Policy: {pol['PolicyName']}")

        inlines = iam.list_role_policies(RoleName=name)['PolicyNames']
        for p in inlines:
            policy = iam.get_role_policy(RoleName=name, PolicyName=p)
            print(f"  📄 Inline Policy: {p} => {policy['PolicyDocument']}")


# 고객 관리형 정책 정보
def list_custom_policies():
    print("\n🔹 [Customer Managed Policies]")
    policies = iam.list_policies(Scope='Local')['Policies']
    for policy in policies:
        arn = policy['Arn']
        name = policy['PolicyName']
        default_version = iam.get_policy(PolicyArn=arn)['Policy']['DefaultVersionId']
        doc = iam.get_policy_version(PolicyArn=arn, VersionId=default_version)['PolicyVersion']['Document']
        print(f"- Policy: {name}")
        print(f"  📄 Document: {doc}")


# 실행
list_users()
list_groups()
list_roles()
list_custom_policies()