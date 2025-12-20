#!/usr/bin/env python
"""Script per verificare la struttura della tabella pezzi_ricambio"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute('DESCRIBE pezzi_ricambio')
    print("\n📋 Struttura tabella pezzi_ricambio:")
    print(f"{'Campo':<40} | {'Tipo':<25} | {'Null':<8} | {'Key':<8} | {'Default':<15}")
    print("-" * 120)
    for row in cursor.fetchall():
        campo, tipo, null, key, default = row[0], row[1], row[2], row[3], row[4]
        print(f"{campo:<40} | {tipo:<25} | {null:<8} | {key:<8} | {str(default):<15}")
