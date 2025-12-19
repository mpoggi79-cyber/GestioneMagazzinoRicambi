from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Gestione Utenti e Autenticazione'
    
    def ready(self):
        """Registra i signals quando l'app è pronta"""
        import accounts.signals  # noqa
