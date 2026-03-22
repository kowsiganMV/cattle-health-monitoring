"""
Logo utility — loads the logo once and provides base64 HTML snippets
for embedding in login page, sidebar, and navbar.
"""

import base64
import os
from functools import lru_cache

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")


@lru_cache(maxsize=1)
def _logo_b64() -> str:
    """Read and cache the logo as a base64 string (loaded once per process)."""
    with open(_LOGO_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()


def logo_src() -> str:
    """Return a data-URI src string for use in <img> tags."""
    return f"data:image/png;base64,{_logo_b64()}"


def logo_html(height: int = 80, margin: str = "0 auto", extra_style: str = "") -> str:
    """Return a centered <img> tag for the logo at the given height."""
    return (
        f'<img src="{logo_src()}" alt="CHM Logo" '
        f'style="height:{height}px; width:auto; display:block; margin:{margin}; '
        f'object-fit:contain; {extra_style}" />'
    )
