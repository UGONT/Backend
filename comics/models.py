# comics/models.py
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from pgvector.django import VectorField


# =====================================================================
# PERFIL DE USUARIO
# =====================================================================

class Perfil(models.Model):
    """Datos extra de cada usuario. Un User puede ser normal y creador a la vez."""
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name="Usuario"
    )
    nickname = models.CharField(max_length=50, unique=True, verbose_name="Nickname")
    edad = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Edad")
    es_creador = models.BooleanField(
        default=False,
        verbose_name="Es creador",
        help_text="Indica si el usuario puede publicar cómics."
    )
    bio = models.TextField(blank=True, verbose_name="Biografía")
    avatar = models.ImageField(
        upload_to='avatares/',
        null=True,
        blank=True,
        verbose_name="Avatar"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return self.nickname


# =====================================================================
# ETIQUETAS (estilos, géneros, temas)
# =====================================================================

class Etiqueta(models.Model):
    """Etiquetas reutilizables para clasificar cómics por estilo, género o tema."""
    
    class Tipo(models.TextChoices):
        ESTILO = 'estilo', 'Estilo'
        GENERO = 'genero', 'Género'
        TEMA = 'tema', 'Tema'
    
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.ESTILO,
        verbose_name="Tipo"
    )

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


# =====================================================================
# COMIC
# =====================================================================

class Comic(models.Model):
    """Cómic publicado en la plataforma, con datos de crowdfunding."""
    
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        EN_CAMPANA = 'en_campana', 'En campaña'
        PUBLICADO = 'publicado', 'Publicado'
        CANCELADO = 'cancelado', 'Cancelado'
    
    # --- Datos básicos ---
    titulo = models.CharField(max_length=200, verbose_name="Título")
    sinopsis = models.TextField(verbose_name="Sinopsis")
    portada = models.ImageField(
        upload_to='portadas/',
        null=True,
        blank=True,
        verbose_name="Portada"
    )
    numero_paginas = models.PositiveIntegerField(default=0, verbose_name="Número de páginas")
    
    # --- Estado y crowdfunding ---
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR,
        verbose_name="Estado"
    )
    crowdfunding_activo = models.BooleanField(
        default=False,
        verbose_name="Crowdfunding activo",
        help_text="Permite pausar las donaciones sin cambiar el estado del cómic."
    )
    meta_recaudacion = models.PositiveIntegerField(default=0, verbose_name="Meta de recaudación (CLP)")
    recaudacion_actual = models.PositiveIntegerField(
        default=0,
        verbose_name="Recaudación actual (CLP)",
        help_text="Denormalizado desde las donaciones completadas."
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True, verbose_name="Inicio de campaña")
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name="Fin de campaña")
    
    # --- Valoraciones (denormalizadas) ---
    valoracion_promedio = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        verbose_name="Valoración promedio",
        help_text="Denormalizado desde las valoraciones de usuarios."
    )
    total_valoraciones = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de valoraciones"
    )
    
    # --- Embeddings (Gemini, 768 dims) ---
    embedding_contenido = VectorField(
        dimensions=768,
        null=True,
        blank=True,
        verbose_name="Embedding de contenido"
    )
    embedding_portada = VectorField(
        dimensions=768,
        null=True,
        blank=True,
        verbose_name="Embedding de portada"
    )
    
    # --- Metadata ---
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Cómic"
        verbose_name_plural = "Cómics"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo


# =====================================================================
# RELACIONES DEL COMIC
# =====================================================================

class ComicAutor(models.Model):
    """Relación N:M entre cómics y autores, con rol específico."""
    
    class Rol(models.TextChoices):
        AUTOR_PRINCIPAL = 'autor_principal', 'Autor principal'
        GUIONISTA = 'guionista', 'Guionista'
        DIBUJANTE = 'dibujante', 'Dibujante'
        COLORISTA = 'colorista', 'Colorista'
        OTRO = 'otro', 'Otro'
    
    comic = models.ForeignKey(
        Comic,
        on_delete=models.CASCADE,
        related_name='autores',
        verbose_name="Cómic"
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comics_como_autor',
        verbose_name="Autor"
    )
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.AUTOR_PRINCIPAL,
        verbose_name="Rol"
    )
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")

    class Meta:
        verbose_name = "Autor del cómic"
        verbose_name_plural = "Autores del cómic"
        unique_together = ('comic', 'autor', 'rol')
        ordering = ['orden']

    def __str__(self):
        return f"{self.autor.username} - {self.get_rol_display()} en {self.comic.titulo}"


