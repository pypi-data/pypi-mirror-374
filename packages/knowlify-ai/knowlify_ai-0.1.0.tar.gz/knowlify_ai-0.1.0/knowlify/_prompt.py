from ._config import PROMPT_PREFIX

def build_task_text(captured_code: str) -> str:
    # Keep it very short; prepend your fixed instruction and then include the code.
    # No extra headers; just the sentence and the code block.
    return f"""{PROMPT_PREFIX}

```python
{captured_code}
```"""
