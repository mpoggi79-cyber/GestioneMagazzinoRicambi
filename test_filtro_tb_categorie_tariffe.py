#!/usr/bin/env python
"""
Script di test per verificare il filtro show_inactive per TbCategorieTariffe
"""
import os
import sys
import django

# Aggiungi il percorso del progetto al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import TbCategorieTariffe
from magazzino.views import ModificaTabellaView
from django.test import RequestFactory

def test_filtro_show_inactive():
    """Test filtro show_inactive per TbCategorieTariffe"""
    print("=== Test Filtro show_inactive per TbCategorieTariffe ===")

    # Verifica dati nel database
    total_records = TbCategorieTariffe.objects.count()
    visible_records = TbCategorieTariffe.objects.filter(is_visible=True).count()
    hidden_records = TbCategorieTariffe.objects.filter(is_visible=False).count()

    print(f"Record totali: {total_records}")
    print(f"Record visibili (is_visible=True): {visible_records}")
    print(f"Record nascosti (is_visible=False): {hidden_records}")

    # Test con show_inactive=False (default)
    print("\n1. Test con show_inactive=False:")
    view = ModificaTabellaView()
    request = RequestFactory().get('/')
    view.request = request
    context = view.get_context_data(nome_tabella='tbcategorietariffe')

    records = context.get('records', [])
    print(f"   Record mostrati: {len(records)}")

    # Verifica che tutti i record mostrati abbiano is_visible=True
    all_visible = all(record['valori'][2] is True for record in records)  # is_visible è il terzo campo
    if all_visible and len(records) == visible_records:
        print("   ✓ Filtro corretto: mostra solo record visibili")
    else:
        print(f"   ✗ Filtro NON corretto. Attesi {visible_records} record visibili, trovati {len(records)}")
        return False

    # Test con show_inactive=True
    print("\n2. Test con show_inactive=True:")
    view = ModificaTabellaView()
    request = RequestFactory().get('/?show_inactive=true')
    view.request = request
    context = view.get_context_data(nome_tabella='tbcategorietariffe')

    records = context.get('records', [])
    print(f"   Record mostrati: {len(records)}")

    if len(records) == total_records:
        print("   ✓ Filtro corretto: mostra tutti i record")
    else:
        print(f"   ✗ Filtro NON corretto. Attesi {total_records} record totali, trovati {len(records)}")
        return False

    # Verifica che ci siano sia record visibili che nascosti
    has_visible = any(record['valori'][2] is True for record in records)
    has_hidden = any(record['valori'][2] is False for record in records)

    if has_visible and has_hidden:
        print("   ✓ Mostra sia record visibili che nascosti")
    else:
        print("   ✗ NON mostra correttamente record visibili e nascosti")
        return False

    print("\n=== Test Filtro COMPLETATO con SUCCESSO ===")
    return True

if __name__ == '__main__':
    success = test_filtro_show_inactive()
    sys.exit(0 if success else 1)