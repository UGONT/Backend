from django.db import models
from pgvector.django import VectorField
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Comic(models.Model):
    portada = models.ImageField(
        upload_to='portadas_comics/', # Subcarpeta dentro del bucket
        null=True, 
        blank=True,
        verbose_name="Imagen de portada"
    )   
    titulo = models.CharField(max_length=200, verbose_name="Título")
    autor = models.CharField(max_length=200, verbose_name="Autor")
    sinopsis = models.TextField(verbose_name="Sinopsis")
    etiquetas_estilo = models.CharField(max_length=255, help_text="Ej: Cyberpunk, Acuarela, Oscuro")
    
    numero_paginas = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de páginas")
    
    valoracion = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Valoración (1-5)"
    )
    
    crowdfunding_activo = models.BooleanField(default=True)
    meta_recaudacion = models.IntegerField(default=0, verbose_name="Meta de recaudación")
    recaudacion_actual = models.IntegerField(default=0, verbose_name="Recaudado actualmente")
    
    embedding = VectorField(dimensions=768, null=True, blank=True)

    def __str__(self):
        return self.titulo

class Tag(models.Model):
    """Etiquetas de gustos/estilos. Reutilizable para usuarios y cómics."""
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    """Datos extra del usuario, ligados 1-a-1 con el User de Django."""
    
    class TipoUsuario(models.TextChoices):
        NORMAL = 'normal', 'Usuario Normal'
        PUBLICADOR = 'publicador', 'Publicador de Cómics'
    
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name="Usuario"
    )
    
    nickname = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nickname"
    )
    edad = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Edad"
    )
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.NORMAL,
        verbose_name="Tipo de usuario"
    )
    gustos = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='perfiles',
        verbose_name="Gustos"
    )

    def __str__(self):
        return f"{self.nickname} ({self.get_tipo_usuario_display()})"
    
    @property
    def es_publicador(self):
        return self.tipo_usuario == self.TipoUsuario.PUBLICADOR


# 🔄 Señales: crean el Perfil automáticamente al crear un User
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance, nickname=instance.username)

@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    instance.perfil.save()

