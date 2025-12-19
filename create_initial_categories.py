#!/usr/bin/env python
"""
Script per creare le 3 macrocategorie iniziali nel sistema.

Esegui con: python create_initial_categories.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import Categoria

def create_initial_categories():
    """Crea le 3 macrocategorie principali"""
    
    macrocategorie = [
        {
            'nome': 'RICAMBI MECCANICI',
            'descrizione': 'Componenti meccanici, cinghie, ingranaggi, cuscinetti, guarnizioni',
            'ordine': 0
        },
        {
            'nome': 'RICAMBI ELETTRICI',
            'descrizione': 'Componenti elettrici, schede, motori, sensori, cavi',
            'ordine': 1
        },
        {
            'nome': 'RICAMBI IDRAULICI',
            'descrizione': 'Componenti idraulici, tubi, valvole, pompe, cilindri',
            'ordine': 2
        }
    ]
    
    print("🚀 Creazione macrocategorie iniziali...\n")
    
    for macro in macrocategorie:
        # Verifica se esiste già
        existing = Categoria.objects.filter(nome_categoria=macro['nome']).first()
        
        if existing:
            print(f"⏭️  '{macro['nome']}' esiste già (ID: {existing.id_categoria})")
        else:
            categoria = Categoria.objects.create(
                nome_categoria=macro['nome'],
                descrizione=macro['descrizione'],
                categoria_padre=None,  # Nessun padre = livello 0
                ordine=macro['ordine'],
                stato_attivo=True
            )
            print(f"✅ Creata: '{categoria.nome_categoria}' (ID: {categoria.id_categoria}, Livello: {categoria.livello})")
    
    print(f"\n✨ Completato! Totale categorie: {Categoria.objects.count()}")
    print(f"📊 Macrocategorie (livello 0): {Categoria.objects.filter(livello=0).count()}")
    print(f"📂 Categorie (livello 1): {Categoria.objects.filter(livello=1).count()}")
    print(f"📄 Sottocategorie (livello 2): {Categoria.objects.filter(livello=2).count()}")
    
    print("\n💡 Suggerimento:")
    print("   Ora puoi accedere a /magazzino/categorie/ per vedere la vista ad albero")
    print("   e iniziare a creare sottocategorie tramite l'interfaccia grafica!")

if __name__ == '__main__':
    try:
        create_initial_categories()
    except Exception as e:
        print(f"\n❌ Errore: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
