#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from magazzino.models import TbContatti

def main():
    contatti = TbContatti.objects.all()
    print(f'Total contacts: {contatti.count()}')

    # Cerca contatti con ruolo popolato
    contatti_con_ruolo = TbContatti.objects.exclude(ruolo__isnull=True).exclude(ruolo='')

    print(f'\nContatti con ruolo popolato: {contatti_con_ruolo.count()}')

    if contatti_con_ruolo.exists():
        print('\nContatti con ruolo:')
        for c in contatti_con_ruolo[:10]:
            print(f'ID: {c.id_contatto}, Nome: {c.nome}, Cognome: {c.cognome}, Ruolo: "{c.ruolo}"')
    else:
        print('\nNessun contatto ha il campo ruolo popolato.')

    # Mostra alcuni contatti anche senza ruolo per confronto
    print('\n\nAlcuni contatti (primi 5):')
    for c in contatti[:5]:
        ruolo_display = f'"{c.ruolo}"' if c.ruolo else 'None/Empty'
        print(f'ID: {c.id_contatto}, Nome: {c.nome}, Cognome: {c.cognome}, Ruolo: {ruolo_display}')

if __name__ == '__main__':
    main()