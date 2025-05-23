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


def analyze_s3_buckets(s3):
    """s3 버킷 기본 정보 분석"""
    buckets = []
    try:
        response = s3.list_buckets()
        for bucket in response['Buckets']:
            bucket_info = {
                'name': bucket['Name'],
                'creation_date': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S'),
                'region': get_bucket_region(s3, bucket['Name']),
                'risk_level': 'low'
            }
            buckets.append(bucket_info)
    except Exception as e:
        return [{"error": str(e)}]

    return buckets


def get_bucket_region(s3, bucket_name):
    """버킷의 리전 정보 조회"""
    try:
        response = s3.get_bucket_location(Bucket=bucket_name)
        region = response['LocationConstraint']
        return region if region else 'us-east-1'
    except Exception:
        return 'unknown'


def analyze_bucket_policies(s3, bucket_names):
    """버킷 정책 분석"""
    bucket_policies = []
    high_risk_policies = []

    for bucket_name in bucket_names:
        try:
            response = s3.get_bucket_policy(Bucket=bucket_name)
            policy = json.loads(response['Policy'])

            policy_info = {
                'bucket': bucket_name,
                'policy': policy,
                'risk_level': 'low',
                'risk_factors': []
            }

            # 정책 위험도 평가
            risk_level, risk_factors = assess_bucket_policy_risk(policy)
            policy_info['risk_level'] = risk_level
            policy_info['risk_factors'] = risk_factors

            bucket_policies.append(policy_info)

            if risk_level == 'high':
                high_risk_policies.append(policy_info)

        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchBucketPolicy':
                bucket_policies.append({
                    'bucket': bucket_name,
                    'error': str(e),
                    'risk_level': 'unknown'
                })

    return bucket_policies, high_risk_policies


def assess_bucket_policy_risk(policy):
    """버킷 정책 위험도 평가"""
    risk_factors = []
    risk_level = 'low'

    for statement in policy.get('Statement', []):
        effect = statement.get('Effect', '')
        principal = statement.get('Principal', {})
        action = statement.get('Action', [])
        resource = statement.get('Resource', [])

        # Principal이 *인 경우 (퍼블릭 액세스)
        if principal == '*' or (isinstance(principal, dict) and principal.get('AWS') == '*'):
            if effect == 'Allow':
                risk_factors.append('퍼블릭 읽기/쓰기 허용')
                risk_level = 'high'

        # 모든 액션 허용
        if action == '*' or (isinstance(action, list) and '*' in action):
            risk_factors.append('모든 s3 액션 허용')
            if risk_level != 'high':
                risk_level = 'medium'

        # 위험한 액션들
        dangerous_actions = ['s3:DeleteBucket', 's3:DeleteObject', 's3:PutBucketPolicy']
        if isinstance(action, list):
            for act in action:
                if any(dangerous in act for dangerous in dangerous_actions):
                    risk_factors.append(f'위험한 액션 허용: {act}')
                    if risk_level != 'high':
                        risk_level = 'medium'

    return risk_level, risk_factors


def analyze_bucket_acls(s3, bucket_names):
    """버킷 ACL 분석"""
    bucket_acls = []
    public_acl_buckets = []

    for bucket_name in bucket_names:
        try:
            response = s3.get_bucket_acl(Bucket=bucket_name)

            acl_info = {
                'bucket': bucket_name,
                'owner': response['Owner']['DisplayName'],
                'grants': [],
                'is_public': False,
                'risk_level': 'low'
            }

            for grant in response['Grants']:
                grantee = grant['Grantee']
                permission = grant['Permission']

                grant_info = {
                    'type': grantee['Type'],
                    'grantee': grantee.get('DisplayName', grantee.get('URI', 'N/A')),
                    'permission': permission
                }

                # 퍼블릭 그룹 확인
                if grantee['Type'] == 'Group':
                    uri = grantee.get('URI', '')
                    if 'AllUsers' in uri or 'AuthenticatedUsers' in uri:
                        acl_info['is_public'] = True
                        acl_info['risk_level'] = 'high'
                        grant_info['grantee'] = 'PUBLIC'

                acl_info['grants'].append(grant_info)

            bucket_acls.append(acl_info)

            if acl_info['is_public']:
                public_acl_buckets.append(acl_info)

        except Exception as e:
            bucket_acls.append({
                'bucket': bucket_name,
                'error': str(e),
                'risk_level': 'unknown'
            })

    return bucket_acls, public_acl_buckets


