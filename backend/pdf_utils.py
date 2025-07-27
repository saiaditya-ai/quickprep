"""
PDF Text Extraction using PyMuPDF
Extracts clean text from PDF files for flashcard generation
"""

import fitz  # PyMuPDF
from typing import Dict
import re

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extract text from PDF using PyMuPDF

    Args:
        pdf_content: PDF file content as bytes

    Returns:
        Extracted text as string
    """
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=pdf_content, filetype="pdf")

        text_content = []

        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Extract text with proper sorting for reading order
            text = page.get_text(sort=True)

            if text.strip():  # Only add non-empty pages
                text_content.append(text)

        doc.close()

        # Join all pages with page breaks
        full_text = "\n\n".join(text_content)

        # Clean up the text
        cleaned_text = clean_text(full_text)

        return cleaned_text

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def clean_text(text: str) -> str:
    """
    Clean extracted text for better processing

    Args:
        text: Raw text from PDF

    Returns:
        Cleaned text
    """
    # Remove excessive whitespace and newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n ', '\n', text)  # Newline followed by space

    # Remove special characters that might interfere with processing
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)

    # Remove page numbers and common PDF artifacts
    text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)  # Numbers at end of lines

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    return text.strip()

def get_text_metadata(pdf_content: bytes) -> Dict:
    """
    Extract metadata from PDF

    Args:
        pdf_content: PDF file content as bytes

    Returns:
        Dictionary with PDF metadata
    """
    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")

        metadata = {
            "page_count": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "modification_date": doc.metadata.get("modDate", "")
        }

        doc.close()
        return metadata

    except Exception as e:
        return {"error": f"Failed to extract metadata: {str(e)}"}
