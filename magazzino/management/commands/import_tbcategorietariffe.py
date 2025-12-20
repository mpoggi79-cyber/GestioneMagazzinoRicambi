#!/usr/bin/env python
"""
Management command per importare dati da tbCategorieTariffe.csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from magazzino.models import TbCategorieTariffe


class Command(BaseCommand):
    help = 'Importa dati da Tabelle CSV/tbCategorieTariffe.csv'

    def handle(self, *args, **options):
        csv_file = os.path.join('Tabelle CSV', 'tbCategorieTariffe.csv')
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'❌ File {csv_file} non trovato'))
            return
        
        # Svuota tabella esistente
        TbCategorieTariffe.objects.all().delete()
        self.stdout.write('🗑️  Tabella tbCategorieTariffe svuotata')
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Gestione booleano IsVisible
                is_visible = row['IsVisible'].upper() in ['VERO', 'TRUE', '1', 'SI', 'SÌ']
                
                TbCategorieTariffe.objects.create(
                    id_categorie_tariffe=int(row['idCategorieTariffe']),
                    categoria_tariffe=row['CategoriaTariffe'],
                    is_visible=is_visible
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Importate {count} categorie tariffe'))
