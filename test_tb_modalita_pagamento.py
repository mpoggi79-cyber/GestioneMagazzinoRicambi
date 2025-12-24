#!/usr/bin/env python
"""
Script di test per verificare la configurazione di TbModalitaPagamento
"""
import os
import sys
import django

# Aggiungi il percorso del progetto al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import TbModalitaPagamento
from magazzino.views import GestioneTabelleView, ModificaTabellaView
from django.test import RequestFactory

def test_tb_modalita_pagamento_config():
    """Test configurazione TbModalitaPagamento"""
    print("=== Test Configurazione TbModalitaPagamento ===")

    # Test modello
    print("1. Test modello TbModalitaPagamento:")
    try:
        # Verifica che il modello esista
        fields = [f.name for f in TbModalitaPagamento._meta.fields]
        print(f"   Campi del modello: {fields}")

        # Verifica numero record
        count = TbModalitaPagamento.objects.count()
        print(f"   Numero record: {count}")

        # Verifica alcuni record
        records = TbModalitaPagamento.objects.all()[:3]
        for record in records:
            print(f"   Record: id={record.id_modalita_pagamento}, nome={record.nome}")

    except Exception as e:
        print(f"   ERRORE modello: {e}")
        return False

    # Test configurazione viste
    print("\n2. Test configurazione viste:")

    # Test GestioneTabelleView
    try:
        view = GestioneTabelleView()
        request = RequestFactory().get('/')
        view.request = request
        context = view.get_context_data()

        found = False
        for tabella in context['tabelle_modificabili']:
            if tabella['nome'] == 'tbmodalitapagamento':
                print("   ✓ TbModalitaPagamento presente in tabelle_modificabili")
                print(f"     Descrizione: {tabella['descrizione']}")
                print(f"     Icona: {tabella['icona']}")
                found = True
                break

        if not found:
            print("   ✗ TbModalitaPagamento NON presente in tabelle_modificabili")
            return False

    except Exception as e:
        print(f"   ERRORE GestioneTabelleView: {e}")
        return False

    # Test ModificaTabellaView
    try:
        view = ModificaTabellaView()
        request = RequestFactory().get('/')
        view.request = request
        context = view.get_context_data(nome_tabella='tbmodalitapagamento')

        print("   ✓ ModificaTabellaView configurata per tbmodalitapagamento")
        print(f"     Nome tabella: {context.get('nome_tabella')}")
        print(f"     Descrizione: {context.get('descrizione_tabella')}")
        print(f"     Campi: {context.get('campi')}")
        print(f"     Filtro stato: {context.get('has_status_filter')}")
        print(f"     Numero record: {len(context.get('records', []))}")

        # Verifica configurazione dettagliata
        expected_fields = ['id_modalita_pagamento', 'nome']
        if context.get('campi') == expected_fields:
            print("   ✓ Campi configurati correttamente")
        else:
            print(f"   ✗ Campi NON corrispondono. Attesi: {expected_fields}, Trovati: {context.get('campi')}")
            return False

        if not context.get('has_status_filter'):
            print("   ✓ Nessun filtro stato (tabella semplice)")
        else:
            print("   ✗ Filtro stato NON dovrebbe essere abilitato")
            return False

    except Exception as e:
        print(f"   ERRORE ModificaTabellaView: {e}")
        return False

    print("\n=== Test COMPLETATO con SUCCESSO ===")
    return True

if __name__ == '__main__':
    success = test_tb_modalita_pagamento_config()
    sys.exit(0 if success else 1)