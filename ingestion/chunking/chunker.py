import uuid
import requests
import re

# -------------------------------
# 0) TABLE DETECTION
# -------------------------------
def is_table_block(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if len(lines) < 2:
        return False

    pipe_lines = sum(1 for line in lines if "|" in line or "\t" in line)
    return pipe_lines >= len(lines) * 0.6  

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
            "http://vllm:10000/v1/chat/completions",
             json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a refinery engineering assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "top_p":0.9,
                "max_token":4096
            },
            timeout=60
        )
        return response.json()["choices"][0]["message"]["reasoning"].strip()
    except Exception:
        return "Refinery engineering content."


# -------------------------------
# 3) Main Chunker (UPDATED)
# -------------------------------
def chunk_markdown(markdown_text: str, source_file: str, max_chars: int = 800, contextualize: bool = True):
    sections = split_by_sections(markdown_text)
    chunk_objects = []
    global_idx = 0

    for section in sections:
        section_name = section["section"]
        text = section["text"]

        atoms = re.split(r'\n\s*\n', text)

        current_chunk_text = ""

        for atom in atoms:
            atom = atom.strip()
            if not atom:
                continue

            # -------------------------------
            # TABLE HANDLING 
            # -------------------------------
            if is_table_block(atom):

                # Flush existing chunk first
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
                    current_chunk_text = ""

                # Add table as atomic chunk
                chunk_objects.append(
                    create_chunk_obj(
                        atom,
                        section_name,
                        source_file,
                        global_idx,
                        markdown_text,
                        contextualize
                    )
                )
                global_idx += 1
                continue

            # -------------------------------
            # Handling LARGE atoms 
            # -------------------------------
            if len(atom) > max_chars:
                sentences = re.split(r'(?<=[.!?])\s+', atom)
                sub_atoms = []
                temp = ""

                for sent in sentences:
                    if len(temp) + len(sent) <= max_chars:
                        temp += " " + sent
                    else:
                        sub_atoms.append(temp.strip())
                        temp = sent
                if temp:
                    sub_atoms.append(temp.strip())
            else:
                sub_atoms = [atom]

            for sub_atom in sub_atoms:

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

                    overlap_text = current_chunk_text[-150:]
                    current_chunk_text = overlap_text + "\n\n" + sub_atom

                else:
                    if current_chunk_text:
                        current_chunk_text += "\n\n" + sub_atom
                    else:
                        current_chunk_text = sub_atom

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

        final_content = f"CONTEXT: {section_name} - {context}\n\nCONTENT: {raw_text}"

    else:
        final_content = raw_text

    # Table hint
    if "|" in raw_text or "\t" in raw_text:
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