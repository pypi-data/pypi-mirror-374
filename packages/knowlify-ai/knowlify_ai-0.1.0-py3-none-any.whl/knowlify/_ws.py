import asyncio
import json
import os
import websockets
from ._config import WS_URL
from ._utils import extract_url
from ._auth import get_api_key
from ._capture import InvalidAPIKeyError, OutOfMinutesError



async def send_task_over_ws(action: str, task: str) -> str | None:
    """
    Connects to the WS endpoint, sends payload, listens for messages, and tries
    to extract a final video URL. Returns the URL (str) or None.
    """
    # Validate parameters
    if not action or not isinstance(action, str):
        raise ValueError("action must be a non-empty string")
    if not task or not isinstance(task, str):
        raise ValueError("task must be a non-empty string")
    
    # Get API key (this will raise ValueError if not initialized)
    api_key = get_api_key()
    
    payload = {
        "action": action,
        "task": task,
        "api_key": api_key,
    }

    # Connect and stream messages
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps(payload))

        final_url: str | None = None

        while True:
            try:
                msg = await ws.recv()
            except websockets.exceptions.ConnectionClosed:
                break

            # Prefer JSON messages
            try:
                obj = json.loads(msg)
            except (json.JSONDecodeError, TypeError):
                obj = None

            if isinstance(obj, dict):
                # Check for API errors first
                if "error" in obj:
                    error_msg = obj.get("error", "")
                    status_code = obj.get("status_code", 0)
                    
                    if error_msg == "Invalid API key" and status_code == 401:
                        raise InvalidAPIKeyError()
                    elif error_msg == "Ran out of minutes" and status_code == 403:
                        raise OutOfMinutesError()
                
                # Common fields we might see
                for key in ("video_url", "url", "link", "final_url"):
                    if key in obj and isinstance(obj[key], str):
                        final_url = obj[key]
                        # If we already have the URL, we can stop listening
                        # Optionally, we could send a close frame; just break and let context manager close.
                        return final_url
                # If no URL in JSON, try to extract from any text fields
                for v in obj.values():
                    if isinstance(v, str):
                        maybe = extract_url(v)
                        if maybe:
                            final_url = maybe
                            return final_url
            else:
                # Non-JSON message; regex for a URL
                maybe = extract_url(str(msg))
                if maybe:
                    final_url = maybe
                    return final_url

        return final_url
