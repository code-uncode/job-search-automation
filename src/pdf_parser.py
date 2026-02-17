import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a given PDF file path."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The PDF file at {pdf_path} was not found.")
    
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

if __name__ == "__main__":
    # Example usage (for local testing)
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            print(extract_text_from_pdf(path))
        except Exception as e:
            print(f"Error: {e}")
