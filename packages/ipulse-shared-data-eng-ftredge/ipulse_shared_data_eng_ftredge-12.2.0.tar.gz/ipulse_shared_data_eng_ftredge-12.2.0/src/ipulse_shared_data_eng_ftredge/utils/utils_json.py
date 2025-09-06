# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=logging-fstring-interpolation
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught

import json
import datetime
from typing import Any, Dict, List, Union

def datetime_to_str(obj: Any) -> str:
    """Convert datetime to ISO format string."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, datetime.time):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not serializable")

def make_json_serializable(data: Any) -> Any:
    """
    Recursively convert a Python object to a JSON-serializable form.
    
    Args:
        data: Any Python object to make JSON-serializable
        
    Returns:
        A JSON-serializable version of the input data
    """
    if data is None:
        return None
    elif isinstance(data, (str, int, float, bool)):
        return data
    elif isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
        return datetime_to_str(data)
    elif isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(make_json_serializable(item) for item in data)
    elif isinstance(data, set):
        return list(make_json_serializable(item) for item in data)
    elif hasattr(data, "__dict__"):
        # Handle custom objects by converting to dict
        return make_json_serializable(data.__dict__)
    else:
        # For any other types, convert to string
        return str(data)

def process_data_for_bigquery(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Process data to ensure it's in the format expected by BigQuery's load_table_from_json.
    
    Args:
        data: A dict or list of dicts with data to load
        
    Returns:
        A list of dicts with all values JSON-serializable
    """
    # Ensure data is a list
    if isinstance(data, dict):
        data = [data]
    
    # Make each item in the list JSON-serializable
    return [make_json_serializable(item) for item in data]

def to_json_string(data: Any) -> str:
    """
    Convert any Python object to a JSON string with proper handling of datetimes.
    
    Args:
        data: Any Python object
        
    Returns:
        JSON string representation
    """
    serializable_data = make_json_serializable(data)
    return json.dumps(serializable_data)
