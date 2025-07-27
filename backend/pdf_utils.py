"""
PDF Text Extraction using PyPDF2
Extracts clean text from PDF files for flashcard generation
"""

import PyPDF2
from typing import Dict
import re
import io

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extract text from PDF using PyPDF2

    Args:
        pdf_content: PDF file content as bytes

    Returns:
        Extracted text as string
    """
    try:
        # Create a BytesIO object from the PDF content
        pdf_stream = io.BytesIO(pdf_content)
        
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_stream)

        text_content = []

        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            
            # Extract text from the page
            text = page.extract_text()

            if text.strip():  # Only add non-empty pages
                text_content.append(text)

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
        pdf_stream = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)

        metadata = {
            "page_count": len(pdf_reader.pages),
            "title": pdf_reader.metadata.get("/Title", "") if pdf_reader.metadata else "",
            "author": pdf_reader.metadata.get("/Author", "") if pdf_reader.metadata else "",
            "subject": pdf_reader.metadata.get("/Subject", "") if pdf_reader.metadata else "",
            "creator": pdf_reader.metadata.get("/Creator", "") if pdf_reader.metadata else "",
            "producer": pdf_reader.metadata.get("/Producer", "") if pdf_reader.metadata else "",
            "creation_date": pdf_reader.metadata.get("/CreationDate", "") if pdf_reader.metadata else "",
            "modification_date": pdf_reader.metadata.get("/ModDate", "") if pdf_reader.metadata else ""
        }

        return metadata

    except Exception as e:
        return {"error": f"Failed to extract metadata: {str(e)}"}
