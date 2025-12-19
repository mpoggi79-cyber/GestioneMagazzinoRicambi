"""
Script per correggere i codici SCM non conformi al formato 10 cifre + 1 lettera maiuscola.
Aggiunge uno 0 come decima cifra prima della lettera finale.
"""

import os
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import PezzoRicambio

def fix_codici_scm():
    """Corregge automaticamente i codici SCM non validi"""
    
    # Trova tutti gli articoli con codice SCM
    articoli = PezzoRicambio.objects.exclude(codice_scm__isnull=True).exclude(codice_scm='')
    
    print(f"Totale articoli con codice SCM: {articoli.count()}")
    print("-" * 70)
    
    # Pattern valido: 10 cifre + 1 lettera maiuscola
    pattern_valido = r'^\d{10}[A-Z]$'
    
    # Pattern per codici con 9 cifre + 1 lettera (bisogna aggiungere 1 cifra)
    pattern_da_correggere = r'^(\d{9})([A-Z])$'
    
    corretti = 0
    gia_validi = 0
    non_correggibili = []
    
    for articolo in articoli:
        codice = articolo.codice_scm
        
        # Verifica se è già valido
        if re.match(pattern_valido, codice):
            gia_validi += 1
            print(f"✓ ID {articolo.id_articolo} ({articolo.codice_interno}): {codice} - già valido")
            continue
        
        # Prova a correggere: 9 cifre + lettera -> aggiungi uno 0
        match = re.match(pattern_da_correggere, codice)
        if match:
            cifre = match.group(1)  # 9 cifre
            lettera = match.group(2)  # 1 lettera
            nuovo_codice = f"{cifre}0{lettera}"  # 9 cifre + 0 + lettera = 10 cifre + lettera
            
            print(f"⚠ ID {articolo.id_articolo} ({articolo.codice_interno}):")
            print(f"  Vecchio: {codice} (lunghezza: {len(codice)})")
            print(f"  Nuovo:   {nuovo_codice} (lunghezza: {len(nuovo_codice)})")
            
            # Salva il nuovo codice
            articolo.codice_scm = nuovo_codice
            articolo.save()
            corretti += 1
        else:
            # Codice non correggibile automaticamente
            non_correggibili.append({
                'id': articolo.id_articolo,
                'codice_interno': articolo.codice_interno,
                'codice_scm': codice,
                'lunghezza': len(codice)
            })
            print(f"✗ ID {articolo.id_articolo} ({articolo.codice_interno}): {codice} - NON correggibile automaticamente")
    
    print("-" * 70)
    print(f"\n📊 RIEPILOGO:")
    print(f"  ✓ Già validi: {gia_validi}")
    print(f"  🔧 Corretti: {corretti}")
    print(f"  ✗ Non correggibili: {len(non_correggibili)}")
    
    if non_correggibili:
        print(f"\n⚠️  ATTENZIONE: {len(non_correggibili)} codici richiedono correzione manuale:")
        for item in non_correggibili:
            print(f"  - ID {item['id']}: {item['codice_interno']} -> SCM: [{item['codice_scm']}] (lunghezza: {item['lunghezza']})")
    
    if corretti > 0:
        print(f"\n✅ {corretti} codici SCM sono stati corretti con successo!")

if __name__ == '__main__':
    print("=" * 70)
    print("CORREZIONE AUTOMATICA CODICI SCM")
    print("=" * 70)
    fix_codici_scm()
    print("=" * 70)
