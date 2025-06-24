from fastapi import APIRouter, WebSocket
import json
from app.analyzing.jenkins.jenkins_analyzer import fetch_jenkins_version, is_version_vulnerable

router = APIRouter()

@router.websocket("/ws/analyzing/jenkins")
async def analyze_jenkins(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({
        "type": "log",
        "message": "WebSocket connected. Jenkins version analyzing ready..."
    }))

    output_file = "jenkins_analyzer.md"
    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        jenkins_url = data.get("jenkins_url")
        if not jenkins_url:
            msg = "Jenkins URL is required."
            await websocket.send_text(json.dumps({"type": "error", "message": msg}))
            return

        await websocket.send_text(json.dumps({
            "type": "log",
            "message": f"Jenkins server version search: {jenkins_url}"
        }))

        version = await fetch_jenkins_version(jenkins_url, websocket)

        if not version:
            msg = "Jenkins version not found."
            await websocket.send_text(json.dumps({"type": "error", "message": msg}))
            return

        vulnerable = is_version_vulnerable(version)
        is_vulnerable_msg = "안전한 버전입니다." if not vulnerable else "취약한 버전입니다."

        if vulnerable:
            await websocket.send_text(json.dumps({
                "type": "log",
                "message": "vulnerable Jenkins version."
            }))
        else:
            await websocket.send_text(json.dumps({
                "type": "log",
                "message": "safe Jenkins version"
            }))

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Jenkins 버전 보안 분석 보고서\n\n")
            f.write(f"**분석 대상:** `{jenkins_url}`\n\n")
            f.write(f"**탐지된 버전:** `{version or 'N/A'}`\n\n")
            f.write("## 분석 결과\n\n")
            f.write("| 항목 | 내용 |\n")
            f.write("|------|------|\n")
            f.write(f"| 버전 | {version or 'N/A'} |\n")
            f.write(f"| 취약 여부 | {'취약함' if vulnerable else '안전함'} |\n\n")

            f.write("## 판단 기준\n\n")
            f.write("- Jenkins 2.440 이하 버전은 [CVE-2024-23897](https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3314)에 따라 취약하다고 간주됩니다.\n\n")

        await websocket.send_text(json.dumps({
            "type": "done",
            "message": f"jenkins analysis finished, file: {output_file}"
        }))
        await websocket.send_text(json.dumps({
            "type": "download_url",
            "url": f"/download/{output_file}"
        }))

    except Exception as e:
        err_msg = f"error in analyzing: {str(e)}"
        await websocket.send_text(json.dumps({"type": "error", "message": err_msg}))
    finally:
        await websocket.close()
