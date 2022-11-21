from typing import Any, Dict


def clean_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove trailing '_' from keys.
    """
    return {k.rstrip("_"): v for k, v in kwargs.items()}
