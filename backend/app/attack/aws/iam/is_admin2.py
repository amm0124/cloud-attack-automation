import boto3
from botocore.exceptions import ClientError

def is_admin(access_key, secret_key, region='us-east-1'):
    try:
        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

        # 관리자 권한 테스트용 API 호출: 계정 전체 사용자 리스트 요청
        response = iam.list_users()
        print(f"[✔] list_users 실행 성공. 사용자 수: {len(response['Users'])}")

        # 시도적으로 정책 정보도 확인
        policies = iam.list_policies(Scope='AWS', OnlyAttached=False)
        print(f"[✔] list_policies 실행 성공. 정책 수: {len(policies['Policies'])}")

        print("\n✅ 해당 키는 관리자 권한을 갖고 있을 가능성이 높습니다.")
        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"[✘] 권한 오류: {error_code}")
        print("❌ 해당 키는 관리자 권한이 없거나 제한된 IAM 권한만 가지고 있습니다.")
        return False


def get_iam_permissions(access_key, secret_key, region='us-east-1'):
    try:
        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

        # 현재 Access Key에 연결된 IAM 사용자 정보 가져오기
        identity = iam.get_user()
        user_arn = identity['User']['Arn']
        print(f"[✔] 사용자 ARN: {user_arn}")

        # 검사할 액션 리스트 (관리자 권한 범위에서 샘플로 선택)
        actions_to_test = [
            "iam:CreateUser",
            "iam:AttachUserPolicy",
            "iam:DeleteUser",
            "ec2:StartInstances",
            "ec2:TerminateInstances",
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteBucket",
            "cloudtrail:StopLogging",
            "cloudtrail:DeleteTrail",
            "sns:DeleteTopic",
            "guardduty:UpdateDetector",
            "iam:PassRole",
        ]

        # 권한 시뮬레이션 수행
        response = iam.simulate_principal_policy(
            PolicySourceArn=user_arn,
            ActionNames=actions_to_test
        )

        # 결과 가공
        result = {
            "UserArn": user_arn,
            "Permissions": []
        }

        for decision in response['EvaluationResults']:
            result["Permissions"].append({
                "Action": decision["EvalActionName"],
                "Allowed": decision["EvalDecision"] == "allowed"
            })

        return result

    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"[✘] 오류 발생: {error_code}")
        return {"error": error_code}

if __name__ == "__main__":
    # 여기에 테스트할 키를 입력하세요

    # new secret key
    #ACCESS_KEY = ""
    #SECRET_KEY = ""

    # old secret key
    ACCESS_KEY = ""
    SECRET_KEY = ""

    result = get_iam_permissions(ACCESS_KEY, SECRET_KEY)
    import json
    print(json.dumps(result, indent=2))

    is_admin(ACCESS_KEY, SECRET_KEY)