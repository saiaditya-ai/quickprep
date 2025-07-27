import os, json, re
import hashlib

HF_TOKEN = os.getenv("HF_API_TOKEN")

# Fallback function for when HF API is not available
def generate_flashcards_fallback(text: str, n_cards: int = 5):
    """Generate simple flashcards from text without AI"""
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    flashcards = []
    
    for i, sentence in enumerate(sentences[:n_cards]):
        if len(sentence) > 50:
            # Create a simple question-answer pair
            question = f"What is mentioned in section {i+1}?"
            answer = sentence[:200] + "..." if len(sentence) > 200 else sentence
            flashcards.append({
                "question": question,
                "answer": answer,
                "difficulty": "medium"
            })
    
    return flashcards

def generate_flashcards(text: str, n_cards: int = 5):
    """Generate flashcards - fallback to simple method if HF fails"""
    try:
        if not HF_TOKEN:
            print("No HF token found, using fallback method")
            return generate_flashcards_fallback(text, n_cards)
        
        # Try to use HF API
        from huggingface_hub import InferenceClient
        
        chat_client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            token=HF_TOKEN,
        )
        
        prompt = (
            f"Create {n_cards} flashcards from the text below.\n"
            "Return **ONLY** a JSON list in the form "
            "[{\"question\":\"...\",\"answer\":\"...\"}, ...]\n\n"
            f"=== TEXT START ===\n{text[:3500]}\n=== TEXT END ==="
        )
        
        raw = chat_client.text_generation(
            prompt,
            max_new_tokens=512,
            temperature=0.2,
        )
        
        # Grab first JSON structure that looks like a list of dicts
        json_str = re.search(r"\[[\s\S]*\]", raw).group(0)
        return json.loads(json_str)
        
    except Exception as e:
        print(f"HF API failed: {e}, using fallback method")
        return generate_flashcards_fallback(text, n_cards)

def get_embedding(text: str):
    """Generate embedding - fallback to hash if HF fails"""
    try:
        if not HF_TOKEN:
            # Simple hash-based embedding
            hash_obj = hashlib.md5(text.encode())
            hash_hex = hash_obj.hexdigest()
            embedding = [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, len(hash_hex), 2)]
            return embedding
        
        from huggingface_hub import InferenceClient
        embed_client = InferenceClient(
            model="sentence-transformers/all-MiniLM-L6-v2",
            token=HF_TOKEN,
        )
        
        vec = embed_client.feature_extraction(text.replace("\n", " "))
        return vec
        
    except Exception as e:
        print(f"Embedding failed: {e}, using hash fallback")
        # Simple hash-based embedding fallback
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        embedding = [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, len(hash_hex), 2)]
        return embedding 
