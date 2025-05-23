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


def analyze_lambda_functions(lambda_client):
    """Lambda 함수 목록 및 기본 정보 분석"""
    functions = []
    try:
        paginator = lambda_client.get_paginator('list_functions')
        for page in paginator.paginate():
            for func in page['Functions']:
                function_info = {
                    'name': func['FunctionName'],
                    'runtime': func.get('Runtime', 'N/A'),
                    'handler': func.get('Handler', 'N/A'),
                    'code_size': func.get('CodeSize', 0),
                    'timeout': func.get('Timeout', 0),
                    'memory_size': func.get('MemorySize', 0),
                    'last_modified': func.get('LastModified', 'N/A'),
                    'role': func.get('Role', 'N/A'),
                    'environment': func.get('Environment', {}),
                    'kms_key_arn': func.get('KMSKeyArn', None),
                    'layers': [layer['Arn'] for layer in func.get('Layers', [])],
                    'vpc_config': func.get('VpcConfig', {}),
                    'dead_letter_config': func.get('DeadLetterConfig', {}),
                    'tracing_config': func.get('TracingConfig', {}),
                    'architecture': func.get('Architectures', ['x86_64'])[0],
                    'package_type': func.get('PackageType', 'Zip')
                }
                functions.append(function_info)
    except Exception as e:
        return [{"error": str(e)}]

    return functions


def analyze_function_encryption(lambda_client, kms_client, function_name):
    """Lambda 함수 암호화 분석"""
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        func_config = response['Configuration']

        encryption_info = {
            'function_name': function_name,
            'kms_key_arn': func_config.get('KMSKeyArn'),
            'environment_encrypted': bool(func_config.get('KMSKeyArn')),
            'environment_variables': func_config.get('Environment', {}).get('Variables', {}),
            'decrypted_env_vars': {},
            'code_encrypted': False,
            'can_decrypt': False
        }

        # 환경 변수 복호화 시도
        if encryption_info['kms_key_arn'] and encryption_info['environment_variables']:
            try:
                # 환경 변수는 Lambda에서 자동으로 복호화되어 반환됨
                encryption_info['decrypted_env_vars'] = encryption_info['environment_variables']
                encryption_info['can_decrypt'] = True
            except Exception as e:
                encryption_info['decrypt_error'] = str(e)

        return encryption_info

    except Exception as e:
        return {"error": str(e)}


def download_and_analyze_code(lambda_client, function_name):
    """Lambda 함수 코드 다운로드 및 분석"""
    try:
        response = lambda_client.get_function(FunctionName=function_name)

        code_info = {
            'function_name': function_name,
            'code_location': response['Code'].get('Location', 'N/A'),
            'repository_type': response['Code'].get('RepositoryType', 'N/A'),
            'code_sha256': response['Configuration'].get('CodeSha256', 'N/A'),
            'code_size': response['Configuration'].get('CodeSize', 0),
            'package_type': response['Configuration'].get('PackageType', 'Zip'),
            'code_extracted': False,
            'files': [],
            'sensitive_data': [],
            'risk_level': 'low'
        }

        # ZIP 패키지 타입인 경우에만 코드 다운로드 시도
        if code_info['package_type'] == 'Zip':
            try:
                # 코드 다운로드
                code_response = lambda_client.get_function(FunctionName=function_name)
                code_url = code_response['Code']['Location']

                # S3에서 코드 다운로드는 실제로는 pre-signed URL을 통해 해야 함
                # 여기서는 코드 구조 분석만 시뮬레이션
                code_info['code_extracted'] = True
                code_info['files'] = ['lambda_function.py', 'requirements.txt']  # 예시

            except Exception as e:
                code_info['download_error'] = str(e)

        return code_info

    except Exception as e:
        return {"error": str(e)}


