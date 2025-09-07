import os

# Endpoint can be overridden for staging if needed
WS_URL = os.environ.get(
    "KNOWLIFY_WS_URL",
    "wss://50fa8sjxo9.execute-api.us-west-2.amazonaws.com/production",
)

# User-facing mode -> backend action mapping
ACTION_MAP = {
    "fast": "finetuned_live_gen",
    "detailed": "Pre-Rendered",
}

# Keep this short (per your instruction).
PROMPT_PREFIX = (
    "Explain this code using a balance of visuals and other teaching elements "
    "to clearly cover the concepts and the implementation."
)

# Hard cap to avoid oversize payloads
MAX_CAPTURE_LINES = 500
