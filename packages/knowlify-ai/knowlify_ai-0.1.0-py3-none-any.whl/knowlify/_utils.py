# knowlify/_utils.py
import re
import threading
import time
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)

def extract_url(s: str) -> str | None:
    m = URL_RE.search(s)
    return m.group(0) if m else None

def ensure_save_dir(dir_name: str = "knowlify_videos") -> Path:
    p = Path.cwd() / dir_name
    p.mkdir(parents=True, exist_ok=True)
    return p

def slugify(text: str, max_words: int = 6, max_len: int = 60) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text)
    s = "-".join(words[:max_words]).lower()
    return s[:max_len] or "video"

def safe_stem(name: str) -> str:
    # keep alnum, dash, underscore
    s = re.sub(r"[^A-Za-z0-9._-]", "-", name).strip("-_.")
    return s or "video"

def guess_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name or "video"
    if not name.lower().endswith(".mp4"):
        name += ".mp4"
    return name

def save_video_link_to_file(url: str, save_dir: Path | None = None) -> None:
    """
    Append video URL to links.txt file in the save directory.
    Each link is on a new line.
    """
    try:
        if save_dir is None:
            save_dir = ensure_save_dir()
        
        links_file = save_dir / "links.txt"
        
        # Append the URL to the file (create if it doesn't exist)
        with links_file.open("a", encoding="utf-8") as f:
            f.write(url + "\n")
            
    except Exception as e:
        # Don't raise an error if we can't save the link - video download is more important
        print(f"[knowlify] Warning: Failed to save link to links.txt: {e}")

def download_mp4_if_possible(url: str, save_dir: Path | None = None, preferred_basename: str | None = None) -> Path | None:
    """
    Best-effort download into save_dir (default: ./knowlify_videos).
    If preferred_basename is provided, use it (sanitized) as the stem.
    Returns saved path on success, else None.
    """
    try:
        if save_dir is None:
            save_dir = ensure_save_dir()

        req = Request(url, headers={"User-Agent": "knowlify/0.1"})
        with urlopen(req, timeout=120) as resp:
            ctype = resp.headers.get("Content-Type", "").lower()
            if ("video" not in ctype) and (not url.lower().endswith(".mp4")):
                return None

            if preferred_basename:
                stem = safe_stem(preferred_basename)
                p = save_dir / f"{stem}.mp4"
            else:
                fname = guess_filename_from_url(url)
                p = save_dir / fname

            if p.exists():
                ts = int(time.time())
                p = p.with_name(f"{p.stem}_{ts}{p.suffix}")

            data = resp.read()
            p.write_bytes(data)
            print(f"[knowlify] Saved video to: {p}")
            
            # Save the video link to links.txt
            save_video_link_to_file(url, save_dir)
            
            return p
    except Exception:
        return None

def run_coro_in_thread(coro_func, *args, **kwargs):
    import asyncio
    result_container = {"value": None, "error": None}
    done = threading.Event()

    def runner():
        try:
            res = asyncio.run(coro_func(*args, **kwargs))
            result_container["value"] = res
        except Exception as e:
            result_container["error"] = e
        finally:
            done.set()

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    done.wait()
    if result_container["error"]:
        raise result_container["error"]
    return result_container["value"]

def spawn_coro_in_thread(coro_func, *args, **kwargs) -> None:
    import asyncio
    def runner():
        try:
            asyncio.run(coro_func(*args, **kwargs))
        except Exception as e:
            print(f"[knowlify] Background error: {e}")
    threading.Thread(target=runner, daemon=True).start()
