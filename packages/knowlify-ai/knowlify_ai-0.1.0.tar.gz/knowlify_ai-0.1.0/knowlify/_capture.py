# knowlify/_capture.py

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Optional, Tuple, Dict, List

from ._config import MAX_CAPTURE_LINES


class KnowlifyError(Exception):
    """Capture-related error."""


class KnowlifyAPIError(Exception):
    """Base API-related error."""
    
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


class InvalidAPIKeyError(KnowlifyAPIError):
    """Raised when the API key is invalid."""
    
    def __init__(self):
        super().__init__("Invalid API key", 401)


class OutOfMinutesError(KnowlifyAPIError):
    """Raised when the account is out of minutes."""
    
    def __init__(self):
        super().__init__("Ran out of minutes", 403)


# -----------------------------
# Active region (start/end) state
# -----------------------------
_region_session: Optional[dict] = None  # {"filename": str, "start_line": int}


# -----------------------------
# Helpers
# -----------------------------
def _caller_user_frame(depth: int = 2):
    """
    Walk up the stack to the user's frame.
      - create(): this -> capture_code_above_call -> _api.create -> user
      - start():  this -> begin_region           -> _api.start   -> user
      - end():    this -> end_region             -> _api.end     -> user
    """
    frame = inspect.currentframe()
    for _ in range(depth):
        if frame is None:
            break
        frame = frame.f_back
    return frame


def _read_source_lines(filename: str) -> List[str]:
    path = Path(filename)
    if not path.exists():
        raise KnowlifyError(f"Source file not found: {path}")
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


# -----------------------------
# Region capture: start()/end()
# -----------------------------
def begin_region() -> None:
    """
    Mark the beginning of a capture region at the caller's location.
    Must later be closed with end() in the same file.
    """
    global _region_session
    if _region_session is not None:
        raise KnowlifyError("A knowlify.start() is already active; call knowlify.end() first.")

    user_frame = _caller_user_frame(depth=2)  # _api.start -> user
    if user_frame is None:
        raise KnowlifyError("Unable to locate caller frame for start().")

    filename = user_frame.f_code.co_filename
    lineno = int(user_frame.f_lineno)  # 1-based line where start() is called

    if not filename or filename == "<stdin>":
        raise KnowlifyError("Could not determine source file. Run from a .py script for v0.")

    _region_session = {
        "filename": str(Path(filename)),
        "start_line": lineno,  # capture begins AFTER this line
    }


def end_region() -> Tuple[str, Dict[str, int | str]]:
    """
    Close the active capture region and return (code, meta).

    Returns:
        code: str  -> code BETWEEN start() and end() (excludes both lines)
        meta: dict -> {"filename": str, "start_line": int, "end_line": int}

    Enforces: a start() exists, same file, and end() is after start().
    """
    global _region_session
    if _region_session is None:
        raise KnowlifyError("knowlify.end() called without a matching knowlify.start().")

    sess = _region_session

    user_frame = _caller_user_frame(depth=2)  # _api.end -> user
    if user_frame is None:
        _region_session = None
        raise KnowlifyError("Unable to locate caller frame for end().")

    filename = user_frame.f_code.co_filename
    end_line = int(user_frame.f_lineno)  # 1-based line of end() call

    if not filename or filename == "<stdin>":
        _region_session = None
        raise KnowlifyError("Could not determine source file. Run from a .py script for v0.")

    if str(Path(filename)) != sess["filename"]:
        _region_session = None
        raise KnowlifyError("knowlify.start() and knowlify.end() must be in the same source file.")

    lines = _read_source_lines(filename)

    # Slice between the two calls:
    # - start_line: line with start(); capture begins on the *next* line
    # - end_line:   line with end();   capture ends on the *previous* line
    start_idx = min(len(lines), int(sess["start_line"]))  # first line AFTER start()
    end_idx = max(0, end_line - 1)                        # last line BEFORE end()

    if end_idx < start_idx:
        _region_session = None
        raise KnowlifyError("knowlify.end() appears before knowlify.start() in the file.")

    region = lines[start_idx:end_idx]

    # Cap length (keep most recent lines if over cap)
    if len(region) > MAX_CAPTURE_LINES:
        region = region[-MAX_CAPTURE_LINES:]

    meta = {
        "filename": str(Path(filename)),
        "start_line": int(sess["start_line"]),
        "end_line": end_line,
    }

    _region_session = None  # clear session
    return "\n".join(region), meta


