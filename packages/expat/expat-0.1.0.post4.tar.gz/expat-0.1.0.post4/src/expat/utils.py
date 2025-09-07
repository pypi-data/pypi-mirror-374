import hashlib
from pathlib import Path


def hash_file(path: Path) -> str:
    hasher = hashlib.md5()

    with path.open("rb") as f:
        file_content = f.read()

    hasher.update(file_content)

    return hasher.hexdigest()
