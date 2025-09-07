# knowlify/_auth.py

_api_key: str | None = None

def init(api_key: str) -> None:
    """Initialize Knowlify with your API key.
    
    Args:
        api_key: Your Knowlify API key
        
    Raises:
        ValueError: If api_key is empty or not a string
    """
    global _api_key
    
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("api_key must be a non-empty string")
    
    _api_key = api_key.strip()

def get_api_key() -> str:
    """Get the current API key.
    
    Returns:
        The current API key
        
    Raises:
        ValueError: If no API key has been set via init()
    """
    if _api_key is None:
        raise ValueError(
            "Knowlify API key not initialized. Please call knowlify.init(api_key='your-secret-key') first."
        )
    return _api_key

def is_initialized() -> bool:
    """Check if the API key has been initialized.
    
    Returns:
        True if API key is set, False otherwise
    """
    return _api_key is not None