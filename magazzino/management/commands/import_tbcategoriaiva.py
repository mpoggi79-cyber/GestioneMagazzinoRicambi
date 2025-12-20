#!/usr/bin/env python
"""
Management command per importare dati da tbCategoriaIVA.csv
"""
import csv
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from magazzino.models import TbCategoriaIVA


class Command(BaseCommand):
    help = 'Importa dati da Tabelle CSV/tbCategoriaIVA.csv'

    def handle(self, *args, **options):
        csv_file = os.path.join('Tabelle CSV', 'tbCategoriaIVA.csv')
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'❌ File {csv_file} non trovato'))
            return
        
        # Svuota tabella esistente
        TbCategoriaIVA.objects.all().delete()
        self.stdout.write('🗑️  Tabella tbCategoriaIVA svuotata')
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Gestione valori IVA con virgola come separatore decimale
                valore_iva_str = row['ValoreIVA'].replace(',', '.')
                
                TbCategoriaIVA.objects.create(
                    id_categoria_iva=int(row['idCategoriaIVA']),
                    nome_categoria=row['NomeCategoria'],
                    valore_iva=Decimal(valore_iva_str)
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Importate {count} categorie IVA'))
