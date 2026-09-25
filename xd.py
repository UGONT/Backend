import requests

API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": "Bearer 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"}

def get_embeddings(texts):
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": texts, "options": {"wait_for_model": True}}
    )
    return response.json()

# Uso
texts = ["Hello world", "How are you?"]
embeddings = get_embeddings(texts)