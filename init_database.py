#!/usr/bin/env python
"""
Script per inizializzare il database con dati di esempio.

Eseguire con: python manage.py shell < init_database.py
oppure: python init_database.py
"""

import os
import django

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import (
    Categoria, UnitaMisura, Fornitore, PezzoRicambio, 
    Giacenza, MovimentoMagazzino
)
from django.contrib.auth.models import User
from accounts.models import ProfiloUtente, RuoloUtente
from datetime import datetime, timedelta

print("\n" + "="*70)
print("🔧 INIZIALIZZAZIONE DATABASE - Gestione Magazzino Ricambi")
print("="*70 + "\n")

# ============================================================================
# 1. CREA CATEGORIE
# ============================================================================
print("📂 Creando categorie...")

categorie_data = [
    ('Meccanica', 'Componenti meccanici generici'),
    ('Elettrica', 'Componenti elettrici e elettronici'),
    ('Pneumatica', 'Componenti pneumatici'),
    ('Accessori consumo', 'Accessori di consumo'),
    ('Idraulica', 'Componenti idraulici'),
    ('Cuscinetti', 'Cuscinetti e rotismi'),
    ('Viti e Bulloneria', 'Viti, bulloni e fasteners'),
]

categorie = {}
for nome, desc in categorie_data:
    cat, created = Categoria.objects.get_or_create(
        nome_categoria=nome,
        defaults={'descrizione': desc, 'stato_attivo': True}
    )
    categorie[nome] = cat
    status = "✨ Creata" if created else "👍 Esiste già"
    print(f"  {status}: {nome}")

# ============================================================================
# 2. CREA UNITÀ DI MISURA
# ============================================================================
print("\n📏 Creando unità di misura...")

unita_data = [
    ('pz', 'Pezzo'),
    ('cf', 'Confezione'),
    ('mt', 'Metro'),
    ('kg', 'Chilogrammo'),
    ('lt', 'Litro'),
    ('sc', 'Scatola'),
]

unita_map = {}
for codice, desc in unita_data:
    unita, created = UnitaMisura.objects.get_or_create(
        codice=codice,
        defaults={'descrizione': desc, 'stato_attivo': True}
    )
    unita_map[codice] = unita
    status = "✨ Creata" if created else "👍 Esiste già"
    print(f"  {status}: {codice} ({desc})")

# ============================================================================
# 3. CREA FORNITORI
# ============================================================================
print("\n🏭 Creando fornitori...")

fornitori_data = [
    {
        'ragione_sociale': 'SCM Italia S.p.A.',
        'indirizzo': 'Via Industria 10',
        'citta': 'Brescia',
        'cap': '25128',
        'provincia': 'BS',
        'telefono': '030123456',
        'email': 'info@scmitalia.it',
        'partita_iva': '01234567890',
        'tempo_medio_consegna_giorni': 5,
    },
    {
        'ragione_sociale': 'Ricambi Legno S.r.l.',
        'indirizzo': 'Via Meccanica 5',
        'citta': 'Udine',
        'cap': '33100',
        'provincia': 'UD',
        'telefono': '0432987654',
        'email': 'vendite@ricambilegno.it',
        'partita_iva': '98765432100',
        'tempo_medio_consegna_giorni': 7,
    },
    {
        'ragione_sociale': 'Forniture Industriali Novara',
        'indirizzo': 'Viale Industria 15',
        'citta': 'Novara',
        'cap': '28100',
        'provincia': 'NO',
        'telefono': '0321555666',
        'email': 'ordini@fornovelevara.it',
        'partita_iva': '11111222223',
        'tempo_medio_consegna_giorni': 3,
    },
]

fornitori = {}
for dati in fornitori_data:
    forn, created = Fornitore.objects.get_or_create(
        partita_iva=dati['partita_iva'],
        defaults=dati
    )
    fornitori[dati['ragione_sociale']] = forn
    status = "✨ Creato" if created else "👍 Esiste già"
    print(f"  {status}: {dati['ragione_sociale']}")

# ============================================================================
# 4. CREA ARTICOLI DI RICAMBIO
# ============================================================================
print("\n🔧 Creando articoli di ricambio...")

articoli_data = [
    {
        'codice_interno': 'RIC-001',
        'codice_scm': 'SCM-BR-001',
        'codice_fornitore': 'FOR-BR-001',
        'descrizione': 'Braccio pantografo principale',
        'categoria': categorie['Meccanica'],
        'unita_misura': unita_map['pz'],
        'giacenza_minima': 2,
        'giacenza_massima': 10,
        'prezzo_acquisto': 150.50,
    },
    {
        'codice_interno': 'RIC-002',
        'codice_scm': 'SCM-MO-002',
        'codice_fornitore': 'FOR-MO-002',
        'descrizione': 'Motore principale 3 HP',
        'categoria': categorie['Elettrica'],
        'unita_misura': unita_map['pz'],
        'giacenza_minima': 1,
        'giacenza_massima': 5,
        'prezzo_acquisto': 450.00,
    },
    {
        'codice_interno': 'RIC-003',
        'codice_scm': 'SCM-CS-003',
        'codice_fornitore': 'FOR-CS-003',
        'descrizione': 'Cuscinetto a sfera 6204',
        'categoria': categorie['Cuscinetti'],
        'unita_misura': unita_map['pz'],
        'giacenza_minima': 5,
        'giacenza_massima': 50,
        'prezzo_acquisto': 12.30,
    },
    {
        'codice_interno': 'RIC-004',
        'codice_scm': 'SCM-VT-004',
        'codice_fornitore': 'FOR-VT-004',
        'descrizione': 'Vite M10x100 acciaio zinco',
        'categoria': categorie['Viti e Bulloneria'],
        'unita_misura': unita_map['cf'],
        'giacenza_minima': 10,
        'giacenza_massima': 200,
        'prezzo_acquisto': 8.50,
    },
    {
        'codice_interno': 'RIC-005',
        'codice_scm': 'SCM-GL-005',
        'codice_fornitore': 'FOR-GL-005',
        'descrizione': 'Guida lineare profilo in alluminio',
        'categoria': categorie['Meccanica'],
        'unita_misura': unita_map['mt'],
        'giacenza_minima': 5,
        'giacenza_massima': 30,
        'prezzo_acquisto': 25.00,
    },
]

