import os, tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from pdf_utils import extract_text_from_pdf
from hf_client import generate_flashcards, get_embedding
from db import save_flashcard

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "QuickPrep backend (HF edition) online"}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Upload a PDF")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    text = extract_text_from_pdf(path)
    if not text.strip():
        raise HTTPException(400, "Could not extract text")

    flashcards = generate_flashcards(text)
    if not flashcards:
        raise HTTPException(500, "Flashcard generation failed")

    # Use a default user_id since we removed auth
    default_user_id = "anonymous_user"
    
    for card in flashcards:
        emb = get_embedding(f"{card['question']} {card['answer']}")
        save_flashcard(user_id=default_user_id, card=card, embedding=emb)

    return {"stored": len(flashcards), "flashcards": flashcards}

@app.get("/flashcards/")
async def get_flashcards():
    """Get all flashcards for the default user"""
    from db import get_flashcards
    flashcards = get_flashcards("anonymous_user")
    return {"flashcards": flashcards}