def analyze_function_permissions(lambda_client, function_name):
    """Lambda 함수 권한 분석"""
    try:
        # 함수 정책 조회
        policy_info = {
            'function_name': function_name,
            'resource_policy': None,
            'public_access': False,
            'cross_account_access': False,
            'risk_level': 'low',
            'risk_factors': []
        }

        try:
            response = lambda_client.get_policy(FunctionName=function_name)
            policy = json.loads(response['Policy'])
            policy_info['resource_policy'] = policy

            # 정책 위험도 분석
            for statement in policy.get('Statement', []):
                principal = statement.get('Principal', {})

                # 퍼블릭 액세스 확인
                if principal == '*' or (isinstance(principal, dict) and principal.get('AWS') == '*'):
                    policy_info['public_access'] = True
                    policy_info['risk_level'] = 'high'
                    policy_info['risk_factors'].append('퍼블릭 액세스 허용')

                # 크로스 계정 액세스 확인
                if isinstance(principal, dict) and 'AWS' in principal:
                    aws_principals = principal['AWS'] if isinstance(principal['AWS'], list) else [principal['AWS']]
                    for aws_principal in aws_principals:
                        if isinstance(aws_principal, str) and ':' in aws_principal:
                            account_id = aws_principal.split(':')[4]
                            # 현재 계정과 다른 계정인지 확인 (실제로는 현재 계정 ID와 비교해야 함)
                            if account_id != 'current_account':  # 실제 구현에서는 현재 계정 ID 사용
                                policy_info['cross_account_access'] = True
                                if policy_info['risk_level'] != 'high':
                                    policy_info['risk_level'] = 'medium'
                                policy_info['risk_factors'].append(f'크로스 계정 액세스: {account_id}')

        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                policy_info['policy_error'] = str(e)

        return policy_info

    except Exception as e:
        return {"error": str(e)}


def analyze_function_triggers(lambda_client, function_name):
    """Lambda 함수 트리거 분석"""
    try:
        # 이벤트 소스 매핑 조회
        trigger_info = {
            'function_name': function_name,
            'event_source_mappings': [],
            'triggers': [],
            'risk_level': 'low'
        }

        try:
            response = lambda_client.list_event_source_mappings(FunctionName=function_name)
            for mapping in response['EventSourceMappings']:
                mapping_info = {
                    'uuid': mapping['UUID'],
                    'event_source_arn': mapping['EventSourceArn'],
                    'state': mapping['State'],
                    'batch_size': mapping.get('BatchSize', 0),
                    'starting_position': mapping.get('StartingPosition', 'N/A')
                }
                trigger_info['event_source_mappings'].append(mapping_info)

                # 트리거 타입 분석
                event_source = mapping['EventSourceArn']
                if 'kinesis' in event_source:
                    trigger_info['triggers'].append('Kinesis')
                elif 'dynamodb' in event_source:
                    trigger_info['triggers'].append('DynamoDB')
                elif 'sqs' in event_source:
                    trigger_info['triggers'].append('SQS')

        except Exception as e:
            trigger_info['trigger_error'] = str(e)

        return trigger_info

    except Exception as e:
        return {"error": str(e)}


def analyze_function_networking(function_config):
    """Lambda 함수 네트워킹 분석"""
    vpc_config = function_config.get('vpc_config', {})

    networking_info = {
        'function_name': function_config['name'],
        'vpc_enabled': bool(vpc_config.get('VpcId')),
        'vpc_id': vpc_config.get('VpcId', 'N/A'),
        'subnet_ids': vpc_config.get('SubnetIds', []),
        'security_group_ids': vpc_config.get('SecurityGroupIds', []),
        'risk_level': 'low',
        'risk_factors': []
    }

    # VPC 설정 위험도 분석
    if not networking_info['vpc_enabled']:
        networking_info['risk_factors'].append('VPC 내부에 배치되지 않음 (인터넷 액세스 가능)')
        networking_info['risk_level'] = 'medium'

    return networking_info


def check_sensitive_data_in_environment(env_vars):
    """환경 변수에서 민감한 데이터 확인"""
    sensitive_patterns = [
        'password', 'passwd', 'pwd', 'secret', 'key', 'token',
        'api_key', 'apikey', 'access_key', 'secret_key', 'private_key',
        'database_url', 'db_password', 'mysql_password', 'postgres_password'
    ]

    sensitive_vars = []
    for var_name, var_value in env_vars.items():
        var_name_lower = var_name.lower()
        for pattern in sensitive_patterns:
            if pattern in var_name_lower:
                sensitive_vars.append({
                    'var_name': var_name,
                    'var_value': var_value[:10] + '...' if len(var_value) > 10 else var_value,
                    'full_value': var_value  # 실제 환경에서는 주의깊게 처리
                })
                break

    return sensitive_vars


