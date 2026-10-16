# comics/serializers.py
from rest_framework import serializers
from .models import Comic, ComicAutor, Etiqueta, ComicExterno

class ComicExternoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComicExterno
        fields = ['id', 'nombre', 'autor', 'imagen_url']

class EtiquetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etiqueta
        fields = ['id', 'nombre', 'tipo']

class AutorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='autor.username', read_only=True)
    nickname = serializers.SerializerMethodField()
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)

    class Meta:
        model = ComicAutor
        fields = ['username', 'nickname', 'rol', 'rol_display', 'orden']

    def get_nickname(self, obj):
        if hasattr(obj.autor, 'perfil'):
            return obj.autor.perfil.nickname
        return obj.autor.username


class ComicSerializer(serializers.ModelSerializer):
    # Compatibilidad con el frontend actual
    descripcion = serializers.CharField(source='sinopsis')
    img = serializers.ImageField(source='portada', read_only=True)
    recaudado = serializers.IntegerField(source='recaudacion_actual')
    meta = serializers.IntegerField(source='meta_recaudacion')

    # Autores y etiquetas
    autores = AutorSerializer(many=True, read_only=True)
    etiquetas = serializers.SerializerMethodField()      # 👈 CAMBIA
    autor = serializers.SerializerMethodField()
    generos = serializers.SerializerMethodField()

    class Meta:
        model = Comic
        fields = [
            'id',
            'titulo',
            'autor',
            'autores',
            'generos',
            'etiquetas',
            'descripcion',
            'img',
            'recaudado',
            'meta',
            'valoracion_promedio',
            'total_valoraciones',
            'estado',
            'crowdfunding_activo',
            'numero_paginas',
            'fecha_inicio',
            'fecha_fin',
        ]

    def get_autor(self, obj):
        autores = obj.autores.select_related('autor').all()
        if not autores:
            return 'Anónimo'
        return ", ".join(
            (a.autor.perfil.nickname if hasattr(a.autor, 'perfil') else a.autor.username)
            for a in autores
        )

    def get_generos(self, obj):
        return [ce.etiqueta.nombre for ce in obj.etiquetas.select_related('etiqueta').all()]

    def get_etiquetas(self, obj):
        """Devuelve las etiquetas como objetos {id, nombre, tipo}."""
        return [
            {
                'id': ce.etiqueta.id,
                'nombre': ce.etiqueta.nombre,
                'tipo': ce.etiqueta.tipo,
            }
            for ce in obj.etiquetas.select_related('etiqueta').all()
        ]