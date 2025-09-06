import json
import logging
from datetime import datetime
from uuid import UUID
from typing import Any, Dict, List, Union

from pydantic import BaseModel

LOGGER = logging.getLogger(__name__)


def sanitize_json(obj: Any) -> Any:
    """
    Recursively sanitize a JSON object to ensure all values are serializable.
    Converts special types like URL objects, UUIDs, datetimes, etc. to strings.

    Args:
        obj: Any Python object to be sanitized

    Returns:
        A JSON-serializable representation of the input object
    """
    # Handle None
    if obj is None:
        return None

    # Handle dictionaries - recursively process each key-value pair
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}

    # Handle lists - recursively process each item
    elif isinstance(obj, list):
        return [sanitize_json(item) for item in obj]

    # Handle Pydantic models - convert to dict and then sanitize
    elif isinstance(obj, BaseModel):
        return sanitize_json(obj.model_dump())

    # Handle URL objects - check by attribute or string pattern
    # URL objects typically have these attributes or string format
    elif (hasattr(obj, "scheme") and hasattr(obj, "host")) or (
        isinstance(obj, str)
        and (obj.startswith("http://") or obj.startswith("https://"))
    ):
        return str(obj)

    # Handle common non-serializable types
    elif isinstance(obj, (datetime, UUID)):
        return str(obj)

    # Handle any other objects that have string representation but aren't primitive types
    elif not isinstance(obj, (str, int, float, bool, type(None))):
        try:
            # Try to convert to string, if it has a meaningful string representation
            LOGGER.debug(f"Converting {type(obj).__name__} to string: {obj}")
            return str(obj)
        except Exception as e:
            LOGGER.warning(f"Could not convert {type(obj).__name__} to string: {e}")
            return None

    # Return primitive types unchanged
    return obj


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex

        if isinstance(obj, datetime):
            # if the obj is datetime, we return the isoformat string
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
