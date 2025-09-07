# knowlify/_api.py

from typing import Literal
import asyncio
import base64
import os
import subprocess
import sys

from ._capture import (
    capture_code_above_call,
    capture_function_by_name,
    begin_region,
    end_region,
    KnowlifyError,
    InvalidAPIKeyError,
    OutOfMinutesError,
)
from ._prompt import build_task_text
from ._config import ACTION_MAP
from ._ws import send_task_over_ws
from ._utils import (
    download_mp4_if_possible,
    run_coro_in_thread,
    slugify,
)
from ._auth import get_api_key

Mode = Literal["fast", "detailed"]


def _generate_video_basename(task_text: str, function_name: str | None = None) -> str:
    """Generate a meaningful basename for the video file."""
    if function_name:
        # If we have a function name, use it as the primary identifier
        base = slugify(function_name)
    else:
        # Try to extract meaningful content from the task
        # Look for function definitions, class names, or significant keywords
        import re
        
        # Extract function names from code
        func_matches = re.findall(r'def\s+(\w+)', task_text)
        class_matches = re.findall(r'class\s+(\w+)', task_text)
        
        if func_matches:
            base = slugify(func_matches[0])
        elif class_matches:
            base = slugify(class_matches[0])
        else:
            # Extract the first line of actual code (skip empty lines and comments)
            lines = task_text.split('\n')
            meaningful_line = None
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    meaningful_line = stripped
                    break
            
            if meaningful_line:
                base = slugify(meaningful_line)
            else:
                base = "knowlify-video"
    
    # Add timestamp for uniqueness
    import time
    timestamp = int(time.time())
    return f"{base}_{timestamp}"


# ---------------- detached worker (used by non-blocking paths) ----------------
def _spawn_detached_worker(action: str, task: str, basename: str | None = None) -> None:
    """
    Fire-and-forget worker that survives after the caller exits.
    It connects over WS, waits for the link, and saves the MP4 into ./knowlify_videos/.
    """
    # Get API key and encode it
    api_key = get_api_key()  # This will raise ValueError if not initialized
    api_key_b64 = base64.b64encode(api_key.encode("utf-8")).decode("ascii")
    
    task_b64 = base64.b64encode(task.encode("utf-8")).decode("ascii")
    cmd = [sys.executable, "-m", "knowlify._worker", "--action", action, "--task_b64", task_b64, "--api_key_b64", api_key_b64]
    if basename:
        cmd.extend(["--basename", basename])

    kwargs: dict = {"close_fds": True}
    if os.name == "nt":
        # Windows detach flags
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        kwargs.update(
            dict(
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )
    else:
        # POSIX detach
        kwargs.update(
            dict(
                start_new_session=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )

    try:
        subprocess.Popen(cmd, **kwargs)
        print("\n[knowlify] Started background job; video will save to ./knowlify_videos/")
    except Exception as e:
        print(f"[knowlify] Failed to start background job: {e}")


# ---------------- public API ----------------
def create(
    mode: Mode = "fast",
    wait: bool = False,
    *,
    function: str | None = None,
    task: str | None = None,
) -> str:
    """
    Create a video from:
      • a custom task string:              create(task="...")  <-- overrides everything
      • a specific function by name:       create(function="my_func" | "MyClass.my_func")
      • the code ABOVE this call:          create()  (legacy one-shot)

    Defaults: mode="fast", wait=False (non-blocking).

    Return:
      • "" immediately in non-blocking mode (video downloads to ./knowlify_videos/ in background)
      • video URL string if wait=True (also saved locally).

    Precedence:
      1) If `task` is provided (non-empty), it is sent AS-IS (no code capture, no prompt prefix).
      2) Else if `function` is provided, capture that function's source.
      3) Else capture everything above the call.
    """
    if mode not in ACTION_MAP:
        raise ValueError('mode must be "fast" or "detailed"')
    
    # Check API key is initialized before doing any work
    get_api_key()  # This will raise ValueError if not initialized

    # --- choose what to send as the WS "task" payload ---
    if isinstance(task, str) and task.strip():
        task_text = task  # send exactly what the caller provided
        basename = _generate_video_basename(task_text)
    else:
        if function:
            code = capture_function_by_name(function)
            basename = _generate_video_basename(code, function)
        else:
            code = capture_code_above_call()
            basename = _generate_video_basename(code)
        task_text = build_task_text(code)  # prepend your short teaching instruction + code block

    action = ACTION_MAP[mode]

    if wait:
        # Blocking path: get the URL and save locally
        try:
            asyncio.get_running_loop()
            url = run_coro_in_thread(send_task_over_ws, action, task_text)
        except RuntimeError:
            url = asyncio.run(send_task_over_ws(action, task_text))

        if isinstance(url, str) and url:
            download_mp4_if_possible(url, preferred_basename=basename)
            return url
        return ""

    # Non-blocking path: detached worker continues after the caller returns
    _spawn_detached_worker(action, task_text, basename)
    return ""


def start() -> None:
    """
    Mark the BEGIN of the capture region. Must be closed by end() in the same file.
    """
    begin_region()


def end(mode: Mode = "fast", wait: bool = False) -> str:
    """
    Mark the END of the capture region and trigger video generation on the code
    BETWEEN start() and end().

    Defaults: mode="fast", wait=False (non-blocking; spawns detached worker).

    Returns:
      • "" immediately in non-blocking mode.
      • video URL (string) if wait=True (also saves to ./knowlify_videos/).
    """
    if mode not in ACTION_MAP:
        raise ValueError('mode must be "fast" or "detailed"')
    
    # Check API key is initialized before doing any work
    get_api_key()  # This will raise ValueError if not initialized

    code_region = end_region()
    task_text = build_task_text(code_region)
    basename = _generate_video_basename(code_region)
    action = ACTION_MAP[mode]

    if wait:
        try:
            asyncio.get_running_loop()
            url = run_coro_in_thread(send_task_over_ws, action, task_text)
        except RuntimeError:
            url = asyncio.run(send_task_over_ws(action, task_text))
        if isinstance(url, str) and url:
            download_mp4_if_possible(url, preferred_basename=basename)
            return url
        return ""

    _spawn_detached_worker(action, task_text, basename)
    return ""
