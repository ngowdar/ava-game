# roku.py — Roku HTTP helper (urllib, threaded)

import threading
import urllib.request
from config import ROKU_IP, ROKU_PORT

# Set to False to disable all Roku commands (no network calls)
ENABLED = False


def _post(url):
    """Fire-and-forget POST with timeout. Silent on errors."""
    if not ENABLED:
        return
    try:
        req = urllib.request.Request(url, data=b"", method="POST")
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


def launch_show(channel_id, content_id, media_type):
    """Launch a show on Roku via ECP deep link (threaded)."""
    if not ENABLED:
        return
    url = f"http://{ROKU_IP}:{ROKU_PORT}/launch/{channel_id}"
    if content_id:
        url += f"?ContentID={content_id}&MediaType={media_type}"
    threading.Thread(target=_post, args=(url,), daemon=True).start()


def send_keypress(key):
    """Send a keypress to Roku (threaded)."""
    if not ENABLED:
        return
    url = f"http://{ROKU_IP}:{ROKU_PORT}/keypress/{key}"
    threading.Thread(target=_post, args=(url,), daemon=True).start()