def analyze_bucket_encryption(s3, bucket_names):
    """버킷 암호화 분석"""
    encryption_status = []
    unencrypted_buckets = []

    for bucket_name in bucket_names:
        try:
            response = s3.get_bucket_encryption(Bucket=bucket_name)
            rules = response['ServerSideEncryptionConfiguration']['Rules']

            encryption_info = {
                'bucket': bucket_name,
                'encrypted': True,
                'encryption_type': [],
                'kms_key': []
            }

            for rule in rules:
                sse = rule['ApplyServerSideEncryptionByDefault']
                encryption_info['encryption_type'].append(sse['SSEAlgorithm'])
                if 'KMSMasterKeyID' in sse:
                    encryption_info['kms_key'].append(sse['KMSMasterKeyID'])

            encryption_status.append(encryption_info)

        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                encryption_info = {
                    'bucket': bucket_name,
                    'encrypted': False,
                    'encryption_type': [],
                    'kms_key': []
                }
                encryption_status.append(encryption_info)
                unencrypted_buckets.append(encryption_info)
            else:
                encryption_status.append({
                    'bucket': bucket_name,
                    'error': str(e),
                    'encrypted': 'unknown'
                })

    return encryption_status, unencrypted_buckets


def analyze_bucket_versioning(s3, bucket_names):
    """버킷 버저닝 분석"""
    versioning_status = []
    unversioned_buckets = []

    for bucket_name in bucket_names:
        try:
            response = s3.get_bucket_versioning(Bucket=bucket_name)
            status = response.get('Status', 'Disabled')
            mfa_delete = response.get('MfaDelete', 'Disabled')

            versioning_info = {
                'bucket': bucket_name,
                'versioning': status,
                'mfa_delete': mfa_delete,
                'enabled': status == 'Enabled'
            }

            versioning_status.append(versioning_info)

            if status != 'Enabled':
                unversioned_buckets.append(versioning_info)

        except Exception as e:
            versioning_status.append({
                'bucket': bucket_name,
                'error': str(e),
                'enabled': 'unknown'
            })

    return versioning_status, unversioned_buckets


def analyze_bucket_logging(s3, bucket_names):
    """버킷 로깅 분석"""
    logging_status = []
    unlogged_buckets = []

    for bucket_name in bucket_names:
        try:
            response = s3.get_bucket_logging(Bucket=bucket_name)

            if 'LoggingEnabled' in response:
                logging_info = {
                    'bucket': bucket_name,
                    'logging_enabled': True,
                    'target_bucket': response['LoggingEnabled']['TargetBucket'],
                    'target_prefix': response['LoggingEnabled'].get('TargetPrefix', '')
                }
            else:
                logging_info = {
                    'bucket': bucket_name,
                    'logging_enabled': False,
                    'target_bucket': 'N/A',
                    'target_prefix': 'N/A'
                }
                unlogged_buckets.append(logging_info)

            logging_status.append(logging_info)

        except Exception as e:
            logging_status.append({
                'bucket': bucket_name,
                'error': str(e),
                'logging_enabled': 'unknown'
            })

    return logging_status, unlogged_buckets


def analyze_public_access_block(s3, bucket_names):
    """퍼블릭 액세스 차단 설정 분석"""
    public_access_status = []
    vulnerable_buckets = []

    for bucket_name in bucket_names:
        try:
            response = s3.get_public_access_block(Bucket=bucket_name)
            config = response['PublicAccessBlockConfiguration']

            access_info = {
                'bucket': bucket_name,
                'block_public_acls': config.get('BlockPublicAcls', False),
                'ignore_public_acls': config.get('IgnorePublicAcls', False),
                'block_public_policy': config.get('BlockPublicPolicy', False),
                'restrict_public_buckets': config.get('RestrictPublicBuckets', False),
                'fully_protected': all([
                    config.get('BlockPublicAcls', False),
                    config.get('IgnorePublicAcls', False),
                    config.get('BlockPublicPolicy', False),
                    config.get('RestrictPublicBuckets', False)
                ])
            }

            public_access_status.append(access_info)

            if not access_info['fully_protected']:
                vulnerable_buckets.append(access_info)

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                access_info = {
                    'bucket': bucket_name,
                    'block_public_acls': False,
                    'ignore_public_acls': False,
                    'block_public_policy': False,
                    'restrict_public_buckets': False,
                    'fully_protected': False
                }
                public_access_status.append(access_info)
                vulnerable_buckets.append(access_info)
            else:
                public_access_status.append({
                    'bucket': bucket_name,
                    'error': str(e),
                    'fully_protected': 'unknown'
                })

    return public_access_status, vulnerable_buckets


