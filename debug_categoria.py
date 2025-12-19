"""
Debug: verifica struttura categorie Pompe/Backer
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import Categoria

# Trova le categorie
pompe = Categoria.objects.get(nome_categoria='Pompe Del Vuoto')
backer = Categoria.objects.get(nome_categoria='Backer')

print("📊 STRUTTURA ATTUALE:")
print(f"\n📁 {pompe.nome_categoria}")
print(f"   - ID: {pompe.pk}")
print(f"   - Livello: {pompe.livello}")
print(f"   - Padre: {pompe.categoria_padre}")

print(f"\n  ├─ {backer.nome_categoria}")
print(f"     - ID: {backer.pk}")
print(f"     - Livello: {backer.livello}")
print(f"     - Padre: {backer.categoria_padre} (ID: {backer.categoria_padre_id})")

print("\n✅ VERIFICA:")
if backer.livello == 1 and backer.categoria_padre_id == pompe.pk:
    print(f"   La struttura è CORRETTA")
    print(f"   Backer (livello {backer.livello}) può avere figli di livello {backer.livello + 1}")
    print(f"   ✅ Puoi creare VDLF250 sotto Backer")
else:
    print(f"   ⚠️ Problema rilevato!")
    print(f"   Backer dovrebbe essere livello 1, è livello {backer.livello}")

print("\n🔧 URL PER TEST:")
print(f"   Crea sotto Backer: http://127.0.0.1:8000/magazzino/categorie/aggiungi/?padre={backer.pk}")

print("\n📋 COSA DOVREBBE SUCCEDERE:")
print("   1. URL passa ?padre=18 (ID di Backer)")
print("   2. Vista get_initial() imposta:")
print(f"      - categoria_padre = Backer (ID {backer.pk})")
print(f"      - macrocategoria = Pompe Del Vuoto (ID {pompe.pk})")
print(f"      - categoria_livello2 = Backer (ID {backer.pk})")
print("   3. Form clean() valida:")
print(f"      - categoria_padre.livello = {backer.livello}")
print(f"      - {backer.livello} >= 2? {backer.livello >= 2}")
print(f"      - Validazione: {'❌ BLOCCATA' if backer.livello >= 2 else '✅ OK'}")
