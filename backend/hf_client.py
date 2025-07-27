import os, json, re
import hashlib

HF_TOKEN = os.getenv("HF_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Advanced flashcard generation without AI
def generate_flashcards_fallback(text: str, n_cards: int = 5):
    """Generate high-quality flashcards from text using advanced text processing"""
    import re
    
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)  # Remove special chars except basic punctuation
    
    flashcards = []
    
    # 1. Extract definitions and explanations
    definition_patterns = [
        # "X is Y" patterns
        (r'([A-Z][a-zA-Z\s]{2,30})\s+is\s+([^.!?]{10,80})[.!?]', "What is {}?"),
        (r'([A-Z][a-zA-Z\s]{2,30})\s+means\s+([^.!?]{10,80})[.!?]', "What does {} mean?"),
        (r'([A-Z][a-zA-Z\s]{2,30})\s+refers to\s+([^.!?]{10,80})[.!?]', "What does {} refer to?"),
        
        # "A X is Y" patterns  
        (r'A\s+([a-zA-Z\s]{3,25})\s+is\s+([^.!?]{10,80})[.!?]', "What is a {}?"),
        (r'An\s+([a-zA-Z\s]{3,25})\s+is\s+([^.!?]{10,80})[.!?]', "What is an {}?"),
        (r'The\s+([a-zA-Z\s]{3,25})\s+is\s+([^.!?]{10,80})[.!?]', "What is the {}?"),
        
        # "X can be defined as Y" patterns
        (r'([A-Z][a-zA-Z\s]{2,30})\s+can be defined as\s+([^.!?]{10,80})[.!?]', "How is {} defined?"),
        (r'([A-Z][a-zA-Z\s]{2,30})\s+is defined as\s+([^.!?]{10,80})[.!?]', "How is {} defined?"),
    ]
    
    for pattern, question_template in definition_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(flashcards) >= n_cards:
                break
                
            term = match.group(1).strip()
            definition = match.group(2).strip()
            
            # Clean up term and definition
            term = re.sub(r'\s+', ' ', term)
            definition = re.sub(r'\s+', ' ', definition)
            
            # Skip if too short or too long
            if len(term) < 3 or len(term) > 40 or len(definition) < 8 or len(definition) > 100:
                continue
                
            # Skip if definition contains question words (likely not a definition)
            if any(word in definition.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which']):
                continue
                
            question = question_template.format(term.lower())
            
            flashcards.append({
                "question": question,
                "answer": definition,
                "difficulty": "medium"
            })
    
    # 2. Extract key facts and relationships
    if len(flashcards) < n_cards:
        fact_patterns = [
            # "X has Y" patterns
            (r'([A-Z][a-zA-Z\s]{2,30})\s+has\s+([^.!?]{5,60})[.!?]', "What does {} have?"),
            (r'([A-Z][a-zA-Z\s]{2,30})\s+contains\s+([^.!?]{5,60})[.!?]', "What does {} contain?"),
            (r'([A-Z][a-zA-Z\s]{2,30})\s+includes\s+([^.!?]{5,60})[.!?]', "What does {} include?"),
            
            # "X does Y" patterns
            (r'([A-Z][a-zA-Z\s]{2,30})\s+performs\s+([^.!?]{5,60})[.!?]', "What does {} perform?"),
            (r'([A-Z][a-zA-Z\s]{2,30})\s+provides\s+([^.!?]{5,60})[.!?]', "What does {} provide?"),
            (r'([A-Z][a-zA-Z\s]{2,30})\s+ensures\s+([^.!?]{5,60})[.!?]', "What does {} ensure?"),
            
            # "X are Y" patterns
            (r'([A-Z][a-zA-Z\s]{2,30})\s+are\s+([^.!?]{5,60})[.!?]', "What are {}?"),
        ]
        
        for pattern, question_template in fact_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(flashcards) >= n_cards:
                    break
                    
                subject = match.group(1).strip()
                fact = match.group(2).strip()
                
                # Clean up
                subject = re.sub(r'\s+', ' ', subject)
                fact = re.sub(r'\s+', ' ', fact)
                
                if len(subject) < 3 or len(subject) > 40 or len(fact) < 5 or len(fact) > 80:
                    continue
                    
                question = question_template.format(subject.lower())
                
                flashcards.append({
                    "question": question,
                    "answer": fact,
                    "difficulty": "medium"
                })
    
    # 3. Extract numbered lists and steps
    if len(flashcards) < n_cards:
        # Look for numbered items
        numbered_items = re.findall(r'(\d+)[.)]\s*([^.!?]{10,100})[.!?]', text)
        
        for i, (num, item) in enumerate(numbered_items[:n_cards - len(flashcards)]):
            if len(item.strip()) < 10:
                continue
                
            question = f"What is step {num} or point {num}?"
            answer = item.strip()
            
            flashcards.append({
                "question": question,
                "answer": answer,
                "difficulty": "medium"
            })
    
    # 4. Create comparison questions
    if len(flashcards) < n_cards:
        # Look for comparison words
        comparison_sentences = re.findall(r'([^.!?]*(?:different|similar|compare|contrast|versus|vs)[^.!?]*)[.!?]', text, re.IGNORECASE)
        
        for sentence in comparison_sentences[:n_cards - len(flashcards)]:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 120:
                continue
                
            question = "What is the comparison or difference mentioned?"
            answer = sentence
            
            flashcards.append({
                "question": question,
                "answer": answer,
                "difficulty": "medium"
            })
    
    # 5. Fallback: Create questions from important sentences
    if len(flashcards) < n_cards:
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 20]
        
        # Filter for sentences with important keywords
        important_sentences = []
        keywords = ['important', 'key', 'main', 'primary', 'essential', 'significant', 
                   'must', 'should', 'required', 'necessary', 'critical', 'fundamental']
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                important_sentences.append(sentence)
        
        for sentence in important_sentences[:n_cards - len(flashcards)]:
            if len(sentence) > 150:
                sentence = sentence[:150] + "..."
                
            question = "What important point is mentioned?"
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

