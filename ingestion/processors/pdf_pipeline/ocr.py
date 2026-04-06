import pytesseract
import numpy as np


def run_ocr_if_needed(page):
    try:
        pix = page["image"]

        img = np.frombuffer(pix.samples, dtype=np.uint8)
        img = img.reshape(pix.height, pix.width, pix.n)

        text = pytesseract.image_to_string(img)

        page["ocr_text"] = text

    except Exception as e:
        print(f"OCR failed: {e}")
        page["ocr_text"] = ""

    return page