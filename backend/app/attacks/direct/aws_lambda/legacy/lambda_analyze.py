import boto3
import json
import base64
import zipfile
import io
import os


def get_lambda_code_info(access_key, secret_key, region='us-east-1'):
    """
    Lambda 함수들의 코드 정보를 조회하는 함수
    """
    # AWS 클라이언트 생성
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    try:
        # 모든 Lambda 함수 목록 조회
        response = lambda_client.list_functions()
        functions = response['Functions']

        print(f"총 {len(functions)}개의 Lambda 함수를 찾았습니다.\n")

        for func in functions:
            function_name = func['FunctionName']
            print(f"=== {function_name} ===")
            print(f"Runtime: {func.get('Runtime', 'N/A')}")
            print(f"Handler: {func.get('Handler', 'N/A')}")
            print(f"Code Size: {func.get('CodeSize', 0)} bytes")
            print(f"Last Modified: {func.get('LastModified', 'N/A')}")

            # 함수의 상세 코드 정보 조회
            try:
                code_response = lambda_client.get_function(FunctionName=function_name)
                code_info = code_response['Code']

                print(f"Repository Type: {code_info.get('RepositoryType', 'N/A')}")
                print(f"Location: {code_info.get('Location', 'N/A')}")

                # 환경 변수 정보
                config = code_response['Configuration']
                env_vars = config.get('Environment', {}).get('Variables', {})
                if env_vars:
                    print("Environment Variables:")
                    for key, value in env_vars.items():
                        print(f"  {key}: {value}")

                print("-" * 50)

            except Exception as e:
                print(f"코드 정보 조회 실패: {str(e)}")
                print("-" * 50)

    except Exception as e:
        print(f"Lambda 함수 목록 조회 실패: {str(e)}")


def extract_and_show_code(zip_content, function_name):
    """
    ZIP 파일에서 코드를 추출하고 내용을 출력하는 함수
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"\n=== {function_name} 파일 목록 ===")
            for file_name in file_list:
                print(f"- {file_name}")

            print(f"\n=== {function_name} 코드 내용 ===")

            # 주요 코드 파일들 출력 (Python, JavaScript, Java 등)
            code_extensions = ['.py', '.js', '.java', '.go', '.cs', '.rb', '.php']

            for file_name in file_list:
                # 디렉토리가 아닌 파일만 처리
                if not file_name.endswith('/'):
                    file_ext = os.path.splitext(file_name)[1].lower()

                    # 코드 파일이거나 중요한 설정 파일인 경우
                    if (file_ext in code_extensions or
                            file_name in ['requirements.txt', 'package.json', 'Dockerfile', 'template.yaml', 'serverless.yml'] or
                            file_name.endswith('.json') or file_name.endswith('.yaml') or file_name.endswith('.yml')):

                        try:
                            with zip_file.open(file_name) as file:
                                content = file.read()

                                # 텍스트 파일인지 확인
                                try:
                                    text_content = content.decode('utf-8')
                                    print(f"\n--- {file_name} ---")
                                    print(text_content)
                                    print(f"--- {file_name} 끝 ---\n")

                                except UnicodeDecodeError:
                                    # 바이너리 파일인 경우
                                    print(f"\n--- {file_name} (바이너리 파일, {len(content)} bytes) ---")

                        except Exception as e:
                            print(f"{file_name} 읽기 실패: {str(e)}")

    except Exception as e:
        print(f"ZIP 파일 추출 실패: {str(e)}")


def get_specific_lambda_code(access_key, secret_key, function_name, region='us-east-1'):
    """
    특정 Lambda 함수의 코드를 다운로드하고 내용을 표시하는 함수
    """
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    try:
        response = lambda_client.get_function(FunctionName=function_name)

        print(f"=== {function_name} 상세 정보 ===")

        # 함수 설정 정보
        config = response['Configuration']
        print(f"Function ARN: {config['FunctionArn']}")
        print(f"Runtime: {config['Runtime']}")
        print(f"Handler: {config['Handler']}")
        print(f"Code Size: {config['CodeSize']} bytes")
        print(f"Timeout: {config['Timeout']} seconds")
        print(f"Memory Size: {config['MemorySize']} MB")

        # 코드 위치 정보
        code = response['Code']
        print(f"\nCode Location: {code['Location']}")

        # 코드 다운로드 및 내용 표시
        if 'ZipFile' in code:
            zip_content = code['ZipFile']

            # ZIP 파일로 저장
            with open(f"{function_name}_code.zip", "wb") as f:
                f.write(zip_content)
            print(f"코드가 {function_name}_code.zip 파일로 저장되었습니다.")

            # ZIP 내용 추출하고 코드 표시
            extract_and_show_code(zip_content, function_name)
        else:
            print("코드가 ZIP 형태가 아니거나 접근할 수 없습니다.")

    except Exception as e:
        print(f"함수 정보 조회 실패: {str(e)}")


def get_all_lambda_codes(access_key, secret_key, region='us-east-1'):
    """
    모든 Lambda 함수의 코드를 조회하고 내용을 표시하는 함수
    """
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    try:
        # 모든 Lambda 함수 목록 조회
        response = lambda_client.list_functions()
        functions = response['Functions']

        print(f"총 {len(functions)}개의 Lambda 함수를 찾았습니다.\n")

        for i, func in enumerate(functions, 1):
            function_name = func['FunctionName']
            print(f"\n{'=' * 60}")
            print(f"[{i}/{len(functions)}] {function_name}")
            print(f"{'=' * 60}")

            # 각 함수의 코드 조회
            get_specific_lambda_code(access_key, secret_key, function_name, region)

            # 다음 함수로 넘어가기 전 구분선
            print(f"{'=' * 60}\n")

    except Exception as e:
        print(f"Lambda 함수 목록 조회 실패: {str(e)}")


# 사용 예시
if __name__ == "__main__":
    # AWS 자격 증명 입력
    AWS_ACCESS_KEY = ""
    AWS_SECRET_KEY = ""
    AWS_REGION = "ap-northeast-2"  # 원하는 리전으로 변경

    # 사용법 선택
    print("Lambda 코드 조회 옵션:")
    print("1. 모든 Lambda 함수 기본 정보만 조회")
    print("2. 특정 Lambda 함수 코드 내용까지 조회")
    print("3. 모든 Lambda 함수 코드 내용까지 조회 (주의: 시간이 오래 걸릴 수 있음)")

    # 옵션 1: 기본 정보만 조회
    print("\n=== 모든 Lambda 함수 기본 정보 ===")
    get_lambda_code_info(AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION)

    # 옵션 2: 특정 함수 코드 내용까지 조회 (함수명을 실제 이름으로 변경)
    # print("\n=== 특정 함수 코드 내용 조회 ===")
    # get_specific_lambda_code(AWS_ACCESS_KEY, AWS_SECRET_KEY, "your-function-name", AWS_REGION)

    # 옵션 3: 모든 함수 코드 내용까지 조회 (주의: 함수가 많으면 매우 오래 걸림)
    # print("\n=== 모든 함수 코드 내용 조회 ===")
    # get_all_lambda_codes(AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION)