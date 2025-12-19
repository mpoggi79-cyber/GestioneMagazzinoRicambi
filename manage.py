#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


###
# ------------------------------------------------
# Gestione Server
# Avvia il server di sviluppo
# python manage.py runserver

# Avvia su porta specifica
# python manage.py runserver 8080

# Fermare il server: Ctrl+C nel terminale
# --------------------------------------------------
# Gestione Database
# Crea nuove migrazioni (dopo aver modificato models.py)
# python manage.py makemigrations

# Applica le migrazioni al database
# python manage.py migrate

# Mostra le migrazioni
# python manage.py showmigrations

# Apri shell Python con Django
# python manage.py shell
# ------------------------------------------------
# Gestione Utenti
# Crea un superuser (admin)
# python manage.py createsuperuser

# Cambia password di un utente
# python manage.py changepassword username
# ------------------------------------------------
# Utility
# Raccogli file statici (per produzione)
# python manage.py collectstatic

# Verifica problemi nel progetto
# python manage.py check

# Pulisci sessioni scadute
# python manage.py clearsessions
# ------------------------------------------------
# Comandi Personalizzati (nel tuo progetto)
# Popola il database con dati di test
# python manage.py populate_db

# Crea fornitore fallback
# python manage.py create_fallback_fornitore
###
