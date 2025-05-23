import boto3
import json
import argparse
from datetime import datetime
from botocore.exceptions import ClientError


def create_aws_session(access_key, secret_key, region):
    """AWS 세션 생성"""
    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )


def get_account_info(session):
    """계정 정보 조회"""
    try:
        sts = session.client('sts')
        return sts.get_caller_identity()
    except Exception as e:
        return {"error": str(e)}


def analyze_aws_managed_policies(iam):
    """AWS 관리형 정책 분석"""
    high_risk_policies = []
    high_risk_names = ['AdministratorAccess', 'PowerUserAccess']

    try:
        paginator = iam.get_paginator('list_policies')
        for page in paginator.paginate(Scope='AWS'):
            for policy in page['Policies']:
                if policy['PolicyName'] in high_risk_names:
                    high_risk_policies.append(policy)
    except Exception as e:
        return [{"error": str(e)}]

    return high_risk_policies


def is_wildcard_permission(actions, resources):
    """와일드카드 권한 확인"""
    action_wildcard = actions == '*' or (isinstance(actions, list) and '*' in actions)
    resource_wildcard = resources == '*' or (isinstance(resources, list) and '*' in resources)
    return action_wildcard and resource_wildcard


def assess_policy_risk(iam, policy):
    """정책 위험도 평가"""
    try:
        policy_version = iam.get_policy_version(
            PolicyArn=policy['Arn'],
            VersionId=policy['DefaultVersionId']
        )
        policy_doc = policy_version['PolicyVersion']['Document']

        for statement in policy_doc.get('Statement', []):
            if statement.get('Effect') == 'Allow':
                actions = statement.get('Action', [])
                resources = statement.get('Resource', [])

                if is_wildcard_permission(actions, resources):
                    return 'high', '모든 리소스에 대한 모든 작업 허용'
                elif resources == '*' or (isinstance(resources, list) and '*' in resources):
                    return 'medium', '모든 리소스에 대한 특정 작업 허용'
    except Exception:
        pass

    return None, None


def analyze_customer_managed_policies(iam):
    """고객 관리형 정책 분석"""
    high_risk_policies = []
    medium_risk_policies = []

    try:
        paginator = iam.get_paginator('list_policies')
        for page in paginator.paginate(Scope='Local'):
            for policy in page['Policies']:
                risk_level, risk_factor = assess_policy_risk(iam, policy)
                if risk_level == 'high':
                    high_risk_policies.append((policy, risk_factor))
                elif risk_level == 'medium':
                    medium_risk_policies.append((policy, risk_factor))
    except Exception as e:
        return [{"error": str(e)}], []

    return high_risk_policies, medium_risk_policies


def is_high_risk_inline_policy(policy_doc):
    """인라인 정책 고위험 여부 확인"""
    for statement in policy_doc.get('Statement', []):
        if statement.get('Effect') == 'Allow':
            actions = statement.get('Action', [])
            resources = statement.get('Resource', [])
            if is_wildcard_permission(actions, resources):
                return True
    return False


