"""
QuickPrep FastAPI Backend
Handles Auth0 authentication, PDF processing, and flashcard generation
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
from dotenv import load_dotenv

from auth import verify_token
from pdf_utils import extract_text_from_pdf
from flashcard_generator import generate_flashcards
from db.vector_store import store_flashcards, search_flashcards
from models.schemas import FlashcardResponse, SearchRequest

# Load environment variables
load_dotenv()

app = FastAPI(title="QuickPrep API", version="1.0.0")

# CORS middleware - Configure for your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "https://quickprep-rcsb2ft9y-sai-adityas-projects-2d3309ca.vercel.app",  # Production frontend
        "https://quickprep-backend.onrender.com"  # Backend URL (for testing)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "QuickPrep API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "QuickPrep API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.post("/upload-pdf", response_model=FlashcardResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    token: dict = Depends(verify_token)
):
    """
    Upload a PDF file and generate flashcards
    Requires valid Auth0 JWT token
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Extract text from PDF
        pdf_content = await file.read()
        text = extract_text_from_pdf(pdf_content)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

        # Generate flashcards using Hugging Face
        flashcards = generate_flashcards(text)

        # Store flashcards with embeddings in Supabase
        user_id = token.get("sub")  # Auth0 user ID
        stored_flashcards = await store_flashcards(flashcards, user_id)

        return FlashcardResponse(
            success=True,
            message=f"Generated {len(flashcards)} flashcards successfully",
            flashcards=stored_flashcards
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/search-flashcards")
async def search_flashcards_endpoint(
    request: SearchRequest,
    token: dict = Depends(verify_token)
):
    """
    Search flashcards using vector similarity
    Requires valid Auth0 JWT token
    """
    try:
        user_id = token.get("sub")
        results = await search_flashcards(request.query, user_id, request.limit)

        return {
            "success": True,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching flashcards: {str(e)}")

@app.get("/protected")
async def protected_route(token: dict = Depends(verify_token)):
    """Protected endpoint for testing Auth0 integration"""
    return {
        "message": f"Hello {token.get('email', 'user')}!",
        "user_id": token.get("sub"),
        "token_info": token
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
