# comics/services.py
import os
from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# Dimensiones fijas para que coincidan con VectorField(dimensions=768)
EMBEDDING_DIMENSIONS = 768


@lru_cache(maxsize=1)
def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Crea el modelo de embeddings una sola vez.
    lru_cache evita instanciarlo en cada request.
    """
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        output_dimensionality=EMBEDDING_DIMENSIONS,
    )


def get_embedding_document(text: str) -> list[float] | None:
    """
    Genera el embedding de un cómic (documento a indexar).
    Usa task_type RETRIEVAL_DOCUMENT para optimizar la búsqueda.
    """
    try:
        model = get_embedding_model()
        # embed_documents usa RETRIEVAL_DOCUMENT internamente
        vector = model.embed_documents([text])[0]
        return vector if vector else None
    except Exception as e:
        print(f"Error generando embedding de documento: {e}")
        return None


def get_embedding_query(text: str) -> list[float] | None:
    """
    Genera el embedding de una consulta de usuario.
    Usa task_type RETRIEVAL_QUERY para optimizar la búsqueda.
    """
    try:
        model = get_embedding_model()
        # embed_query usa RETRIEVAL_QUERY internamente
        vector = model.embed_query(text)
        return vector if vector else None
    except Exception as e:
        print(f"Error generando embedding de consulta: {e}")
        return None