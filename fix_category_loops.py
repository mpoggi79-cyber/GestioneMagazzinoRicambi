"""
Script per correggere i loop circolari nelle categorie
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import Categoria

def fix_circular_loops():
    """Rileva e corregge loop circolari nelle categorie"""
    
    print("🔍 Ricerca loop circolari...")
    
    # Ottieni tutte le categorie
    categorie = Categoria.objects.all()
    fixed = []
    
    for cat in categorie:
        if not cat.categoria_padre:
            continue
            
        # Traccia il percorso per rilevare loop
        visited = set()
        current = cat.categoria_padre
        has_loop = False
        
        while current:
            if current.pk == cat.pk:
                # Loop: la categoria punta a se stessa nella catena
                has_loop = True
                break
            
            if current.pk in visited:
                # Loop rilevato
                has_loop = True
                break
            
            visited.add(current.pk)
            current = current.categoria_padre
        
        if has_loop:
            print(f"⚠️  LOOP RILEVATO: {cat.nome_categoria} (ID {cat.pk}) - padre ID {cat.categoria_padre_id}")
            fixed.append(cat)
    
    if not fixed:
        print("✅ Nessun loop rilevato!")
        return
    
    print(f"\n📋 Trovate {len(fixed)} categorie con loop:\n")
    for cat in fixed:
        print(f"  - {cat.nome_categoria} (ID {cat.pk})")
        print(f"    Padre attuale: {cat.categoria_padre.nome_categoria if cat.categoria_padre else 'Nessuno'} (ID {cat.categoria_padre_id})")
    
    # Analizza la struttura corretta
    print("\n🔧 Correzione dei dati...")
    print("\nStruttura desiderata (da analisi dei nomi):")
    print("  - Pompe Del Vuoto (17) dovrebbe essere una MACROCATEGORIA (livello 0)")
    print("    - Backer (18) sottocategoria di Pompe (livello 1)")
    print("    - Busch (19) sottocategoria di Pompe (livello 1)")
    print("    - ritchle (20) sottocategoria di Pompe (livello 1)")
    print("    - Modello : VTLF250 (21) sottocategoria di Pompe (livello 1)")
    print("\n  - AUTO (15) dovrebbe essere rimossa (loop con Motore)")
    
    risposta = input("\n❓ Vuoi procedere con la correzione automatica? (s/n): ")
    
    if risposta.lower() != 's':
        print("❌ Operazione annullata")
        return
    
    # Correzione automatica
    print("\n🔧 Applicazione correzioni...")
    
    # Fix: Pompe Del Vuoto diventa macrocategoria
    pompe = Categoria.objects.get(pk=17)
    pompe.categoria_padre = None
    pompe.livello = 0
    pompe.save()
    print(f"✅ {pompe.nome_categoria} (17) -> Macrocategoria (livello 0)")
    
    # Fix: Backer, Busch, ritchle, VTLF250 diventano sottocategorie di Pompe
    for cat_id in [18, 19, 20, 21]:
        cat = Categoria.objects.get(pk=cat_id)
        cat.categoria_padre_id = 17
        cat.livello = 1
        cat.save()
        print(f"✅ {cat.nome_categoria} ({cat_id}) -> Sottocategoria di Pompe Del Vuoto (livello 1)")
    
    # Fix: AUTO - rimuovi il padre circolare
    auto = Categoria.objects.get(pk=15)
    auto.categoria_padre = None
    auto.livello = 0
    auto.save()
    print(f"✅ {auto.nome_categoria} (15) -> Macrocategoria (livello 0)")
    
    # Ricalcola i livelli di tutte le sottocategorie di AUTO
    for cat in Categoria.objects.filter(categoria_padre_id=15):
        cat.livello = 1
        cat.save()
        print(f"✅ {cat.nome_categoria} ({cat.pk}) -> Sottocategoria di AUTO (livello 1)")
    
    print("\n✅ Correzione completata!")
    print("\n📊 Riepilogo finale:")
    
    # Mostra struttura corretta
    macrocategorie = Categoria.objects.filter(categoria_padre__isnull=True).order_by('ordine', 'nome_categoria')
    for macro in macrocategorie:
        print(f"\n📁 {macro.nome_categoria} (ID {macro.pk}, livello {macro.livello})")
        for sub in macro.sottocategorie.all().order_by('ordine', 'nome_categoria'):
            print(f"  ├─ {sub.nome_categoria} (ID {sub.pk}, livello {sub.livello})")
            for subsub in sub.sottocategorie.all().order_by('ordine', 'nome_categoria'):
                print(f"  │  └─ {subsub.nome_categoria} (ID {subsub.pk}, livello {subsub.livello})")

if __name__ == '__main__':
    fix_circular_loops()
