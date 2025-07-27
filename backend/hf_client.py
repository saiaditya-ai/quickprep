import os, json, re
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_API_TOKEN") 


chat_client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    token=HF_TOKEN,
)

# ❷ Embeddings – small, fast 384-dim model
embed_client = InferenceClient(
    model="sentence-transformers/all-MiniLM-L6-v2",
    token=HF_TOKEN,
)

def generate_flashcards(text: str, n_cards: int = 5):
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
    try:
        json_str = re.search(r"\[[\s\S]*\]", raw).group(0)
        return json.loads(json_str)
    except Exception:
        return []

def get_embedding(text: str):
    vec = embed_client.feature_extraction(text.replace("\n", " "))
    return vec 
