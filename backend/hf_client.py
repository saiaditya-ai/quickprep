import os, json, re
import hashlib

HF_TOKEN = os.getenv("HF_API_TOKEN")

# Fallback function for when HF API is not available
def generate_flashcards_fallback(text: str, n_cards: int = 5):
    """Generate better flashcards from text without AI"""
    import re
    
    # Clean and split text into meaningful chunks
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 30]
    
    flashcards = []
    
    # Look for definition patterns
    definition_patterns = [
        (r'(.+?)\s+is\s+(.+?)(?:[.!?]|$)', "What is {}?"),
        (r'(.+?)\s+means\s+(.+?)(?:[.!?]|$)', "What does {} mean?"),
        (r'(.+?)\s+refers to\s+(.+?)(?:[.!?]|$)', "What does {} refer to?"),
        (r'A\s+(.+?)\s+is\s+(.+?)(?:[.!?]|$)', "What is a {}?"),
        (r'The\s+(.+?)\s+is\s+(.+?)(?:[.!?]|$)', "What is the {}?"),
    ]
    
    for pattern, question_template in definition_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(flashcards) >= n_cards:
                break
                
            term = match.group(1).strip()
            definition = match.group(2).strip()
            
            # Skip if term or definition is too long/short
            if len(term) > 50 or len(term) < 3 or len(definition) > 150 or len(definition) < 10:
                continue
                
            question = question_template.format(term)
            answer = definition
            
            flashcards.append({
                "question": question,
                "answer": answer,
                "difficulty": "medium"
            })
    
    # If we don't have enough from definitions, create from key sentences
    if len(flashcards) < n_cards:
        key_sentences = []
        for sentence in sentences:
            # Look for sentences with key indicators
            if any(indicator in sentence.lower() for indicator in 
                   ['important', 'key', 'main', 'primary', 'essential', 'significant', 'because', 'therefore', 'however']):
                key_sentences.append(sentence)
        
        for sentence in key_sentences[:n_cards - len(flashcards)]:
            # Create a more specific question based on content
            words = sentence.split()
            if len(words) > 15:
                # Take first part as context, last part as answer
                mid_point = len(words) // 2
                context = ' '.join(words[:mid_point])
                answer_part = ' '.join(words[mid_point:])
                
                question = f"Complete this statement: {context}..."
                answer = answer_part
                
                if len(answer) > 100:
                    answer = answer[:100] + "..."
                    
                flashcards.append({
                    "question": question,
                    "answer": answer,
                    "difficulty": "medium"
                })
    
    # If still not enough, create simple fact-based questions
    if len(flashcards) < n_cards:
        remaining_sentences = sentences[:n_cards - len(flashcards)]
        for i, sentence in enumerate(remaining_sentences):
            if len(sentence) > 100:
                sentence = sentence[:100] + "..."
                
            question = f"What key point is mentioned about this topic?"
            answer = sentence
            
            flashcards.append({
                "question": question,
                "answer": answer,
                "difficulty": "medium"
            })
    
    return flashcards[:n_cards]

def clean_flashcard(card):
    """Clean up flashcard to ensure proper length and format"""
    question = card.get("question", "").strip()
    answer = card.get("answer", "").strip()
    
    # Limit question length
    if len(question) > 120:
        question = question[:120] + "?"
    
    # Limit answer length
    if len(answer) > 200:
        # Try to find a good breaking point
        sentences = answer.split('. ')
        if len(sentences) > 1 and len(sentences[0]) < 150:
            answer = sentences[0] + "."
        else:
            answer = answer[:200] + "..."
    
    return {
        "question": question,
        "answer": answer,
        "difficulty": card.get("difficulty", "medium")
    }

def generate_flashcards(text: str, n_cards: int = 5):
    """Generate flashcards - fallback to simple method if HF fails"""
    try:
        if not HF_TOKEN:
            print("No HF token found, using fallback method")
            cards = generate_flashcards_fallback(text, n_cards)
            return [clean_flashcard(card) for card in cards]
        
        # Try to use HF API
        from huggingface_hub import InferenceClient
        
        chat_client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            token=HF_TOKEN,
        )
        
        prompt = (
            f"Create {n_cards} concise flashcards from the text below.\n"
            "RULES:\n"
            "- Questions should be short (max 15 words)\n"
            "- Answers should be brief (max 25 words)\n"
            "- Focus on key concepts, definitions, and important facts\n"
            "- Make questions specific and testable\n"
            "Return **ONLY** a JSON list in the form:\n"
            "[{\"question\":\"What is...?\",\"answer\":\"Brief answer here\"}, ...]\n\n"
            f"=== TEXT START ===\n{text[:2000]}\n=== TEXT END ==="
        )
        
        raw = chat_client.text_generation(
            prompt,
            max_new_tokens=512,
            temperature=0.2,
        )
        
        # Grab first JSON structure that looks like a list of dicts
        json_str = re.search(r"\[[\s\S]*\]", raw).group(0)
        cards = json.loads(json_str)
        return [clean_flashcard(card) for card in cards]
        
    except Exception as e:
        print(f"HF API failed: {e}, using fallback method")
        cards = generate_flashcards_fallback(text, n_cards)
        return [clean_flashcard(card) for card in cards]

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
