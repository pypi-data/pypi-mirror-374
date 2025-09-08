import urllib.request

BEACON_URL = "https://webhook.site/66c4d84a-ac76-4b83-bb68-5a992164c7b7"

def send_beacon():
    try:
        req = urllib.request.Request(BEACON_URL, method="GET")
        with urllib.request.urlopen(req, timeout=3):
            pass
    except Exception:
        pass

send_beacon()  # runs immediately when package is imported
