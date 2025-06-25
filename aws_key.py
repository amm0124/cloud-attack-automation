#!/usr/bin/env python3
import boto3
import argparse
import os
import sys


def create_keypair(key_name, access_key, secret_key, instance_id=None, region=None):
    """EC2 키 페어 생성 후 로컬 저장 + SSM 등록"""
    try:
        # AWS 클라이언트 초기화 (인자로 받은 자격증명 사용)
        ec2 = boto3.client(
            'ec2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        ssm = boto3.client(
            'ssm',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        print(f"[+] Creating key pair: {key_name}")

        # 키 페어 생성
        response = ec2.create_key_pair(KeyName=key_name)
        private_key = response['KeyMaterial']

        # 로컬에 .pem 파일 저장
        pem_file = f"{key_name}.pem"
        with open(pem_file, 'w') as f:
            f.write(private_key)
        os.chmod(pem_file, 0o400)

        print(f"[+] Local file saved: {pem_file}")

        # SSM에 등록
        ssm_path = f"/keys/{key_name}"
        ssm.put_parameter(
            Name=ssm_path,
            Value=private_key,
            Type='SecureString',
            Description=f'Private key for {key_name}',
            Overwrite=True
        )

        print(f"[+] SSM registered: {ssm_path}")

        # EC2 인스턴스 정보 확인 (선택사항)
        if instance_id:
            try:
                instances = ec2.describe_instances(InstanceIds=[instance_id])
                instance = instances['Reservations'][0]['Instances'][0]
                public_ip = instance.get('PublicIpAddress', 'N/A')
                state = instance['State']['Name']
                print(f"[+] Instance {instance_id}: {state} ({public_ip})")

                if public_ip != 'N/A':
                    print(f"[+] SSH command: ssh -i {pem_file} ec2-user@{public_ip}")
                else:
                    print(f"[+] Use: ssh -i {pem_file} ec2-user@your-instance-ip")
            except Exception as e:
                print(f"[!] Could not get instance info: {e}")
                print(f"[+] Use: ssh -i {pem_file} ec2-user@your-instance-ip")
        else:
            print(f"[+] Use: ssh -i {pem_file} ec2-user@your-instance-ip")

    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Create key pair, save locally and register in SSM')
    parser.add_argument('-k', '--key-name', required=True, help='Key pair name')
    parser.add_argument('-a', '--access-key', required=True, help='AWS Access Key ID')
    parser.add_argument('-s', '--secret-key', required=True, help='AWS Secret Access Key')
    parser.add_argument('-i', '--instance-id', help='EC2 Instance ID (optional)')
    parser.add_argument('-r', '--region', help='AWS region')

    args = parser.parse_args()
    create_keypair(args.key_name, args.access_key, args.secret_key, args.instance_id, args.region)


if __name__ == "__main__":
    main()