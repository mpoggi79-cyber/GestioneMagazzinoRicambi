#!/usr/bin/env python
"""
Management command per importare dati da tbContatti.csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from magazzino.models import TbContatti


class Command(BaseCommand):
    help = 'Importa dati da Tabelle CSV/tbContatti.csv'

    def handle(self, *args, **options):
        csv_file = os.path.join('Tabelle CSV', 'tbContatti.csv')

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'❌ File {csv_file} non trovato'))
            return

        # Svuota tabella esistente
        TbContatti.objects.all().delete()
        self.stdout.write('🗑️  Tabella tbContatti svuotata')

        count = 0
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                count += 1
                # Gestione campi vuoti e conversioni
                id_cliente = int(row['idCliente \'FK\'']) if row['idCliente \'FK\''] else None
                id_fornitore = int(row['idFornitore \'FK\'']) if row['idFornitore \'FK\''] else None
                id_appellativo = int(row['idAppellativo \'FK\'']) if row['idAppellativo \'FK\''] else None

                # Gestione numeri di telefono (formato scientifico)
                telefono_azienda = self._clean_phone_number(row['TelefonoAzienda'])
                cellulare_azienda = self._clean_phone_number(row['CellulareAzienda'])
                cellulare_personale = self._clean_phone_number(row['CellularePersonale'])

                # Correzione automatica: se Ruolo è vuoto ma Nota contiene un ruolo, sposta il valore
                ruolo = row['Ruolo'].strip()
                nota = row['Nota'].strip()
                
                if not ruolo and nota:
                    # Controlla se la nota sembra contenere un ruolo
                    ruoli_tipici = ['titolare', 'amministrazione', 'segretario', 'direttore', 'manager', 'responsabile']
                    if any(ruolo_tipico.lower() in nota.lower() for ruolo_tipico in ruoli_tipici):
                        ruolo = nota
                        nota = ''  # Svuota la nota

                TbContatti.objects.create(
                    id_contatto=int(row['idContatto']),
                    id_cliente=id_cliente,
                    id_fornitore=id_fornitore,
                    id_appellativo=id_appellativo,
                    nome=row['Nome'],
                    cognome=row['Cognome'],
                    ruolo=ruolo,
                    telefono_azienda=telefono_azienda,
                    cellulare_azienda=cellulare_azienda,
                    email_azienda=row['emailAzienda'],
                    cellulare_personale=cellulare_personale,
                    email_personale=row['eMailPersonale'],
                    nota=nota
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Importati {count} contatti'))

    def _clean_phone_number(self, phone_str):
        """Pulisce e converte i numeri di telefono dal formato scientifico"""
        if not phone_str:
            return ''

        # Rimuovi spazi e converti da formato scientifico
        phone_str = phone_str.strip()
        if 'E+' in phone_str:
            try:
                # Converte da formato scientifico (es. "3,91E+11" -> "391000000000")
                parts = phone_str.replace(',', '.').split('E+')
                base = float(parts[0])
                exp = int(parts[1])
                result = str(int(base * (10 ** exp)))
                return result
            except (ValueError, IndexError):
                return phone_str
        return phone_str