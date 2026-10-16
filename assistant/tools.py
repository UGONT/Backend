# assistant/tools.py
from typing import Optional
from langchain_core.tools import tool
from pgvector.django import CosineDistance
from django.db.models import Q

from comics.models import Comic, ComicAutor, ComicEtiqueta, Etiqueta, Donacion, Perfil, ComicExterno
from comics.services import get_embedding_query

from django.db.models import Avg


# =====================================================================
# HELPERS INTERNOS (no son tools)
# =====================================================================

def _nombre_autor(comic) -> str:
    """Devuelve los autores como string plano."""
    autores = comic.autores.select_related('autor').all()
    if not autores:
        return 'Anónimo'
    return ", ".join(
        (a.autor.perfil.nickname if hasattr(a.autor, 'perfil') else a.autor.username)
        for a in autores
    )


def _formatear_comic(comic, incluir_sinopsis: bool = True) -> str:
    """Formatea un cómic en texto plano para el LLM."""
    partes = [
        f"Título: {comic.titulo}",
        f"Autor: {_nombre_autor(comic)}",
        f"Estado: {comic.get_estado_display()}",
        f"Meta: ${comic.meta_recaudacion} CLP",
        f"Recaudado: ${comic.recaudacion_actual} CLP",
    ]
    if comic.valoracion_promedio:
        partes.append(f"Valoración: {comic.valoracion_promedio}/5 ({comic.total_valoraciones} votos)")
    if incluir_sinopsis and comic.sinopsis:
        partes.append(f"Sinopsis: {comic.sinopsis}")
    return " | ".join(partes)


def _formatear_lista(comics, titulo: str = "Resultados") -> str:
    """Formatea una lista de cómics para el LLM."""
    comics = list(comics)
    if not comics:
        return "No se encontraron cómics con esos criterios."
    lineas = [f"{titulo} ({len(comics)} encontrados):"]
    for c in comics:
        lineas.append(f"- {_formatear_comic(c, incluir_sinopsis=False)}")
    return "\n".join(lineas)


# =====================================================================
# BÚSQUEDA SEMÁNTICA
# =====================================================================

@tool
def buscar_comics_similares(query: str) -> str:
    """
    Busca cómics usando búsqueda semántica sobre su contenido (título, sinopsis, estilos).
    Úsala cuando el usuario haga una pregunta amplia como "busco algo de piratas",
    "cómic con historia triste", "algo parecido a X", o describa una temática.
    """
    query_vector = get_embedding_query(query)
    if not query_vector:
        return "Error: no se pudo generar el vector de búsqueda."

    resultados = (
        Comic.objects
        .exclude(embedding_contenido__isnull=True)
        .order_by(CosineDistance('embedding_contenido', query_vector))[:5]
    )
    return _formatear_lista(resultados, "Cómics similares")


@tool
def buscar_comics_por_estilo_visual(descripcion: str) -> str:
    """
    Busca cómics por similitud visual de su portada.
    Úsala cuando el usuario pida algo "parecido visualmente a X",
    "con arte tipo acuarela", "estilo oscuro", "colores vibrantes", etc.
    """
    query_vector = get_embedding_query(descripcion)
    if not query_vector:
        return "Error: no se pudo generar el vector visual."

    resultados = (
        Comic.objects
        .exclude(embedding_portada__isnull=True)
        .order_by(CosineDistance('embedding_portada', query_vector))[:5]
    )
    return _formatear_lista(resultados, "Cómics con estilo visual similar")


# =====================================================================
# FILTROS EXACTOS
# =====================================================================

@tool
def buscar_comics_por_autor(nombre_autor: str) -> str:
    """
    Busca todos los cómics de un autor específico.
    Úsala cuando el usuario mencione un autor por nombre o nickname.
    """
    comics = Comic.objects.filter(
        Q(autores__autor__username__icontains=nombre_autor) |
        Q(autores__autor__perfil__nickname__icontains=nombre_autor)
    ).distinct()

    return _formatear_lista(comics, f"Cómics de '{nombre_autor}'")


@tool
def buscar_comics_por_genero(genero: str) -> str:
    """
    Busca cómics que tengan una etiqueta específica (género, estilo o tema).
    Úsala cuando el usuario pida un género concreto como "fantasía", "terror",
    "ciencia ficción", o un estilo como "acuarela", "cyberpunk".
    """
    comics = Comic.objects.filter(
        etiquetas__etiqueta__nombre__icontains=genero
    ).distinct()

    return _formatear_lista(comics, f"Cómics de '{genero}'")


@tool
def filtrar_comics_por_estado(estado: str) -> str:
    """
    Filtra cómics por su estado.
    Valores válidos: 'borrador', 'en_campana', 'publicado', 'cancelado'.
    Úsala cuando el usuario pregunte por cómics "en campaña", "publicados", etc.
    """
    # Normalizar entradas comunes
    mapa = {
        "en campaña": "en_campana",
        "en_campana": "en_campana",
        "campaña": "en_campana",
        "publicados": "publicado",
        "borradores": "borrador",
    }
    estado_norm = mapa.get(estado.lower(), estado.lower())
    comics = Comic.objects.filter(estado=estado_norm)
    
    comics = Comic.objects.filter(estado=estado)
    return _formatear_lista(comics, f"Cómics en estado '{estado}'")


