"""
Script per inizializzare le configurazioni di backup nel database.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import Configurazione

# Inizializza configurazioni di backup
Configurazione.set_value(
    'backup_dir',
    r'D:\SVILUPPO MATTEO\Progetti\GestioneMagazzinoRicambi Goose\backups',
    'string',
    'Cartella di destinazione per i backup del database'
)

Configurazione.set_value(
    'backup_retention_days',
    30,
    'integer',
    'Giorni di conservazione dei backup prima della pulizia automatica'
)

Configurazione.set_value(
    'mysql_bin_path',
    r'C:\xampp\mysql\bin',
    'string',
    'Percorso della cartella bin di MySQL/MariaDB'
)

print("✓ Configurazioni di backup inizializzate con successo!")
print("\nConfigurazione attuale:")
for key in ['backup_dir', 'backup_retention_days', 'mysql_bin_path']:
    config = Configurazione.objects.get(chiave=key)
    print(f"  {config.chiave}: {config.valore} ({config.tipo_dato})")
