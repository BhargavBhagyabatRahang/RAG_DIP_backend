from .extractor import extract_pdf
from .ocr import run_ocr_if_needed
from .markdown import build_markdown


def process_pdf(file_path: str, mode: str = "auto") -> str:

    try:
        pages = extract_pdf(file_path)
    except Exception as e:
        raise RuntimeError(f"Extraction failed: {e}")

    results = []

    for page in pages:

        # OCR decision
        if mode in ["ocr", "full"] or (mode == "auto" and len(page["blocks"]) == 0):
            page = run_ocr_if_needed(page)

        page_content = []

        for block in page.get("blocks", []):
            text = block[4] if len(block) > 4 else ""
            if text.strip():
                page_content.append(text)

        # OCR fallback
        if "ocr_text" in page:
            page_content.append(page["ocr_text"])

        results.append(page_content)

    return build_markdown(results)