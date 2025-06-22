import asyncio
from fastapi import APIRouter, WebSocket
import json
from app.attacks.indirect.jenkins_attack import launch_exploit

router = APIRouter()

@router.websocket("/ws/attack/jenkins")
async def attack_jenkins(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket connected. attack request ready..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        jenkins_url = data.get("jenkins_url")
        file_path = data.get("file_path", "/etc/passwd")

        if not jenkins_url:
            await websocket.send_text(json.dumps({"type": "error", "message": "jenkins_url is needed."}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"type": "log", "message": f"attack start: {jenkins_url}, file path: {file_path}"}))

        loop = asyncio.get_running_loop()
        # 동기 함수 launch_exploit을 별도 쓰레드에서 실행
        result = await loop.run_in_executor(None, launch_exploit, jenkins_url, file_path)

        # result를 문자열로 변환 (bytes면 디코딩 시도)
        if isinstance(result, bytes):
            try:
                result_str = result.decode("utf-8", errors="replace")
            except Exception:
                result_str = str(result)
        else:
            result_str = str(result)

        await websocket.send_text(json.dumps({"type": "result", "message": result_str}))

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": f"error in attack: {str(e)}"}))

    finally:
        await websocket.close()
