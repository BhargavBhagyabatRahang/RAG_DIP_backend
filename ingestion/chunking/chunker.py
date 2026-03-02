import uuid
import re

def chunk_markdown(markdown_text: str, source_file: str, max_chars: int = 500, overlap: int = 50):
    """
    Splits markdown into chunks with Line Numbers and Section Headings.
    Ensuring 'chunk_index' is present to fix the KeyError.
    """
    lines = markdown_text.splitlines()
    chunks_data = []
    
    current_text = ""
    current_section = "Introduction"
    start_line = 1
    
    for i, line in enumerate(lines, 1):
        # Updating section if a header is found
        if line.startswith('#'):
            current_section = line.lstrip('#').strip()

        # Checking if adding this line exceeds the limit
        if len(current_text) + len(line) > max_chars and current_text:
            chunks_data.append({
                "text": current_text.strip(),
                "section": current_section,
                "line_start": start_line
            })
            # Starting new chunk with overlap for context continuity
            current_text = current_text[-overlap:] + "\n" + line + "\n"
            start_line = i
        else:
            if not current_text:
                start_line = i
            current_text += line + "\n"

    # Capturing the last remaining chunk
    if current_text.strip():
        chunks_data.append({
            "text": current_text.strip(),
            "section": current_section,
            "line_start": start_line
        })

    # Final transformation into the object format API/Writer expects
    chunk_objects = []
    for idx, data in enumerate(chunks_data):
        chunk_objects.append({
            "chunk_id": str(uuid.uuid4()),
            "chunk_index": idx,  
            "text": data["text"],
            "metadata": {
                "source_file": f"{source_file}.md",
                "section_name": data["section"],
                "line_number": data["line_start"],
                "location_trace": f"Section: {data['section']}, Line: {data['line_start']}",
                "chunk_index": idx,
                "project": "Intelligent Process Knowledge System"
            }
        })

    return chunk_objects