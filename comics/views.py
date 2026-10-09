from django.shortcuts import render

# comics/views.py
from rest_framework import viewsets
from .models import Comic
from .serializers import ComicSerializer


class ComicViewSet(viewsets.ReadOnlyModelViewSet):
    #  GET /api/comics/       → lista todos los cómics
    #  GET /api/comics/{id}/  → detalle de un cómic
    queryset = Comic.objects.all().order_by('-id')
    serializer_class = ComicSerializer