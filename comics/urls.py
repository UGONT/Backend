# comics/urls.py
from rest_framework.routers import DefaultRouter
from .views import ComicViewSet

router = DefaultRouter()
router.register(r'comics', ComicViewSet, basename='comic')

urlpatterns = router.urls