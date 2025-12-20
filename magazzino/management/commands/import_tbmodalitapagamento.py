#!/usr/bin/env python
"""
Management command per importare dati da tbModalitaPagamento.csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from magazzino.models import TbModalitaPagamento


class Command(BaseCommand):
    help = 'Importa dati da Tabelle CSV/tbModalitaPagamento.csv'

    def handle(self, *args, **options):
        csv_file = os.path.join('Tabelle CSV', 'tbModalitaPagamento.csv')
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'❌ File {csv_file} non trovato'))
            return
        
        # Svuota tabella esistente
        TbModalitaPagamento.objects.all().delete()
        self.stdout.write('🗑️  Tabella tbModalitaPagamento svuotata')
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                TbModalitaPagamento.objects.create(
                    id_modalita_pagamento=int(row['idModalitaPagamento']),
                    nome=row['Nome']
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Importate {count} modalità pagamento'))