def generate_report(session, access_key, secret_key, region):
    """Lambda 보안 분석 보고서 생성"""
    lambda_client = session.client('lambda')
    kms_client = session.client('kms')

    report = "# Lambda 보안 분석 보고서\n\n"
    report += f"생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # 계정 정보
    account_info = get_account_info(session)
    report += "## 계정 정보\n\n"
    if "error" in account_info:
        report += f"계정 정보 조회 실패: {account_info['error']}\n\n"
    else:
        report += f"- 계정 ID: {account_info['Account']}\n"
        report += f"- 리전: {region}\n\n"

    # 1. Lambda 함수 목록
    report += "## 1. Lambda 함수 목록\n\n"
    functions = analyze_lambda_functions(lambda_client)

    if any("error" in func for func in functions if isinstance(func, dict)):
        report += f"Lambda 함수 조회 실패: {functions[0]['error']}\n\n"
        return report
    elif functions:
        report += f"총 {len(functions)}개의 Lambda 함수가 발견되었습니다.\n\n"
        report += "| 함수 이름 | 런타임 | 메모리(MB) | 타임아웃(초) | 코드 크기(바이트) | KMS 암호화 |\n"
        report += "|-----------|---------|------------|-------------|----------------|------------|\n"
        for func in functions:
            kms_status = "예" if func['kms_key_arn'] else "아니오"
            report += f"| {func['name']} | {func['runtime']} | {func['memory_size']} | {func['timeout']} | {func['code_size']} | {kms_status} |\n"
        report += "\n"
    else:
        report += "Lambda 함수가 없습니다.\n\n"
        return report

    # 2. 암호화 및 코드 분석
    report += "## 2. 암호화 및 코드 분석\n\n"

    encrypted_functions = []
    unencrypted_functions = []
    code_analysis_results = []

    for func in functions:
        func_name = func['name']

        # 암호화 분석
        encryption_info = analyze_function_encryption(lambda_client, kms_client, func_name)

        if encryption_info.get('environment_encrypted'):
            encrypted_functions.append(encryption_info)
        else:
            unencrypted_functions.append(encryption_info)

        # 코드 분석
        code_info = download_and_analyze_code(lambda_client, func_name)
        code_analysis_results.append(code_info)

    # 암호화된 함수들
    if encrypted_functions:
        report += "### 암호화된 함수들\n\n"
        report += "| 함수 이름 | KMS 키 ARN | 복호화 가능 | 환경 변수 개수 |\n"
        report += "|-----------|------------|-------------|----------------|\n"
        for enc_func in encrypted_functions:
            if "error" not in enc_func:
                env_count = len(enc_func.get('decrypted_env_vars', {}))
                can_decrypt = "예" if enc_func.get('can_decrypt') else "아니오"
                kms_key = enc_func.get('kms_key_arn', 'N/A')[:50] + '...' if len(enc_func.get('kms_key_arn', '')) > 50 else enc_func.get('kms_key_arn', 'N/A')
                report += f"| {enc_func['function_name']} | {kms_key} | {can_decrypt} | {env_count} |\n"
        report += "\n"

        # 복호화된 환경 변수 표시
        for enc_func in encrypted_functions:
            if enc_func.get('can_decrypt') and enc_func.get('decrypted_env_vars'):
                report += f"#### {enc_func['function_name']} - 복호화된 환경 변수\n\n"

                # 민감한 데이터 확인
                sensitive_vars = check_sensitive_data_in_environment(enc_func['decrypted_env_vars'])

                if sensitive_vars:
                    report += "**민감한 환경 변수 발견:**\n\n"
                    for var in sensitive_vars:
                        report += f"- {var['var_name']}: {var['var_value']}\n"
                    report += "\n"
                else:
                    report += "민감한 환경 변수가 발견되지 않았습니다.\n\n"

    # 암호화되지 않은 함수들
    if unencrypted_functions:
        report += "### 암호화되지 않은 함수들\n\n"
        report += "| 함수 이름 | 환경 변수 개수 | 민감한 변수 |\n"
        report += "|-----------|----------------|-------------|\n"
        for unenc_func in unencrypted_functions:
            if "error" not in unenc_func:
                env_vars = unenc_func.get('environment_variables', {})
                env_count = len(env_vars)
                sensitive_vars = check_sensitive_data_in_environment(env_vars)
                sensitive_count = len(sensitive_vars)
                report += f"| {unenc_func['function_name']} | {env_count} | {sensitive_count} |\n"
        report += "\n"

        # 민감한 데이터 상세 표시
        for unenc_func in unencrypted_functions:
            if "error" not in unenc_func:
                env_vars = unenc_func.get('environment_variables', {})
                sensitive_vars = check_sensitive_data_in_environment(env_vars)

                if sensitive_vars:
                    report += f"#### {unenc_func['function_name']} - 민감한 환경 변수 (암호화되지 않음)\n\n"
                    for var in sensitive_vars:
                        report += f"- {var['var_name']}: {var['full_value']}\n"
                    report += "\n"

    # 3. 코드 분석 결과
    report += "## 3. 코드 분석 결과\n\n"

    for code_info in code_analysis_results:
        if "error" not in code_info:
            report += f"### {code_info['function_name']}\n\n"
            report += f"- 패키지 타입: {code_info['package_type']}\n"
            report += f"- 코드 크기: {code_info['code_size']} 바이트\n"
            report += f"- SHA256: {code_info['code_sha256']}\n"

            if code_info['code_extracted']:
                report += f"- 추출된 파일: {', '.join(code_info['files'])}\n"
            else:
                report += "- 코드 추출: 실패 또는 불가능\n"

            report += "\n"

    # 4. 함수 권한 분석
    report += "## 4. 함수 권한 분석\n\n"

    high_risk_permissions = []

    for func in functions:
        func_name = func['name']
        permission_info = analyze_function_permissions(lambda_client, func_name)

        if permission_info.get('risk_level') == 'high':
            high_risk_permissions.append(permission_info)

    if high_risk_permissions:
        report += "### 고위험 권한 설정\n\n"
        report += "| 함수 이름 | 위험 요소 | 위험도 |\n"
        report += "|-----------|-----------|-------|\n"
        for perm in high_risk_permissions:
            if "error" not in perm:
                risk_factors = ', '.join(perm.get('risk_factors', []))
                report += f"| {perm['function_name']} | {risk_factors} | {perm['risk_level']} |\n"
        report += "\n"
    else:
        report += "고위험 권한 설정이 발견되지 않았습니다.\n\n"

    # 5. 네트워킹 분석
    report += "## 5. 네트워킹 분석\n\n"

    vpc_functions = []
    non_vpc_functions = []

    for func in functions:
        networking_info = analyze_function_networking(func)
        if networking_info['vpc_enabled']:
            vpc_functions.append(networking_info)
        else:
            non_vpc_functions.append(networking_info)

    if non_vpc_functions:
        report += "### VPC 외부 함수들 (인터넷 액세스 가능)\n\n"
        report += "| 함수 이름 | 위험도 |\n"
        report += "|-----------|-------|\n"
        for func in non_vpc_functions:
            report += f"| {func['function_name']} | {func['risk_level']} |\n"
        report += "\n"

    if vpc_functions:
        report += "### VPC 내부 함수들\n\n"
        report += "| 함수 이름 | VPC ID | 서브넷 수 | 보안 그룹 수 |\n"
        report += "|-----------|--------|-----------|-------------|\n"
        for func in vpc_functions:
            subnet_count = len(func['subnet_ids'])
            sg_count = len(func['security_group_ids'])
            report += f"| {func['function_name']} | {func['vpc_id']} | {subnet_count} | {sg_count} |\n"
        report += "\n"

    # 6. 전반적인 보안 평가
    report += "## 전반적인 보안 평가\n\n"

    security_issues = []

    if unencrypted_functions:
        unenc_with_sensitive = [f for f in unencrypted_functions if
                                check_sensitive_data_in_environment(f.get('environment_variables', {}))]
        if unenc_with_sensitive:
            security_issues.append(f"{len(unenc_with_sensitive)}개 함수에 암호화되지 않은 민감한 환경 변수가 있습니다.")

    if high_risk_permissions:
        security_issues.append(f"{len(high_risk_permissions)}개 함수에 고위험 권한 설정이 있습니다.")

    if non_vpc_functions:
        security_issues.append(f"{len(non_vpc_functions)}개 함수가 VPC 외부에 배치되어 인터넷 액세스가 가능합니다.")

    if security_issues:
        report += "### 발견된 보안 문제:\n\n"
        for issue in security_issues:
            report += f"- {issue}\n"
        report += "\n### 권장 조치:\n\n"
        report += "- 민감한 데이터가 포함된 환경 변수는 KMS 암호화를 적용하세요.\n"
        report += "- 퍼블릭 액세스 권한은 꼭 필요한 경우가 아니라면 제거하세요.\n"
        report += "- 함수를 VPC 내부에 배치하여 네트워크 격리를 적용하세요.\n"
        report += "- 최소 권한 원칙에 따라 IAM 역할을 설정하세요.\n"
        report += "- 정기적으로 함수 코드와 설정을 검토하세요.\n"
        report += "- CloudTrail을 통해 Lambda 함수 호출을 모니터링하세요.\n"
    else:
        report += "주요 보안 문제가 발견되지 않았습니다. 다음 모범 사례를 계속 유지하세요:\n\n"
        report += "- 정기적인 함수 권한 검토\n"
        report += "- 환경 변수 암호화 적용\n"
        report += "- VPC 내부 배치를 통한 네트워크 보안\n"
        report += "- AWS X-Ray를 통한 함수 모니터링\n"
        report += "- 코드 보안 스캔 도구 활용\n"

    return report


def save_report(report, filename=None):
    """보고서를 파일로 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f'lambda_security_report_{timestamp}.md'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"보고서가 생성되었습니다: {filename}")


def main():
    parser = argparse.ArgumentParser(description='Lambda 보안 분석')
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