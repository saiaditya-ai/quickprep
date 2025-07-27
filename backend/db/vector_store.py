"""
Supabase Vector Store Integration
Handles storing and searching flashcards with embeddings using pgvector
"""

from supabase import create_client, Client
# from sentence_transformers import SentenceTransformer
import hashlib
from typing import List, Dict, Optional
import os
import asyncio
from datetime import datetime

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize embedding model
embedding_model = None

def get_embedding_model():
    """Placeholder for embedding model"""
    return None

def generate_embedding(text: str) -> List[float]:
    """
    Generate simple hash-based embedding for text (simplified for deployment)

    Args:
        text: Input text

    Returns:
        Simple embedding vector as list of floats
    """
    # Create a simple hash-based embedding (384 dimensions to match expected format)
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Convert hex to numbers and normalize to create embedding-like vector
    embedding = []
    for i in range(0, len(hash_hex), 2):
        val = int(hash_hex[i:i+2], 16) / 255.0  # Normalize to 0-1
        embedding.append(val)
    
    # Pad to 384 dimensions (repeat pattern)
    while len(embedding) < 384:
        embedding.extend(embedding[:min(16, 384 - len(embedding))])
    
    return embedding[:384]

async def store_flashcards(flashcards: List[Dict], user_id: str) -> List[Dict]:
    """
    Store flashcards with embeddings in Supabase

    Args:
        flashcards: List of flashcard dictionaries
        user_id: Auth0 user ID

    Returns:
        List of stored flashcards with IDs
    """
    stored_flashcards = []

    for flashcard in flashcards:
        try:
            # Generate embeddings for question and answer
            question_embedding = generate_embedding(flashcard["question"])
            answer_embedding = generate_embedding(flashcard["answer"])

            # Combine question and answer for context embedding
            combined_text = f"{flashcard['question']} {flashcard['answer']}"
            combined_embedding = generate_embedding(combined_text)

            # Prepare data for insertion
            flashcard_data = {
                "user_id": user_id,
                "question": flashcard["question"],
                "answer": flashcard["answer"],
                "source_text": flashcard.get("source_text", ""),
                "difficulty": flashcard.get("difficulty", "medium"),
                "question_embedding": question_embedding,
                "answer_embedding": answer_embedding,
                "combined_embedding": combined_embedding,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Insert into Supabase
            result = supabase.table("flashcards").insert(flashcard_data).execute()

            if result.data:
                stored_flashcard = result.data[0]
                # Remove embeddings from response (too large)
                stored_flashcard.pop("question_embedding", None)
                stored_flashcard.pop("answer_embedding", None)
                stored_flashcard.pop("combined_embedding", None)
                stored_flashcards.append(stored_flashcard)

        except Exception as e:
            print(f"Error storing flashcard: {e}")
            continue

    return stored_flashcards

async def search_flashcards(query: str, user_id: str, limit: int = 10) -> List[Dict]:
    """
    Search flashcards using simple text matching (simplified for deployment)

    Args:
        query: Search query
        user_id: Auth0 user ID
        limit: Maximum number of results

    Returns:
        List of matching flashcards
    """
    try:
        # Simple text search using ilike (case-insensitive LIKE)
        result = supabase.table("flashcards")\
            .select("id, question, answer, source_text, difficulty, created_at")\
            .eq("user_id", user_id)\
            .or_(f"question.ilike.%{query}%,answer.ilike.%{query}%,source_text.ilike.%{query}%")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()

        return result.data if result.data else []

    except Exception as e:
        print(f"Error searching flashcards: {e}")
        return []

async def get_user_flashcards(user_id: str, limit: int = 50) -> List[Dict]:
    """
    Get all flashcards for a user

    Args:
        user_id: Auth0 user ID
        limit: Maximum number of flashcards to return

    Returns:
        List of user's flashcards
    """
    try:
        result = supabase.table("flashcards")\
            .select("id, question, answer, source_text, difficulty, created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()

        return result.data if result.data else []

    except Exception as e:
        print(f"Error fetching user flashcards: {e}")
        return []

async def delete_flashcard(flashcard_id: int, user_id: str) -> bool:
    """
    Delete a flashcard

    Args:
        flashcard_id: ID of flashcard to delete
        user_id: Auth0 user ID (for security)

    Returns:
        True if successful, False otherwise
    """
    try:
        result = supabase.table("flashcards")\
            .delete()\
            .eq("id", flashcard_id)\
            .eq("user_id", user_id)\
            .execute()

        return len(result.data) > 0

    except Exception as e:
        print(f"Error deleting flashcard: {e}")
        return False
