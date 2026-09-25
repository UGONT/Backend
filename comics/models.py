from django.db import models
from pgvector.django import VectorField

class Comic(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    author = models.CharField(max_length=200, verbose_name="Autor")
    synopsis = models.TextField(verbose_name="Sinopsis")
    style_tags = models.CharField(max_length=255, help_text="Ej: Cyberpunk, Acuarela, Oscuro")
    
    # Datos de Crowdfunding
    is_funding_active = models.BooleanField(default=True)
    funding_goal = models.IntegerField(default=0, verbose_name="Meta de recaudación")
    current_funding = models.IntegerField(default=0, verbose_name="Recaudado actualmente")
    
    # Campo para la IA (768 dimensiones es el estándar para modelos Open Source de Hugging Face)
    embedding = VectorField(dimensions=768, null=True, blank=True)

    def __str__(self):
        return self.title