def generate_report(session, access_key, secret_key, region):
    """s3 보안 분석 보고서 생성"""
    s3 = session.client('s3')

    report = "# s3 보안 분석 보고서\n\n"
    report += f"생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # 계정 정보
    account_info = get_account_info(session)
    report += "## 계정 정보\n\n"
    if "error" in account_info:
        report += f"계정 정보 조회 실패: {account_info['error']}\n\n"
    else:
        report += f"- 계정 ID: {account_info['Account']}\n"
        report += f"- 분석 리전: {region}\n\n"

    # 1. s3 버킷 목록
    report += "## 1. s3 버킷 목록\n\n"
    buckets = analyze_s3_buckets(s3)

    if any("error" in bucket for bucket in buckets if isinstance(bucket, dict)):
        report += f"s3 버킷 조회 실패: {buckets[0]['error']}\n\n"
        return report
    elif buckets:
        bucket_names = [bucket['name'] for bucket in buckets if 'name' in bucket]
        report += f"총 {len(buckets)}개의 s3 버킷이 발견되었습니다.\n\n"
        report += "| 버킷 이름 | 생성일 | 리전 |\n"
        report += "|----------|--------|------|\n"
        for bucket in buckets:
            if 'name' in bucket:
                report += f"| {bucket['name']} | {bucket['creation_date']} | {bucket['region']} |\n"
        report += "\n"
    else:
        report += "s3 버킷이 없습니다.\n\n"
        return report

    # 2. 버킷 정책 분석
    report += "## 2. 버킷 정책 분석\n\n"
    bucket_policies, high_risk_policies = analyze_bucket_policies(s3, bucket_names)

    if high_risk_policies:
        report += "### 고위험 버킷 정책\n\n"
        report += "| 버킷 이름 | 위험 요소 | 위험도 |\n"
        report += "|----------|---------|-------|\n"
        for policy in high_risk_policies:
            risk_factors_str = ', '.join(policy['risk_factors'])
            report += f"| {policy['bucket']} | {risk_factors_str} | 높음 |\n"
        report += "\n"
    else:
        report += "고위험 버킷 정책이 발견되지 않았습니다.\n\n"

    # 3. 버킷 ACL 분석
    report += "## 3. 버킷 ACL 분석\n\n"
    bucket_acls, public_acl_buckets = analyze_bucket_acls(s3, bucket_names)

    if public_acl_buckets:
        report += "### 퍼블릭 ACL이 설정된 버킷\n\n"
        report += "| 버킷 이름 | 퍼블릭 권한 | 위험도 |\n"
        report += "|----------|-------------|-------|\n"
        for acl in public_acl_buckets:
            public_grants = [grant for grant in acl['grants'] if grant['grantee'] == 'PUBLIC']
            permissions = ', '.join([grant['permission'] for grant in public_grants])
            report += f"| {acl['bucket']} | {permissions} | 높음 |\n"
        report += "\n"
    else:
        report += "퍼블릭 ACL이 설정된 버킷이 없습니다.\n\n"

    # 4. 퍼블릭 액세스 차단 설정
    report += "## 4. 퍼블릭 액세스 차단 설정\n\n"
    public_access_status, vulnerable_buckets = analyze_public_access_block(s3, bucket_names)

    if vulnerable_buckets:
        report += "### 퍼블릭 액세스 차단이 완전하지 않은 버킷\n\n"
        report += "| 버킷 이름 | Block Public ACLs | Ignore Public ACLs | Block Public Policy | Restrict Public Buckets |\n"
        report += "|----------|-------------------|-------------------|-------------------|------------------------|\n"
        for bucket in vulnerable_buckets:
            if 'error' not in bucket:
                report += f"| {bucket['bucket']} | {bucket['block_public_acls']} | {bucket['ignore_public_acls']} | {bucket['block_public_policy']} | {bucket['restrict_public_buckets']} |\n"
        report += "\n"
    else:
        report += "모든 버킷에 퍼블릭 액세스 차단이 완전히 설정되어 있습니다.\n\n"

    # 5. 암호화 설정
    report += "## 5. 암호화 설정\n\n"
    encryption_status, unencrypted_buckets = analyze_bucket_encryption(s3, bucket_names)

    if unencrypted_buckets:
        report += "### 암호화되지 않은 버킷\n\n"
        report += "| 버킷 이름 | 암호화 상태 |\n"
        report += "|----------|-------------|\n"
        for bucket in unencrypted_buckets:
            report += f"| {bucket['bucket']} | 암호화 안됨 |\n"
        report += "\n"
    else:
        report += "모든 버킷이 암호화되어 있습니다.\n\n"

    # 6. 버전 관리
    report += "## 6. 버전 관리\n\n"
    versioning_status, unversioned_buckets = analyze_bucket_versioning(s3, bucket_names)

    if unversioned_buckets:
        report += "### 버전 관리가 비활성화된 버킷\n\n"
        report += "| 버킷 이름 | 버전 관리 상태 | MFA Delete |\n"
        report += "|----------|----------------|------------|\n"
        for bucket in unversioned_buckets:
            if 'error' not in bucket:
                report += f"| {bucket['bucket']} | {bucket['versioning']} | {bucket['mfa_delete']} |\n"
        report += "\n"
    else:
        report += "모든 버킷에 버전 관리가 활성화되어 있습니다.\n\n"

    # 7. 액세스 로깅
    report += "## 7. 액세스 로깅\n\n"
    logging_status, unlogged_buckets = analyze_bucket_logging(s3, bucket_names)

    if unlogged_buckets:
        report += "### 액세스 로깅이 비활성화된 버킷\n\n"
        report += "| 버킷 이름 | 로깅 상태 |\n"
        report += "|----------|----------|\n"
        for bucket in unlogged_buckets:
            if 'error' not in bucket:
                report += f"| {bucket['bucket']} | 비활성화 |\n"
        report += "\n"
    else:
        report += "모든 버킷에 액세스 로깅이 설정되어 있습니다.\n\n"

    # 8. 전반적인 보안 평가
    report += "## 전반적인 보안 평가\n\n"

    security_issues = []
    if high_risk_policies:
        security_issues.append(f"{len(high_risk_policies)}개 버킷에 고위험 정책이 설정되어 있습니다.")
    if public_acl_buckets:
        security_issues.append(f"{len(public_acl_buckets)}개 버킷이 퍼블릭 ACL로 노출되어 있습니다.")
    if vulnerable_buckets:
        security_issues.append(f"{len(vulnerable_buckets)}개 버킷의 퍼블릭 액세스 차단이 불완전합니다.")
    if unencrypted_buckets:
        security_issues.append(f"{len(unencrypted_buckets)}개 버킷이 암호화되지 않았습니다.")
    if unversioned_buckets:
        security_issues.append(f"{len(unversioned_buckets)}개 버킷의 버전 관리가 비활성화되어 있습니다.")
    if unlogged_buckets:
        security_issues.append(f"{len(unlogged_buckets)}개 버킷의 액세스 로깅이 비활성화되어 있습니다.")

    if security_issues:
        report += "### 발견된 보안 문제:\n\n"
        for issue in security_issues:
            report += f"- {issue}\n"
        report += "\n### 권장 조치:\n\n"
        report += "- 모든 버킷에 퍼블릭 액세스 차단 설정을 완전히 활성화하세요.\n"
        report += "- 퍼블릭 읽기/쓰기 권한이 꼭 필요한 경우가 아니라면 제거하세요.\n"
        report += "- 모든 버킷에 기본 암호화를 설정하세요.\n"
        report += "- 중요한 데이터가 있는 버킷은 버전 관리를 활성화하세요.\n"
        report += "- 감사 목적으로 액세스 로깅을 활성화하세요.\n"
        report += "- 정기적으로 버킷 정책과 ACL을 검토하세요.\n"
    else:
        report += "주요 보안 문제가 발견되지 않았습니다. 다음 모범 사례를 계속 유지하세요:\n\n"
        report += "- 정기적인 버킷 정책 및 권한 검토\n"
        report += "- CloudTrail을 통한 s3 API 호출 모니터링\n"
        report += "- 최소 권한 원칙 적용\n"
        report += "- 데이터 분류에 따른 적절한 보안 설정\n"

    return report


def save_report(report, filename=None):
    """보고서를 파일로 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f's3_security_report_{timestamp}.md'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"보고서가 생성되었습니다: {filename}")


def main():
    parser = argparse.ArgumentParser(description='s3 보안 분석')
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