import os
from pathlib import Path

EXTENSION_MAP = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "docx",
    ".pptx": "pptx",
    ".ppt": "pptx",
    ".xlsx": "xlsx",
    ".xls": "xlsx",
    ".txt": "txt",
    ".jpg": "images",
    ".jpeg": "images",
    ".png": "images",
}

def get_upload_subdir(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return EXTENSION_MAP.get(ext, "others")
