#!/usr/bin/env python
"""
Script per creare un fornitore fallback "Non Specificato"
Questo fornitore viene usato quando si elimina un altro fornitore
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import Fornitore

def create_fallback_fornitore():
    """Crea o recupera il fornitore fallback"""
    fornitore, created = Fornitore.objects.get_or_create(
        id=999,
        defaults={
            'ragione_sociale': 'Non Specificato',
            'cognome_contatto': 'Sistema',
            'nome_contatto': 'Fallback',
            'telefono': '',
            'email': '',
            'indirizzo': '',
            'cap': '',
            'citta': '',
            'provincia': '',
            'paese': '',
            'note': 'Fornitore generico usato quando si elimina un fornitore con articoli associati. NON ELIMINARE.',
        }
    )
    
    if created:
        print(f"✅ Fornitore fallback creato: {fornitore.ragione_sociale} (ID: {fornitore.id})")
    else:
        print(f"✓ Fornitore fallback già esistente: {fornitore.ragione_sociale} (ID: {fornitore.id})")
    
    return fornitore

if __name__ == '__main__':
    create_fallback_fornitore()
