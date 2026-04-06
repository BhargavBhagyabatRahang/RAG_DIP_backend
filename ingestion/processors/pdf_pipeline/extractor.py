import fitz  # PyMuPDF


def extract_pdf(path):
    doc = fitz.open(path)
    pages = []

    for page in doc:
        blocks = page.get_text("blocks")

        pages.append({
            "blocks": blocks,
            "image": page.get_pixmap()
        })

    return pages