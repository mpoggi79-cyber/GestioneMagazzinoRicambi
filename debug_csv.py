#!/usr/bin/env python
with open('Tabelle CSV/tbcontatti.csv', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    # Riga 4 è Carlo Gellosi (indice 3)
    line = lines[3]
    print('Riga Carlo Gellosi:')
    print(repr(line))
    print()
    print('Suddivisa per ; :')
    parts = line.strip().split(';')
    for i, part in enumerate(parts):
        print(f'{i}: "{part}"')

    print(f'\nTotale colonne: {len(parts)}')
    print(f'Header ha 13 colonne, questa riga ne ha: {len(parts)}')