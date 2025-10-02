import os
from typing import Dict, Any, Optional

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


CATEGORY_TO_FILE = {
    'web': 'web_prompt.yaml',
    'pwn': 'pwn_prompt.yaml',
    'crypto': 'crypto_prompt.yaml',
    'forensics': 'forensics_prompt.yaml',
    'rev': 'rev_prompt.yaml',
    'reversing': 'rev_prompt.yaml',
}


def _prompts_dir() -> str:
    # Resolve relative to this file to be robust to CWD
    return os.path.join(os.path.dirname(__file__), 'prompts')


def load_category_prompts(category: str) -> Optional[Dict[str, str]]:
    """
    Load the baseline prompt YAML for a given category if available.

    Returns a dict with keys like 'system', 'initial', 'continue', 'nc_server_description', 'web_server_description'.
    Returns None if PyYAML is not installed or the file is missing.
    """
    if not category:
        return None

    if yaml is None:
        return None

    filename = CATEGORY_TO_FILE.get(category.lower())
    if not filename:
        return None

    path = os.path.join(_prompts_dir(), filename)
    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            # Normalize keys to strings
            return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}
    except Exception:
        return None


def render_template(template: str, context: Dict[str, Any]) -> str:
    """
    Render a simple Python .format() template with nested keys supported via dotted names
    like {challenge.name}. We implement a simple resolver over a flat mapping.
    """
    if not template:
        return ''

    # Flatten nested context using dotted paths
    flat: Dict[str, Any] = {}

    def _flatten(prefix: str, obj: Any) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = f"{prefix}.{k}" if prefix else str(k)
                _flatten(key, v)
        else:
            flat[prefix] = obj

    _flatten('', context)

    # Remove leading dot entries
    flat = {k.lstrip('.') : v for k, v in flat.items()}

    try:
        return template.format(**flat)
    except Exception:
        # Best-effort: return the raw template if formatting fails
        return template 