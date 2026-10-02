from langchain_core.tools import tool
from comics.models import Comic
from comics.services import get_embedding
from pgvector.django import CosineDistance

@tool
def buscar_comics_similares(query: str) -> str:
    """
    Busca en el catálogo de cómics usando búsqueda semántica vectorial.
    Úsala SIEMPRE que el usuario pida recomendaciones, busque un género específico, o pregunte qué cómics hay disponibles en la plataforma.
    """
    # 1. Convertimos la consulta del usuario en un vector de 768 dimensiones
    query_vector = get_embedding(query)
    
    if not query_vector:
        return "Error del sistema: No se pudo generar el vector de búsqueda."
    
    # 2. Buscamos en PostgreSQL ordenando por similitud (Cosine Distance)
    # Seleccionamos las 3 mejores coincidencias
    resultados = Comic.objects.order_by(CosineDistance('embedding', query_vector))[:3]
    
    if not resultados:
        return "No se encontraron cómics en el catálogo que coincidan con la búsqueda."
    
    # 3. Formateamos los datos puros en texto para que el LLM los procese
    respuesta = "Cómics encontrados en la base de datos:\n"
    for comic in resultados:
        respuesta += f"- Título: {comic.title} | Autor: {comic.author} | Sinopsis: {comic.synopsis} | Meta: ${comic.funding_goal} | Recaudado: ${comic.current_funding}\n"
    
    return respuesta