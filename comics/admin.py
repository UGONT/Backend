from django.contrib import admin
from .models import Comic

@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'current_funding', 'funding_goal', 'is_funding_active')
    search_fields = ('title', 'author', 'style_tags')
    list_filter = ('is_funding_active',)
    # Ocultamos el campo embedding del panel manual; la IA lo llenará automáticamente
    exclude = ('embedding',)