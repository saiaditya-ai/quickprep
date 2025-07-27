import os
from supabase import create_client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE = "flashcards"

def save_flashcard(user_id: str, card: dict, embedding: list):
    supabase.table(TABLE).insert({
        "user_id":   user_id,
        "question":  card["question"],
        "answer":    card["answer"],
        "embedding": embedding,
    }).execute()

def get_flashcards(user_id: str):
    """Get all flashcards for a user"""
    result = supabase.table(TABLE).select("*").eq("user_id", user_id).execute()
    return result.data if result.data else []
