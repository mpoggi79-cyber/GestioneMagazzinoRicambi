#!/usr/bin/env python
"""
Script per verificare che tutto il sistema sia correttamente configurato.

Eseguire con: python check_system.py
"""

import os
import sys
import django
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version as package_version

print("\n" + "="*70)
print("🔍 VERIFICA SISTEMA - Gestione Magazzino Ricambi")
print("="*70 + "\n")

# ============================================================================
# 1. VERIFICA PYTHON
# ============================================================================
print("📦 1. VERIFICA PYTHON")
print("-" * 70)

python_version = sys.version_info
print(f"✅ Python versione: {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
    print("⚠️  Attenzione: Python 3.10+ consigliato!")
else:
    print("✅ Versione Python compatibile")

# ============================================================================
# 2. VERIFICA VIRTUAL ENVIRONMENT
# ============================================================================
print("\n🐍 2. VERIFICA VIRTUAL ENVIRONMENT")
print("-" * 70)

if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("✅ Virtual environment attivo")
    print(f"   Path: {sys.prefix}")
else:
    print("⚠️  Virtual environment NON attivo!")
    print("   Attiva con: venv\\Scripts\\activate.ps1")

# ============================================================================
# 3. VERIFICA DIPENDENZE
# ============================================================================
print("\n📚 3. VERIFICA DIPENDENZE")
print("-" * 70)

dependencies = {
    'django': ('Django', 'Django'),
    'pymysql': ('PyMySQL', 'PyMySQL'),
    'argon2': ('argon2-cffi', 'argon2-cffi'),
    'crispy_forms': ('django-crispy-forms', 'django-crispy-forms'),
    'crispy_bootstrap5': ('crispy-bootstrap5', 'crispy-bootstrap5'),
}

for module, dependency_info in dependencies.items():
    name, package_name = dependency_info
    try:
        __import__(module)
        try:
            installed_version = package_version(package_name)
        except PackageNotFoundError:
            installed_version = 'sconosciuta'
        print(f"✅ {name}: {installed_version}")
    except ImportError:
        print(f"❌ {name}: NON INSTALLATO")

# ============================================================================
# 4. VERIFICA STRUTTURA PROGETTO
# ============================================================================
print("\n📁 4. VERIFICA STRUTTURA PROGETTO")
print("-" * 70)

base_dir = Path(__file__).resolve().parent

required_dirs = {
    'config': 'Configurazione Django',
    'accounts': 'App Autenticazione',
    'magazzino': 'App Magazzino',
    'templates': 'Template HTML',
    'static': 'File Statici',
    'logs': 'Log Files',
    'venv': 'Virtual Environment',
}

for dir_name, description in required_dirs.items():
    dir_path = base_dir / dir_name
    if dir_path.exists():
        print(f"✅ {dir_name}/: {description}")
    else:
        print(f"❌ {dir_name}/: MANCANTE")

required_files = {
    'manage.py': 'Gestione Django',
    'database_creation.sql': 'Script DB',
    'requirements.txt': 'Dipendenze',
    'README.md': 'Documentazione',
}

for file_name, description in required_files.items():
    file_path = base_dir / file_name
    if file_path.exists():
        print(f"✅ {file_name}: {description}")
    else:
        print(f"❌ {file_name}: MANCANTE")

# ============================================================================
# 5. VERIFICA DJANGO
# ============================================================================
print("\n🎯 5. VERIFICA DJANGO")
print("-" * 70)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    print("✅ Django setup completato")
except Exception as e:
    print(f"❌ Errore Django setup: {e}")
    sys.exit(1)

from django.conf import settings
print(f"✅ Settings: {settings.SETTINGS_MODULE}")
print(f"✅ Debug mode: {settings.DEBUG}")
print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")

# ============================================================================
# 6. VERIFICA DATABASE
# ============================================================================
print("\n🗄️  6. VERIFICA DATABASE")
print("-" * 70)

from django.db import connections
from django.db.utils import OperationalError

try:
    db_conn = connections['default']
    db_conn.ensure_connection()
    
    print("✅ Connessione al database riuscita!")
    print(f"   Engine: {db_conn.settings_dict['ENGINE']}")
    print(f"   Database: {db_conn.settings_dict['NAME']}")
    print(f"   Host: {db_conn.settings_dict['HOST']}")
    print(f"   User: {db_conn.settings_dict['USER']}")
    
except OperationalError as e:
    print(f"❌ Errore di connessione: {e}")
    print("\n💡 Suggerimenti:")
    print("   1. Assicurati che MySQL sia avviato in XAMPP")
    print("   2. Verifica che il database 'GMR' esista")
    print("   3. Esegui: database_creation.sql")

# ============================================================================
# 7. VERIFICA APP INSTALLATE
# ============================================================================
print("\n📦 7. VERIFICA APP DJANGO")
print("-" * 70)

print("App installate:")
for app in settings.INSTALLED_APPS:
    if not app.startswith('django.'):
        print(f"  ✅ {app}")

# ============================================================================
# 8. VERIFICA MIGRATIONS
# ============================================================================
print("\n🔄 8. VERIFICA MIGRATIONS")
print("-" * 70)

from django.core.management import call_command
from io import StringIO

try:
    output = StringIO()
    call_command('showmigrations', verbosity=1, stdout=output)
    
    result = output.getvalue()
    if 'No migrations' in result or len(result.split('\n')) > 5:
        print("✅ Migrazioni caricate")
    else:
        print("⚠️  Verifica manualmente le migrazioni")
        
except Exception as e:
    print(f"❌ Errore migrazioni: {e}")

# ============================================================================
# 9. VERIFICA MODELS
# ============================================================================
print("\n📋 9. VERIFICA MODELS")
print("-" * 70)

try:
    from magazzino.models import (
        Categoria, PezzoRicambio, Fornitore, MovimentoMagazzino, Giacenza
    )
    from accounts.models import ProfiloUtente, LogAccesso
    
    print("✅ Models magazzino caricati")
    print("✅ Models accounts caricati")
    
except ImportError as e:
    print(f"❌ Errore caricamento models: {e}")

# ============================================================================
# 10. VERIFICA USERS
# ============================================================================
print("\n👥 10. VERIFICA UTENTI")
print("-" * 70)

from django.contrib.auth.models import User

user_count = User.objects.count()
print(f"✅ Utenti nel sistema: {user_count}")

if user_count > 0:
    print("\n   Utenti esistenti:")
    for user in User.objects.all()[:5]:
        try:
            profilo = user.profilo
            ruolo = profilo.get_ruolo_display()
        except:
            ruolo = "Sconosciuto"
        
        print(f"   • {user.username} ({user.email}) - Ruolo: {ruolo}")
    
    if user_count > 5:
        print(f"   ... e altri {user_count - 5} utenti")
else:
    print("⚠️  Nessun utente nel sistema")
    print("   Esegui: python manage.py migrate")
    print("   Poi, se vuoi dati demo: python manage.py populate_db")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("✅ VERIFICA COMPLETATA!")
print("="*70 + "\n")

print("🚀 Prossimi step:")
print("   1. Se tutto è ✅: python manage.py runserver")
print("   2. Vai a: http://localhost:8000")
print("   3. Login con admin / admin")
print("\n")
