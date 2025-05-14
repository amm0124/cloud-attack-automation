#!/usr/bin/env python3
"""
Git 저장소를 클론하고 Gitleaks로 시크릿을 스캔한 후, HTML 보고서를 생성하는 스크립트 (개선된 버전)

이 스크립트는 다음 작업을 수행합니다:
1. git clone --mirror로 저장소를 클론합니다.
2. gitleaks detect 명령으로 시크릿을 스캔합니다.
3. 스캔 결과를 시크릿 값이 제대로 표시되는 HTML 보고서로 변환합니다.
4. 클론한 폴더를 삭제합니다.

사용법:
  python improved_gitleaks_reporter.py <GitHub URL> [출력 디렉토리]
"""

import argparse
import json
import os
import subprocess
import sys
import shutil
from datetime import datetime
from pathlib import Path
import tempfile


def clone_repository(repo_url, temp_dir=None):
    """
    저장소를 임시 디렉토리에 클론합니다.
    
    Args:
        repo_url: 클론할 GitHub 저장소 URL
        temp_dir: 클론할 디렉토리 (None이면 임시 디렉토리 생성)
        
    Returns:
        클론된 디렉토리 경로
    """
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()
    
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    clone_path = os.path.join(temp_dir, repo_name)
    
    print(f"[*] 저장소 클론 중: {repo_url} -> {clone_path}")
    try:
        # mirror 옵션으로 클론 - 전체 히스토리와 모든 브랜치 포함
        subprocess.run(
            ["git", "clone", "--mirror", repo_url, clone_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"[+] 저장소 클론 완료: {clone_path}")
        return clone_path
    except subprocess.CalledProcessError as e:
        print(f"[!] 저장소 클론 실패: {e.stderr.decode() if hasattr(e.stderr, 'decode') else str(e)}")
        sys.exit(1)


def run_gitleaks(repo_path, output_file):
    """
    Gitleaks를 실행하여 시크릿을 스캔합니다.
    
    Args:
        repo_path: 스캔할 저장소 경로
        output_file: 결과를 저장할 파일 경로
        
    Returns:
        성공 여부
    """
    print(f"[*] Gitleaks 스캔 시작: {repo_path}")
    try:
        # Gitleaks 명령 실행
        subprocess.run(
            [
                "gitleaks", "detect",
                "--source", repo_path,
                "--report-format", "json",
                "--report-path", output_file,
                "-v"  # 자세한 출력
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if os.path.exists(output_file):
            print(f"[+] Gitleaks 스캔 완료: {output_file}")
            return True
        else:
            print(f"[!] Gitleaks 결과 파일이 생성되지 않았습니다: {output_file}")
            return False
            
    except subprocess.CalledProcessError as e:
        # 시크릿을 발견하면 Gitleaks는 오류 코드를 반환할 수 있음
        print(f"[*] Gitleaks 실행 중 알림: {e.stderr.decode() if hasattr(e.stderr, 'decode') else str(e)}")
        
        # 그래도 결과 파일이 생성되었는지 확인
        if os.path.exists(output_file):
            print(f"[+] Gitleaks 결과 파일 생성됨: {output_file}")
            return True
        else:
            print(f"[!] Gitleaks 결과 파일이 생성되지 않았습니다")
            return False


def generate_html_report(json_file, output_dir):
    """
    Gitleaks JSON 결과를 HTML 보고서로 변환합니다.
    
    Args:
        json_file: Gitleaks JSON 결과 파일 경로
        output_dir: HTML 보고서를 저장할 디렉토리
        
    Returns:
        생성된 HTML 파일 경로
    """
    if not os.path.exists(json_file):
        print(f"[!] JSON 파일을 찾을 수 없습니다: {json_file}")
        return None
    
    try:
        with open(json_file, 'r') as f:
            results = json.load(f)
    except json.JSONDecodeError:
        print(f"[!] JSON 파일 파싱 실패: {json_file}")
        return None
    
    # 결과가 리스트가 아닌 다른 형식인지 확인
    if isinstance(results, dict) and 'leaks' in results:
        results = results['leaks']
    
    if not isinstance(results, list):
        print(f"[!] 예상치 못한 JSON 형식: {type(results)}")
        results = []
    
    # 결과 분석
    total_secrets = len(results)
    
    # 유형별 분류
    secret_types = {}
    for result in results:
        rule_id = result.get('RuleID', 'Unknown')
        if rule_id not in secret_types:
            secret_types[rule_id] = 0
        secret_types[rule_id] += 1
    
    # 파일별 분류
    file_secrets = {}
    for result in results:
        file_path = result.get('File', 'Unknown')
        if file_path not in file_secrets:
            file_secrets[file_path] = 0
        file_secrets[file_path] += 1
    
    # 커밋별 분류
    commit_secrets = {}
    for result in results:
        commit = result.get('Commit', 'Unknown')
        if commit not in commit_secrets:
            commit_secrets[commit] = 0
        commit_secrets[commit] += 1
    
    # 저장소 이름 추출
    repo_name = os.path.basename(json_file).replace('gitleaks-report.json', '').strip('-_')
    if not repo_name:
        repo_name = "Repository"
    
    # 테이블 행 생성
    table_rows = ""
    for idx, result in enumerate(results):
        rule_id = result.get('RuleID', 'Unknown')
        file_path = result.get('File', 'Unknown')
        line_start = result.get('StartLine', 0)
        line_end = result.get('EndLine', line_start)
        line_info = str(line_start) if line_start == line_end else f"{line_start}-{line_end}"
        commit = result.get('Commit', 'Unknown')[:7]  # 커밋 해시 축약
        secret = result.get('Secret', 'Unknown')
        
        # HTML에서 안전하게 표시하기 위해 이스케이프
        secret_escaped = secret.replace('<', '&lt;').replace('>', '&gt;')
        
        # 작성자와 날짜 정보 추출
        author = result.get('Author', 'Unknown')
        date = result.get('Date', '')
        
        # 행 HTML 생성 - 각 행에 고유 ID 추가
        table_rows += f"""
        <tr data-file="{file_path}" data-type="{rule_id}">
            <td>{rule_id}</td>
            <td>{file_path}</td>
            <td>{line_info}</td>
            <td>{commit}</td>
            <td>
                <button class="secret-toggle-btn" onclick="toggleSecret('secret-{idx}')">시크릿 값 보기</button>
                <div id="secret-{idx}" class="secret-content" style="display:none;">
                    <pre><code>{secret_escaped}</code></pre>
                </div>
            </td>
            <td>{author}</td>
            <td>{date}</td>
        </tr>
        """
    
    # HTML 템플릿
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{repo_name} - Gitleaks 스캔 보고서</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .summary {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .alert {{
                background-color: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .success {{
                background-color: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .chart-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .chart {{
                flex: 1;
                min-width: 300px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th, td {{
                padding: 12px 15px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .secret-toggle-btn {{
                background-color: #f2f2f2;
                color: #444;
                cursor: pointer;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
            .secret-toggle-btn:hover {{
                background-color: #e8e8e8;
            }}
            .secret-content {{
                margin-top: 8px;
                background-color: #fafafa;
                border-radius: 4px;
                padding: 10px;
                border-left: 3px solid #3498db;
            }}
            pre {{
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                font-size: 13px;
                margin: 0;
            }}
            .filter-section {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .filter-group {{
                margin-bottom: 15px;
            }}
            .filter-group label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            .filter-group select, .filter-group input {{
                padding: 8px;
                width: 100%;
                max-width: 300px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }}
            .footer {{
                margin-top: 40px;
                text-align: center;
                font-size: 14px;
                color: #7f8c8d;
            }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>{repo_name} - Gitleaks 스캔 보고서</h1>
            <p>생성 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="summary">
                <h2>요약</h2>
                <p>총 {total_secrets}개의 시크릿이 발견되었습니다.</p>
            </div>
            
            {
                '<div class="alert"><h3>⚠️ 주의: '+str(total_secrets)+'개의 시크릿이 발견되었습니다</h3><p>발견된 시크릿을 검토하고 적절한 조치를 취하세요.</p></div>' 
                if total_secrets > 0 else 
                '<div class="success"><h3>✅ 좋은 소식: 시크릿이 발견되지 않았습니다</h3><p>이 저장소에서 민감한 정보가 발견되지 않았습니다.</p></div>'
            }
            
            <div class="chart-container">
                <div class="chart">
                    <h3>시크릿 유형</h3>
                    <canvas id="secretTypesChart"></canvas>
                </div>
                <div class="chart">
                    <h3>파일별 시크릿</h3>
                    <canvas id="fileSecretsChart"></canvas>
                </div>
            </div>
            
            <div class="filter-section">
                <h3>필터 및 검색</h3>
                <div class="filter-group">
                    <label for="filter-file">파일 필터:</label>
                    <select id="filter-file" onchange="applyFilters()">
                        <option value="all">모든 파일</option>
                        {"".join([f'<option value="{file_path}">{file_path}</option>' for file_path in file_secrets])}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="filter-type">유형 필터:</label>
                    <select id="filter-type" onchange="applyFilters()">
                        <option value="all">모든 유형</option>
                        {"".join([f'<option value="{rule_id}">{rule_id}</option>' for rule_id in secret_types])}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="search-input">검색:</label>
                    <input type="text" id="search-input" placeholder="파일명, 시크릿 유형 등 검색..." onkeyup="applyFilters()">
                </div>
            </div>
            
            <h2>발견된 시크릿</h2>
            <table id="secrets-table">
                <thead>
                    <tr>
                        <th>유형</th>
                        <th>파일</th>
                        <th>라인</th>
                        <th>커밋</th>
                        <th>시크릿 값</th>
                        <th>작성자</th>
                        <th>날짜</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            
            <div class="footer">
                <p>이 보고서는 Gitleaks를 사용하여 생성되었습니다.</p>
                <p>생성 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </div>
        
        <script>
            // 시크릿 유형 차트
            const secretTypesCtx = document.getElementById('secretTypesChart').getContext('2d');
            new Chart(secretTypesCtx, {{
                type: 'pie',
                data: {{
                    labels: {json.dumps(list(secret_types.keys()))},
                    datasets: [{{
                        data: {json.dumps(list(secret_types.values()))},
                        backgroundColor: [
                            '#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
                            '#9b59b6', '#1abc9c', '#d35400', '#34495e',
                            '#7f8c8d', '#27ae60', '#c0392b', '#8e44ad'
                        ],
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'right',
                        }}
                    }}
                }}
            }});
            
            // 파일별 시크릿 차트
            const fileSecretsCtx = document.getElementById('fileSecretsChart').getContext('2d');
            new Chart(fileSecretsCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(list(file_secrets.keys()))},
                    datasets: [{{
                        label: '시크릿 수',
                        data: {json.dumps(list(file_secrets.values()))},
                        backgroundColor: '#3498db',
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            
            // 시크릿 값 토글 함수
            function toggleSecret(secretId) {{
                const element = document.getElementById(secretId);
                if (element.style.display === "none" || element.style.display === "") {{
                    element.style.display = "block";
                }} else {{
                    element.style.display = "none";
                }}
            }}
            
            // 필터 적용 함수
            function applyFilters() {{
                const fileFilter = document.getElementById('filter-file').value;
                const typeFilter = document.getElementById('filter-type').value;
                const searchText = document.getElementById('search-input').value.toLowerCase();
                
                const rows = document.querySelectorAll('#secrets-table tbody tr');
                
                rows.forEach(row => {{
                    const fileValue = row.getAttribute('data-file');
                    const typeValue = row.getAttribute('data-type');
                    const rowText = row.textContent.toLowerCase();
                    
                    const fileMatch = fileFilter === 'all' || fileValue === fileFilter;
                    const typeMatch = typeFilter === 'all' || typeValue === typeFilter;
                    const textMatch = searchText === '' || rowText.includes(searchText);
                    
                    if (fileMatch && typeMatch && textMatch) {{
                        row.style.display = '';
                    }} else {{
                        row.style.display = 'none';
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    # 출력 파일 경로
    os.makedirs(output_dir, exist_ok=True)
    html_file = os.path.join(output_dir, f"{repo_name}_gitleaks_report.html")
    
    # HTML 파일 저장
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"[+] HTML 보고서 생성 완료: {html_file}")
    return html_file


def cleanup(temp_dir):
    """
    임시 디렉토리 정리
    
    Args:
        temp_dir: 삭제할 디렉토리 경로
    """
    print(f"[*] 임시 디렉토리 정리 중: {temp_dir}")
    try:
        shutil.rmtree(temp_dir)
        print(f"[+] 임시 디렉토리 삭제 완료")
    except Exception as e:
        print(f"[!] 임시 디렉토리 삭제 실패: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Git 저장소를 클론하고 Gitleaks로 스캔한 후 HTML 보고서를 생성합니다.')
    parser.add_argument('repo_url', help='스캔할 GitHub 저장소 URL')
    parser.add_argument('--output', '-o', default='./reports', help='HTML 보고서를 저장할 디렉토리 (기본값: ./reports)')
    args = parser.parse_args()
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 저장소 클론
        repo_path = clone_repository(args.repo_url, temp_dir)
        
        # Gitleaks 결과 파일 경로
        gitleaks_output = os.path.join(temp_dir, "gitleaks-report.json")
        
        # Gitleaks 실행
        if run_gitleaks(repo_path, gitleaks_output):
            # HTML 보고서 생성
            html_report = generate_html_report(gitleaks_output, args.output)
            if html_report:
                print(f"[+] 프로세스 완료! 보고서: {html_report}")
        
    finally:
        # 항상 임시 디렉토리 정리
        cleanup(temp_dir)


if __name__ == "__main__":
    main()