def analyze_inline_policies(iam):
    """인라인 정책 분석"""
    high_risk_policies = []

    try:
        # 사용자 인라인 정책
        users = iam.list_users()['Users']
        for user in users:
            try:
                policy_names = iam.list_user_policies(UserName=user['UserName'])['PolicyNames']
                for policy_name in policy_names:
                    policy_doc = iam.get_user_policy(
                        UserName=user['UserName'], PolicyName=policy_name
                    )['PolicyDocument']

                    if is_high_risk_inline_policy(policy_doc):
                        high_risk_policies.append((
                            policy_name,
                            f"User: {user['UserName']}",
                            "모든 리소스에 대한 모든 작업 허용"
                        ))
            except Exception:
                continue

        # 그룹 인라인 정책
        groups = iam.list_groups()['Groups']
        for group in groups:
            try:
                policy_names = iam.list_group_policies(GroupName=group['GroupName'])['PolicyNames']
                for policy_name in policy_names:
                    policy_doc = iam.get_group_policy(
                        GroupName=group['GroupName'], PolicyName=policy_name
                    )['PolicyDocument']

                    if is_high_risk_inline_policy(policy_doc):
                        high_risk_policies.append((
                            policy_name,
                            f"Group: {group['GroupName']}",
                            "모든 리소스에 대한 모든 작업 허용"
                        ))
            except Exception:
                continue

        # 역할 인라인 정책
        roles = iam.list_roles()['Roles']
        for role in roles:
            try:
                policy_names = iam.list_role_policies(RoleName=role['RoleName'])['PolicyNames']
                for policy_name in policy_names:
                    policy_doc = iam.get_role_policy(
                        RoleName=role['RoleName'], PolicyName=policy_name
                    )['PolicyDocument']

                    if is_high_risk_inline_policy(policy_doc):
                        high_risk_policies.append((
                            policy_name,
                            f"Role: {role['RoleName']}",
                            "모든 리소스에 대한 모든 작업 허용"
                        ))
            except Exception:
                continue

    except Exception as e:
        return [{"error": str(e)}]

    return high_risk_policies


def analyze_permission_boundaries(iam):
    """권한 경계 분석"""
    users_with_boundaries = []
    roles_with_boundaries = []

    try:
        # 사용자 권한 경계
        users = iam.list_users()['Users']
        for user in users:
            try:
                response = iam.get_user(UserName=user['UserName'])
                if 'PermissionsBoundary' in response['User']:
                    users_with_boundaries.append((
                        user['UserName'],
                        response['User']['PermissionsBoundary']['PermissionsBoundaryArn']
                    ))
            except Exception:
                continue

        # 역할 권한 경계
        roles = iam.list_roles()['Roles']
        for role in roles:
            try:
                if 'PermissionsBoundary' in role:
                    roles_with_boundaries.append((
                        role['RoleName'],
                        role['PermissionsBoundary']['PermissionsBoundaryArn']
                    ))
            except Exception:
                continue

    except Exception as e:
        return [("error", str(e))], []

    return users_with_boundaries, roles_with_boundaries


def analyze_service_control_policies(organizations):
    """서비스 제어 정책 분석"""
    try:
        # Organizations 계정 확인
        try:
            organizations.describe_organization()
        except ClientError:
            return [{"message": "이 계정은 AWS Organizations의 관리 계정이 아니거나 조직에 속해있지 않습니다."}]

        policies = organizations.list_policies(Filter='SERVICE_CONTROL_POLICY')['Policies']

        if not policies:
            return [{"message": "서비스 제어 정책이 없습니다."}]

        scp_analysis = []
        for policy in policies:
            policy_detail = organizations.describe_policy(PolicyId=policy['Id'])['Policy']
            policy_content = json.loads(policy_detail['Content'])
            targets = organizations.list_targets_for_policy(PolicyId=policy['Id'])['Targets']
            target_names = [target['Name'] for target in targets]

            # 위험도 평가
            risk_level = "낮음"
            for statement in policy_content.get('Statement', []):
                if statement.get('Effect') == 'Deny' and statement.get('Resource') == '*':
                    risk_level = "높음"
                    break

            scp_analysis.append({
                'name': policy['Name'],
                'id': policy['Id'],
                'targets': ', '.join(target_names) if target_names else 'None',
                'risk_level': risk_level
            })

        return scp_analysis

    except Exception as e:
        return [{"error": str(e)}]