def generate_flashcards_with_gemini(text: str, n_cards: int = 5):
    """Generate high-quality flashcards using Google Gemini API"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try different model names
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'models/gemini-1.5-flash']
        
        model = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"✅ Using Gemini model: {model_name}")
                break
            except Exception as e:
                print(f"❌ Model {model_name} failed: {e}")
                continue
        
        if not model:
            raise Exception("No valid Gemini model found")
        
        prompt = f"""
        Create {n_cards} high-quality flashcards from the following text. 

        REQUIREMENTS:
        - Questions should be clear, specific, and testable (10-80 characters)
        - Answers should be concise and accurate (10-150 characters)
        - Focus on key concepts, definitions, facts, and important information
        - Avoid yes/no questions
        - Make questions that test understanding, not just memorization

        OUTPUT FORMAT:
        Return ONLY a valid JSON array in this exact format:
        [
            {{"question": "What is...?", "answer": "Brief accurate answer"}},
            {{"question": "How does...?", "answer": "Brief explanation"}},
            {{"question": "Why is...?", "answer": "Brief reason"}}
        ]

        TEXT TO PROCESS:
        {text[:4000]}

        Generate exactly {n_cards} flashcards as a JSON array:
        """
        
        print("🚀 Making Gemini API call...")
        response = model.generate_content(prompt)
        
        print(f"📥 Gemini response: {response.text[:300]}...")
        
        # Extract JSON from response
        json_match = re.search(r'\[[\s\S]*\]', response.text)
        if not json_match:
            raise Exception("No JSON array found in Gemini response")
        
        json_str = json_match.group(0)
        cards = json.loads(json_str)
        
        # Validate and clean cards
        valid_cards = []
        for card in cards:
            if isinstance(card, dict) and 'question' in card and 'answer' in card:
                question = card['question'].strip()
                answer = card['answer'].strip()
                
                if len(question) > 5 and len(answer) > 5:
                    valid_cards.append({
                        "question": question,
                        "answer": answer,
                        "difficulty": "medium"
                    })
        
        print(f"✅ Gemini API success! Generated {len(valid_cards)} valid cards")
        return valid_cards[:n_cards]
        
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        raise

def generate_flashcards(text: str, n_cards: int = 5):
    """Generate flashcards - try Gemini first, then fallback"""
    print(f"=== FLASHCARD GENERATION DEBUG ===")
    print(f"GEMINI_API_KEY present: {bool(GEMINI_API_KEY)}")
    print(f"HF_TOKEN present: {bool(HF_TOKEN)}")
    print(f"Text length: {len(text)}")
    print(f"Requested cards: {n_cards}")
    
    # Try Gemini API first (best quality)
    if GEMINI_API_KEY:
        try:
            print("🌟 Trying Gemini API...")
            cards = generate_flashcards_with_gemini(text, n_cards)
            return [clean_flashcard(card) for card in cards]
        except Exception as e:
            print(f"❌ Gemini API failed: {e}")
    
    # Fallback to local method
    print("🔄 Using local fallback method...")
    cards = generate_flashcards_fallback(text, n_cards)
    print(f"✅ Local fallback success! Generated {len(cards)} cards")
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
