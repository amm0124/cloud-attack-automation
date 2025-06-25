# python lambda_disable.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region ap-northeast-2 --function-name my-function

import boto3
import argparse

def disable_lambda_function(access_key, secret_key, region, function_name):
    """Lambda 함수를 비활성화하고 결과를 반환"""
    try:
        # boto3 클라이언트 생성
        lambda_client = boto3.client(
            'lambda',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # 현재 함수 정보 확인
        function_info = lambda_client.get_function(FunctionName=function_name)
        current_state = function_info['Configuration']['State']

        # Reserved Concurrency를 0으로 설정하여 비활성화
        lambda_client.put_reserved_concurrency_settings(
            FunctionName=function_name,
            ReservedConcurrencyLimit=0
        )

        return f"""# Lambda 함수 비활성화 결과

## 함수 정보
- **함수 이름**: {function_name}
- **리전**: {region}
- **이전 상태**: {current_state}

## 변경 사항
- **Reserved Concurrency**: 0 (비활성화)

## 결과
Lambda 함수가 성공적으로 비활성화되었습니다.
"""

    except Exception as e:
        return f"""# Lambda 함수 비활성화 실패

## 오류 정보
- **함수 이름**: {function_name}
- **리전**: {region}
- **오류 메시지**: {str(e)}

## 결과
Lambda 함수 비활성화에 실패했습니다.
"""

def main():
    parser = argparse.ArgumentParser(description='Lambda 함수 비활성화')
    parser.add_argument('--access-key', required=True, help='AWS Access Key')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--function-name', required=True, help='Lambda Function Name')

    args = parser.parse_args()

    result = disable_lambda_function(
        args.access_key,
        args.secret_key,
        args.region,
        args.function_name
    )

    print(result)

if __name__ == "__main__":
    main()