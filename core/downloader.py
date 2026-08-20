import hashlib
import os
import threading
import time

import requests

USER_AGENT = "MD-Server/1.0 (Android; Termux)"


def sha1_file(path, chunk=8192):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


class DownloadState:
    def __init__(self, label, url, dest, expected_size=None, sha1=None):
        self.label = label
        self.url = url
        self.dest = dest
        self.expected_size = expected_size or 0
        self.sha1 = sha1
        self.received = 0
        self.speed = 0.0
        self.status = "starting"
        self.error = ""
        self.done = False
        self.success = False
        self.started = time.time()


def download(ds: DownloadState, session=None, timeout=30, progress_cb=None):
    """Download url into dest with progress. progress_cb(state) called on each chunk."""
    session = session or requests.Session()
    tmp = ds.dest + ".part"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(ds.dest)), exist_ok=True)
        total = ds.expected_size
        headers = {"User-Agent": USER_AGENT}
        resp = session.get(ds.url, stream=True, timeout=timeout, headers=headers)
        resp.raise_for_status()
        if total <= 0 and resp.headers.get("Content-Length"):
            total = int(resp.headers["Content-Length"])
            ds.expected_size = total
        ds.status = "downloading"
        window = []
        start = time.time()
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                f.write(chunk)
                ds.received += len(chunk)
                now = time.time()
                window.append((now, ds.received))
                while window and now - window[0][0] > 3:
                    window.pop(0)
                if window:
                    dt = now - window[0][0]
                    if dt > 0:
                        ds.speed = (ds.received - window[0][1]) / dt
                if progress_cb:
                    progress_cb(ds)
        os.replace(tmp, ds.dest)
        if ds.sha1:
            actual = sha1_file(ds.dest)
            if actual.lower() != ds.sha1.lower():
                ds.status = "failed"
                ds.error = f"sha1_mismatch: expected {ds.sha1}, got {actual}"
                return False
        ds.status = "completed"
        ds.success = True
        ds.done = True
        return True
    except requests.exceptions.ConnectionError:
        ds.status = "failed"
        ds.error = "connection_failed"
    except requests.exceptions.RequestException as e:
        ds.status = "failed"
        ds.error = f"http:{e}"
    except OSError as e:
        ds.status = "failed"
        ds.error = f"storage:{e}"
    except Exception as e:
        ds.status = "failed"
        ds.error = str(e)
    if progress_cb:
        progress_cb(ds)
    return False


def download_with_retry(ds: DownloadState, max_retries=3, progress_cb=None):
    for attempt in range(max_retries):
        ds.status = "starting"
        ok = download(ds, progress_cb=progress_cb)
        if ok:
            return True
        time.sleep(1.5 * (attempt + 1))
    return False


def background_download(ds: DownloadState, *args, **kwargs) -> threading.Thread:
    t = threading.Thread(target=download_with_retry, args=(ds,) + args, kwargs=kwargs, daemon=True)
    t.start()
    return t