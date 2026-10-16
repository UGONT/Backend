from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ComicViewSet,
    ComicExternoViewSet,
    EtiquetaViewSet,
    actualizar_mis_gustos,
)

router = DefaultRouter()
router.register(r'comics', ComicViewSet, basename='comic')
router.register(r'comics-externos', ComicExternoViewSet, basename='comic-externo')
router.register(r'etiquetas', EtiquetaViewSet, basename='etiqueta')

urlpatterns = [
    path('perfil/gustos/', actualizar_mis_gustos, name='actualizar-gustos'),
]

urlpatterns += router.urls