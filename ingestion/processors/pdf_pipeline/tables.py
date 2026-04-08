import camelot


def extract_tables(pdf_path, page_number=1):
    try:
        tables = camelot.read_pdf(
            pdf_path,
            pages=str(page_number),
            flavor="lattice"  # good for structured tables
        )

        if tables.n == 0:
            return ""

        return tables[0].df.to_markdown()

    except Exception as e:
        print(f"Table extraction failed: {e}")
        return ""  # fallback