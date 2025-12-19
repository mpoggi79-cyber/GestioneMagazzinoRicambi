# Istruzioni AI Copilot per Gestione Magazzino Ricambi

**Progetto**: Sistema di gestione magazzino Django 5.2 ("Gestione Magazzino Ricambi Goose")  
**Status**: v1.0 pronto per produzione | Database: MySQL 10.4 | Modelli: 11 | View: 22 | Template: 22 | Python: 3.10+

---

## 🏗️ Panoramica Architettura

### Struttura a Tre Livelli
- **Backend**: Django 5.2.8 CBV (class-based views) con LoginRequiredMixin + mixin personalizzati
- **Database**: MySQL 10.4 (via PyMySQL, NON mysqlclient) con 11 modelli su 2 app
- **Frontend**: Template Bootstrap 5.3 + crispy-forms + crispy-bootstrap5 + Font Awesome 6.4

### Due App Principali
| App | Scopo | Modelli Chiave |
|-----|-------|-----------|
| **accounts** | Autenticazione e autorizzazione | ProfiloUtente, RuoloUtente (4 ruoli: ADMIN, GESTORE_MAGAZZINO, OPERATORE, VISUALIZZATORE), LogAccesso |
| **magazzino** | Logica di dominio magazzino | Categoria (gerarchica), PezzoRicambio, Fornitore, MovimentoMagazzino, Giacenza, Inventario, DettaglioInventario, ModelloMacchinaSCM, MatricolaMacchinaSCM |

---

## 🔐 Pattern Permessi & Autorizzazione

