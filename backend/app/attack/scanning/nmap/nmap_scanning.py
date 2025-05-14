import subprocess
import sys
import json
from datetime import datetime

def run_nmap(ip, port):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    xml_output = f"nmap_scan_{ip}_{port}_{timestamp}.xml"
    json_output = f"nmap_scan_{ip}_{port}_{timestamp}.json"

    # nmap 명령 실행
    cmd = [
        "nmap",
        "-Pn",
        "-sV",
        "--script", "vulners",
        "-p", str(port),
        "-oX", xml_output,
        ip
    ]

    try:
        print(f"[+] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

        # XML -> JSON 변환 (선택 사항)
        try:
            import xmltodict
            with open(xml_output) as xml_file:
                data_dict = xmltodict.parse(xml_file.read())
            with open(json_output, "w") as json_file:
                json.dump(data_dict, json_file, indent=2)
            print(f"[+] Results saved to: {xml_output}, {json_output}")
        except ImportError:
            print("[-] Install 'xmltodict' to enable JSON export: pip install xmltodict")

    except subprocess.CalledProcessError as e:
        print(f"[-] Nmap command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ip = input("Enter target IP: ").strip()
    port = input("Enter target port: ").strip()

    run_nmap(ip, port)