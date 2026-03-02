import requests
from pathlib import Path

LIBREOFFICE_URL = "http://gotenberg:3000/forms/libreoffice/convert"

SUPPORTED_CONVERTIBLE_EXTENSIONS = (
    ".docx", ".doc", ".pptx", ".ppt",
    ".txt", ".xlsx",
    ".pdf", ".jpg", ".png", ".jpeg", ".svg"
)

def convert_to_pdf(input_path: str, output_dir: str) -> str:
    input_path = Path(input_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.suffix.lower() == ".pdf":
        return str(input_path)

    with open(input_path, "rb") as f:
        files = {"files": (input_path.name, f)}

        try:
            response = requests.post(LIBREOFFICE_URL, files=files)
            response.raise_for_status()

            pdf_path = output_dir / (input_path.stem + ".pdf")

            with open(pdf_path, "wb") as out_file:
                out_file.write(response.content)

            return str(pdf_path)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Communication error with LibreOffice service: {e}"
            )
