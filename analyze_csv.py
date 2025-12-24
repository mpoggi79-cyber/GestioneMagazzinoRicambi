#!/usr/bin/env python
import csv

def main():
    with open('Tabelle CSV/tbcontatti.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        headers = reader.fieldnames
        print('Headers del CSV:')
        for i, h in enumerate(headers):
            print(f'{i}: "{h}"')

        # Mostra i primi 5 record
        print('\nPrimi 5 record:')
        rows = list(reader)
        for i, row in enumerate(rows[:5]):
            ruolo = row.get('Ruolo', 'NOT_FOUND')
            print(f'Record {i+1}: Ruolo = "{ruolo}"')

        # Cerca record con ruolo non vuoto
        print('\nRecord con ruolo popolato:')
        count_with_role = 0
        for row in rows:
            ruolo = row.get('Ruolo', '').strip()
            if ruolo:
                count_with_role += 1
                if count_with_role <= 3:  # Mostra solo i primi 3
                    nome = row.get('Nome', '').strip()
                    cognome = row.get('Cognome', '').strip()
                    print(f'  {cognome} {nome}: "{ruolo}"')

        print(f'\nTotale record con ruolo popolato: {count_with_role}')

if __name__ == '__main__':
    main()