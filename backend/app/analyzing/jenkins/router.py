from fastapi import APIRouter, WebSocket
import json
from app.analyzing.jenkins.jenkins_analyzer import fetch_jenkins_version, is_version_vulnerable

router = APIRouter()

@router.websocket("/ws/analyzing/jenkins")
async def analyze_jenkins(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. Jenkins 버전 분석 대기 중..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        jenkins_url = data.get("jenkins_url")
        if not jenkins_url:
            await websocket.send_text(json.dumps({"type": "error", "message": "jenkins_url이 필요합니다."}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"type": "log", "message": f"Jenkins 서버 버전 조회 중: {jenkins_url}"}))

        # Jenkins 버전 조회
        version = await fetch_jenkins_version(jenkins_url)

        if not version:
            await websocket.send_text(json.dumps({"type": "error", "message": "Jenkins 버전 정보를 찾을 수 없습니다."}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"type": "log", "message": f"발견된 Jenkins 버전: {version}"}))

        # 취약 여부 판단
        vulnerable = is_version_vulnerable(version)

        if vulnerable:
            await websocket.send_text(json.dumps({"type": "result", "vulnerable": True, "message": "취약한 Jenkins 버전입니다."}))
        else:
            await websocket.send_text(json.dumps({"type": "result", "vulnerable": False, "message": "안전한 Jenkins 버전입니다."}))

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": f"분석 중 오류 발생: {str(e)}"}))

    finally:
        await websocket.close()
