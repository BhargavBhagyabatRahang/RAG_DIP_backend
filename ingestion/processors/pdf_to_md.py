from pathlib import Path
import traceback

from ingestion.processors.pdf_pipeline.orchestrator import process_pdf


def pdf_to_markdown(pdf_path: str, base_output_dir: str, mode: str = "ocr") -> str:
    """
    Convert a PDF to Markdown using custom PDF pipeline.

    Args:
        pdf_path (str): input PDF
        base_output_dir (str): base output directory
        mode (str): processing mode ("auto", "fast", "ocr", "full")

    Returns:
        str: path to generated markdown file
    """

    try:
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Create output directory
        output_dir = Path(base_output_dir) / pdf_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run the pipeline
        md_content = process_pdf(str(pdf_path), mode=mode)

        # Save markdown
        md_file = output_dir / f"{pdf_path.stem}.md"
        md_file.write_text(md_content, encoding="utf-8")

        return str(md_file)

    except Exception as e:
        print("===== PDF PIPELINE ERROR =====")
        traceback.print_exc()

        raise RuntimeError(
            f"PDF to Markdown conversion failed\nReason: {str(e)}"
        )