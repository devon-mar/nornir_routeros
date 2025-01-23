from typing import Any


def clean_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Remove trailing '_' from keys.
    """
    return {k.rstrip("_"): v for k, v in kwargs.items()}
