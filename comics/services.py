# comics/services.py
import os
from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from google import genai
from google.genai import types

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
    
def construir_texto_comic(comic) -> str:
    """
    Arma el texto contextual que representa a un cómic para el embedding.
    Incluye título, autores, etiquetas y sinopsis.
    """
    autores = ", ".join(
        (a.autor.perfil.nickname if hasattr(a.autor, 'perfil') else a.autor.username)
        for a in comic.autores.select_related('autor').all()
    )
    etiquetas = ", ".join(
        ce.etiqueta.nombre
        for ce in comic.etiquetas.select_related('etiqueta').all()
    )
    
    return (
        f"Título: {comic.titulo}. "
        f"Autores: {autores or 'Desconocido'}. "
        f"Estilos: {etiquetas or 'No especificado'}. "
        f"Sinopsis: {comic.sinopsis or ''}"
    )
    
# Cliente de Google GenAI (se crea una sola vez)
@lru_cache(maxsize=1)
def get_genai_client():
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def get_embedding_image(image_file) -> list[float] | None:
    """
    Genera el embedding de una imagen (portada) usando Gemini Embedding 2.
    `image_file` es el ImageField de Django (o cualquier archivo con .read()).
    
    Retorna una lista de 768 floats, o None si falla.
    """
    try:
        client = get_genai_client()
        
        # Leer los bytes de la imagen
        image_bytes = image_file.read()
        if not image_bytes:
            print("[embedding_img] Archivo vacío.")
            return None
        
        # Detectar el mime type (PNG o JPEG)
        # Django guarda el nombre; usamos eso como pista
        name = getattr(image_file, 'name', '').lower()
        if name.endswith('.png'):
            mime_type = 'image/png'
        elif name.endswith(('.jpg', '.jpeg')):
            mime_type = 'image/jpeg'
        else:
            mime_type = 'image/png'  # fallback
        
        # Llamada al modelo multimodal
        result = client.models.embed_content(
            model='gemini-embedding-2',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
            ],
            config=types.EmbedContentConfig(
                output_dimensionality=768,
            ),
        )
        
        # Extraer el vector
        if result.embeddings and len(result.embeddings) > 0:
            vector = result.embeddings[0].values
            return list(vector) if vector else None
        return None
        
    except Exception as e:
        print(f"[embedding_img] Error: {e}")
        return None