"""
Management command per popolare tbUnitaMisura da CSV.
"""

import os
import csv
from django.core.management.base import BaseCommand
from magazzino.models import TbUnitaMisura


class Command(BaseCommand):
    help = 'Popola la tabella tbUnitaMisura con i dati dal file CSV'
    
    def handle(self, *args, **options):
        # Path al file CSV
        csv_path = os.path.join('Tabelle CSV', 'tbUnitaMisura.csv')
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'File non trovato: {csv_path}'))
            return
        
        # Cancella dati esistenti (opzionale)
        count_existing = TbUnitaMisura.objects.count()
        if count_existing > 0:
            self.stdout.write(self.style.WARNING(f'Trovate {count_existing} unità esistenti. Le elimino...'))
            TbUnitaMisura.objects.all().delete()
        
        # Leggi CSV e importa
        created_count = 0
        with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:  # utf-8-sig rimuove BOM
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                # Salta righe vuote o senza ID
                id_val = row.get('idUnitaMisura', '').strip()
                if not id_val or id_val == '':
                    continue
                
                # Converti stato_attivo
                stato_attivo = row.get('stato_attivo', 'VERO').upper() == 'VERO'
                
                # Crea record
                unita = TbUnitaMisura.objects.create(
                    id_unita_misura=int(id_val),
                    denominazione=row['Denominazione'].strip(),
                    denominazione_stampa=row.get('DenominazioneStampa', '').strip() or None,
                    stato_attivo=stato_attivo
                )
                created_count += 1
                
                self.stdout.write(self.style.SUCCESS(
                    f"✓ ID {unita.id_unita_misura}: {unita.denominazione}"
                ))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Import completato: {created_count} unità di misura create'))