@tool
def filtrar_comics_por_valoracion(minimo: float) -> str:
    """
    Filtra cómics con valoración promedio mayor o igual a `minimo`.
    `minimo` es un número entre 0 y 5.
    Úsala cuando el usuario pida "los mejor valorados", "con 4 estrellas o más", etc.
    """
    comics = (
        Comic.objects
        .filter(valoracion_promedio__gte=minimo, total_valoraciones__gt=0)
        .order_by('-valoracion_promedio')
    )
    return _formatear_lista(comics, f"Cómics con valoración ≥ {minimo}")


@tool
def filtrar_comics_por_meta(meta_minima: int = 0, meta_maxima: int = 10_000_000) -> str:
    """
    Filtra cómics cuya meta de recaudación esté entre `meta_minima` y `meta_maxima` (CLP).
    Úsala cuando el usuario pida "campañas con meta baja", "cómics que necesitan
    menos de $50.000", o "proyectos grandes de más de $1.000.000".
    """
    comics = Comic.objects.filter(
        meta_recaudacion__gte=meta_minima,
        meta_recaudacion__lte=meta_maxima,
    ).order_by('meta_recaudacion')
    return _formatear_lista(comics, f"Cómics con meta entre ${meta_minima} y ${meta_maxima}")


# =====================================================================
# DETALLE DE UN CÓMIC
# =====================================================================

@tool
def obtener_detalle_comic(titulo: str) -> str:
    """
    Devuelve el detalle completo de un cómic: autores, etiquetas, capítulos,
    niveles de recompensa y estadísticas de donación.
    Úsala cuando el usuario pregunte por un cómic específico por su título.
    """
    comic = (
        Comic.objects
        .filter(titulo__icontains=titulo)
        .prefetch_related('autores__autor', 'etiquetas__etiqueta', 'capitulos', 'recompensas')
        .first()
    )
    if not comic:
        return f"No se encontró ningún cómic con título parecido a '{titulo}'."

    lineas = [
        f"📖 {comic.titulo}",
        f"Autor: {_nombre_autor(comic)}",
        f"Estado: {comic.get_estado_display()}",
        f"Sinopsis: {comic.sinopsis}",
        f"Páginas: {comic.numero_paginas}",
    ]

    etiquetas = [ce.etiqueta.nombre for ce in comic.etiquetas.all()]
    if etiquetas:
        lineas.append(f"Etiquetas: {', '.join(etiquetas)}")

    lineas.append(
        f"Recaudación: ${comic.recaudacion_actual} / ${comic.meta_recaudacion} CLP"
    )
    if comic.valoracion_promedio:
        lineas.append(f"Valoración: {comic.valoracion_promedio}/5 ({comic.total_valoraciones} votos)")

    capitulos = comic.capitulos.all()
    if capitulos:
        lineas.append(f"Capítulos: {capitulos.count()} ({', '.join(c.titulo for c in capitulos[:5])})")

    recompensas = comic.recompensas.all()
    if recompensas:
        lineas.append("Recompensas:")
        for r in recompensas:
            lineas.append(f"  · ${r.monto_minimo}+ → {r.titulo}: {r.descripcion}")

    donaciones = comic.donaciones.filter(estado_pago=Donacion.EstadoPago.COMPLETADO).count()
    lineas.append(f"Donaciones completadas: {donaciones}")

    return "\n".join(lineas)




def make_recomendar_para_mi(user_id: int):
    """
    Crea un tool de recomendación personalizada, atado al user_id actual.
    Se llama desde la vista en cada request (no al cargar el módulo).
    """
    
    @tool
    def recomendar_para_mi() -> str:
        """
        Recomienda cómics personalizados para el usuario actual basándose en:
        - Sus gustos declarados (etiquetas preferidas)
        - Los cómics que ya leyó
        
        Úsala cuando el usuario pida recomendaciones personalizadas como
        "recomiéndame algo", "qué me puede gustar", "algo para mí".
        """
        from comics.models import Perfil, Comic
        
        try:
            perfil = Perfil.objects.get(usuario_id=user_id)
        except Perfil.DoesNotExist:
            return "El usuario no tiene perfil configurado."
        
        gustos = list(perfil.gustos.values_list('nombre', flat=True))
        leidos = list(perfil.comics_leidos.all())
        
        if not gustos and not leidos:
            return (
                "El usuario no ha declarado gustos ni cómics leídos. "
                "Sugiere que los agregue en su perfil o pregúntale qué le gusta."
            )
        
        # Estrategia 1: buscar por similitud a los cómics leídos
        resultados = []
        if leidos:
            vectores = [c.embedding for c in leidos if c.embedding is not None]
            if vectores:
                promedio = [
                    sum(v[i] for v in vectores) / len(vectores)
                    for i in range(len(vectores[0]))
                ]
                resultados = list(
                    Comic.objects
                    .exclude(embedding_contenido__isnull=True)
                    .filter(estado__in=['publicado', 'en_campana'])
                    .order_by(CosineDistance('embedding_contenido', promedio))[:5]
                )
        
        # Estrategia 2: si no hay leídos o no hay resultados, filtrar por gustos
        if not resultados and gustos:
            resultados = list(
                Comic.objects
                .filter(etiquetas__etiqueta__nombre__in=gustos)
                .filter(estado__in=['publicado', 'en_campana'])
                .distinct()[:5]
            )
        
        if not resultados:
            return "No encontré cómics que coincidan con los gustos actuales del usuario."
        
        contexto = (
            f"Perfil del usuario: gustos={gustos}, "
            f"cómics leídos={[c.nombre for c in leidos]}.\n\n"
            f"Cómics recomendados:\n"
        )
        for c in resultados:
            contexto += f"- {_formatear_comic(c)}\n"
        
        return contexto
    
    return recomendar_para_mi