import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TABLE = "flashcards"

# Initialize supabase client with error handling
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized successfully")
    else:
        print("Warning: Supabase credentials not found")
        supabase = None
except Exception as e:
    print(f"Error initializing Supabase: {e}")
    supabase = None

def save_flashcard(user_id: str, card: dict, embedding: list):
    """Save flashcard to database"""
    try:
        if not supabase:
            print("Supabase not available, skipping save")
            return
            
        result = supabase.table(TABLE).insert({
            "user_id":   user_id,
            "question":  card["question"],
            "answer":    card["answer"],
            "embedding": embedding,
        }).execute()
        
        print(f"Flashcard saved successfully: {card['question'][:50]}...")
        
    except Exception as e:
        print(f"Error saving flashcard: {e}")

def get_flashcards(user_id: str):
    """Get all flashcards for a user"""
    try:
        if not supabase:
            print("Supabase not available, returning empty list")
            return []
            
        result = supabase.table(TABLE).select("*").eq("user_id", user_id).execute()
        flashcards = result.data if result.data else []
        print(f"Retrieved {len(flashcards)} flashcards for user {user_id}")
        return flashcards
        
    except Exception as e:
        print(f"Error getting flashcards: {e}")
        return []

def delete_flashcard(card_id: int, user_id: str):
    """Delete a flashcard"""
    try:
        if not supabase:
            print("Supabase not available, cannot delete")
            return False
            
        result = supabase.table(TABLE).delete().eq("id", card_id).eq("user_id", user_id).execute()
        success = len(result.data) > 0
        print(f"Deleted flashcard {card_id}: {success}")
        return success
        
    except Exception as e:
        print(f"Error deleting flashcard: {e}")
        return False

def update_flashcard(card_id: int, user_id: str, updates: dict):
    """Update a flashcard"""
    try:
        if not supabase:
            print("Supabase not available, cannot update")
            return None
            
        result = supabase.table(TABLE).update(updates).eq("id", card_id).eq("user_id", user_id).execute()
        updated_card = result.data[0] if result.data else None
        print(f"Updated flashcard {card_id}: {updated_card is not None}")
        return updated_card
        
    except Exception as e:
        print(f"Error updating flashcard: {e}")
        return None
