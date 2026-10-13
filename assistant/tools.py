# assistant/tools.py
from langchain_core.tools import tool
from comics.models import Comic
from comics.services import get_embedding_query
from pgvector.django import CosineDistance


@tool
def buscar_comics_similares(query: str) -> str:
    """
    Busca en el catálogo de cómics usando búsqueda semántica vectorial.
    Úsala SIEMPRE que el usuario pida recomendaciones, busque un género específico,
    o pregunte qué cómics hay disponibles en la plataforma.
    """
    query_vector = get_embedding_query(query)

    if not query_vector:
        return "Error del sistema: No se pudo generar el vector de búsqueda."

    resultados = (
        Comic.objects
        .exclude(embedding__isnull=True)
        .order_by(CosineDistance('embedding', query_vector))[:3]
    )

    if not resultados:
        return "No se encontraron cómics en el catálogo que coincidan con la búsqueda."

    respuesta = "Cómics encontrados en la base de datos:\n"
    for comic in resultados:
        respuesta += (
            f"- Título: {comic.titulo} | "
            f"Autor: {comic.autor or 'Desconocido'} | "
            f"Sinopsis: {comic.sinopsis} | "
            f"Meta: ${comic.meta_recaudacion} | "
            f"Recaudado: ${comic.recaudacion_actual}\n"
        )

    return respuesta