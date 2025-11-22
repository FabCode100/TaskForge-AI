import os
from pathlib import Path
from typing import Tuple

from ..core.config import settings


def ensure_storage_path() -> Path:
    p = Path(settings.storage_path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_file(filename: str, data: bytes) -> Tuple[str, str]:
    storage = ensure_storage_path()
    dest = storage / filename
    with open(dest, "wb") as f:
        f.write(data)
    url = str(dest.resolve())
    return filename, url
