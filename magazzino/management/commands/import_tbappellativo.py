#!/usr/bin/env python
"""
Management command per importare dati da tbAppellativo.csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from magazzino.models import TbAppellativo


class Command(BaseCommand):
    help = 'Importa dati da Tabelle CSV/tbAppellativo.csv'

    def handle(self, *args, **options):
        csv_file = os.path.join('Tabelle CSV', 'tbAppellativo.csv')
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'❌ File {csv_file} non trovato'))
            return
        
        # Svuota tabella esistente
        TbAppellativo.objects.all().delete()
        self.stdout.write('🗑️  Tabella tbAppellativo svuotata')
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                TbAppellativo.objects.create(
                    id_appellativo=int(row['idAppellativo']),
                    descrizione=row['Descrizione']
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Importati {count} appellativi'))
