# gitleaks + trufflehog를 통한 자격 증명 정보 수집
import subprocess
import sys
import os
import json
import argparse
from datetime import datetime


def clone_repo(repo_url):
    repo_name = repo_url.split('/')[-1].replace('.git', '')

    try:
        subprocess.run(["git", "clone", repo_url, repo_name], check=True, capture_output=True)
        return repo_name
    except subprocess.CalledProcessError as e:
        print(f"{repo_url} 클론 실패: {e}")
        sys.exit(1)


def run_gitleaks(repo_path, output_file):
    print("[1/8] - gitleaks를 통해 주요 자격증명 정보 수집 시작")

    try:
        subprocess.run([
            "gitleaks", "detect",
            "--source", repo_path,
            "--report-format", "json",
            "--report-path", output_file
        ], capture_output=True)

        print("[2/8] - gitleaks를 통해 주요 자격증명 정보 수집 완료")
        return os.path.exists(output_file)
    except subprocess.CalledProcessError:
        return os.path.exists(output_file)


def run_trufflehog(repo_url, output_file):
    print("[4/8] - trufflehog v2를 통한 자격 증명 정보 수집 시작..")

    try:
        result = subprocess.run([
            "trufflehog", "--json", "--regex", repo_url
        ], capture_output=True, text=True)

        print(f"[5/8] - trufflehog v2를 통한 자격 증명 정보 수집 완료")

        if result.stdout.strip():
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            return True

        return False
    except Exception as e:
        print(f"Trufflehog scan failed: {e}")
        return False


def parse_gitleaks_results(output_file):
    print("[3/8] - gitleaks 결과 파싱 시작..")
    if not os.path.exists(output_file):
        return []

    with open(output_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def parse_trufflehog_results(output_file):
    print("[6/8] - trufflehog 분석 결과 파싱 시작..")
    if not os.path.exists(output_file):
        return []

    results = []
    with open(output_file, 'r') as f:
        for line in f:
            try:
                results.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return results


def generate_markdown_report(repo_url, gitleaks_results, trufflehog_results, output_file):
    print("[7/8] - 마크다운 보고서 생성 시작..")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Security Scan Report\n\n")
        f.write(f"**Repository:** {repo_url}\n")
        f.write(f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Gitleaks 결과
        f.write(f"## Gitleaks Results\n\n")
        if gitleaks_results:
            f.write(f"**Total findings:** {len(gitleaks_results)}\n\n")
            for i, result in enumerate(gitleaks_results, 1):
                f.write(f"### Finding {i}\n")
                f.write(f"- **Rule:** {result.get('RuleID', 'N/A')}\n")
                f.write(f"- **File:** {result.get('File', 'N/A')}\n")
                f.write(f"- **Line:** {result.get('StartLine', 'N/A')}\n")
                f.write(f"- **Commit:** {result.get('Commit', 'N/A')}\n")
                f.write(f"- **Description:** {result.get('Description', 'N/A')}\n")
                if result.get('Secret'):
                    f.write(f"- **Secret:** `{result['Secret'][:50]}...`\n")
                f.write("\n")
        else:
            f.write("No secrets found by Gitleaks.\n\n")

        # Trufflehog 결과
        f.write(f"## Trufflehog Results\n\n")
        if trufflehog_results:
            f.write(f"**Total findings:** {len(trufflehog_results)}\n\n")
            for i, result in enumerate(trufflehog_results, 1):
                f.write(f"### Finding {i}\n")
                f.write(f"- **Repository:** {result.get('repository', 'N/A')}\n")
                f.write(f"- **Path:** {result.get('path', 'N/A')}\n")
                f.write(f"- **Branch:** {result.get('branch', 'N/A')}\n")
                f.write(f"- **Commit:** {result.get('commit', 'N/A')}\n")
                f.write(f"- **Commit Hash:** {result.get('commitHash', 'N/A')}\n")
                f.write(f"- **Date:** {result.get('date', 'N/A')}\n")
                if result.get('diff'):
                    f.write(f"- **Diff:** ```\n{result['diff'][:200]}...\n```\n")
                if result.get('stringsFound'):
                    f.write(f"- **Strings Found:** {', '.join(result['stringsFound'][:3])}\n")
                f.write("\n")
        else:
            f.write("No secrets found by Trufflehog.\n\n")


def main():
    parser = argparse.ArgumentParser(description='GitHub repository를 통한 자격 증명 정보 수집')
    parser.add_argument('repo_url', help='GitHub repository URL')
    parser.add_argument('-o', '--output', default='security_report.md', help='Output markdown file')

    args = parser.parse_args()

    # gitleaks - repository clone
    repo_name = clone_repo(args.repo_url)

    try:
        # Gitleaks 스캔
        gitleaks_output = "gitleaks_results.json"
        gitleaks_found = run_gitleaks(repo_name, gitleaks_output)
        gitleaks_results = parse_gitleaks_results(gitleaks_output) if gitleaks_found else []

        # Trufflehog 스캔
        trufflehog_output = "trufflehog_results.json"
        trufflehog_found = run_trufflehog(args.repo_url, trufflehog_output)
        trufflehog_results = parse_trufflehog_results(trufflehog_output) if trufflehog_found else []

        # 마크다운 보고서 생성
        generate_markdown_report(args.repo_url, gitleaks_results, trufflehog_results, args.output)

        print(f"[8/8] - 마크다운 보고서 생성 완료 및 다운로드 가능")

    finally:
        # 정리
        if os.path.exists(repo_name):
            subprocess.run(["rm", "-rf", repo_name], check=True)
        for temp_file in [gitleaks_output, trufflehog_output]:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    main()