def generate_report(session, access_key, secret_key, region):
    """전체 보고서 생성"""
    iam = session.client('iam')
    organizations = session.client('organizations')

    report = "# AWS IAM 정책 위험도 분석 보고서\n\n"
    report += f"생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # 계정 정보
    account_info = get_account_info(session)
    report += "## 계정 정보\n\n"
    if "error" in account_info:
        report += f"계정 정보 조회 실패: {account_info['error']}\n\n"
    else:
        report += f"- 계정 ID: {account_info['Account']}\n"
        report += f"- ARN: {account_info['Arn']}\n"
        report += f"- Access key: {access_key}\n"
        report += f"- Secret Key: {secret_key}\n"
        report += f"- Region: {region}\n\n"

    # 1. AWS 관리형 정책
    report += "## 1. AWS 관리형 정책\n\n"
    aws_managed_policies = analyze_aws_managed_policies(iam)

    if any("error" in policy for policy in aws_managed_policies if isinstance(policy, dict)):
        report += f"AWS 관리형 정책 조회 실패: {aws_managed_policies[0]['error']}\n\n"
    elif aws_managed_policies:
        report += "### 고위험 AWS 관리형 정책\n\n"
        report += "| 정책 이름 | ARN | 위험도 |\n"
        report += "|---------|-----|-------|\n"
        for policy in aws_managed_policies:
            report += f"| {policy['PolicyName']} | {policy['Arn']} | 높음 |\n"
        report += "\n"
    else:
        report += "고위험 AWS 관리형 정책이 사용되지 않습니다.\n\n"

    # 2. 고객 관리형 정책
    report += "## 2. 고객 관리형 정책\n\n"
    high_risk_policies, medium_risk_policies = analyze_customer_managed_policies(iam)

    if any("error" in policy for policy in high_risk_policies if isinstance(policy, dict)):
        report += f"고객 관리형 정책 조회 실패: {high_risk_policies[0]['error']}\n\n"
    else:
        if high_risk_policies:
            report += "### 고위험 고객 관리형 정책\n\n"
            report += "| 정책 이름 | ARN | 위험 요소 | 위험도 |\n"
            report += "|---------|-----|---------|-------|\n"
            for policy, risk_factor in high_risk_policies:
                report += f"| {policy['PolicyName']} | {policy['Arn']} | {risk_factor} | 높음 |\n"
            report += "\n"

        if medium_risk_policies:
            report += "### 중위험 고객 관리형 정책\n\n"
            report += "| 정책 이름 | ARN | 위험 요소 | 위험도 |\n"
            report += "|---------|-----|---------|-------|\n"
            for policy, risk_factor in medium_risk_policies:
                report += f"| {policy['PolicyName']} | {policy['Arn']} | {risk_factor} | 중간 |\n"
            report += "\n"

        if not high_risk_policies and not medium_risk_policies:
            report += "위험한 고객 관리형 정책이 발견되지 않았습니다.\n\n"

    # 3. 인라인 정책
    report += "## 3. 인라인 정책\n\n"
    inline_policies = analyze_inline_policies(iam)

    if any("error" in policy for policy in inline_policies if isinstance(policy, dict)):
        report += f"인라인 정책 조회 실패: {inline_policies[0]['error']}\n\n"
    elif inline_policies:
        report += "### 고위험 인라인 정책\n\n"
        report += "| 정책 이름 | 연결 대상 | 위험 요소 | 위험도 |\n"
        report += "|---------|---------|---------|-------|\n"
        for policy_name, attached_to, risk_factor in inline_policies:
            report += f"| {policy_name} | {attached_to} | {risk_factor} | 높음 |\n"
        report += "\n"
    else:
        report += "고위험 인라인 정책이 발견되지 않았습니다.\n\n"

    # 4. 권한 경계
    report += "## 4. 권한 경계 (Permission Boundaries)\n\n"
    users_boundaries, roles_boundaries = analyze_permission_boundaries(iam)

    if any(user[0] == "error" for user in users_boundaries):
        report += f"권한 경계 조회 실패: {users_boundaries[0][1]}\n\n"
    elif users_boundaries or roles_boundaries:
        report += "권한 경계가 설정된 엔터티:\n\n"

        if users_boundaries:
            report += "### 사용자\n\n"
            report += "| 사용자 이름 | 권한 경계 ARN |\n"
            report += "|-----------|-------------|\n"
            for user_name, boundary_arn in users_boundaries:
                report += f"| {user_name} | {boundary_arn} |\n"
            report += "\n"

        if roles_boundaries:
            report += "### 역할\n\n"
            report += "| 역할 이름 | 권한 경계 ARN |\n"
            report += "|-----------|-------------|\n"
            for role_name, boundary_arn in roles_boundaries:
                report += f"| {role_name} | {boundary_arn} |\n"
            report += "\n"
    else:
        report += "권한 경계가 설정된 엔터티가 없습니다.\n\n"

    # 5. 서비스 제어 정책
    report += "## 5. 서비스 제어 정책 (SCPs)\n\n"
    scp_analysis = analyze_service_control_policies(organizations)

    if any("error" in item for item in scp_analysis if isinstance(item, dict)):
        report += f"서비스 제어 정책 조회 실패: {scp_analysis[0]['error']}\n\n"
    elif any("message" in item for item in scp_analysis if isinstance(item, dict)):
        report += f"{scp_analysis[0]['message']}\n\n"
    else:
        report += "| 정책 이름 | 정책 ID | 대상 | 위험도 |\n"
        report += "|---------|---------|-----|-------|\n"
        for policy in scp_analysis:
            report += f"| {policy['name']} | {policy['id']} | {policy['targets']} | {policy['risk_level']} |\n"
        report += "\n"

    # 전반적인 보안 평가
    report += "## 전반적인 보안 평가\n\n"

    security_issues = []
    if aws_managed_policies and not any("error" in policy for policy in aws_managed_policies if isinstance(policy, dict)):
        security_issues.append("고위험 AWS 관리형 정책이 사용 중입니다.")
    if high_risk_policies and not any("error" in policy for policy in high_risk_policies if isinstance(policy, dict)):
        security_issues.append("고위험 고객 관리형 정책이 발견되었습니다.")
    if inline_policies and not any("error" in policy for policy in inline_policies if isinstance(policy, dict)):
        security_issues.append("고위험 인라인 정책이 발견되었습니다.")

    if security_issues:
        report += "### 발견된 보안 문제:\n\n"
        for issue in security_issues:
            report += f"- {issue}\n"
        report += "\n### 권장 조치:\n\n"
        report += "- 모든 리소스에 대한 '*' 액세스 권한은 최소 권한 원칙에 위배됩니다. 필요한 권한만 허용하도록 정책을 검토하세요.\n"
        report += "- 고위험 정책은 특정 리소스와 작업으로 범위를 제한하세요.\n"
        report += "- 인라인 정책보다 관리형 정책을 사용하여 정책 관리를 중앙화하세요.\n"
    else:
        report += "주요 보안 문제가 발견되지 않았습니다. 다음 모범 사례를 계속 유지하세요:\n\n"
        report += "- 정기적인 IAM 정책 검토\n"
        report += "- 최소 권한 원칙 적용\n"
        report += "- AWS 액세스 분석기를 사용한 외부 액세스 모니터링\n"

    return report


def save_report(report, filename=None):
    """보고서를 파일로 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f'aws_policy_risk_report_{timestamp}.md'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"보고서가 생성되었습니다: {filename}")


def main():
    parser = argparse.ArgumentParser(description='AWS IAM 정책 위험도 분석')
    parser.add_argument('access_key', help='AWS access key')
    parser.add_argument('secret_key', help='AWS secret key')
    parser.add_argument('region', help='AWS region')
    parser.add_argument('-o', '--output', help='출력 파일명')

    args = parser.parse_args()

    # AWS 세션 생성
    session = create_aws_session(args.access_key, args.secret_key, args.region)

    # 보고서 생성
    report = generate_report(session, args.access_key, args.secret_key, args.region)

    # 보고서 저장
    save_report(report, args.output)


if __name__ == "__main__":
    main()