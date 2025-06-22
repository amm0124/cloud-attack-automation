from fastapi import APIRouter, WebSocket
import json
from app.attacks.indirect.jenkins_attack import launch_exploit

router = APIRouter()

@router.websocket("/ws/attack/jenkins")
async def attack_jenkins(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 공격 요청 대기 중..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        jenkins_url = data.get("jenkins_url")
        file_path = data.get("file_path", "/etc/passwd")  # 기본적으로 /etc/passwd 조회

        if not jenkins_url:
            await websocket.send_text(json.dumps({"type": "error", "message": "jenkins_url이 필요합니다."}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"type": "log", "message": f"공격 시작: {jenkins_url}, 파일 경로: {file_path}"}))

        # 공격 수행 (동기 함수라서 쓰레드로 감싸거나 별도 프로세스로 돌려도 됨)
        launch_exploit(jenkins_url, file_path)

        await websocket.send_text(json.dumps({"type": "result", "message": "공격 요청이 완료되었습니다."}))

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": f"공격 중 오류 발생: {str(e)}"}))

    finally:
        await websocket.close()
