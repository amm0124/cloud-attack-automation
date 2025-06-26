# python lambda_download.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region ap-northeast-2 --function-name my-function --output-file result.zip

import boto3
import argparse
import zipfile
import tempfile
import os
from datetime import datetime

def download_lambda_function(access_key, secret_key, region, function_name, output_file):
    """Lambda 함수를 다운로드하고 ZIP으로 패키징"""
    try:
        # boto3 클라이언트 생성
        lambda_client = boto3.client(
            'lambda',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # 함수 정보 확인
        function_info = lambda_client.get_function(FunctionName=function_name)
        function_arn = function_info['Configuration']['FunctionArn']
        runtime = function_info['Configuration']['Runtime']
        code_sha256 = function_info['Configuration']['CodeSha256']

        # 함수 코드 다운로드
        code_response = lambda_client.get_function(FunctionName=function_name)
        code_url = code_response['Code']['Location']

        # 코드 다운로드
        import requests
        response = requests.get(code_url)

        # 마크다운 보고서 생성
        report = f"""# Lambda 함수 다운로드 결과

## 함수 정보
- **함수 이름**: {function_name}
- **함수 ARN**: {function_arn}
- **런타임**: {runtime}
- **코드 SHA256**: {code_sha256}
- **리전**: {region}

## 다운로드 정보
- **다운로드 시간**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **포함 파일**: 
  - `{function_name}_report.md` (이 보고서)
  - `{function_name}_code.zip` (Lambda 함수 코드)

## 결과
Lambda 함수가 성공적으로 다운로드되었습니다.
"""

        # 출력 디렉토리 생성
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # ZIP 파일에 마크다운과 Lambda 코드 저장
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 마크다운 보고서 추가
            zipf.writestr(f"{function_name}_report.md", report)
            # Lambda 함수 코드 추가
            zipf.writestr(f"{function_name}_code.zip", response.content)

        return True, f"Lambda 함수 다운로드 완료: {output_file}"

    except Exception as e:
        return False, f"Lambda 함수 다운로드 실패: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Lambda 함수 다운로드')
    parser.add_argument('--access-key', required=True, help='AWS Access Key')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--function-name', required=True, help='Lambda Function Name')
    parser.add_argument('--output-file', default='lambda_download.zip', help='Output ZIP file (default: lambda_download.zip)')

    args = parser.parse_args()

    success, message = download_lambda_function(
        args.access_key,
        args.secret_key,
        args.region,
        args.function_name,
        args.output_file
    )

    print(message)

if __name__ == "__main__":
    main()