# -----------------------------
# One-shot capture: create()
# -----------------------------
def capture_code_above_call() -> str:
    """
    Return everything ABOVE the line that calls knowlify.create(...).
    Excludes the create() line; respects MAX_CAPTURE_LINES (most recent lines).
    """
    user_frame = _caller_user_frame(depth=2)  # _api.create -> user
    if user_frame is None:
        raise KnowlifyError("Unable to locate caller frame.")

    filename = user_frame.f_code.co_filename
    lineno = int(user_frame.f_lineno)  # line where create() is called

    if not filename or filename == "<stdin>":
        raise KnowlifyError("Could not determine source file. Run from a script file for v0.")

    lines = _read_source_lines(filename)
    above = lines[: max(0, lineno - 1)]

    if len(above) > MAX_CAPTURE_LINES:
        above = above[-MAX_CAPTURE_LINES:]

    return "\n".join(above)


# -----------------------------
# Function-targeted capture
# -----------------------------
def capture_function_by_name(func_name: str) -> str:
    """
    Capture the source for a specific function in the caller's file.

    Supports:
      - Top-level functions:         "my_func"
      - Class methods (one level):   "MyClass.my_method"

    If multiple matches exist (e.g., redefinitions), prefers the one defined
    closest *before* the call site; falls back to the first match.

    Respects MAX_CAPTURE_LINES; truncates from the end if needed.
    """
    user_frame = _caller_user_frame(depth=2)  # _api.create -> user
    if user_frame is None:
        raise KnowlifyError("Unable to locate caller frame.")

    filename = user_frame.f_code.co_filename
    call_lineno = int(user_frame.f_lineno)
    if not filename or filename == "<stdin>":
        raise KnowlifyError("Could not determine source file. Run from a script file for v0.")

    src_path = Path(filename)
    if not src_path.exists():
        raise KnowlifyError(f"Source file not found: {src_path}")

    src = src_path.read_text(encoding="utf-8", errors="ignore")
    lines = src.splitlines()
    try:
        tree = ast.parse(src, filename=str(src_path))
    except SyntaxError as e:
        raise KnowlifyError(f"Failed to parse file to locate function '{func_name}': {e}") from e

    target_class: Optional[str] = None
    target_func: str = func_name
    if "." in func_name:
        parts = func_name.split(".", 1)
        if len(parts) == 2:
            target_class, target_func = parts[0], parts[1]

    candidates: List[ast.FunctionDef] = []

    if target_class:
        # Find a class with that name, then a method within
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == target_class:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == target_func:
                        candidates.append(item)
    else:
        # Top-level def
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == target_func:
                candidates.append(node)

    if not candidates:
        raise KnowlifyError(f"Function '{func_name}' not found in {src_path.name}.")

    # Prefer the one defined closest BEFORE the call site; otherwise first entry
    def sort_key(n: ast.FunctionDef):
        ln = int(getattr(n, "lineno", 10**9))
        return (0 if ln <= call_lineno else 1, -ln)

    candidates.sort(key=sort_key)
    node = candidates[0]

    # Determine slice bounds
    start_idx = max(0, int(getattr(node, "lineno", 1)) - 1)  # inclusive start (def line)
    end_lineno = getattr(node, "end_lineno", None)

    if end_lineno is None:
        # Fallback: indentation-based scan to find the end of the block
        def_line = lines[start_idx] if start_idx < len(lines) else ""
        base_indent = len(def_line) - len(def_line.lstrip())
        j = start_idx + 1
        while j < len(lines):
            line = lines[j]
            if line.strip() == "":
                j += 1
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent:
                break
            j += 1
        end_idx = j  # exclusive
    else:
        # AST's end_lineno is inclusive; convert to exclusive
        end_idx = min(len(lines), int(end_lineno))

    code_lines = lines[start_idx:end_idx]

    if len(code_lines) > MAX_CAPTURE_LINES:
        code_lines = code_lines[:MAX_CAPTURE_LINES]

    return "\n".join(code_lines)
