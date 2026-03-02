import subprocess
from pathlib import Path


def pdf_to_markdown(pdf_path: str, base_output_dir: str) -> str:
    """
    Convert a PDF to Markdown using MinerU CLI.
    MinerU generates files on disk; this function returns
    the absolute path of the generated .md file.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Create per-document output directory
    output_dir = Path(base_output_dir) / pdf_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    # MinerU CLI command
    cmd = [
        "mineru",
        "--path", str(pdf_path),
        "-o", str(output_dir)
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # DEBUG (optional – keep for now)
        print("===== MinerU STDOUT =====")
        print(result.stdout)
        print("===== MinerU STDERR =====")
        print(result.stderr)

        # MinerU creates nested folders → search recursively
        md_files = list(output_dir.rglob("*.md"))
        if not md_files:
            raise RuntimeError("MinerU did not generate a Markdown file")

        # Return the first markdown file found
        return str(md_files[0])

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"MinerU CLI failed\n"
            f"STDOUT:\n{e.stdout}\n"
            f"STDERR:\n{e.stderr}"
        )