**Tutte le view CRUD ereditano da mixin personalizzati** (vedi [magazzino/views.py](magazzino/views.py#L36-L61)):

- `CanViewMixin`: Chiunque sia autenticato può visualizzare
- `CanEditMixin`: Controlla `profilo.può_modificare_dati()` (solo ADMIN e GESTORE_MAGAZZINO)
- Le view Edit/Create/Delete rifiutano con messages.error() → redirect al dashboard

**Controlli Ruoli in ProfiloUtente** ([accounts/models.py](accounts/models.py#L84-L95)):
```python
def può_modificare_dati(self):
    return self.ruolo in [RuoloUtente.ADMIN, RuoloUtente.GESTORE_MAGAZZINO]
```

→ Controlla sempre il ruolo dell'utente prima delle operazioni CRUD; non bypassare mai i mixin.

---

## 📊 Pattern Dati Critici

### Categoria (Gerarchica)
- **FK auto-referenziata**: `categoria_padre` + `livello` (campo calcolato per ottimizzazione query)
- **Vincolo chiave**: `PROTECT` in cancellazione per mantenere la gerarchia
- **Ordinamento**: Per livello → ordine → nome_categoria
- Vedi [models.py](magazzino/models.py#L16-L70) per la struttura

### PezzoRicambio ↔ Giacenza (Relazione 1:1)
- Giacenza memorizza i livelli di stock (disponibile, impegnata, prenotata)
- **Logica minimo/massimo applicata nelle regole di business**, non nei vincoli DB
- MovimentoMagazzino aggiorna sia PezzoRicambio che Giacenza

### MovimentoMagazzino (Audit Trail)
- Scelte tipo: CARICO, SCARICO, RETTIFICA, RESO
- Immutabile una volta creato; memorizza operatore, data, note
- Non modificare direttamente; creare nuovi movimenti RETTIFICA per correzioni

---

## ⚙️ Comandi Developer

### Setup & Database
```bash
# Creare database MySQL dallo schema (eseguire per primo!)
mysql -u root < database_creation.sql

# Applicare tutte le migrazioni Django
python manage.py migrate

# Caricare dati di test (8 categorie, 5 fornitori, 19 articoli, 77 movimenti, 4 utenti)
python manage.py populate_db

# Testare connessione DB
python test_db_connection.py
```

### Esecuzione
```bash
# Server di sviluppo (porta 8000)
python manage.py runserver

# Porta personalizzata se 8000 è occupata
python manage.py runserver 8001

# Interfaccia admin: http://localhost:8000/admin (utente: admin/admin)
```

### Test & Validazione
```bash
# Eseguire test Django
python manage.py test

# Verificare sintassi dello script di creazione database
python database_creation.sql  # via tab SQL di phpMyAdmin

# Verificare interfaccia admin per struttura modelli
python manage.py shell  # poi: from magazzino.models import *
```

---

## 📝 Workflow Comuni

### Aggiungere una Nuova View CRUD
1. Definire il modello in [magazzino/models.py](magazzino/models.py)
2. Creare il form in [magazzino/forms.py](magazzino/forms.py) (usare `crispy_forms` con Bootstrap5)
3. Creare CBV in [magazzino/views.py](magazzino/views.py):
   - List: `CategoriaListView(CanViewMixin, SortableListMixin, ListView)`
   - Create: `CategoriaCreateView(CanEditMixin, CreateView)` + success_url
   - Update: `CategoriaUpdateView(CanEditMixin, UpdateView)` + verificare proprietà
   - Delete: `CategoriaDeleteView(CanEditMixin, DeleteView)` con gestione ProtectedError
4. Aggiungere URL patterns in [magazzino/urls.py](magazzino/urls.py) (app_name='magazzino')
5. Creare template in [templates/magazzino/](templates/magazzino/) (ereditare da base.html)

### Registrare Movimento di Stock
1. Creare MovimentoMagazzino (tipo: CARICO/SCARICO/RETTIFICA/RESO)
2. Aggiorna automaticamente Giacenza via signals (vedi [magazzino/signals.py](magazzino/signals.py))
3. Design immutabile: nessun aggiornamento ai movimenti; usare RETTIFICA per correzioni

### Gestire Categorie Gerarchiche
- Query figli: `categoria.sottocategorie.all()`
- Verificare profondità gerarchia tramite campo `livello` prima delle operazioni
- Usare `categoria_padre` con PROTECT per prevenire rotture di catene

---

## 🔧 Convenzioni Specifiche Progetto

### Naming Modelli
- **Nomi italiani**: i nomi dei campi sono in italiano (es. `giacenza_minima`, `codice_scm`, `operatore`)
- **Colonne PK**: Sempre `id_<model_minuscolo>` (es. `id_categoria`, `id_pezzo`)
- **Riferimenti FK**: Usare `db_column` per matching naming legacy (es. `id_categoria_padre`)
- **Campi timestamp**: `creato_il` (auto_now_add), `modificato_il` (auto_now) - naming standard

### Naming View
- `<Model>ListView` per pagine lista/ricerca
- `<Model>CreateView` per form di creazione
- `<Model>DetailView` per visualizzazione singolo oggetto (dettaglio read-only + link modifica)
- `<Model>UpdateView` per form di modifica
- `<Model>DeleteView` con template di conferma
- **Dashboard views**: Usare `TemplateView` con logica aggregata (es. `DashboardView`)

### Validazione Form
- Usare metodi `clean_<fieldname>()` per validazione specifica campo
- Usare `clean()` per validazione cross-field (es. min ≤ max)
- Widget personalizzati: `MatricolaSelectWidget` aggiunge data attributes per interop JS
- Crispy-forms: sempre usare `{% load crispy_forms_tags %}` + `{{ form|crispy }}`

### Signals & Automazione
- **MovimentoMagazzino**: Signal `post_save` aggiorna automaticamente Giacenza (vedi [magazzino/signals.py](magazzino/signals.py))
- **PezzoRicambio immagini**: Signal `pre_save` processa automaticamente:
  - Immagine principale: ridimensionata a max 800x800px (qualità 90%, JPEG)
  - Thumbnail: generato automaticamente 300x300px crop centrato (qualità 85%)
  - Conversione RGBA/PNG → RGB/JPEG con sfondo bianco
- **CRITICO**: Non aggiornare mai manualmente Giacenza; creare sempre MovimentoMagazzino
- Campi `auto_now_add`: creato_il (timestamp creazione) - NON modificare manualmente
- Campi `auto_now`: modificato_il, ultimo_accesso (timestamp aggiornamento automatico)

### Struttura Template
- Tutti ereditano da [base.html](templates/base.html)
- Navbar, sidebar (albero categorie), footer auto-generati
- Usare crispy forms: `{% load crispy_forms_tags %}`
- Font Awesome 6.4 per icone (es. `<i class="fas fa-plus"></i>`)

### Middleware & Sicurezza
- `NoCacheMiddleware` disabilita caching per utenti autenticati (prevenire perdite info su PC condivisi)
- Protezione CSRF abilitata; tutti i form usano {% csrf_token %}
- Hashing Argon2 per password (argon2-cffi)

---

## 📦 Dipendenze Chiave & Integrazione

| Dipendenza | Versione | Utilizzo |
|------------|----------|---------|
| Django | 5.2.8 | Framework core |
| PyMySQL | 1.1.2 | Driver MySQL (non mysqlclient) |
| crispy-forms + crispy-bootstrap5 | 2.5 + 2025.6 | Rendering form |
| argon2-cffi | 25.1.0 | Hashing password |

**Nessuna REST API di terze parti**; tutti i dati locali. Punti di integrazione esterna: dati SCM (ModelloMacchinaSCM, MatricolaMacchinaSCM) importati via management command.

---

## ⚠️ Gotcha Critici

1. **PyMySQL, non mysqlclient**: Config DB usa PyMySQL; query potrebbero differire leggermente
2. **Auto-timestamp**: `auto_now_add=True` crea, `auto_now=True` aggiorna — non impostare manualmente
3. **Vincoli Categoria**: PROTECT in FK previene cancellazione accidentale; gestire ProtectedError in view
4. **Accesso basato ruolo**: Sempre verificare via mixin, non fidarsi mai di controlli client-side
5. **Movimenti immutabili**: Design previene modifica dati storici; forzare in view + form
6. **Query gerarchiche**: Sempre filtrare per `livello` quando implementare logica genitore/figlio
7. **File media**: Memorizzati in [media/articoli/](media/articoli/); configurare MEDIA_URL in settings per serving

---

## 📚 Struttura Documentazione

| File | Scopo |
|------|-------|
| [README.md](README.md) | Riferimento tecnico completo (684 righe) |
| [START_HERE.md](START_HERE.md) | Setup guidato in 5 minuti |
| [QUICK_START.md](QUICK_START.md) | Deploy rapido 3 step |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Architettura + schemi modelli |
| [MANUALE_AMMINISTRATORE.md](MANUALE_AMMINISTRATORE.md) | Procedure amministratore |
| [GESTIONE_UTENTI.md](GESTIONE_UTENTI.md) | Guida gestione utenti e ruoli |

**→ Consultare sempre prima di implementare feature; risparmi 2-3 ore di raccolta contesto.**

---

## 🧪 Riferimento Dati di Test

Dopo `python manage.py populate_db`:
- **8 categorie** (gerarchiche: Meccanica → Motore/Cambio, Elettrica → etc.)
- **7 unità di misura** (pz, m, kg, L, etc.)
- **5 fornitori** (con email, telefono, indirizzo)
- **19 articoli** (con livelli stock minimo/massimo)
- **77 movimenti** (CARICO/SCARICO/RETTIFICA, ultimi 30 giorni)
- **4 utenti di test**: admin/admin, gestore/gestore, operatore/operatore, visualizzatore/visualizzatore

→ Usare per sviluppo; reset con `mysql -u root < database_creation.sql` + `python manage.py migrate` + `python manage.py populate_db`