class ComicEtiqueta(models.Model):
    """Relación N:M entre cómics y etiquetas."""
    comic = models.ForeignKey(
        Comic,
        on_delete=models.CASCADE,
        related_name='etiquetas',
        verbose_name="Cómic"
    )
    etiqueta = models.ForeignKey(
        Etiqueta,
        on_delete=models.CASCADE,
        related_name='comics',
        verbose_name="Etiqueta"
    )

    class Meta:
        verbose_name = "Etiqueta del cómic"
        verbose_name_plural = "Etiquetas del cómic"
        unique_together = ('comic', 'etiqueta')

    def __str__(self):
        return f"{self.comic.titulo} - {self.etiqueta.nombre}"


# =====================================================================
# CAPÍTULOS
# =====================================================================

class Capitulo(models.Model):
    """Capítulos de un cómic (contenido en texto)."""
    comic = models.ForeignKey(
        Comic,
        on_delete=models.CASCADE,
        related_name='capitulos',
        verbose_name="Cómic"
    )
    numero = models.PositiveIntegerField(verbose_name="Número")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    contenido = models.TextField(verbose_name="Contenido")
    fecha_publicacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de publicación",
        help_text="Null si aún no está publicado."
    )
    es_gratis = models.BooleanField(default=True, verbose_name="Es gratis")

    class Meta:
        verbose_name = "Capítulo"
        verbose_name_plural = "Capítulos"
        unique_together = ('comic', 'numero')
        ordering = ['comic', 'numero']

    def __str__(self):
        return f"{self.comic.titulo} - Cap. {self.numero}: {self.titulo}"


# =====================================================================
# RECOMPENSAS
# =====================================================================

class NivelRecompensa(models.Model):
    """Niveles de recompensa asociados a un cómic según el monto donado."""
    comic = models.ForeignKey(
        Comic,
        on_delete=models.CASCADE,
        related_name='recompensas',
        verbose_name="Cómic"
    )
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    monto_minimo = models.PositiveIntegerField(verbose_name="Monto mínimo (CLP)")
    stock = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Stock",
        help_text="Null = sin límite."
    )
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")

    class Meta:
        verbose_name = "Nivel de recompensa"
        verbose_name_plural = "Niveles de recompensa"
        ordering = ['comic', 'monto_minimo']

    def __str__(self):
        return f"{self.titulo} ({self.comic.titulo})"


# =====================================================================
# DONACIONES
# =====================================================================

class Donacion(models.Model):
    """Aporte económico de un usuario a un cómic."""
    
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        COMPLETADO = 'completado', 'Completado'
        FALLIDO = 'fallido', 'Fallido'
        REEMBOLSADO = 'reembolsado', 'Reembolsado'
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='donaciones',
        verbose_name="Usuario"
    )
    comic = models.ForeignKey(
        Comic,
        on_delete=models.CASCADE,
        related_name='donaciones',
        verbose_name="Cómic"
    )
    monto = models.PositiveIntegerField(verbose_name="Monto (CLP)")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    estado_pago = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
        verbose_name="Estado del pago"
    )
    metodo_pago = models.CharField(max_length=50, blank=True, verbose_name="Método de pago")
    id_transaccion_externo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="ID de transacción externo"
    )
    es_anonima = models.BooleanField(default=False, verbose_name="Donación anónima")
    mensaje = models.TextField(blank=True, verbose_name="Mensaje")
    nivel_recompensa = models.ForeignKey(
        NivelRecompensa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donaciones',
        verbose_name="Nivel de recompensa"
    )
    direccion_envio = models.TextField(blank=True, verbose_name="Dirección de envío")

    class Meta:
        verbose_name = "Donación"
        verbose_name_plural = "Donaciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} → {self.comic.titulo}: ${self.monto}"


# =====================================================================
# VALORACIONES
# =====================================================================

class Valoracion(models.Model):
    """Puntuación (1-5) de un usuario a un cómic."""
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='valoraciones',
        verbose_name="Usuario"
    )
    comic = models.ForeignKey(
        Comic,
        on_delete=models.CASCADE,
        related_name='valoraciones',
        verbose_name="Cómic"
    )
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Puntuación"
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"
        unique_together = ('usuario', 'comic')
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} → {self.comic.titulo}: {self.puntuacion}/5"