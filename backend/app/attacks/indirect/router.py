import asyncio
from fastapi import APIRouter, WebSocket
import json
from app.attacks.indirect.jenkins_attack import launch_exploit

router = APIRouter()

@router.websocket("/ws/attack/indirect/jenkins")
async def attack_jenkins(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket connected. attack request ready..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        jenkins_url = data.get("jenkins_url")
        file_path = data.get("file_path", "/home/ubuntu/,jenkins/secrets/master.key")

        if not jenkins_url:
            await websocket.send_text(json.dumps({"type": "error", "message": "jenkins_url is needed."}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"type": "log", "message": f"attack start: {jenkins_url}, file path: {file_path}"}))

        report_file = await launch_exploit(jenkins_url, file_path, websocket)

        # 필요시 report_file을 클라이언트에 알려줌
        # (이미 launch_exploit 내부에서 download_url 전송함)

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": f"error in attack: {str(e)}"}))

    finally:
        await websocket.close()
