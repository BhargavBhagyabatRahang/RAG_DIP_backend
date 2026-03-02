import os


EXTENSION_MAP = {
    "pdf": [".pdf"],
    "docx": [".docx", ".doc"],
    "ppt": [".ppt", ".pptx"],
    "xlsx": [".xls", ".xlsx"],
    "txt": [".txt"],
    "images": [".png", ".jpg", ".jpeg", ".tiff", ".bmp",".svg"],
}


def detect_file_category(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    for category, extensions in EXTENSION_MAP.items():
        if ext in extensions:
            return category

    return "others"
