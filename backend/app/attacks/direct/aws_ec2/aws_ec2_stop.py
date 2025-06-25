# python ec2_stop.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region ap-northeast-2 --instance-id i-1234567890abcdef0
# python /Users/geonho/workspace/cloud-attack-automation/backend/app/attacks/direct/aws_ec2/aws_ec2_stop.py

import boto3
import argparse
import sys

def stop_ec2_instance(access_key, secret_key, region, instance_id):
   """EC2 인스턴스를 중지하고 결과를 반환"""
   try:
       # boto3 클라이언트 생성
       ec2 = boto3.client(
           'ec2',
           aws_access_key_id=access_key,
           aws_secret_access_key=secret_key,
           region_name=region
       )

       # EC2 인스턴스 중지
       response = ec2.stop_instances(InstanceIds=[instance_id])

       # 결과 생성
       stopping_instance = response['StoppingInstances'][0]
       current_state = stopping_instance['CurrentState']['Name']
       previous_state = stopping_instance['PreviousState']['Name']

       return f"""# EC2 인스턴스 중지 결과

## 인스턴스 정보
- **인스턴스 ID**: {instance_id}
- **리전**: {region}

## 상태 변경
- **이전 상태**: {previous_state}
- **현재 상태**: {current_state}

## 결과
EC2 인스턴스가 성공적으로 중지되었습니다.
"""

   except Exception as e:
       return f"""# EC2 인스턴스 중지 실패

## 오류 정보
- **인스턴스 ID**: {instance_id}
- **리전**: {region}
- **오류 메시지**: {str(e)}

## 결과
EC2 인스턴스 중지에 실패했습니다.
"""

def main():
   parser = argparse.ArgumentParser(description='EC2 인스턴스 중지')
   parser.add_argument('--access-key', required=True, help='AWS Access Key')
   parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
   parser.add_argument('--region', required=True, help='AWS Region')
   parser.add_argument('--instance-id', required=True, help='EC2 Instance ID')

   args = parser.parse_args()

   result = stop_ec2_instance(
       args.access_key,
       args.secret_key,
       args.region,
       args.instance_id
   )

   with open("ec2_stop_result.md", "w", encoding="utf-8") as f:
       f.write(result)


if __name__ == "__main__":
   main()