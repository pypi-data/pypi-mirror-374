"""
Common utilities for both v1 and v2 API tools.
"""
import os
from typing import Any, Dict

PROMPT_TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompt_template.md")

def get_api_version():
    """Get API version from environment."""
    return os.getenv("AIRFLOW_API_VERSION", "v1").lower()
