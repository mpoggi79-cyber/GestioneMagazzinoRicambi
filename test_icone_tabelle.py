#!/usr/bin/env python
"""
Script di test per verificare le icone delle tabelle
"""
import os
import sys
import django

# Aggiungi il percorso del progetto al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.views import GestioneTabelleView
from django.test import RequestFactory

def test_icone_tabelle():
    """Test icone tabelle"""
    print("=== Test Icone Tabelle ===")

    view = GestioneTabelleView()
    request = RequestFactory().get('/')
    view.request = request
    context = view.get_context_data()

    print("Tabelle con icone:")
    for tabella in context['tabelle_modificabili']:
        icona = tabella.get('icona', 'NON DEFINITA')
        print(f"  {tabella['nome']}: {tabella['descrizione']} → {icona}")

        if 'icona' not in tabella:
            print(f"    ❌ Manca icona per {tabella['nome']}")
            return False

    print("\n✅ Tutte le tabelle hanno un'icona!")
    return True

if __name__ == '__main__':
    success = test_icone_tabelle()
    sys.exit(0 if success else 1)