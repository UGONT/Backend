from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Comic
from .services import get_embedding

@receiver(pre_save, sender=Comic)
def generate_comic_embedding(sender, instance, **kwargs):
    # 1. Armamos un bloque de texto rico en contexto para la IA
    texto_contexto = f"Título: {instance.title}. Estilo: {instance.style_tags}. Sinopsis: {instance.synopsis}"
    
    # 2. Solo llamamos a la API si el cómic es nuevo o si se modificó algún texto importante.
    # (Para simplificar en este MVP, lo generaremos siempre que se presione "Guardar")
    print(f"Generando embedding para: {instance.title}...")
    
    vector = get_embedding(texto_contexto)
    
    if vector:
        # Hugging Face puede devolver una lista anidada dependiendo del modelo
        # Extraemos la lista plana de 768 dimensiones
        if isinstance(vector, list) and isinstance(vector[0], list):
             instance.embedding = vector[0]
        else:
             instance.embedding = vector
        
        print("Vector generado y asignado con éxito.")
    else:
        print("Fallo al generar el vector. Se guardará como NULL.")