#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per testare la connessione al database MySQL.

Eseguire con: python test_db_connection.py
"""

import os
import django
import sys

# Configura le impostazioni di Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    print("[OK] Django setup completato con successo!")
except Exception as e:
    print(f"[ERRORE] Errore durante il setup di Django: {e}")
    sys.exit(1)

# Testa la connessione al database
from django.db import connections
from django.db.utils import OperationalError

try:
    db_conn = connections['default']
    db_conn.ensure_connection()
    print("[OK] Connessione al database MySQL riuscita!")
    print(f"   Database: {db_conn.settings_dict['NAME']}")
    print(f"   Host: {db_conn.settings_dict['HOST']}")
    print(f"   User: {db_conn.settings_dict['USER']}")
except OperationalError as e:
    print(f"[ERRORE] Errore di connessione al database: {e}")
    print("\nSUGGERIMENTI:")
    print("   1. Assicurati che XAMPP MySQL sia avviato")
    print("   2. Verifica che il database 'GMR' esista")
    print("   3. Controlla le credenziali in config/settings.py")
    sys.exit(1)

print("\n" + "="*60)
print("[OK] TUTTO PRONTO! Il sistema e' connesso al database.")
print("="*60)
