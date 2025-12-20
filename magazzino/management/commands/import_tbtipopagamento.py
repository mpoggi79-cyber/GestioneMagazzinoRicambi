#!/usr/bin/env python
"""
Management command per importare dati da tbTipoPagamento.csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from magazzino.models import TbTipoPagamento


class Command(BaseCommand):
    help = 'Importa dati da Tabelle CSV/tbTipoPagamento.csv'

    def handle(self, *args, **options):
        csv_file = os.path.join('Tabelle CSV', 'tbTipoPagamento.csv')
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'❌ File {csv_file} non trovato'))
            return
        
        # Svuota tabella esistente
        TbTipoPagamento.objects.all().delete()
        self.stdout.write('🗑️  Tabella tbTipoPagamento svuotata')
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                TbTipoPagamento.objects.create(
                    id_tipo_pagamento=int(row['idTipoPagamento']),
                    descrizione=row['descrizione'],
                    data_rif_scad=row['DataRifScad'],
                    giorni_data_rif=int(row['GiorniDataRif']),
                    giorno_addebito=int(row['GiornoAddebito'])
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Importati {count} tipi pagamento'))
