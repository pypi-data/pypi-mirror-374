import requests

server_url = "http://127.0.0.1:8765"


def log(msg):
    try:
        requests.post(f"{server_url}/log", json={"msg": msg})
    except Exception:
        print("⚠️ DeskLog server 未运行，日志未能发送")
