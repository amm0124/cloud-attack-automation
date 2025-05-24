import boto3
import os
import argparse


def create_pem_key(access_key, secret_key, region, instance_id, key_name):
    """AWS EC2 키 페어 생성 및 .pem 파일 저장"""
    try:
        # AWS EC2 클라이언트 초기화
        ec2 = boto3.client(
            'ec2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        print(f"[+] Creating key pair: {key_name}")

        # 키 페어 생성
        response = ec2.create_key_pair(KeyName=key_name)
        key_material = response['KeyMaterial']

        # .pem 파일 저장
        pem_file = f"{key_name}.pem"
        with open(pem_file, 'w') as f:
            f.write(key_material)

        # 파일 권한 설정 (읽기 전용)
        os.chmod(pem_file, 0o400)

        print(f"[+] Key pair saved: {pem_file}")

        # 인스턴스 정보 확인 (선택사항)
        if instance_id:
            try:
                instances = ec2.describe_instances(InstanceIds=[instance_id])
                instance = instances['Reservations'][0]['Instances'][0]
                public_ip = instance.get('PublicIpAddress', 'N/A')
                state = instance['State']['Name']

                print(f"[+] Instance {instance_id}: {state} ({public_ip})")
            except Exception as e:
                print(f"[!] Could not get instance info: {e}")

        return pem_file

    except Exception as e:
        print(f"[-] Error creating key pair: {e}")
        return None


def main():

    parser = argparse.ArgumentParser(description='Create AWS EC2 Key Pair')
    parser.add_argument('-a', '--access_key', help='AWS Access Key ID')
    parser.add_argument('-s', '--secret_key', help='AWS Secret Access Key')
    parser.add_argument('-r', '--region', help='AWS Region (e.g., ap-northeast-2)')
    parser.add_argument('-i', '--instance_id', help='Instance ID to check (optional)')
    parser.add_argument('-o', '--key_name',  help='Key pair name')

    args = parser.parse_args()

    print(f"[+] AWS EC2 Key Pair Creator")
    print(f"[+] Region: {args.region}")
    print(f"[+] Key Name: {args.key_name}")

    # 키 페어 생성
    pem_file = create_pem_key(
        args.access_key,
        args.secret_key,
        args.region,
        args.instance_id,
        args.key_name
    )

    if pem_file:
        print(f"\n[+] Success! Use this command to connect:")
        if args.instance_id:
            print(f"ssh -i {pem_file} ubuntu@<instance-public-ip>")
        else:
            print(f"ssh -i {pem_file} ubuntu@your-instance-ip")
    else:
        print("[-] Failed to create key pair")


if __name__ == "__main__":
    main()