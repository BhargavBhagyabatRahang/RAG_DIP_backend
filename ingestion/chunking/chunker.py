import uuid
import requests
import re

# -------------------------------
# 1) Section Splitter
# -------------------------------
def split_by_sections(markdown_text):
    sections = []
    header_pattern = re.compile(r'^(#+)\s+(.*)$', re.MULTILINE)

    matches = list(header_pattern.finditer(markdown_text))
    if not matches:
        return [{"section": "Full Document", "text": markdown_text}]

    for i, match in enumerate(matches):
        section_name = match.group(2).strip()
        start_pos = match.start()
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(markdown_text)
        section_content = markdown_text[start_pos:end_pos].strip()

        sections.append({
            "section": section_name,
            "text": section_content
        })

    return sections


# -------------------------------
# 2) Context Generator (same)
# -------------------------------
def generate_contextual_explanation(full_doc: str, chunk_text: str):
    model_name = "Refinery_LLM:latest"
    doc_summary = full_doc[:5000]

    prompt = f"""You are a refinery engineering assistant.
Generate ONE precise technical context sentence (max 25 words).

Focus on:
- equipment
- process
- engineering purpose

DOCUMENT SUMMARY:
{doc_summary}

CHUNK:
{chunk_text}

Context:"""

    try:
        response = requests.post(
            "http://ollama:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=60
        )
        return response.json().get("response", "").strip()
    except Exception:
        return "Refinery engineering content."


# -------------------------------
# 3) Main Chunker
# -------------------------------
def chunk_markdown(markdown_text: str, source_file: str, max_chars: int = 800, contextualize: bool = True):
    sections = split_by_sections(markdown_text)
    chunk_objects = []
    global_idx = 0

    for section in sections:
        section_name = section["section"]
        text = section["text"]

        # Splitting into atoms
        atoms = re.split(r'\n\s*\n', text)

        current_chunk_text = ""

        for atom in atoms:
            atom = atom.strip()
            if not atom:
                continue

            # -------------------------------
            # Handling LARGE atoms
            # -------------------------------
            if len(atom) > max_chars:
                sub_atoms = [
                    atom[i:i + max_chars]
                    for i in range(0, len(atom), max_chars)
                ]
            else:
                sub_atoms = [atom]

            for sub_atom in sub_atoms:

                # -------------------------------
                # Safe merging
                # -------------------------------
                if len(current_chunk_text) + len(sub_atom) > max_chars and current_chunk_text:

                    chunk_objects.append(
                        create_chunk_obj(
                            current_chunk_text,
                            section_name,
                            source_file,
                            global_idx,
                            markdown_text,
                            contextualize
                        )
                    )

                    global_idx += 1

                    # -------------------------------
                    # Smart overlapping
                    # -------------------------------
                    overlap_text = current_chunk_text[-150:]
                    current_chunk_text = overlap_text + "\n\n" + sub_atom

                else:
                    if current_chunk_text:
                        current_chunk_text += "\n\n" + sub_atom
                    else:
                        current_chunk_text = sub_atom

        # Final chunks in section
        if current_chunk_text:
            chunk_objects.append(
                create_chunk_obj(
                    current_chunk_text,
                    section_name,
                    source_file,
                    global_idx,
                    markdown_text,
                    contextualize
                )
            )
            global_idx += 1

    return chunk_objects


# -------------------------------
# 4) Chunk Object Creator
# -------------------------------
def create_chunk_obj(raw_text, section_name, source_file, idx, full_doc, contextualize):

    context = ""

    if contextualize:
        print(f"Contextualizing Chunk {idx}...")
        context = generate_contextual_explanation(full_doc, raw_text)

        # -------------------------------
        # Section-aware context
        # -------------------------------
        final_content = f"CONTEXT: {section_name} - {context}\n\nCONTENT: {raw_text}"

    else:
        final_content = raw_text

    # -------------------------------
    # Table hint
    # -------------------------------
    if "|" in raw_text:
        context += " Contains tabular data."

    return {
        "chunk_id": str(uuid.uuid4()),
        "chunk_index": idx,
        "text": final_content,
        "metadata": {
            "source_file": source_file,
            "section_name": section_name,
            "chunk_index": idx,
            "original_text": raw_text,
            "contextual_summary": context
        }
    }