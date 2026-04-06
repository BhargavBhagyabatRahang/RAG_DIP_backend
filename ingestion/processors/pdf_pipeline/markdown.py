def build_markdown(pages):
    md = ""

    for i, page in enumerate(pages):
        md += f"\n\n# Page {i+1}\n\n"

        for item in page:
            md += item + "\n\n"

    return md