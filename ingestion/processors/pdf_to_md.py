from pathlib import Path
import traceback

from ingestion.processors.pdf_pipeline.orchestrator import process_pdf


def pdf_to_markdown(pdf_path: str, base_output_dir: str = None, mode: str = "auto") -> str:
    """
    Convert a PDF to Markdown using custom pipeline.

    Output path (hardcoded):
    <project_root>/data/markdown/<pdf_name>/<pdf_name>/hybrid_auto/<pdf_name>.md
    """

    try:
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        pdf_name = pdf_path.stem

        # Resolve project root 
        project_root = Path(__file__).resolve().parents[3]

        # Build hardcoded directory structure
        output_dir = (
            project_root
            / "data"
            / "markdown"
            / pdf_name
            / pdf_name
            / "hybrid_auto"
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        #  Run pipeline
        md_content = process_pdf(str(pdf_path), mode="auto")

        #  Final markdown file
        md_file = output_dir / f"{pdf_name}.md"
        md_file.write_text(md_content, encoding="utf-8")

        return str(md_file)

    except Exception as e:
        print("===== PDF PIPELINE ERROR =====")
        traceback.print_exc()

        raise RuntimeError(
            f"PDF to Markdown conversion failed\nReason: {str(e)}"
        )