#!/usr/bin/env python
"""
Management command per importare dati da tbPrestazioni.csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from magazzino.models import TbPrestazioni, UnitaMisura, TbCategorieTariffe, TbCategoriaIVA


class Command(BaseCommand):
    help = 'Importa dati da Tabelle CSV/tbPrestazioni.csv'

    def handle(self, *args, **options):
        csv_file = os.path.join('Tabelle CSV', 'tbPrestazioni.csv')
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'❌ File {csv_file} non trovato'))
            return
        
        # Svuota tabella esistente
        TbPrestazioni.objects.all().delete()
        self.stdout.write('🗑️  Tabella tbPrestazioni svuotata')
        
        count = 0
        errors = 0
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                try:
                    # Gestisci prezzo con virgola e punto (formato italiano)
                    prezzo_str = row['PrezzoUnitario'].replace('.', '').replace(',', '.')
                    prezzo = float(prezzo_str)
                    
                    # Gestisci boolean
                    visualizza = row['VisualizzaPreventivo'].upper() == 'VERO'
                    
                    # Gestisci ordine stampa (può essere vuoto)
                    ordine = int(row['OrdineStampa']) if row['OrdineStampa'] else None
                    
                    TbPrestazioni.objects.create(
                        id_prestazione=int(row['idPrestazione']),
                        denominazione=row['Denominazione'],
                        id_unita_misura_id=int(row["idUnitaMisura 'FK'"]),
                        prezzo_unitario=prezzo,
                        id_categorie_tariffe_id=int(row["idCategorieTariffe 'FK'"]),
                        id_categoria_iva_id=int(row["idCategoriaIVA 'FK'"]),
                        visualizza_preventivo=visualizza,
                        ordine_stampa=ordine
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️  Errore riga {row}: {e}'))
                    errors += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Importate {count} prestazioni'))
        if errors:
            self.stdout.write(self.style.WARNING(f'⚠️  {errors} errori'))