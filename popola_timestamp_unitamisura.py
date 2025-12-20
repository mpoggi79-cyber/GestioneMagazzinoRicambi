"""
Script per popolare i campi creato_il e modificato_il in tbUnitaMisura
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from magazzino.models import TbUnitaMisura

def popola_timestamp():
    """Popola i timestamp vuoti con la data corrente"""
    
    now = timezone.now()
    
    # Trova tutti i record con timestamp NULL
    unita_da_aggiornare = TbUnitaMisura.objects.filter(
        creato_il__isnull=True
    ) | TbUnitaMisura.objects.filter(
        modificato_il__isnull=True
    )
    
    count = unita_da_aggiornare.count()
    
    if count == 0:
        print("✅ Tutti i record hanno già i timestamp popolati")
        return
    
    print(f"📋 Trovati {count} record da aggiornare")
    
    # Aggiorna tutti i record
    for unita in unita_da_aggiornare:
        if not unita.creato_il:
            unita.creato_il = now
        if not unita.modificato_il:
            unita.modificato_il = now
        unita.save()
        
        print(f"✓ Aggiornato ID {unita.id_unita_misura}: {unita.denominazione}")
    
    print(f"\n✅ Completato! {count} record aggiornati con timestamp: {now}")


if __name__ == '__main__':
    popola_timestamp()
