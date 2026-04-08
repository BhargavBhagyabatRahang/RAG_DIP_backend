from pix2tex.cli import LatexOCR

model = None


def get_model():
    global model
    if model is None:
        try:
            model = LatexOCR()
        except Exception as e:
            print(f"pix2tex model load failed: {e}")
            model = None
    return model


def extract_formula(image):
    try:
        model = get_model()

        if model is None:
            return "[formula]"

        latex = model(image)

        if not latex.strip():
            return "[formula]"

        return f"$$ {latex} $$"

    except Exception as e:
        print(f"Formula extraction failed: {e}")
        return "[formula]"