# comics/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Perfil,
    Etiqueta,
    Comic,
    ComicAutor,
    ComicEtiqueta,
    Capitulo,
    NivelRecompensa,
    Donacion,
    Valoracion,
)


# =====================================================================
# PERFIL (inline dentro de User)
# =====================================================================

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = "Perfil"


class UserAdmin(BaseUserAdmin):
    inlines = [PerfilInline]
    list_display = ('username', 'email', 'get_nickname', 'is_staff')

    @admin.display(description='Nickname')
    def get_nickname(self, obj):
        return obj.perfil.nickname if hasattr(obj, 'perfil') else '-'


# Re-registramos User con el inline de Perfil
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# =====================================================================
# PERFIL (registro independiente)
# =====================================================================

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'usuario', 'es_creador', 'edad', 'fecha_registro')
    list_filter = ('es_creador',)
    search_fields = ('nickname', 'usuario__username', 'usuario__email')


# =====================================================================
# ETIQUETA
# =====================================================================

@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nombre',)


# =====================================================================
# COMIC (con inlines)
# =====================================================================

class ComicAutorInline(admin.TabularInline):
    model = ComicAutor
    extra = 1
    autocomplete_fields = ('autor',)


class ComicEtiquetaInline(admin.TabularInline):
    model = ComicEtiqueta
    extra = 1
    autocomplete_fields = ('etiqueta',)


class NivelRecompensaInline(admin.TabularInline):
    model = NivelRecompensa
    extra = 0


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'get_autores',
        'estado',
        'crowdfunding_activo',
        'meta_recaudacion',
        'recaudacion_actual',
        'valoracion_promedio',
    )
    list_filter = ('estado', 'crowdfunding_activo')
    search_fields = ('titulo', 'sinopsis')
    inlines = [ComicAutorInline, ComicEtiquetaInline, NivelRecompensaInline]
    readonly_fields = (
        'recaudacion_actual',
        'valoracion_promedio',
        'total_valoraciones',
        'fecha_creacion',
    )
    fieldsets = (
        ('Datos básicos', {
            'fields': ('titulo', 'sinopsis', 'portada', 'numero_paginas')
        }),
        ('Estado y crowdfunding', {
            'fields': (
                'estado',
                'crowdfunding_activo',
                'meta_recaudacion',
                'recaudacion_actual',
                'fecha_inicio',
                'fecha_fin',
            )
        }),
        ('Valoraciones', {
            'fields': ('valoracion_promedio', 'total_valoraciones')
        }),
        ('Embeddings (solo lectura)', {
            'fields': ('embedding_contenido', 'embedding_portada'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('fecha_creacion',),
        }),
    )

    @admin.display(description='Autores')
    def get_autores(self, obj):
        autores = obj.autores.select_related('autor').all()
        if not autores:
            return '-'
        return ", ".join(a.autor.username for a in autores)


# =====================================================================
# CAPITULO
# =====================================================================

@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ('comic', 'numero', 'titulo', 'es_gratis', 'fecha_publicacion')
    list_filter = ('es_gratis',)
    search_fields = ('titulo', 'comic__titulo')
    ordering = ('comic', 'numero')


# =====================================================================
# NIVEL DE RECOMPENSA
# =====================================================================

@admin.register(NivelRecompensa)
class NivelRecompensaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'comic', 'monto_minimo', 'stock', 'orden')
    search_fields = ('titulo', 'comic__titulo')


# =====================================================================
# DONACION
# =====================================================================

@admin.register(Donacion)
class DonacionAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'comic',
        'monto',
        'estado_pago',
        'fecha',
        'es_anonima',
    )
    list_filter = ('estado_pago', 'es_anonima')
    search_fields = ('usuario__username', 'comic__titulo', 'id_transaccion_externo')
    readonly_fields = ('fecha',)
    raw_id_fields = ('usuario', 'comic', 'nivel_recompensa')


# =====================================================================
# VALORACION
# =====================================================================

@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'comic', 'puntuacion', 'fecha')
    list_filter = ('puntuacion',)
    search_fields = ('usuario__username', 'comic__titulo')
    readonly_fields = ('fecha',)
    raw_id_fields = ('usuario', 'comic')