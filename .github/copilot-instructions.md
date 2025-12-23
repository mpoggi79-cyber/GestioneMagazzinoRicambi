# Istruzioni AI Copilot per Gestione Magazzino Ricambi

**Progetto**: Sistema di gestione magazzino Django 5.2 ("Gestione Magazzino Ricambi Goose")  
**Status**: v1.1 CLIENTI MODULE + BACKUP SYSTEM | Database: MySQL 10.4 | Modelli: 16 | View: 47 | Template: 40 | Python: 3.10+

---

## 🏗️ Panoramica Architettura

### Struttura a Tre Livelli
- **Backend**: Django 5.2.8 CBV (class-based views) con LoginRequiredMixin + mixin personalizzati
- **Database**: MySQL 10.4 (via PyMySQL, NON mysqlclient) con 16 modelli su 2 app
- **Frontend**: Template Bootstrap 5.3 + crispy-forms + crispy-bootstrap5 + Font Awesome 6.4

### Due App Principali
| App | Scopo | Modelli Chiave |
|-----|-------|-----------|
| **accounts** | Autenticazione e autorizzazione | ProfiloUtente, RuoloUtente (4 ruoli: ADMIN, GESTORE_MAGAZZINO, OPERATORE, VISUALIZZATORE), LogAccesso |
| **magazzino** | Logica di dominio magazzino + clienti | **Magazzino**: Categoria (gerarchica), PezzoRicambio, Fornitore, MovimentoMagazzino, Giacenza, Inventario, DettaglioInventario, ModelloMacchinaSCM, MatricolaMacchinaSCM<br>**Clienti**: tbappellativo, tbcategoriaiva, tbcontatti, tbcategorieTariffe, tbtipopagamento, tbmodalitapagamento |

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
- **Protezione loop**: Il metodo `save()` verifica loop infiniti (max 10 livelli di profondità)
- Vedi [magazzino/models.py](magazzino/models.py#L16-L70) per la struttura

### PezzoRicambio ↔ Giacenza (Relazione 1:1)
- Giacenza memorizza i livelli di stock (disponibile, impegnata, prenotata)
- **Logica minimo/massimo applicata nelle regole di business**, non nei vincoli DB
- MovimentoMagazzino aggiorna sia PezzoRicambio che Giacenza
- **Immagini**: Signal `pre_save` processa automaticamente immagine principale (max 800x800px) + thumbnail (300x300px)

### MovimentoMagazzino (Audit Trail)
- Scelte tipo: CARICO, SCARICO, RETTIFICA, RESO
- Immutabile una volta creato; memorizza operatore, data, note
- Non modificare direttamente; creare nuovi movimenti RETTIFICA per correzioni
- **Invariante critica**: Ogni MovimentoMagazzino DEVE aggiornare Giacenza associata via signal

### ModelloMacchinaSCM & MatricolaMacchinaSCM
- Relazione 1:Many per associare articoli a specifiche macchine SCM
- MatricolaMacchinaSCM usa widget personalizzato `MatricolaSelectWidget` con data-attributes per JS interop
- Importabili via management command per integrazioni esterne

### Tabelle Clienti (Modulo Fatturazione - Fase 1)
- **TbAppellativo**: Titoli onorifici (Sig., Dott., Prof., etc.) - 7 record
- **TbCategoriaIVA**: Aliquote IVA (22%, 10%, 0%, etc.) - 7 record  
- **TbContatti**: Anagrafica clienti/fornitori con campi estesi - relazione con TbAppellativo
- **TbCategorieTariffe**: Classificazione servizi (Assistenza, Produzione, etc.) - 21 record
- **TbTipoPagamento**: Condizioni pagamento (Bonifico 30gg, RI.BA., etc.) - 23 record
- **TbModalitaPagamento**: Metodi pagamento (Contanti, Carta, Assegno, etc.) - 8 record
- **Importazione**: Via management commands dedicati per ogni tabella

---

## 📐 Schemi Modelli & Relazioni

### Modelli Magazzino (magazzino/models.py)
```
Categoria ──┬─→ Categoria (self FK, PROTECT) [Gerarchia]
            └─→ PezzoRicambio
                    ├─ Giacenza (1:1) ←── MovimentoMagazzino
                    ├─ Fornitore (FK)
                    ├─ tbunitamisura (FK)
                    └─ MatricolaMacchinaSCM (Many)

ModelloMacchinaSCM ─→ MatricolaMacchinaSCM (1:Many)
                            ↓
                       PezzoRicambio

Inventario ──→ DettaglioInventario ──→ PezzoRicambio
    (Stato: NON_INIZIATO, IN_CORSO, COMPLETATO)
```

### Modelli Clienti (magazzino/models.py)
```
TbAppellativo (7 record)
├── idAppellativo: AutoField(PK)
└── Descrizione: CharField(max_length=50)

TbCategoriaIVA (7 record)  
├── idCategoriaIVA: AutoField(PK)
├── NomeCategoria: CharField(max_length=100)
└── ValoreIVA: DecimalField(5,3) - es: 0.22 = 22%

TbContatti (Clienti/Fornitori)
├── idContatto: AutoField(PK)
├── idAppellativo: ForeignKey(TbAppellativo)
├── RagioneSociale: CharField(max_length=200)
├── Nome: CharField(max_length=100, null=True)
├── Cognome: CharField(max_length=100, null=True)
├── Indirizzo: TextField(null=True)
├── CAP: CharField(max_length=10, null=True)
├── Città: CharField(max_length=100, null=True)
├── Provincia: CharField(max_length=5, null=True)
├── Telefono: CharField(max_length=20, null=True)
├── Fax: CharField(max_length=20, null=True)
├── Cellulare: CharField(max_length=20, null=True)
├── Email: EmailField(null=True)
├── PIVA: CharField(max_length=20, null=True)
├── CodiceFiscale: CharField(max_length=20, null=True)
└── idCliente: IntegerField(unique=True) - campo legacy

TbCategorieTariffe (21 record)
├── idCategorieTariffe: AutoField(PK)
├── CategoriaTariffe: CharField(max_length=200)
└── IsVisible: BooleanField(default=True)

TbTipoPagamento (23 record)
├── idTipoPagamento: AutoField(PK)
├── descrizione: CharField(max_length=200)
├── DataRifScad: CharField(max_length=50)
├── GiorniDataRif: IntegerField
└── GiornoAddebito: IntegerField

TbModalitaPagamento (8 record)
├── idModalitaPagamento: AutoField(PK)
└── Nome: CharField(max_length=100)
```

**Conteggio modelli**:
- **Magazzino app**: Categoria, PezzoRicambio, Giacenza, Fornitore, tbunitamisura, MovimentoMagazzino, Inventario, DettaglioInventario, ModelloMacchinaSCM, MatricolaMacchinaSCM, Configurazione (11 totali)
- **Clienti app**: TbAppellativo, TbCategoriaIVA, TbContatti, TbCategorieTariffe, TbTipoPagamento, TbModalitaPagamento (6 totali)
- **Accounts app**: User (Django built-in), ProfiloUtente, RuoloUtente, LogAccesso (4 modelli custom)
- **TOTALE**: 16 modelli

---

### Setup & Database
```bash
# Creare database MySQL dallo schema (eseguire per primo!)
mysql -u root < database_creation.sql

# Applicare tutte le migrazioni Django
python manage.py migrate

# Caricare dati di test (8 categorie, 5 fornitori, 19 articoli, 77 movimenti, 4 utenti)
python manage.py populate_db

# Caricare dati clienti (66 record totali)
python manage.py import_tbappellativo
python manage.py import_tbcategoriaiva
python manage.py import_tbcategorietariffe
python manage.py import_tbtipopagamento
python manage.py import_tbmodalitapagamento

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

### Gestire Sistema Backup
- **Backup automatici**: Giornalieri compressi con retention policy (30 giorni)
- **3 metodi ripristino**: 
  - Web UI (`/backup/` - solo ADMIN)
  - Management command (`python manage.py restore_backup`)
  - Script PowerShell emergenza (`.\restore_db_emergency.ps1`)
- **File backup**: `backups/backup_gmr_YYYYMMDD_HHMMSS.sql.gz`
- **Monitoraggio**: BackupManager traccia spazio e pulizia automatica

### Gestire Tabelle Clienti
- **Interfaccia web**: `/gestione-tabelle/` (ADMIN/GESTORE) per selezione tabella
- **Visualizzazione**: `/modifica-tabella/<nome>/` per vedere/modificare record
- **Permessi**: Solo ADMIN e GESTORE_MAGAZZINO possono accedere
- **Importazione**: Management commands dedicati per ogni tabella CSV

---

## 🔧 Convenzioni Specifiche Progetto

### Naming Modelli
- **Nomi italiani**: i nomi dei campi sono in italiano (es. `giacenza_minima`, `codice_scm`, `operatore`)
- **Colonne PK**: Sempre `id_<model_minuscolo>` (es. `id_categoria`, `id_pezzo`)
- **Riferimenti FK**: Usare `db_column` per matching naming legacy (es. `id_categoria_padre`)
- **Campi timestamp**: `creato_il` (auto_now_add), `modificato_il` (auto_now) - naming standard
- **Modelli clienti**: Nomi tabella legacy (es. `TbAppellativo`, `TbCategoriaIVA`) con campi legacy (`idAppellativo`, `idCategoriaIVA`)

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

### 🖼️ Elaborazione Immagini (Signal pre_save)
**File**: [magazzino/signals.py](magazzino/signals.py#L65-L135)

Automatico per ogni PezzoRicambio.immagine upload:
1. **Immagine principale**: Ridimensionata max 800x800px (aspect ratio preservato), JPEG qualità 90%
2. **Thumbnail**: Generato 300x300px (crop centrato), JPEG qualità 85%
3. **Conversione formato**: PNG/RGBA → RGB con sfondo bianco (Pillow Image.new)
4. **Eliminazione**: Signal `post_delete` rimuove file fisici quando articolo cancellato

**Nota**: Non carica mai immagini manualmente nel database; il signal le elabora automaticamente.

### Signals & Automazione Dati
- **MovimentoMagazzino** → **Giacenza**: Signal `post_save` aggiorna stock disponibile/impegnata/prenotata
- **PezzoRicambio**: Signal `pre_save` processa immagini (vedi sezione "Elaborazione Immagini" sopra)
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

## 🐛 Debugging & Troubleshooting

### Errori Comuni Database
```bash
# "Table doesn't exist" dopo git pull
python manage.py migrate
python manage.py populate_db  # Ri-carica dati test

# Errore connessione MySQL "Connection refused"
# → XAMPP: MySQL non avviato. Avviare → MySQL admin
# → O eseguire: mysql -u root < database_creation.sql

# Errore "Foreign key constraint fails" su DELETE
# → Verificare se modello ha FK con PROTECT (categoria_padre, etc)
# Soluzione: Eliminare prima gli oggetti dipendenti o usa ON_DELETE=CASCADE
```

### Debug Django Shell
```bash
# Ispezionare modelli in tempo reale
python manage.py shell
>>> from magazzino.models import *
>>> c = Categoria.objects.first()
>>> c.livello  # Verifica gerarchia
>>> c.sottocategorie.all()  # Query figli
>>> m = MovimentoMagazzino.objects.last()
>>> m.pezzo_ricambio.giacenza.disponibile  # Navigare relazioni
```

### Log & Debugging Signals
- Signal image processing: Controlla logs in [logs/](logs/) per errori elaborazione immagini
- Attiva `DEBUG=True` in [config/settings.py](config/settings.py) per tracciare SQL queries
- Usa `logger.info()` e `logger.error()` nei signal handler per monitoraggio

### Errori di Permessi Comuni
```python
# ❌ Errore: ProtectedError quando elimini categoria con sottocategorie
# Soluzione: Eliminare ricorsivamente oppure usare cleanup script
Categoria.objects.filter(categoria_padre=None).delete()  # Solo root

# ❌ Errore: "Non hai i permessi" ma sei admin
# Soluzione: Verifica ProfiloUtente.ruolo in shell
>>> admin = User.objects.get(username='admin')
>>> admin.profilo.ruolo  # Deve essere 'ADMIN'
>>> admin.profilo.può_modificare_dati()  # Deve tornare True
```

---

## ⚠️ Gotcha Critici - AGGIORNAMENTO v1.1

1. **PyMySQL, non mysqlclient**: Config DB usa PyMySQL; query potrebbero differire leggermente da MySQL nativo
2. **Auto-timestamp**: `auto_now_add=True` crea, `auto_now=True` aggiorna — non impostare manualmente mai
3. **Vincoli Categoria**: PROTECT in FK previene cancellazione accidentale; **sempre** gestire `ProtectedError` in view Delete
4. **Accesso basato ruolo**: **Sempre** verificare via `CanEditMixin`/`CanViewMixin`, non fidarsi mai di controlli client-side
5. **Movimenti immutabili**: Design previene modifica dati storici; riportare errori via form validation + RETTIFICA
6. **Query gerarchiche**: Sempre filtrare per `livello` quando implementare logica genitore/figlio per ottimizzare query
7. **File media**: Memorizzati in `media/articoli/`; configurare MEDIA_URL/MEDIA_ROOT in settings per serving locale
8. **Signal image processing**: Affidati a `pre_save` per processamento; **non** salvare immagini raw direttamente nel DB
9. **Crispy forms obbligatorio**: Tutte le form HTML devono usare `{% load crispy_forms_tags %}` + `{{ form|crispy }}`
10. **Protezione CSRF**: Ogni form POST deve avere `{% csrf_token %}`; Django lo verifica automatico ma è obbligatorio nei template
11. **Modelli clienti legacy**: Nomi tabella `Tb*` e campi `id*` (senza underscore) per compatibilità legacy
12. **Sistema backup**: **Mai** modificare direttamente file backup; usare sempre BackupManager
13. **Tabelle clienti**: Importare sempre via management commands dedicati, non inserimenti diretti

---

## � Checklista AI Agent: Decisioni Comuni

| Domanda | Risposta | Riferimento |
|---------|----------|-------------|
| Devo permettere edit a questo campo? | Controlla `CanEditMixin` in view CRUD e `può_modificare_dati()` in form | [magazzino/views.py#L50-L61](magazzino/views.py#L50-L61) |
| Come aggiunge stock correttamente? | **Sempre** crea `MovimentoMagazzino`; **mai** modificare `Giacenza` direttamente | [magazzino/models.py#L669-L750](magazzino/models.py#L669-L750) |
| Dove vanno le immagini? | `media/articoli/` auto-gestito da signals; non toccare manualmente | [magazzino/signals.py](magazzino/signals.py) |
| Categoria padre può avere loop? | **NO** - `save()` verifica max 10 livelli di profondità | [magazzino/models.py#L83-L95](magazzino/models.py#L83-L95) |
| Quale DB driver usiamo? | **PyMySQL** (non mysqlclient) - può differire da MySQL standar | [requirements.txt](requirements.txt) |
| Come gestisco validazione cross-field? | Usa `clean()` nel form, non nel modello | [magazzino/forms.py](magazzino/forms.py) |
| Aggiungo una nuova app? | **NO** - tutto in `accounts` + `magazzino`. Creare modello + view + form in queste | [config/settings.py#L37-L45](config/settings.py#L37-L45) |
| Come testo in locale? | `populate_db` carica dati test; accedi con admin/admin | [README.md](README.md#L10-L25) |
| Come gestisco backup database? | **3 metodi**: Web UI (/backup/), management command, script PowerShell emergenza | [BACKUP_RECOVERY_GUIDE.md](BACKUP_RECOVERY_GUIDE.md) |
| Come accedo tabelle clienti? | **Interfaccia web**: /gestione-tabelle/ (solo ADMIN/GESTORE) | [magazzino/views.py](magazzino/views.py#L2009-L2100) |
| File sensibili a non committare? | `settings.py` (SECRET_KEY), `.env` (se usato), `media/articoli/` | [.gitignore](../.gitignore) |

---

## �📚 Struttura Documentazione

| File | Scopo |
|------|-------|
| [README.md](README.md) | Riferimento tecnico completo (684 righe) |
| [START_HERE.md](START_HERE.md) | Setup guidato in 5 minuti |
| [QUICK_START.md](QUICK_START.md) | Deploy rapido 3 step |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Architettura + schemi modelli |
| [MANUALE_AMMINISTRATORE.md](MANUALE_AMMINISTRATORE.md) | Procedure amministratore |
| [GESTIONE_UTENTI.md](GESTIONE_UTENTI.md) | Guida gestione utenti e ruoli |
| [BACKUP_RECOVERY_GUIDE.md](BACKUP_RECOVERY_GUIDE.md) | **Guida backup & recovery 3 metodi** |

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

Dopo import tabelle clienti:
- **7 appellativi** (Sig., Dott., Prof., etc.)
- **7 categorie IVA** con aliquote (22%, 0%, etc.)
- **21 categorie tariffe** (Assistenza, Produzione, etc.)
- **23 tipi pagamento** (Bonifico 30gg, 60gg, RI.BA., etc.)
- **8 modalità pagamento** (Contanti, Assegno, Carta, etc.)
- **TOTALE**: 66 record clienti + dati magazzino completi

→ Usare per sviluppo; reset con `mysql -u root < database_creation.sql` + `python manage.py migrate` + `python manage.py populate_db`
