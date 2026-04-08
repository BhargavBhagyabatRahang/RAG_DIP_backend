from .extractor import extract_pdf
from .ocr import run_ocr_if_needed
from .layout import detect_layout
from .tables import extract_tables
from .formulas import extract_formula
from .markdown import build_markdown

import traceback


def process_pdf(file_path: str, mode: str = "ocr") -> str:

    # SAFE EXTRACTION
    try:
        pages = extract_pdf(file_path)
    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Extraction failed: {e}")

    results = []

    for page_index, page in enumerate(pages):

        # OCR decision
        try:
            if mode in ["ocr", "full"] or (mode == "auto" and len(page["blocks"]) == 0):
                page = run_ocr_if_needed(page)
        except Exception as e:
            print(f"OCR failed on page {page_index}: {e}")

        page_content = []

        # Layout detection
        try:
            layout_blocks = detect_layout(page)
        except Exception as e:
            print(f"Layout failed: {e}")
            layout_blocks = []

        # If layout fails → fallback to raw blocks
        if not layout_blocks:
            for block in page.get("blocks", []):
                text = block[4] if len(block) > 4 else ""
                if text.strip():
                    page_content.append(text)

        else:
            for block in layout_blocks:

                try:
                    if block["type"] == "Table":
                        table_md = extract_tables(file_path, page_index + 1)
                        if table_md:
                            page_content.append(table_md)

                    elif block["type"] == "Equation":
                        formula = extract_formula(page["image"])
                        page_content.append(formula)

                    else:
                        page_content.append("[text block]")

                except Exception as e:
                    print(f"Block processing failed: {e}")

        # OCR fallback
        if "ocr_text" in page:
            page_content.append(page["ocr_text"])

        results.append(page_content)

    return build_markdown(results)