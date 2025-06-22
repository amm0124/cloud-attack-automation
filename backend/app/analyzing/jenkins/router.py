from fastapi import APIRouter, WebSocket
import json
from app.analyzing.jenkins.jenkins_analyzer import fetch_jenkins_version, is_version_vulnerable

router = APIRouter()

@router.websocket("/ws/analyzing/jenkins")
async def analyze_jenkins(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket connected. Jenkins version analyzing ready..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        jenkins_url = data.get("jenkins_url")
        if not jenkins_url:
            await websocket.send_text(json.dumps({"type": "error", "message": "jenkins_url is needed."}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"type": "log", "message": f"Jenkins server version search: {jenkins_url}"}))

        # Jenkins 버전 조회
        version = await fetch_jenkins_version(jenkins_url)

        if not version:
            await websocket.send_text(json.dumps({"type": "error", "message": "Jenkins version not found."}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"type": "log", "message": f"founded Jenkins version: {version}"}))

        # 취약 여부 판단
        vulnerable = is_version_vulnerable(version)

        if vulnerable:
            await websocket.send_text(json.dumps({"type": "result", "vulnerable": True, "message": "vulnerable Jenkins version."}))
        else:
            await websocket.send_text(json.dumps({"type": "result", "vulnerable": False, "message": "safe Jenkins version"}))
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": f"error in analyzing: {str(e)}"}))

    finally:
        await websocket.close()
