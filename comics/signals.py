# comics/signals.py
from django.db.models import Avg, Count, Sum
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import (
    Comic,
    ComicAutor,
    ComicEtiqueta,
    Donacion,
    Valoracion,
)
from .services import get_embedding_document, construir_texto_comic, get_embedding_image


# =====================================================================
# EMBEDDING DEL CÓMIC
# =====================================================================

def _regenerar_embedding_contenido(comic_pk: int) -> None:
    """
    Genera el embedding del cómic y lo guarda directamente en la BD.
    Usamos .update() para NO disparar señales de nuevo (evita loops).
    """
    try:
        comic = Comic.objects.get(pk=comic_pk)
    except Comic.DoesNotExist:
        return

    texto = construir_texto_comic(comic)
    print(f"[embedding] Generando para: {comic.titulo}")
    vector = get_embedding_document(texto)

    if vector:
        Comic.objects.filter(pk=comic_pk).update(embedding_contenido=vector)
        print(f"[embedding] OK ({len(vector)} dims)")
    else:
        print("[embedding] Fallo al generar el vector.")


# Guarda el texto viejo antes de guardar, para comparar después
@receiver(pre_save, sender=Comic)
def _capturar_texto_viejo(sender, instance, **kwargs):
    if instance.pk:
        try:
            viejo = Comic.objects.get(pk=instance.pk)
            instance._texto_viejo = construir_texto_comic(viejo)
            instance._portada_vieja = viejo.portada.name if viejo.portada else None
        except Comic.DoesNotExist:
            instance._texto_viejo = None
            instance._portada_vieja = None
    else:
        instance._texto_viejo = None
        instance._portada_vieja = None


@receiver(post_save, sender=Comic)
def embedding_on_comic_save(sender, instance, created, **kwargs):
    """
    Regenera los embeddings (contenido e imagen) cuando:
    - Es un cómic nuevo
    - Cambió el texto semántico (contenido)
    - Se subió o cambió la portada
    """
    texto_nuevo = construir_texto_comic(instance)
    texto_viejo = getattr(instance, '_texto_viejo', None)

    # --- Embedding de contenido ---
    if created or texto_viejo != texto_nuevo:
        _regenerar_embedding_contenido(instance.pk)

    # --- Embedding de portada ---
    # Solo si hay portada y es nueva o cambió
    if instance.portada:
        # Comparamos si cambió la ruta del archivo
        portada_vieja = getattr(instance, '_portada_vieja', None)
        portada_nueva = instance.portada.name if instance.portada else None
        
        if created or portada_vieja != portada_nueva:
            _regenerar_embedding_portada(instance.pk)


# Cuando cambian los autores o etiquetas, regeneramos el embedding del cómic
@receiver(post_save, sender=ComicAutor)
@receiver(post_delete, sender=ComicAutor)
def embedding_on_autor_change(sender, instance, **kwargs):
    _regenerar_embedding_contenido(instance.comic_id)


@receiver(post_save, sender=ComicEtiqueta)
@receiver(post_delete, sender=ComicEtiqueta)
def embedding_on_etiqueta_change(sender, instance, **kwargs):
    _regenerar_embedding_contenido(instance.comic_id)


# =====================================================================
# DENORMALIZACIÓN: recaudación actual
# =====================================================================

def _recalcular_recaudacion(comic_id: int) -> None:
    try:
        comic = Comic.objects.get(pk=comic_id)
    except Comic.DoesNotExist:
        return

    total = (
        comic.donaciones
        .filter(estado_pago=Donacion.EstadoPago.COMPLETADO)
        .aggregate(total=Sum('monto'))['total']
    ) or 0

    Comic.objects.filter(pk=comic_id).update(recaudacion_actual=total)


@receiver(post_save, sender=Donacion)
@receiver(post_delete, sender=Donacion)
def recalcular_recaudacion(sender, instance, **kwargs):
    _recalcular_recaudacion(instance.comic_id)


# =====================================================================
# DENORMALIZACIÓN: valoraciones
# =====================================================================

def _recalcular_valoraciones(comic_id: int) -> None:
    try:
        comic = Comic.objects.get(pk=comic_id)
    except Comic.DoesNotExist:
        return

    resultado = comic.valoraciones.aggregate(
        promedio=Avg('puntuacion'),
        total=Count('id'),
    )

    Comic.objects.filter(pk=comic_id).update(
        valoracion_promedio=resultado['promedio'] or 0,
        total_valoraciones=resultado['total'] or 0,
    )


@receiver(post_save, sender=Valoracion)
@receiver(post_delete, sender=Valoracion)
def recalcular_valoraciones(sender, instance, **kwargs):
    _recalcular_valoraciones(instance.comic_id)
    

# =====================================================================
# EMBEDDING DE LA PORTADA
# =====================================================================

def _regenerar_embedding_portada(comic_pk: int) -> None:
    """Genera el embedding de la portada del cómic y lo guarda."""
    try:
        comic = Comic.objects.get(pk=comic_pk)
    except Comic.DoesNotExist:
        return

    if not comic.portada:
        print(f"[embedding_img] Sin portada para: {comic.titulo}")
        return

    print(f"[embedding_img] Generando para: {comic.titulo}")
    vector = get_embedding_image(comic.portada)

    if vector:
        Comic.objects.filter(pk=comic_pk).update(embedding_portada=vector)
        print(f"[embedding_img] OK ({len(vector)} dims)")
    else:
        print("[embedding_img] Fallo al generar el vector.")