"""
Script per esportare tutte le tabelle esistenti del database Django in formato CSV.

Esporta i modelli esistenti da:
- magazzino (Categoria, tbunitamisura, Fornitore, PezzoRicambio, Giacenza, MovimentoMagazzino, etc.)
- accounts (ProfiloUtente, LogAccesso)
"""

import os
import sys
import django
import csv
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
from magazzino.models import (
    Categoria, tbunitamisura, Fornitore, PezzoRicambio, 
    Giacenza, MovimentoMagazzino, Inventario, DettaglioInventario,
    ModelloMacchinaSCM, MatricolaMacchinaSCM
)
from accounts.models import ProfiloUtente, LogAccesso


def export_model_to_csv(model_class, output_dir='Tabelle CSV Esportate'):
    """
    Esporta un modello Django in file CSV.
    
    Args:
        model_class: La classe del modello da esportare
        output_dir: Directory di output per i file CSV
    """
    # Crea directory se non esiste
    os.makedirs(output_dir, exist_ok=True)
    
    # Nome file CSV dal nome della tabella database
    table_name = model_class._meta.db_table
    filename = f"{table_name}.csv"
    filepath = os.path.join(output_dir, filename)
    model_name = model_class._meta.model_name
    
    # Ottieni tutti i campi del modello (esclusi ManyToMany)
    fields = [
        field for field in model_class._meta.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    
    # Header CSV con nomi delle colonne
    fieldnames = []
    for field in fields:
        col_name = field.name
        # Aggiungi 'FK' se è ForeignKey
        if field.get_internal_type() == 'ForeignKey':
            col_name = f"{field.db_column or field.name} 'FK'"
        fieldnames.append(col_name)
    
    # Ottieni tutti i record
    queryset = model_class.objects.all()
    count = queryset.count()
    
    if count == 0:
        print(f"⚠️  {model_name}: Nessun dato da esportare")
        return
    
    # Scrivi CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        
        # Scrivi header
        writer.writerow(fieldnames)
        
        # Scrivi righe
        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field.name)
                
                # Gestisci None
                if value is None:
                    row.append('')
                # Gestisci ForeignKey (prendi l'ID)
                elif field.get_internal_type() == 'ForeignKey':
                    row.append(value.pk if value else '')
                # Gestisci Boolean
                elif isinstance(value, bool):
                    row.append('VERO' if value else 'FALSO')
                # Gestisci datetime
                elif isinstance(value, datetime):
                    row.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                # Altri tipi
                else:
                    row.append(str(value))
            
            writer.writerow(row)
    
    print(f"✅ {table_name}.csv - {count} righe esportate")


def main():
    """Esporta tutte le tabelle principali"""
    
    print("=" * 60)
    print("EXPORT DATABASE → CSV")
    print("=" * 60)
    print()
    
    # Lista modelli da esportare
    models_to_export = [
        # Magazzino
        ('Categoria', Categoria),
        ('UnitaMisura', UnitaMisura),
        ('Fornitore', Fornitore),
        ('PezzoRicambio', PezzoRicambio),
        ('Giacenza', Giacenza),
        ('MovimentoMagazzino', MovimentoMagazzino),
        ('Inventario', Inventario),
        ('DettaglioInventario', DettaglioInventario),
        ('ModelloMacchinaSCM', ModelloMacchinaSCM),
        ('MatricolaMacchinaSCM', MatricolaMacchinaSCM),
    ]
    
    # Esporta ogni modello
    for name, model in models_to_export:
        try:
            export_model_to_csv(model)
        except Exception as e:
            print(f"❌ Errore esportando {name}: {e}")
    
    print()
    print("=" * 60)
    print("✅ EXPORT COMPLETATO")
    print("=" * 60)
    print()
    print(f"📁 File salvati in: Tabelle CSV Esportate/")


if __name__ == '__main__':
    main()
