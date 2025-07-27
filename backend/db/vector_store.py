"""
Supabase Vector Store Integration
Handles storing and searching flashcards with embeddings using pgvector
"""

from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
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
    """Initialize and return the embedding model"""
    global embedding_model
    if embedding_model is None:
        # Using a lightweight, fast model for embeddings
        embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return embedding_model

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using SentenceTransformers

    Args:
        text: Input text

    Returns:
        Embedding vector as list of floats
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()

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
    Search flashcards using vector similarity

    Args:
        query: Search query
        user_id: Auth0 user ID
        limit: Maximum number of results

    Returns:
        List of matching flashcards with similarity scores
    """
    try:
        # Generate embedding for search query
        query_embedding = generate_embedding(query)

        # Use Supabase RPC to call the match_flashcards function
        result = supabase.rpc("match_flashcards", {
            "query_embedding": query_embedding,
            "match_threshold": 0.3,  # Minimum similarity threshold
            "match_count": limit,
            "user_id_filter": user_id
        }).execute()

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
