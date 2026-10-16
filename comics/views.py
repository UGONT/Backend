from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
# comics/views.py
from rest_framework import viewsets, mixins
from .models import Comic, ComicExterno, Etiqueta
from .serializers import ComicSerializer, ComicExternoSerializer, EtiquetaSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Perfil, Etiqueta, ComicExterno

class ComicViewSet(viewsets.ReadOnlyModelViewSet):
    #  GET /api/comics/       → lista todos los cómics
    #  GET /api/comics/{id}/  → detalle de un cómic
    queryset = Comic.objects.all().order_by('-id')
    serializer_class = ComicSerializer
    
class ComicExternoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """GET /api/comics-externos/ — lista de cómics para elegir."""
    queryset = ComicExterno.objects.all()
    serializer_class = ComicExternoSerializer
    # permission_classes = [IsAuthenticated]  # opcional
    
class EtiquetaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """GET /api/etiquetas/ — lista de etiquetas para elegir gustos."""
    queryset = Etiqueta.objects.all()
    serializer_class = EtiquetaSerializer
    
    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_mis_gustos(request):
    """
    PATCH /api/perfil/gustos/
    Body: { "gustos": [1,2,3], "comics_leidos": [4,5,6] }
    """
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    
    gustos_ids = request.data.get('gustos', [])
    comics_ids = request.data.get('comics_leidos', [])
    
    perfil.gustos.set(Etiqueta.objects.filter(id__in=gustos_ids))
    perfil.comics_leidos.set(ComicExterno.objects.filter(id__in=comics_ids))
    
    return Response({
        "gustos": [e.id for e in perfil.gustos.all()],
        "comics_leidos": [c.id for c in perfil.comics_leidos.all()],
    })