articoli = {}
for dati in articoli_data:
    art, created = PezzoRicambio.objects.get_or_create(
        codice_interno=dati['codice_interno'],
        defaults=dati
    )
    articoli[dati['codice_interno']] = art
    status = "✨ Creato" if created else "👍 Esiste già"
    print(f"  {status}: {dati['codice_interno']} - {dati['descrizione']}")

# ============================================================================
# 5. CREA GIACENZE
# ============================================================================
print("\n📊 Creando giacenze iniziali...")

quantita_iniziali = {
    'RIC-001': 8,
    'RIC-002': 3,
    'RIC-003': 25,
    'RIC-004': 150,
    'RIC-005': 15,
}

for codice, quantita in quantita_iniziali.items():
    art = articoli[codice]
    giacs, created = Giacenza.objects.get_or_create(
        articolo=art,
        defaults={
            'quantita_disponibile': quantita,
            'quantita_impegnata': 0,
            'quantita_prenotata': 0,
        }
    )
    status = "✨ Creata" if created else "👍 Esiste già"
    print(f"  {status}: {codice} - Quantità: {quantita}")

# ============================================================================
# 6. CREA UTENTI DI TEST
# ============================================================================
print("\n👥 Creando utenti di test...")

utenti_data = [
    {
        'username': 'admin',
        'email': 'admin@magazzinoricambi.it',
        'first_name': 'Amministratore',
        'last_name': 'Sistema',
        'password': 'Admin@12345',
        'ruolo': RuoloUtente.ADMIN,
        'is_superuser': True,
        'is_staff': True,
    },
    {
        'username': 'gestore_magazzino',
        'email': 'gestore@magazzinoricambi.it',
        'first_name': 'Marco',
        'last_name': 'Rossi',
        'password': 'Gestore@12345',
        'ruolo': RuoloUtente.GESTORE_MAGAZZINO,
        'is_superuser': False,
        'is_staff': True,
    },
    {
        'username': 'operatore1',
        'email': 'operatore1@magazzinoricambi.it',
        'first_name': 'Luca',
        'last_name': 'Bianchi',
        'password': 'Operatore@12345',
        'ruolo': RuoloUtente.OPERATORE,
        'is_superuser': False,
        'is_staff': False,
    },
    {
        'username': 'operatore2',
        'email': 'operatore2@magazzinoricambi.it',
        'first_name': 'Giovanni',
        'last_name': 'Verdi',
        'password': 'Operatore@12345',
        'ruolo': RuoloUtente.OPERATORE,
        'is_superuser': False,
        'is_staff': False,
    },
    {
        'username': 'visualizzatore',
        'email': 'visualizzatore@magazzinoricambi.it',
        'first_name': 'Elena',
        'last_name': 'Neri',
        'password': 'Visualizzatore@12345',
        'ruolo': RuoloUtente.VISUALIZZATORE,
        'is_superuser': False,
        'is_staff': False,
    },
]

for dati_utente in utenti_data:
    password = dati_utente.pop('password')
    ruolo = dati_utente.pop('ruolo')
    
    user, created = User.objects.get_or_create(
        username=dati_utente['username'],
        defaults=dati_utente
    )
    
    if created:
        user.set_password(password)
        user.save()
        user.profilo.ruolo = ruolo
        user.profilo.save()
        print(f"  ✨ Creato: {user.get_full_name()} ({ruolo})")
    else:
        print(f"  👍 Esiste già: {user.get_full_name()}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("✅ INIZIALIZZAZIONE COMPLETATA CON SUCCESSO!")
print("="*70)

print("\n📊 Statistiche:")
print(f"  • Categorie: {Categoria.objects.count()}")
print(f"  • Unità di misura: {UnitaMisura.objects.count()}")
print(f"  • Fornitori: {Fornitore.objects.count()}")
print(f"  • Articoli: {PezzoRicambio.objects.count()}")
print(f"  • Giacenze: {Giacenza.objects.count()}")
print(f"  • Utenti: {User.objects.count()}")

print("\n🔐 Credenziali di accesso per il test:")
print("  Username: admin")
print("  Password: Admin@12345")
print("  URL Admin: http://localhost:8000/admin/")

print("\n💡 Prossimi step:")
print("  1. Esegui: python manage.py runserver")
print("  2. Accedi a: http://localhost:8000/admin/")
print("  3. Usa le credenziali sopra")

print("\n" + "="*70 + "\n")
