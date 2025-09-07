# knowlify/_worker.py
import argparse
import asyncio
import base64

from ._ws import send_task_over_ws
from ._utils import download_mp4_if_possible
from ._auth import init
from ._capture import InvalidAPIKeyError, OutOfMinutesError

async def _run(action: str, task: str, api_key: str, basename: str | None) -> None:
    # Initialize the API key in this process
    init(api_key)
    try:
        url = await send_task_over_ws(action, task)
        if isinstance(url, str) and url:
            download_mp4_if_possible(url, preferred_basename=basename)
    except (InvalidAPIKeyError, OutOfMinutesError) as e:
        # Save error to text file in knowlify_videos folder
        import os
        from pathlib import Path
        import time
        
        videos_dir = Path("knowlify_videos")
        videos_dir.mkdir(exist_ok=True)
        
        # Use the same basename logic as the video would have used
        if basename:
            error_filename = f"{basename}_ERROR.txt"
        else:
            timestamp = int(time.time())
            error_filename = f"knowlify-error_{timestamp}.txt"
        
        error_path = videos_dir / error_filename
        error_content = f"""Knowlify API Error
==================
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
Error: {e}
Status Code: {e.status_code}

This error occurred while trying to generate your video.
Please check your API key and account status.
"""
        
        try:
            error_path.write_text(error_content, encoding="utf-8")
            print(f"[knowlify] Error saved to: {error_path}")
        except Exception as write_err:
            print(f"[knowlify] Error: {e} (Failed to save error file: {write_err})")
        return

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--action", required=True)
    p.add_argument("--task_b64", required=True)
    p.add_argument("--api_key_b64", required=True)
    p.add_argument("--basename", default=None)
    args = p.parse_args()

    task = base64.b64decode(args.task_b64.encode("ascii")).decode("utf-8", "ignore")
    api_key = base64.b64decode(args.api_key_b64.encode("ascii")).decode("utf-8", "ignore")
    asyncio.run(_run(args.action, task, api_key, args.basename))

if __name__ == "__main__":
    main()
