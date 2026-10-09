# comics/serializers.py
from rest_framework import serializers
from .models import Comic


class ComicSerializer(serializers.ModelSerializer):
    # Campos renombrados para que coincidan con el frontend
    descripcion = serializers.CharField(source='sinopsis')
    generos = serializers.SerializerMethodField()
    img = serializers.ImageField(source='portada', read_only=True)
    recaudado = serializers.IntegerField(source='recaudacion_actual')
    meta = serializers.IntegerField(source='meta_recaudacion')
    #autor_nickname = serializers.SerializerMethodField()

    class Meta:
        model = Comic
        fields = [
            'id',
            'titulo',
            'autor',
            #'autor_nickname',# o usa autor_nickname si el autor real es el publicador
            'generos',
            'descripcion',
            'img',
            'recaudado',
            'meta',
            #'publicador',
        ]

    def get_generos(self, obj):
        # Convierte "Cyberpunk, Acuarela" -> ["Cyberpunk", "Acuarela"]
        if not obj.etiquetas_estilo:
            return []
        return [tag.strip() for tag in obj.etiquetas_estilo.split(',') if tag.strip()]
    
    def get_autor_nickname(self, obj):
        if obj.publicador and hasattr(obj.publicador, 'perfil'):
            return obj.publicador.perfil.nickname
        return None