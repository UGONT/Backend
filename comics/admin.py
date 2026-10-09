from django.contrib import admin
from .models import Comic
from django.contrib.auth.admin import UserAdmin

@admin.register(Comic)

class ComicAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'recaudacion_actual', 'meta_recaudacion', 'crowdfunding_activo')
    search_fields = ('titulo', 'autor', 'etiquetas_estilo')
    list_filter = ('crowdfunding_activo',)

    # Ocultamos el campo embedding del panel manual; la IA lo llenará automáticamente
    exclude = ('embedding',)


