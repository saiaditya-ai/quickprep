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
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://quickprep-murex.vercel.app",  # Current Vercel frontend
        "https://quickprep-kgfv.onrender.com"  # Your Render backend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "QuickPrep backend (HF edition) online",
        "message": "Backend is running on Render",
        "cors_enabled": True,
        "endpoints": ["/", "/test-hf", "/upload-pdf", "/flashcards", "/search-flashcards"]
    }

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
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
            try:
                emb = get_embedding(f"{card['question']} {card['answer']}")
                save_flashcard(user_id=default_user_id, card=card, embedding=emb)
            except Exception as e:
                print(f"Error saving flashcard: {e}")
                # Continue with other flashcards

        return {"stored": len(flashcards), "flashcards": flashcards}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in upload_pdf: {e}")
        raise HTTPException(500, f"Internal server error: {str(e)}")

@app.get("/flashcards/")
async def get_flashcards():
    """Get all flashcards for the default user"""
    try:
        from db import get_flashcards
        flashcards = get_flashcards("anonymous_user")
        return {"flashcards": flashcards}
    except Exception as e:
        print(f"Error getting flashcards: {e}")
        return {"flashcards": []}

@app.post("/search-flashcards")
async def search_flashcards(request: dict):
    """Search flashcards by query"""
    try:
        from db import get_flashcards
        query = request.get("query", "").lower()
        limit = request.get("limit", 10)
        
        all_flashcards = get_flashcards("anonymous_user")
        
        # Simple text search
        if query:
            filtered = [
                card for card in all_flashcards 
                if query in card.get("question", "").lower() or 
                   query in card.get("answer", "").lower()
            ]
        else:
            filtered = all_flashcards
            
        return {"results": filtered[:limit]}
    except Exception as e:
        print(f"Error searching flashcards: {e}")
        return {"results": []}

@app.delete("/flashcards/{card_id}")
async def delete_flashcard(card_id: int):
    """Delete a flashcard"""
    try:
        from db import delete_flashcard
        success = delete_flashcard(card_id, "anonymous_user")
        return {"success": success}
    except Exception as e:
        print(f"Error deleting flashcard: {e}")
        return {"success": False}

@app.put("/flashcards/{card_id}")
async def update_flashcard(card_id: int, updates: dict):
    """Update a flashcard"""
    try:
        from db import update_flashcard
        updated_card = update_flashcard(card_id, "anonymous_user", updates)
        return updated_card or {"error": "Card not found"}
    except Exception as e:
        print(f"Error updating flashcard: {e}")
        return {"error": str(e)}

@app.get("/user/stats")
async def get_user_stats():
    """Get user statistics"""
    try:
        from db import get_flashcards
        flashcards = get_flashcards("anonymous_user")
        
        total = len(flashcards)
        easy = len([c for c in flashcards if c.get("difficulty") == "easy"])
        medium = len([c for c in flashcards if c.get("difficulty") == "medium"])
        hard = len([c for c in flashcards if c.get("difficulty") == "hard"])
        
        return {
            "total_flashcards": total,
            "easy_cards": easy,
            "medium_cards": medium,
            "hard_cards": hard
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            "total_flashcards": 0,
            "easy_cards": 0,
            "medium_cards": 0,
            "hard_cards": 0
        }

@app.get("/protected")
async def protected_route():
    """Protected route for testing (no auth required now)"""
    return {"message": "This endpoint is accessible without authentication"}
