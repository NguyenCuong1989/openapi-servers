import os
import pathlib

# Constants
# ALLOWED_DIRECTORIES can be a comma-separated list of paths via env var.
_default = os.path.expanduser("~/tmp")
_allowed_raw = os.getenv("ALLOWED_DIRECTORIES", _default)
ALLOWED_DIRECTORIES = [
    str(pathlib.Path(os.path.expanduser(p.strip())).resolve())
    for p in _allowed_raw.split(",")
    if p.strip()
]