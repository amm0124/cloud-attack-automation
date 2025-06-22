import asyncio
import json


async def run_nmap_scan(target_ip_range: str, output_file: str, websocket=None):
    cmd = [
        "nmap",
        "-p", "8080,80,443",
        "-sV",
        "-oX", output_file,
        target_ip_range
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    if websocket:
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(json.dumps({"type": "log", "message": line.decode().strip()}))
    else:
        await process.wait()

    await process.wait()
    return output_file
