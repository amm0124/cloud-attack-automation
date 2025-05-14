


import boto3

# 자격 증명 입력
session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
    region_name='us-east-1'  # 원하는 리전으로 변경
)

iam = session.client('iam')

# 사용자 목록
users = iam.list_users()
print("== Users ==")
for user in users['Users']:
    print(user['UserName'])

# 그룹 목록
groups = iam.list_groups()
print("\n== Groups ==")
for group in groups['Groups']:
    print(group['GroupName'])

# 역할 목록
roles = iam.list_roles()
print("\n== Roles ==")
for role in roles['Roles']:
    print(role['RoleName'])

# 고객 관리형 정책 목록
policies = iam.list_policies(Scope='Local')
print("\n== Customer Managed Policies ==")
for policy in policies['Policies']:
    print(policy['PolicyName'])