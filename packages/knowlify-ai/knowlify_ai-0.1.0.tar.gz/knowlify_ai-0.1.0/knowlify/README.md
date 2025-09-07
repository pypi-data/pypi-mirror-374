# Knowlify Python SDK

Turn your Python code into explanatory videos with a simple function call.

## Installation

```bash
pip install knowlify-ai
```

## Quick Start

```python
import knowlify

# Initialize with your API key
knowlify.init(api_key="your-api-key-here")

# Create a video from code above this call
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Generate video
knowlify.create()  # defaults to "fast" mode
```

## API Reference

### `knowlify.init(api_key: str)`

Initialize Knowlify with your API key.

**Parameters:**
- `api_key` (str): Your Knowlify API key

**Example:**
```python
knowlify.init(api_key="your-secret-key")
```

### `knowlify.create(mode="fast", wait=False, *, function=None, task=None)`

Create a video from your code.

**Parameters:**
- `mode` (str): Video generation mode - `"fast"` or `"detailed"` (default: `"fast"`)
- `wait` (bool): Whether to wait for completion (default: `False`)
- `function` (str, optional): Specific function name to capture (e.g., `"my_func"` or `"MyClass.method"`)
- `task` (str, optional): Custom task description (overrides code capture)

**Returns:**
- `str`: Video URL if `wait=True`, empty string if `wait=False`

**Examples:**

```python
# Capture code above the call
knowlify.create()

# Capture specific function
knowlify.create(function="fibonacci")

# Capture class method
knowlify.create(function="MyClass.calculate")

# Custom task
knowlify.create(task="explain this sorting algorithm")

# Detailed mode with wait
url = knowlify.create(mode="detailed", wait=True)
print(f"Video URL: {url}")
```

### `knowlify.start()` and `knowlify.end(mode="fast", wait=False)`

Capture code between start and end markers.

**Example:**
```python
knowlify.start()

# Your code here
def complex_algorithm():
    # ... complex logic ...
    return result

knowlify.end()  # Generates video of code between start() and end()
```

## Modes

- **`"fast"`**: Quick generation, good for simple explanations
- **`"detailed"`**: More comprehensive, better for complex topics

## Error Handling

```python
import knowlify

try:
    knowlify.create()
except knowlify.InvalidAPIKeyError:
    print("Invalid API key")
except knowlify.OutOfMinutesError:
    print("Out of minutes")
except knowlify.KnowlifyAPIError as e:
    print(f"API error: {e}")
```

## Output

- **Non-blocking mode** (`wait=False`): Videos save to `./knowlify_videos/` in background
- **Blocking mode** (`wait=True`): Returns video URL and saves locally

## Requirements

- Python 3.8+
- Valid Knowlify API key
## License

MIT License - see LICENSE file for details.

## Support

Visit [knowlify.com](https://knowlify.com) for more information.