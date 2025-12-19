from django.apps import AppConfig


class MagazzinoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'magazzino'
    
    def ready(self):
        """Importa i signals quando l'app è pronta"""
        import magazzino.signals
