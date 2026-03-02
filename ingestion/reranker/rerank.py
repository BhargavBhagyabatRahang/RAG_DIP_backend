import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from pathlib import Path


class ONNXReranker:
    def __init__(self, model_dir: str):
        model_path = Path(model_dir) / "model.onnx"

        self.session = ort.InferenceSession(str(model_path))
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)

    def rerank(self, query: str, documents: list[str], top_k: int = 3):
        pairs = [[query, doc] for doc in documents]

        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            return_tensors="np"
        )

        ort_inputs = {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"],
        }

        if "token_type_ids" in inputs:
            ort_inputs["token_type_ids"] = inputs["token_type_ids"]

        outputs = self.session.run(None, ort_inputs)

        scores = outputs[0].flatten()

        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]
