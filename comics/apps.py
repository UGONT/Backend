# comics/apps.py
from django.apps import AppConfig


class ComicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comics'

    def ready(self):
        import comics.signals  # noqa: F401