import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from magazzino.views import GestioneTabelleView, ModificaTabellaView
from django.test import RequestFactory

print("=== Test TbCategorieTariffe ===")

# Test GestioneTabelleView
view = GestioneTabelleView()
request = RequestFactory().get('/')
view.request = request
context = view.get_context_data()

print("Tabelle modificabili:")
for tabella in context['tabelle_modificabili']:
    if tabella['nome'] == 'tbcategorietariffe':
        print(f"✅ {tabella['nome']}: {tabella['descrizione']}")
        break
else:
    print("❌ tbcategorietariffe non trovato")

# Test ModificaTabellaView
view2 = ModificaTabellaView()
request2 = RequestFactory().get('/')
view2.request = request2
context2 = view2.get_context_data(nome_tabella='tbcategorietariffe')

print(f"Configurazione: {context2.get('nome_tabella')}")
print(f"Descrizione: {context2.get('descrizione_tabella')}")
print(f"Campi: {context2.get('campi')}")
print(f"Campo stato: {context2.get('has_status_filter')}")

print("Test completato!")