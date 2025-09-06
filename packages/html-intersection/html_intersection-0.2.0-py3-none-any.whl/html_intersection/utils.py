import os
from typing import Optional


def read_file_with_fallback_encoding(file_path: str) -> Optional[str]:
    encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


def write_file_with_encoding(file_path: str, content: str) -> bool:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def list_html_files(directory: str) -> list[str]:
    if not os.path.isdir(directory):
        return []
    return [
        filename
        for filename in os.listdir(directory)
        if filename.endswith(".html")
    ]


