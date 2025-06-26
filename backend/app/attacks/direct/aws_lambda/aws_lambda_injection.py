import boto3
import argparse
import time

def wait_for_function_update(lambda_client, function_name, max_wait=300):
    """함수 업데이트 완료까지 대기"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = lambda_client.get_function(FunctionName=function_name)
            state = response['Configuration']['State']
            if state == 'Active':
                return True
            elif state in ['Failed', 'Inactive']:
                return False
            print(f"함수 상태: {state}, 대기 중...")
            time.sleep(5)
        except Exception as e:
            print(f"상태 확인 중 오류: {e}")
            time.sleep(5)
    return False

def upload_lambda_function(access_key, secret_key, region, function_name, zip_file_path):
    """Lambda 함수에 zip 파일을 업로드하고 결과를 반환"""
    try:
        lambda_client = boto3.client(
            'lambda',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()

        try:
            # 기존 함수 확인 및 상태 대기
            lambda_client.get_function(FunctionName=function_name)

            # 함수가 업데이트 가능한 상태까지 대기
            print("함수 상태 확인 중...")
            if not wait_for_function_update(lambda_client, function_name):
                raise Exception("함수가 업데이트 가능한 상태가 되지 않았습니다.")

            # 기존 함수 코드 업데이트
            print("함수 코드 업데이트 중...")
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )

            # 코드 업데이트 완료 대기
            print("코드 업데이트 완료 대기 중...")
            if not wait_for_function_update(lambda_client, function_name):
                raise Exception("코드 업데이트가 완료되지 않았습니다.")

            action = "업데이트"

        except lambda_client.exceptions.ResourceNotFoundException:
            # 새 함수 생성 (기본 역할 사용)
            print("새 함수 생성 중...")
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.12',
                Role='arn:aws:iam::123456789012:role/service-role/lambda-basic-execution',
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content}
            )
            action = "생성"

        return f"""# Lambda 함수 업로드 결과

## 함수 정보
- **함수 이름**: {function_name}
- **런타임**: python3.12
- **리전**: {region}

## 결과
Lambda 함수가 성공적으로 {action}되었습니다.
- **함수 ARN**: {response['FunctionArn']}
- **코드 크기**: {response['CodeSize']} bytes
- **최종 상태**: {response['State']}
"""

    except Exception as e:
        return f"""# Lambda 함수 업로드 실패

## 오류 정보
- **함수 이름**: {function_name}
- **오류 메시지**: {str(e)}

## 결과
Lambda 함수 업로드에 실패했습니다.
"""

def main():
    parser = argparse.ArgumentParser(description='Lambda 함수 ZIP 업로드')
    parser.add_argument('--access-key', required=True, help='AWS Access Key')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--function-name', required=True, help='Lambda Function Name')
    parser.add_argument('--zip-file', required=True, help='ZIP File Path')
    parser.add_argument('--output-file', default='upload_result.md', help='Output file (default: upload_result.md)')

    args = parser.parse_args()

    result = upload_lambda_function(
        args.access_key,
        args.secret_key,
        args.region,
        args.function_name,
        args.zip_file
    )

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print("Lambda 함수 업로드 완료.")

if __name__ == "__main__":
    main()