from fastapi import APIRouter, WebSocket
import json
import datetime
from app.collecting.nmap.nmap_scan import run_nmap_scan

router = APIRouter()

@router.websocket("/ws/collecting/nmap")
async def collect_nmap_scan(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. nmap 스캔 요청 대기 중..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)
        target_ip_range = data.get("target_ip_range")
        if not target_ip_range:
            await websocket.send_text(json.dumps({"type": "error", "message": "target_ip_range 파라미터 필요"}))
            await websocket.close()
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"nmap_scan_{timestamp}.xml"

        await run_nmap_scan(target_ip_range, output_file, websocket)

        await websocket.send_text(json.dumps({"type": "done", "message": f"nmap 스캔 완료, 결과파일: {output_file}"}))
        await websocket.send_text(json.dumps({"type": "download_url", "url": f"/download/{output_file}"}))

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
    finally:
        await websocket.close()
