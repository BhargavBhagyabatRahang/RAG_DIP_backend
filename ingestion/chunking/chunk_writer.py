import os
import json

def save_chunks(chunks, base_name, chunk_dir):

    if not os.path.exists(chunk_dir):
        os.makedirs(chunk_dir, exist_ok=True)

    saved_files = []

    for chunk in chunks:
        # Using padded index for easy sorting (001, 002...)
        filename = f"chunk_{chunk['chunk_index']:03}.json"
        path = os.path.join(chunk_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            # indent=4 makes it readable for peers to review manually
            json.dump(chunk, f, indent=4, ensure_ascii=False)

        saved_files.append(path)

    return saved_files