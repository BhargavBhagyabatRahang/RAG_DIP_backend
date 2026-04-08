import layoutparser as lp

model = None

def get_model():
    global model
    if model is None:
        try:
            model = lp.Detectron2LayoutModel(
                'lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config'
            )
        except Exception as e:
            print(f"Layout model load failed: {e}")
            model = None
    return model


def detect_layout(page):
    try:
        model = get_model()

        if model is None:
            return []  # fallback

        image = page["image"]
        layout = model.detect(image)

        blocks = []
        for b in layout:
            blocks.append({
                "type": b.type,
                "bbox": b.coordinates
            })

        return blocks

    except Exception as e:
        print(f"Layout detection failed: {e}")
        return []  # fallback