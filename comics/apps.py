from django.apps import AppConfig


class ComicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comics'

    def ready(self):
        # Importamos las señales cuando Django arranca
        import comics.signals
