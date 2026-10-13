# comics/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Comic
from .services import get_embedding_document


@receiver(pre_save, sender=Comic)
def generate_comic_embedding(sender, instance, **kwargs):
    texto_contexto = (
        f"Título: {instance.titulo}. "
        f"Autor: {instance.autor or 'Desconocido'}. "
        f"Estilo: {instance.etiquetas_estilo or 'No especificado'}. "
        f"Sinopsis: {instance.sinopsis or 'Sin sinopsis disponible'}"
    )

    print(f"Generando embedding para: {instance.titulo}...")

    vector = get_embedding_document(texto_contexto)

    if vector:
        instance.embedding = vector
        print(f"Embedding generado con éxito ({len(vector)} dimensiones).")
    else:
        print("Fallo al generar el embedding. Se guardará como NULL.")