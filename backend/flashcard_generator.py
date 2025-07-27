"""
Flashcard Generation using Hugging Face Transformers
Generates question-answer pairs from text using pre-trained models
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Dict, Tuple
import re
import os

# Initialize models (using smaller, efficient models for production)
summarizer = None
qa_pipeline = None

def initialize_models():
    """Initialize Hugging Face models for flashcard generation"""
    global summarizer, qa_pipeline

    try:
        # Summarization model for creating concise content
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            tokenizer="facebook/bart-large-cnn",
            device=-1  # Use CPU (set to 0 for GPU)
        )

        # For question generation, we'll use a pre-trained model
        qa_pipeline = pipeline(
            "text2text-generation",
            model="mrm8488/t5-base-finetuned-question-generation-ap",
            tokenizer="mrm8488/t5-base-finetuned-question-generation-ap",
            device=-1
        )

    except Exception as e:
        print(f"Warning: Could not initialize all models: {e}")
        # Fallback to rule-based generation if models fail to load

def chunk_text(text: str, max_length: int = 512) -> List[str]:
    """
    Split text into chunks suitable for model processing

    Args:
        text: Input text to chunk
        max_length: Maximum tokens per chunk

    Returns:
        List of text chunks
    """
    # Split by sentences first
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Check if adding this sentence would exceed max length
        if len(current_chunk.split()) + len(sentence.split()) > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # Sentence is too long, split by words
                words = sentence.split()
                for i in range(0, len(words), max_length):
                    chunks.append(" ".join(words[i:i + max_length]))
        else:
            current_chunk += " " + sentence if current_chunk else sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def generate_flashcards_with_ai(text: str, max_cards: int = 20) -> List[Dict[str, str]]:
    """
    Generate flashcards using AI models

    Args:
        text: Input text
        max_cards: Maximum number of flashcards to generate

    Returns:
        List of flashcard dictionaries
    """
    global summarizer, qa_pipeline

    if not summarizer or not qa_pipeline:
        initialize_models()

    flashcards = []
    chunks = chunk_text(text, max_length=400)

    for chunk in chunks[:max_cards // 2]:  # Limit chunks to control output
        try:
            # Summarize chunk for context
            summary = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
            summarized_text = summary[0]['summary_text']

            # Generate question from summarized text
            question_input = f"generate question: {summarized_text}"
            question_result = qa_pipeline(question_input, max_length=64, num_return_sequences=1)

            if question_result and len(question_result) > 0:
                question = question_result[0]['generated_text'].strip()

                # Create flashcard
                flashcard = {
                    "question": question,
                    "answer": summarized_text,
                    "source_text": chunk[:200] + "..." if len(chunk) > 200 else chunk
                }
                flashcards.append(flashcard)

        except Exception as e:
            print(f"Error generating flashcard from chunk: {e}")
            continue

    return flashcards

def generate_flashcards_rule_based(text: str, max_cards: int = 20) -> List[Dict[str, str]]:
    """
    Generate flashcards using rule-based approach as fallback

    Args:
        text: Input text
        max_cards: Maximum number of flashcards to generate

    Returns:
        List of flashcard dictionaries
    """
    flashcards = []

    # Split text into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    for i, paragraph in enumerate(paragraphs[:max_cards]):
        if len(paragraph.split()) < 10:  # Skip very short paragraphs
            continue

        # Extract key sentences (first and last of paragraph)
        sentences = [s.strip() for s in re.split(r'[.!?]+', paragraph) if s.strip()]

        if len(sentences) >= 2:
            question = f"What is discussed in section {i + 1} of the document?"
            answer = sentences[0] + ". " + (sentences[-1] if len(sentences) > 1 else "")

            flashcard = {
                "question": question,
                "answer": answer[:200] + "..." if len(answer) > 200 else answer,
                "source_text": paragraph[:300] + "..." if len(paragraph) > 300 else paragraph
            }
            flashcards.append(flashcard)

    # Generate definition-based flashcards
    definition_patterns = [
        r'(.+?) is (.+?)(?:[.!?]|$)',
        r'(.+?) refers to (.+?)(?:[.!?]|$)',
        r'(.+?) means (.+?)(?:[.!?]|$)',
        r'A (.+?) is (.+?)(?:[.!?]|$)'
    ]

    for pattern in definition_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            term = match.group(1).strip()
            definition = match.group(2).strip()

            if len(term.split()) <= 5 and len(definition.split()) >= 3:
                flashcard = {
                    "question": f"What is {term}?",
                    "answer": definition,
                    "source_text": match.group(0)
                }
                flashcards.append(flashcard)

                if len(flashcards) >= max_cards:
                    break

    return flashcards[:max_cards]

def generate_flashcards(text: str, max_cards: int = 20) -> List[Dict[str, str]]:
    """
    Main function to generate flashcards from text

    Args:
        text: Input text from PDF
        max_cards: Maximum number of flashcards to generate

    Returns:
        List of flashcard dictionaries with question, answer, and metadata
    """
    try:
        # Try AI-based generation first
        flashcards = generate_flashcards_with_ai(text, max_cards)

        # If AI generation fails or produces few results, use rule-based approach
        if len(flashcards) < max_cards // 2:
            rule_based_cards = generate_flashcards_rule_based(text, max_cards - len(flashcards))
            flashcards.extend(rule_based_cards)

        # Add metadata to each flashcard
        for i, card in enumerate(flashcards):
            card["id"] = i + 1
            card["created_at"] = None  # Will be set when stored in database
            card["difficulty"] = "medium"  # Default difficulty

        return flashcards[:max_cards]

    except Exception as e:
        print(f"Error in flashcard generation: {e}")
        # Fallback to rule-based approach
        return generate_flashcards_rule_based(text, max_cards)
