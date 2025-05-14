import boto3
from botocore.exceptions import ClientError
import json

ACCESS_KEY = ""
SECRET_KEY = ""

session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key=''
)

iam = session.client('iam')
sts = session.client('sts')

# 1. 현재 Caller 정보 (User 또는 Role)
identity = sts.get_caller_identity()
arn = identity['Arn']
print(f"🔐 현재 인증된 주체 ARN: {arn}")
account_id = identity['Account']

# Try get user name
try:
    user = iam.get_user()
    principal_type = "User"
    principal_name = user['User']['UserName']
except ClientError:
    principal_type = "Role"
    principal_name = arn.split("/")[-1]

print(f"▶️ 타입: {principal_type}, 이름: {principal_name}")


# 2. Attached Policies
def get_attached_policies():
    if principal_type == "User":
        resp = iam.list_attached_user_policies(UserName=principal_name)
    else:
        resp = iam.list_attached_role_policies(RoleName=principal_name)
    return resp['AttachedPolicies']

# 3. Inline Policies
def get_inline_policies():
    if principal_type == "User":
        policy_names = iam.list_user_policies(UserName=principal_name)['PolicyNames']
        return [iam.get_user_policy(UserName=principal_name, PolicyName=name) for name in policy_names]
    else:
        policy_names = iam.list_role_policies(RoleName=principal_name)['PolicyNames']
        return [iam.get_role_policy(RoleName=principal_name, PolicyName=name) for name in policy_names]

# 4. Simulate permissions
def simulate_permissions():
    print("▶️ simulate_principal_policy 실행 중...")
    # AWS 전체 서비스 액션 샘플 (대표 200개)
    # 전체 1000+개는 분할 시뮬레이션 필요. 간단히 추려서 데모
    services = [
        "s3:*", "ec2:*", "iam:*", "lambda:*", "dynamodb:*", "cloudwatch:*", "kms:*", "rds:*", "sts:*",
        "logs:*", "events:*", "sns:*", "sqs:*", "cloudtrail:*", "ecr:*", "eks:*", "athena:*", "glue:*"
    ]
    results = iam.simulate_principal_policy(
        PolicySourceArn=arn,
        ActionNames=services
    )['EvaluationResults']
    allowed = [r['EvalActionName'] for r in results if r['EvalDecision'] == 'allowed']
    return allowed


# 5. Custom Policies (Local)
def get_custom_policies():
    policies = iam.list_policies(Scope='Local')['Policies']
    result = []
    for p in policies:
        version = iam.get_policy(PolicyArn=p['Arn'])['Policy']['DefaultVersionId']
        doc = iam.get_policy_version(PolicyArn=p['Arn'], VersionId=version)['PolicyVersion']['Document']
        result.append({
            'PolicyName': p['PolicyName'],
            'Arn': p['Arn'],
            'Document': doc
        })
    return result


# === 실행 ===
print("\n📌 [1] 연결된 Managed Policies")
for p in get_attached_policies():
    print(f" - {p['PolicyName']} ({p['PolicyArn']})")

print("\n📌 [2] 인라인 정책 내용")
for p in get_inline_policies():
    print(f" - {p['PolicyName']}")
    print(json.dumps(p['PolicyDocument'], indent=2))

print("\n📌 [3] 시뮬레이션된 허용된 권한")
for action in simulate_permissions():
    print(f" ✅ {action}")

print("\n📌 [4] 계정 내 고객 관리형 정책")
for p in get_custom_policies():
    print(f" - {p['PolicyName']}")
    print(json.dumps(p['Document'], indent=2))