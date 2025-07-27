"""
Pydantic Models for Request/Response Schemas
Defines data structures for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class FlashcardBase(BaseModel):
    """Base flashcard model"""
    question: str = Field(..., min_length=5, max_length=500, description="The flashcard question")
    answer: str = Field(..., min_length=5, max_length=1000, description="The flashcard answer")
    source_text: Optional[str] = Field(None, max_length=2000, description="Source text from PDF")
    difficulty: Optional[str] = Field("medium", description="Difficulty level: easy, medium, hard")

class FlashcardCreate(FlashcardBase):
    """Model for creating flashcards"""
    pass

class FlashcardResponse(BaseModel):
    """Model for flashcard API responses"""
    success: bool
    message: str
    flashcards: List[Dict]

class Flashcard(FlashcardBase):
    """Complete flashcard model with database fields"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    """Model for flashcard search requests"""
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")

class SearchResponse(BaseModel):
    """Model for search API responses"""
    success: bool
    results: List[Dict]
    query: str
    count: int

class UserProfile(BaseModel):
    """Model for user profile information"""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None

class PDFUploadResponse(BaseModel):
    """Model for PDF upload responses"""
    success: bool
    message: str
    filename: str
    text_length: int
    flashcard_count: int

class ErrorResponse(BaseModel):
    """Model for API error responses"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
