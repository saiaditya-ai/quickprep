import fitz

def extract_text_from_pdf(path: str) -> str:
    with fitz.open(path) as doc:
        return "".join(page.get_text() for page in doc)
