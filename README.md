# 🏭 Gestione Magazzino Ricambi Goose By Matteo

**Status**: ✅ v1.1.2 UNIFORMAZIONE UX COMPLETATA | Django 5.2.8 | MySQL 10.4 | Bootstrap 5.3  
**Completamento**: 47 view totali | 16 modelli | 40+ template | 4 ruoli | **10 tabelle gestibili** | **Sistema Backup** | **Audit Logging** | **20 Test** | **Uniformazione Dettagli Articolo**

---

## 📑 Indice Contenuti

1. [Avvio Rapido](#-avvio-rapido-3-comandi)
2. [Stato Applicazione](#-stato-applicazione)
3. [Ultime Modifiche v1.1.2](#-ultime-modifiche-v112---uniformazione-ux-dettaglio-articolo)
4. [Setup Passo-Passo](#-setup-passo-passo)
5. [Decisioni Architetturali](#-decisioni-architetturali-critiche)
6. [Modelli Dati](#-modelli-dati-16-totali)
7. [View & URL](#-view--url-22-class-based-view)
8. [Permessi](#-permessi-basati-su-ruolo)
9. [Uniformazione UX Articoli](#-uniformazione-ux-articoli)
10. [Gestione Tabelle](#%EF%B8%8F-sistema-gestione-tabelle-clienti)
11. [Audit Logging](#-audit-logging-per-modifiche-tabelle)
12. [Sicurezza](#-implementazione-sicurezza)
13. [Dati Test](#-dati-di-test-populate_dbpy)
14. [Comandi Utili](#%EF%B8%8F-comandi-utili)
15. [Troubleshooting](#-troubleshooting)
16. [Struttura Progetto](#-struttura-progetto)
17. [Backup & Recovery](#-backup--recovery)
18. [Come Contribuire](#-come-contribuire)
19. [Licenza](#-licenza)

---

## 🚀 AVVIO RAPIDO (3 COMANDI)

```bash
# 1. Creare database MySQL (XAMPP → MySQL START)
mysql -u root < database_creation.sql

# 2. Setup Django
python manage.py migrate
python manage.py populate_db

# 3. Eseguire server
python manage.py runserver
# Accedere: http://localhost:8000 → admin / admin
```

**Per primo avvio più dettagliato**, vedi sezione "Setup Passo-Passo" sotto.

---

## ✅ STATO APPLICAZIONE

| Componente | Stato | Dettagli |
|-----------|-------|---------|
| **Backend Django 5.2.8** | ✅ Completo | 47 CBV totali (22 magazzino + 25 altre), 16 modelli ORM, 5 form |
| **Database MySQL 10.4** | ✅ Operativo | 77 movimenti, 19 articoli, **+74 record clienti (6 tabelle)** |
| **Frontend Bootstrap 5.3** | ✅ Completo | 40+ template HTML responsive, Font Awesome 6.4 |
| **Modulo Clienti - Fase 1** | ✅ **COMPLETATA** | **6 tabelle gestibili + modifica record reale** |
| **Sistema Gestione Tabelle** | ✅ **IMPLEMENTATO** | **Interfaccia web per visualizzare + modificare tabelle clienti (ADMIN/GESTORE)** |
| **Modifica Record Tabelle** | ✅ **PIANO 1** | **View generica ModificaRecordTabellaView con whitelist + validazione permessi** |
| **Audit Logging Tabelle** | ✅ **PIANO 1** | **Logger strutturato con marker [AUDIT_TABELLE] e diff campi + file logs/django.log** |
| **Uniformazione Dettagli Articolo** | ✅ **v1.1.2** | **Riordinamento gruppi + breadcrumb gerarchia categoria** |
| **Sistema Backup Database** | ✅ **COMPLETATO** | **3 metodi ripristino: Web, Management Command, PowerShell emergenza** |
| **Autenticazione** | ✅ Funzionante | Login/logout, 4 ruoli, ProfiloUtente, LogAccesso |
| **Permessi** | ✅ Implementati | CanEditMixin, CanViewMixin, controlli basati su ruolo |
| **CRUD Operazioni** | ✅ Testate | Categoria, PezzoRicambio, Fornitore, MovimentoMagazzino, Giacenza, Inventario |
| **Report & Statistiche** | ✅ Funzionanti | Dashboard, report_giacenze, report_movimenti |
| **Suite Test** | ✅ **20 VERDI** | **Inclusi 3 test gestione tabelle (modifica, permessi, visibilità)** |
| **Sicurezza** | ✅ Implementata | Protezione CSRF, hashing Argon2, session security, CSS compatibile |
| **Deploy** | ✅ Pronto | Pronto per produzione con Gunicorn + Nginx |

---

## 📌 ULTIME MODIFICHE v1.1.2 - UNIFORMAZIONE UX DETTAGLIO ARTICOLO

### 🎯 Sintesi
Uniformazione della pagina dettaglio articolo `/articoli/<id>/` con la struttura organizzativa della pagina modifica articolo, garantendo coerenza informativa e UX consistente.

### 🔄 Modifiche Applicate

#### 1. **Riordinamento Gruppi Sezioni**
**Prima (v1.1.1)**: Informazioni Articolo → Codici SCM → Fornitore → Giacenza → Movimenti  
**Adesso (v1.1.2)**: **Dati SCM → Dati Fornitore → Dati Articolo** → Giacenza → Movimenti

**Motivazione**: Allineamento con ordine logico della pagina modifica articolo per ridurre cognitive load dell'utente.

#### 2. **Uniformazione Titoli Sezioni**
- `Codici e Dati SCM` → `Dati SCM` (coerente con form)
- `Fornitore Principale` → `Dati Fornitore` (naming coerente)
- Aggiunta etichetta `Dati Articolo` per raggruppare anagrafica e soglie

#### 3. **Riordino Campi nei Gruppi**
- **Dati SCM**: Aggiunto `Prezzo Acquisto SCM` (era assente nel dettaglio) ✓
- **Dati Fornitore**: Spostati `Codice Fornitore` e `Prezzo Acquisto Fornitore` (coerenza con form) ✓
- **Dati Articolo**: Mantiene anagrafica, unità, giacenze, stati e metadati temporali

#### 4. **Aggiunta Breadcrumb Categoria**
Nel gruppo Dati Articolo, sotto il campo Categoria, visualizzazione gerarchia:
```django
{{ articolo.categoria.get_breadcrumb }}  {# Es: Meccanica > Motore > Filtri #}
```
**Vantaggio**: Facilita comprensione della classificazione gerarchica senza navigare in menu.

### 📊 Impatto UX
- ✅ **Coerenza**: Ordine sezioni identico tra dettaglio e modifica
- ✅ **Completezza**: Tutti i campi del form visibili nel dettaglio
- ✅ **Navigabilità**: Breadcrumb categoria migliora orientamento nella gerarchia
- ✅ **Naming**: Titoli uniformi riducono confusione cognitiva

### 🧪 Test & Verifica
- ✅ Template sintattico corretto (nessun errore Django)
- ✅ Breadcrumb utilizza metodo modello `get_breadcrumb()` (nessuna duplicazione logica)
- ⏳ **DA VERIFICARE**: Test visuale su http://127.0.0.1:8000/articoli/30/ (browser)

**Riferimento**: [File modificato](templates/magazzino/pezzoricambio_detail.html)

---

## 🏗️ DECISIONI ARCHITETTURALI CRITICHE

### 1️⃣ **PyMySQL, Non mysqlclient**
- **Scelta**: Driver pure Python (nessuna dipendenza C)
- **Motivo**: Compatibilità XAMPP cross-platform Windows/Linux
- **Implicazione**: Alcune query edge-case potrebbero differire da MySQL nativo
- **Riferimento**: [AGENTS.md - Architettura](AGENTS.md#-perché-pymysql-e-non-mysqlclient)

### 2️⃣ **Signal-Based per Giacenza Updates**
- **Scelta**: MovimentoMagazzino append-only (audit trail); Giacenza aggiornata via signal
- **Motivo**: Traccia storica immutabile + automazione consistente
- **Invariante Critica**: `Giacenza.disponibile = stock_totale - SCARICO + CARICO`
- **Implicazione**: **NUNCA** modificare Giacenza direttamente; sempre via MovimentoMagazzino
- **Riferimento**: [AGENTS.md - Signal-Based](AGENTS.md#-perché-signalbased-per-giacenza-updates)

### 3️⃣ **Class-Based View con Mixin**
- **Scelta**: Utilizzo CBV + custom mixin (CanViewMixin, CanEditMixin)
- **Motivo**: Riusabilità autorizzazione, riduzione errori sicurezza
- **Implicazione**: Sempre ereditare dai mixin giusti; non implementare auth in view
- **Riferimento**: [AGENTS.md - Perché CBV](AGENTS.md#-perché-cbv-con-mixin-e-non-fbv)

### 4️⃣ **Categorie Gerarchiche con Self-FK + PROTECT**
- **Scelta**: Categoria.categoria_padre con PROTECT su DELETE
- **Motivo**: Prevenire accidentale orphaning + logica anti-loop (max 10 livelli)
- **Implicazione**: Cancellazioni falliscono se categoria ha sottocategorie → gestire ProtectedError
- **Riferimento**: [AGENTS.md - Gerarchia Categorie](AGENTS.md#-gerarchia-categorie-self-referencing-fk-con-protect)

---

## 🧲 AUTOMAZIONE DATI - COME FUNZIONANO I SIGNAL

### Pattern Movimento di Stock (Critico)
```
1. Crea MovimentoMagazzino (tipo: CARICO/SCARICO/RETTIFICA/RESO)
2. Model.save() → memorizza movimento (IMMUTABILE) + timestamp + operatore
3. Signal @receiver(post_save) → aggiorna Giacenza.disponibile AUTOMATICAMENTE
4. View restituisce success_message con saldo nuovo
```
**⚠️ Regola**: **NUNCA** creare/aggiornare Giacenza direttamente. Sempre via MovimentoMagazzino.

### Pattern Caricamento Immagini (Automatico)
```
1. User carica PNG/JPEG in PezzoRicambio.immagine (form field)
2. Signal @receiver(pre_save) elabora automaticamente:
   - Immagine principale → ridimensiona 800x800px (JPEG 90%)
   - Thumbnail → genera 300x300px (JPEG 85%)
   - PNG/RGBA → converte RGB con sfondo bianco
3. File salvati in media/articoli/YYYY/MM/DD/
4. Signal @receiver(post_delete) pulisce file quando articolo eliminato
```
**⚠️ Regola**: Non caricare mai immagini raw nel DB. Il signal gestisce tutto.

### Pattern Autorizzazione (Permission Gates)
```
1. Request entra in View CBV che eredita CanViewMixin/CanEditMixin
2. Mixin.test_func() verifica LoginRequiredMixin + profilo.può_modificare_dati()
3. Se non autorizzato → messages.error() + redirect dashboard
4. Se autorizzato → proceed a get_context_data() / form_valid()
```
**⚠️ Regola**: Sempre usare mixin. Non bypassare mai i controlli di autorizzazione.

---

## 🌳 UNIFORMAZIONE UX ARTICOLI

### Pagina Dettaglio Articolo (`/articoli/<id>/`)

#### Ordine Sezioni (v1.1.2)
1. **Dati SCM** — Codici e riferimenti macchina
   - Codice SCM, Descrizione SCM, Prezzo Acquisto SCM (✓ nuovo in v1.1.2)
   - Modello Macchina, Matricola Macchina

2. **Dati Fornitore** — Riferimenti commerciali
   - Fornitore Principale (link), Città, Telefono
   - Codice Fornitore (✓ spostato in v1.1.2), Prezzo Acquisto Fornitore (✓ spostato in v1.1.2)

3. **Dati Articolo** — Anagrafica e soglie operative
   - Codice Interno, Descrizione
   - Categoria + **Breadcrumb gerarchia** (✓ nuovo in v1.1.2) — Es: Meccanica > Motore > Filtri
   - Unità Misura, Giacenza Min/Max
   - Disponibilità (badge), Stato (badge)
   - Creato il, Modificato il

4. **Giacenza** (Sidebar) — Livelli stock
   - Quantità Disponibile, Impegnata, Prenotata, Libera
   - Timestamp ultimo aggiornamento

5. **Ultimi Movimenti** (Bottom) — Audit trail
   - Tabella: Data, Tipo, Quantità, Operatore, Documento

#### Allineamento con Pagina Modifica (`/articoli/<id>/update/`)
Ordine sezioni identico tra dettaglio e form per coerenza UX e riduzione cognitive load.

**Pattern Implementativo**:
- Template-based HTML riarrange (nessun cambio logica Django)
- Uso di metodo modello `Categoria.get_breadcrumb()` per breadcrumb (coerenza con codebase)
- Test template: nessun errore Django rilevato ✅

---

## ⚠️ GOTCHA CRITICI - AVOID THESE MISTAKES

| Errore | Causa | Soluzione | Severità |
|--------|-------|----------|----------|
| **Giacenza aggiornata manualmente** | Codice bypassa signal system | Sempre usa MovimentoMagazzino | 🔴 CRITICA |
| **ProtectedError su categoria DELETE** | FK con PROTECT previene cancellazione | Elimina sottocategorie prima | 🟡 MEDIA |
| **N+1 query in loop** | Template richiama `.all()` in ciclo | Usa `select_related()`/`prefetch_related()` | 🟡 MEDIA |
| **Immagine non elaborata** | Signal pre_save non triggerato | Verifica signal.py è registrato in apps.py | 🟡 MEDIA |
| **Accesso negato su view autorizzata** | Mixin mancante o ruolo sbagliato | Verifica CanEditMixin e ruolo ProfiloUtente | 🟡 MEDIA |
| **Breadcrumb categoria non visibile** | categoria_padre è null (radice) | Verificare che get_breadcrumb() torni valore | 🟠 BASSA |
| **CSRF token mancante** | Form POST senza {% csrf_token %} | Aggiungi token in tutti i template POST | 🟠 BASSA |

**Riferimento completo**: [AGENTS.md - Gotcha Critici](AGENTS.md#-gotcha-critici---aggiornamento-v11)

---

## 📦 SETUP PASSO-PASSO

### Prerequisites

- **Python 3.10+** (disponibile: 3.14.0)
- **MySQL 5.7+** (via XAMPP 10.4)
- **pip** (incluso con Python)
- **Virtual Environment** (già creato: `venv/`)

### 1️⃣ Creare il Database

**Opzione A: Tramite phpMyAdmin (Consigliato)**

```
1. Start XAMPP → Cliccare START su MySQL
2. Aprire browser → http://localhost/phpmyadmin
3. Cliccare tab "SQL" (menu superiore)
4. Aprire file dal progetto: database_creation.sql
5. Copiare tutto il contenuto
6. Incollare nel campo SQL di phpMyAdmin
7. Cliccare "Go" (pulsante esecuzione)
```

**Opzione B: Tramite Terminale**

```powershell
cd "D:\SVILUPPO MATTEO\Progetti\GestioneMagazzinoRicambi Goose"
mysql -u root < database_creation.sql
```

### 2️⃣ Verificare Connessione Database

```bash
python test_db_connection.py
```

Output atteso:
```
✅ Django setup completed successfully!
✅ MySQL database connection successful!
   Database: GMR
   Host: 127.0.0.1
   User: root
```

### 3️⃣ Applicare Migrazioni Django

```bash
python manage.py migrate
```

### 4️⃣ Caricare Dati di Test (CONSIGLIATO)

**Dati Magazzino**:
```bash
python manage.py populate_db
```

Crea:
- **8 categorie** gerarchiche (Motori, Trasmissioni, Componenti Meccanici, Idraulica, Pneumatica, Controllo, Connettori, Varia)
- **14 unità di misura** via tbUnitaMisura (Pz, Lt, Mt, Set, Coppia, Conf, Ore, gg, km, etc.)
- **5 fornitori** (MotorTech, HydraulicSys, ElectroComponents, FastSupply, QualityParts)
- **19 articoli** con giacenze associate
- **77 movimenti** ultimi 30 giorni (CARICO/SCARICO/RETTIFICA/RESO)
- **4 utenti test**:
  - `admin` / `admin` (ADMIN - Accesso completo)
  - `gestore` / `gestore` (GESTORE_MAGAZZINO - CRUD + Report)
  - `operatore` / `operatore` (OPERATORE - Solo creazione movimenti)
  - `visualizzatore` / `visualizzatore` (VISUALIZZATORE - Solo lettura)

**Dati Clienti - Fase 1** ✅:
```bash
python manage.py import_tbappellativo
python manage.py import_tbcategoriaiva
python manage.py import_tbcategorietariffe
python manage.py import_tbtipopagamento
python manage.py import_tbmodalitapagamento
```

Importa:
- **7 appellativi** (Sig., Dott., Prof., etc.)
- **7 categorie IVA** con aliquote (22%, 0%, etc.)
- **21 categorie tariffe** (Assistenza, Produzione, etc.)
- **23 tipi pagamento** (Bonifico 30gg, 60gg, RI.BA., etc.)
- **8 modalità pagamento** (Contanti, Assegno, Carta, etc.)

**TOTALE**: 66 record clienti + dati magazzino completi

### 5️⃣ Avviare Server di Sviluppo

```bash
python manage.py runserver
```

Accedere: **http://localhost:8000/accounts/login/** con credenziali `admin` / `admin`

---

## 📊 MODELLI DATI (16 TOTALI)

### Dominio Magazzino (9 modelli)

```
Categoria
├── nome_categoria: CharField(max_length=100, unique=True)
├── descrizione: TextField(blank=True)
├── categoria_padre: ForeignKey(self, null=True) - Gerarchia
├── livello: IntegerField(default=0)
└── ordine: PositiveIntegerField(default=0)

TbUnitaMisura ✅ (sostituisce UnitaMisura)
├── idUnitaMisura: AutoField(PK, db_column='idUnitaMisura')
├── Denominazione: CharField(max_length=50) - es: Pz, Ore, km
├── DenominazioneStampa: CharField(max_length=100, null=True)
├── stato_attivo: BooleanField(default=True)
├── creato_il: DateTimeField(auto_now_add=True)
└── modificato_il: DateTimeField(auto_now=True)
📊 14 righe: Pz(9), Lt(10), Mt(11), Set(12), Coppia(13), Conf(14), Ore(4), gg(3), km(2), etc.

Fornitore
├── ragione_sociale: CharField(max_length=200)
├── partita_iva: CharField(max_length=20, unique=True)
├── email: EmailField()
├── telefono: CharField(max_length=20)
├── indirizzo: TextField()
└── è_attivo: BooleanField(default=True)

PezzoRicambio (Articles)
├── codice_interno: CharField(max_length=50, unique=True)
├── codice_scm: CharField(max_length=50, blank=True)
├── codice_fornitore: CharField(max_length=50, blank=True)
├── descrizione: TextField()
├── categoria: ForeignKey(Categoria)
├── unita_misura: ForeignKey(TbUnitaMisura) - db_column='idUnitaMisura'
├── fornitore: ForeignKey(Fornitore)
├── giacenza_minima: PositiveIntegerField()
├── giacenza_massima: PositiveIntegerField()
├── prezzo_acquisto: DecimalField(max_digits=10, decimal_places=2)
└── è_attivo: BooleanField(default=True)

Giacenza (Stock Levels)
├── pezzo: OneToOneField(PezzoRicambio)
├── quantita_disponibile: PositiveIntegerField(default=0)
├── quantita_impegnata: PositiveIntegerField(default=0)
├── quantita_prenotata: PositiveIntegerField(default=0)
├── ultimo_movimento: DateTimeField(auto_now=True)
├── giacenza_minima: PositiveIntegerField()
└── giacenza_massima: PositiveIntegerField()

MovimentoMagazzino (Warehouse Movements)
├── pezzo: ForeignKey(PezzoRicambio)
├── tipo_movimento: CharField (CARICO/SCARICO/RETTIFICA/RESO)
├── data: DateTimeField(auto_now_add=True)
├── quantita: PositiveIntegerField()
├── operatore: ForeignKey(User)
├── note: TextField(blank=True)
└── documento_riferimento: CharField(max_length=100, blank=True)

Inventario
├── data_inventario: DateField()
├── operatore: ForeignKey(User)
├── stato: CharField (APERTO/CHIUSO)
└── note: TextField(blank=True)

DettaglioInventario
├── inventario: ForeignKey(Inventario)
├── pezzo: ForeignKey(PezzoRicambio)
├── quantita_rilevata: PositiveIntegerField()
├── quantita_sistema: PositiveIntegerField()
└── discrepanza: IntegerField()

DocumentoAllegato
├── pezzo: ForeignKey(PezzoRicambio)
├── nome_file: CharField(max_length=255)
├── tipo: CharField(max_length=50)
├── data_upload: DateTimeField(auto_now_add=True)
└── dimensione: BigIntegerField()
```

### Authentication Domain (2 models)

```
ProfiloUtente (OneToOneField to User)
├── user: OneToOneField(User)
├── ruolo: CharField (ADMIN/GESTORE_MAGAZZINO/OPERATORE/VISUALIZZATORE)
└── è_attivo: BooleanField(default=True)

LogAccesso (Audit Trail)
├── user: ForeignKey(User)
├── data_ora: DateTimeField(auto_now_add=True)
├── indirizzo_ip: GenericIPAddressField()
└── successo: BooleanField()
```

### Dominio Clienti e Fatturazione - FASE 1 ✅ (5 modelli base)

```
TbAppellativo
├── idAppellativo: AutoField(PK, db_column='idAppellativo')
└── Descrizione: CharField(max_length=50) - es: Sig., Dott., Prof.
📊 7 righe importate

TbCategoriaIVA
├── idCategoriaIVA: AutoField(PK, db_column='idCategoriaIVA')
├── NomeCategoria: CharField(max_length=100) - es: Manodopera, Ricambi
└── ValoreIVA: DecimalField(5,3) - es: 0.22 = 22%
📊 7 righe importate

TbCategorieTariffe
├── idCategorieTariffe: AutoField(PK, db_column='idCategorieTariffe')
├── CategoriaTariffe: CharField(max_length=200)
└── IsVisible: BooleanField(default=True)
📊 21 righe importate

TbTipoPagamento
├── idTipoPagamento: AutoField(PK, db_column='idTipoPagamento')
├── descrizione: CharField(max_length=200) - es: Bonifico 30 gg D.F.
├── DataRifScad: CharField(max_length=50) - DF/FM
├── GiorniDataRif: IntegerField
└── GiornoAddebito: IntegerField
📊 23 righe importate

TbModalitaPagamento
├── idModalitaPagamento: AutoField(PK, db_column='idModalitaPagamento')
└── Nome: CharField(max_length=100) - es: Bonifico bancario
📊 8 righe importate

✅ TOTALE FASE 1: 74 record in 6 tabelle gestibili
```

---

## 🎯 VIEW & URL (22 CLASS-BASED VIEW)

### URL Magazzino
```
/                              → Dashboard (statistiche)

/categorie/                    → CategoriaListView
/categorie/create/             → CategoriaCreateView
/categorie/<id>/update/        → CategoriaUpdateView
/categorie/<id>/delete/        → CategoriaDeleteView

/articoli/                     → PezzoRicambioListView
/articoli/create/              → PezzoRicambioCreateView
/articoli/<id>/                → PezzoRicambioDetailView
/articoli/<id>/update/         → PezzoRicambioUpdateView
/articoli/<id>/delete/         → PezzoRicambioDeleteView

/fornitori/                    → FornitoreListView
/fornitori/create/             → FornitoreCreateView
/fornitori/<id>/               → FornitoreDetailView
/fornitori/<id>/update/        → FornitoreUpdateView
/fornitori/<id>/delete/        → FornitoreDeleteView

/modelli-scm/                  → ModelloSCMListView
/modelli-scm/create/           → ModelloSCMCreateView
/modelli-scm/<id>/update/      → ModelloSCMUpdateView
/modelli-scm/<id>/delete/      → ModelloSCMDeleteView

/matricole-scm/                → MatricolaSCMListView
/matricole-scm/create/         → MatricolaSCMCreateView
/matricole-scm/<id>/update/    → MatricolaSCMUpdateView
/matricole-scm/<id>/delete/    → MatricolaSCMDeleteView

/movimenti/                    → MovimentoListView
/movimenti/create/             → MovimentoCreateView
/movimenti/<id>/               → MovimentoDetailView

/giacenze/                     → GiacenzaListView
/giacenze/<id>/                → GiacenzaDetailView

/report/giacenze/              → ReportGiacenzeView
/report/movimenti/             → ReportMovimentiView

/backup/                       → BackupListView (solo ADMIN)
/backup/settings/              → BackupSettingsView (solo ADMIN)

/gestione-tabelle/             → GestioneTabelleView (ADMIN/GESTORE)
/modifica-tabella/<nome>/      → ModificaTabellaView (ADMIN/GESTORE)
```

### URL Accounts
```
/accounts/login/               → LoginView
/accounts/logout/              → LogoutView
/accounts/profile/             → ProfileView
/accounts/profile/edit/        → EditProfileView
```

---

## 🔐 PERMESSI BASATI SU RUOLO

### Matrice Permessi

| Feature | ADMIN | GESTORE_MAGAZZINO | OPERATORE | VISUALIZZATORE |
|---------|-------|-------------------|-----------|----------------|
| **CRUD Categorie** | ✅ | ✅ | ❌ | 🔍 |
| **CRUD Articoli** | ✅ | ✅ | ❌ | 🔍 |
| **CRUD Fornitori** | ✅ | ✅ | ❌ | 🔍 |
| **Crea Movimenti** | ✅ | ✅ | ✅ | ❌ |
| **Modifica Movimenti** | ✅ | ✅ | ❌ | ❌ |
| **View Report Giacenze** | ✅ | ✅ | ❌ | 🔍 |
| **View Report Movimenti** | ✅ | ✅ | ❌ | 🔍 |
| **Accesso Admin Panel** | ✅ | ❌ | ❌ | ❌ |

**Legenda**: ✅ = Accesso completo | ❌ = Nessun accesso | 🔍 = Solo lettura

### Implementazione

```python
# In views.py - Controllo Permessi
class CanEditMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.profilo.può_modificare_dati()

class CanViewMixin(UserPassesTestMixin):
    def test_func(self):
        return True  # Tutti gli utenti autenticati possono visualizzare

# Utilizzo
class PezzoRicambioCreateView(CanEditMixin, CreateView):
    model = PezzoRicambio
    form_class = PezzoRicambioForm
    template_name = 'magazzino/pezzoricambio_form.html'
```

---

## 🎨 TEMPLATE (22 TOTALI)

### Struttura
```
templates/
├── base.html (navbar, sidebar, footer con Bootstrap 5.3)
├── accounts/
│   ├── login.html
│   ├── profile.html
│   └── edit_profile.html
│   ├── utente_list.html, utente_form.html, utente_detail.html, utente_confirm_delete.html (4)
└── magazzino/
    ├── dashboard.html (dashboard statistiche)
    ├── categoria_list.html, categoria_form.html, categoria_confirm_delete.html, categoria_tree_item.html (4)
    ├── pezzoricambio_list.html, pezzoricambio_form.html, pezzoricambio_detail.html, pezzoricambio_confirm_delete.html (4)
    ├── fornitore_list.html, fornitore_form.html, fornitore_detail.html, fornitore_confirm_delete.html (4)
    ├── modello_scm_list.html, modello_scm_form.html, modello_scm_confirm_delete.html (3)
    ├── matricola_scm_list.html, matricola_scm_form.html, matricola_scm_confirm_delete.html (3)
    ├── movimento_list.html, movimento_form.html, movimento_detail.html (3)
    ├── giacenza_list.html, giacenza_detail.html (2)
    ├── report_giacenze.html (report giacenze)
    ├── report_movimenti.html (report movimenti 30gg)
    ├── backup_list.html, backup_settings.html (2 - sistema backup)
    ├── gestione_tabelle.html, modifica_tabella.html (2 - gestione tabelle clienti)
    └── [40 template totali]
```

### 🎛️ SISTEMA GESTIONE TABELLE CLIENTI

**Interfaccia web completa per visualizzare, ricercare e modificare tabelle clienti senza accesso SQL.**

#### URL di Accesso
- **Pagina Principale**: `/gestione-tabelle/` (solo ADMIN/GESTORE)
- **Modifica Record**: `/modifica-tabella/<nome_tabella>/record/<pk>/` (form interattivo)

#### Funzionalità Disponibili

| Operazione | Descrizione | Permessi |
|-----------|-------------|----------|
| **Visualizzazione** | Lista paginata di tutti i record | ADMIN, GESTORE |
| **Ricerca** | Filtro per campo (es. nome, email) | ADMIN, GESTORE |
| **Filtro Stato** | Toggle "Mostra Inattivi" (per tabelle con stato_attivo) | ADMIN, GESTORE |
| **Modifica Record** | Form interattivo con validazione | ADMIN, GESTORE |
| **Audit Log** | Tracciamento automatico di ogni modifica | Automatico |

#### Flusso Operativo - Modifica Record
```
1. Accedi a /gestione-tabelle/
2. Seleziona tabella (es. tbappellativo)
3. Clicca link "Modifica" su un record
4. Compila form con nuovi valori
5. Clicca "Salva Modifiche"
6. Modifica persiste in DB + audit log generato
7. Redirect a lista aggiornata con success message
```

#### 🗂️ Tabelle Gestibili (10 totali)

| ID | Tabella | Descrizione | Record | Filtro Stato |
|----|---------|-------------|--------|-------------|
| 1 | `tbappellativo` | Appellativi (Sig., Dott., Prof.) | 7 | ❌ |
| 2 | `tbunitamisura` | Unità di Misura (Pz, Lt, Mt, etc.) | 14 | ✅ |
| 3 | `tbtipopagamento` | Tipo Pagamento (Bonifico, RI.BA.) | 23 | ❌ |
| 4 | `tbprestazioni` | Prestazioni (Lavori, Manutenzione) | 0 | ✅ |
| 5 | `tbcategorietariffe` | Categorie Tariffe (Assistenza, Prod.) | 21 | ✅ |
| 6 | `tbcategoriaiva` | Categoria IVA (22%, 10%, 0%) | 7 | ❌ |
| 7 | `tbcontatti` | Contatti Clienti/Fornitori | 0 | ❌ |
| 8 | `modelli_macchine_scm` | Modelli Macchine SCM | 0 | ✅ |
| 9 | `matricole_macchine_scm` | Matricole Macchine SCM | 0 | ✅ |
| 10 | `tbmodalitapagamento` | Modalità Pagamento (Contanti, Carta) | 8 | ❌ |

**Legenda**: Filtro Stato ✅ = disponibile toggle "Mostra Inattivi", ❌ = tabella non filtrabile

#### Gestione Record Inattivi (tbunitamisura)
Per tabelle con campo `stato_attivo`:
- **Default**: Mostra sia record attivi che inattivi
- **Toggle**: Checkbox "Mostra Inattivi" per includere/escludere record con `stato_attivo=False`
- **Uso**: Utile per consultare elementi deprecati senza rinominare DB

Esempio: La tbunitamisura può contenere unità obsolete nascoste ma consultabili tramite toggle.

#### Implementazione Backend
- **View**: `ModificaTabellaView` (lista) + `ModificaRecordTabellaView` (modifica singolo record)
- **Whitelist Tabelle**: Configurazione centralizzata in `_get_tabelle_permesse_config()`
- **Form Dinamico**: Utilizzato `modelform_factory` per generare form specifici per tabella
- **Permessi**: Controllo `CanEditMixin` (solo ADMIN e GESTORE_MAGAZZINO)
- **Validazione**: Form validation lato server + feedback errori lato client

### Caratteristiche Design
- **Framework**: Bootstrap 5.3 (CDN)
- **Icone**: Font Awesome 6.4 (CDN)
- **Colori**:
  - Primary: #1a5f7a (blu scuro)
  - Secondary: #2a8db8 (blu chiaro)
  - Alerts: #e74c3c (rosso), #27ae60 (verde), #f39c12 (arancione)
- **Responsive**: Mobile-first, tutti i breakpoint (xs, sm, md, lg, xl)
- **Componenti**: Navbar, sidebar, card, modal, table, form, badge

---

## � AUDIT LOGGING PER MODIFICHE TABELLE

**Ogni modifica ai record attraverso l'interfaccia web genera un log di audit permanente.**

### Dove Trovare i Log
- **File**: `logs/django.log`
- **Marker**: Ricerca `[AUDIT_TABELLE]` per filtrare le modifiche
- **Formato**: Strutturato con utente, tabella, modello, record_pk, diff campi

### Esempio Log Entry
```
[AUDIT_TABELLE] utente=admin tabella=tbappellativo modello=TbAppellativo record_pk=3 modifiche=Descrizione: 'Dott.' -> 'Dott. AGGIORNATO' | data_modifica=2026-05-10 14:32:15
```

### Implementazione Tecnica
- **Logger**: `magazzino.views`
- **Level**: INFO
- **Trigger**: Metodo `form_valid()` in `ModificaRecordTabellaView`
- **Dati Tracciati**:
  - Utente che ha effettuato modifica
  - Nome tabella e modello ORM
  - Primary key del record modificato
  - Diff per ogni campo (vecchio → nuovo)
  - Timestamp modifica

### Come Interpretare i Log
```bash
# Cercare tutte le modifiche di un utente
grep "utente=operatore" logs/django.log | grep AUDIT_TABELLE

# Cercare modifiche a una tabella specifica
grep "tabella=tbunitamisura" logs/django.log

# Cercare modifiche a un record specifico
grep "record_pk=12" logs/django.log
```

**Nota**: I log aiutano il team a tracciare chi ha modificato cosa e quando. Verificare regolarmente per identificare eventuali modifiche non autorizzate.

---

## �🔒 IMPLEMENTAZIONE SICUREZZA

### Autenticazione & Autorizzazione
- ✅ Integrazione Django User model
- ✅ Hashing password con Argon2 (più forte di PBKDF2)
- ✅ Role-based access control (4 ruoli distinti)
- ✅ Controllo permessi su ogni operazione CRUD
- ✅ Log audit (modello LogAccesso)

### Sicurezza Session & Cookie
- ✅ `SESSION_COOKIE_HTTPONLY = True` (JS non può accedere)
- ✅ `SESSION_COOKIE_SAMESITE = 'Strict'` (protezione CSRF)
- ✅ `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` (sicurezza)
- ✅ HTTPS ready (impostare `SESSION_COOKIE_SECURE = True` in produzione)

### Protezione Form & Dati
- ✅ Token CSRF su tutti i form POST ({% csrf_token %})
- ✅ Django ORM previene SQL injection
- ✅ Auto-escaping output HTML (prevenzione XSS)
- ✅ Validazione form server-side + client-side

### Checklist Produzione

Aggiornare `config/settings.py` per la produzione:
```python
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')  # Usare variabile ambiente
ALLOWED_HOSTS = ['yourdomain.it', 'www.yourdomain.it']
SESSION_COOKIE_SECURE = True  # Richiede HTTPS
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 anno
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 📊 DATI DI TEST (populate_db.py)

Eseguendo `python manage.py populate_db` vengono creati:

```
8 Categorie
├── Motori e Riduttori
├── Trasmissioni
├── Componenti Meccanici
├── Idraulica
├── Pneumatica
├── Sistemi di Controllo
├── Connettori
└── Varia

7 Unità di Misura
├── Pezzo (pc)
├── Chilogrammi (kg)
├── Litri (l)
├── Ore (h)
├── Metri (m)
├── Millimetri (mm)
└── Watt (W)

5 Fornitori
├── MotorTech SpA
├── HydraulicSys srl
├── ElectroComponents Ltd
├── FastSupply GmbH
└── QualityParts Sdn Bhd

19 Articoli (PezzoRicambio)
└── Con record Giacenza associati

77 Movimenti (ultimi 30 giorni)
├── Mix di CARICO, SCARICO, RETTIFICA, RESO
├── Distribuiti tra 19 articoli
└── Collegati agli utenti test

4 Utenti Test (con ProfiloUtente)
├── admin / admin (ADMIN)
├── gestore / gestore (GESTORE_MAGAZZINO)
├── operatore / operatore (OPERATORE)
└── visualizzatore / visualizzatore (VISUALIZZATORE)
```

---

## 🛠️ COMANDI UTILI

### Django Management

```bash
# Database
python manage.py migrate              # Applicare migrazioni
python manage.py makemigrations       # Creare migrazioni
python manage.py showmigrations       # Mostrare stato migrazioni

# Utenti & Auth
python manage.py createsuperuser      # Creare utente admin
python manage.py changepassword user  # Cambiare password utente

# Dati
python manage.py dumpdata > backup.json      # Esportare tutti i dati
python manage.py loaddata backup.json        # Importare dati
python manage.py populate_db                 # Caricare dati test

# Utilities
python manage.py shell                # Shell Python interattivo
python manage.py check                # Verificare problemi
python manage.py check --deploy       # Controlli produzione
python manage.py collectstatic        # Raccogliere file static
python manage.py clearsessions        # Pulire sessioni vecchie
```

### MySQL (Diretto)

```bash
# Backup
mysqldump -u root GMR > backup_$(date +%Y%m%d).sql

# Restore (ATTENZIONE: sovrascrive il DB attuale!)
mysql -u root GMR < backup_file.sql

# Accesso diretto
mysql -u root GMR
```

---

## 🆘 TROUBLESHOOTING

### Errori Database

| Problema | Causa | Soluzione |
|----------|-------|----------|
| "Connessione database rifiutata" | MySQL non in esecuzione | Avviare XAMPP → START su MySQL |
| "Tabella non esiste" dopo git pull | Migrazioni non applicate | `python manage.py migrate` |
| "Foreign key constraint fails" | FK con PROTECT previene delete | Eliminare dipendenze prima o usare CASCADE |
| "Table doesn't exist" | Database non creato | `mysql -u root < database_creation.sql` |

### Errori Django

| Problema | Causa | Soluzione |
|----------|-------|----------|
| "Porta 8000 già in use" | Altro processo occupa porta | `python manage.py runserver 8001` |
| "ModuleNotFoundError" | Dipendenza mancante | `pip install -r requirements.txt` |
| "TemplateDoesNotExist" | File template mancante | Verificare path in templates/ |
| "Permission Denied su CRUD" | Ruolo utente insufficiente | Verificare ProfiloUtente.ruolo in admin |
| "Login fallisce con password corretta" | Dati test non caricati | `python manage.py populate_db` |

### Errori Permessi Comuni

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

### Pattern di Integrazione Cross-Component

**Flusso Movimento di Stock (Critico)**:
```
1. Crea MovimentoMagazzino (tipo=CARICO/SCARICO/RETTIFICA/RESO)
2. Model.save() memorizza movimento (immutabile) + timestamp + operatore
3. Signal @receiver(post_save) aggiorna Giacenza.disponibile automaticamente
4. View restituisce success_message con saldo nuovo
```
→ **Mai** creare/aggiornare Giacenza direttamente; sempre via MovimentoMagazzino

**Flusso Caricamento Articolo (Immagini)**:
```
1. User carica PNG/JPEG in PezzoRicambio.immagine (form field)
2. Signal @receiver(pre_save) processa:
   - Immagine principale → ridimensiona 800x800px JPEG 90%
   - Thumbnail → genera 300x300px JPEG 85%
   - PNG/RGBA → converte RGB con sfondo bianco
3. File salvati in media/articoli/YYYY/MM/DD/
4. Signal @receiver(post_delete) pulisce file quando articolo cancellato
```
→ **Non** salvare mai immagini raw nel DB; il signal gestisce tutto

**Flusso Backup Database (3 Metodi)**:
```
Metodo 1 (Web UI): /backup/ → BackupListView → click "Ripristina" → BackupRestoreView
Metodo 2 (CLI): python manage.py restore_backup → scegli backup da lista interattiva
Metodo 3 (PowerShell): .\restore_db_emergency.ps1 → script standalone XAMPP

BackupManager traccia: backup_dir, retention_days (30), mysql_bin_path
File backup: backups/backup_gmr_YYYYMMDD_HHMMSS.sql.gz (auto-cleanup vecchi)
```
→ **Preferisci metodo 1 o 2**; PowerShell solo emergenza (Windows-only)

---

## � ULTIME MODIFICHE - PIANO 1 STABILIZZAZIONE (v1.1.1)

**Data**: 10 maggio 2026  
**Scope**: Stabilizzazione architettura, audit logging, collaudi end-to-end

### ✅ Completamenti Implementati

| Item | Descrizione | File Interessati |
|------|-------------|------------------|
| **Modifica Record Reale** | Implementata view generica per edit record tabelle con whitelist | `magazzino/views.py`, `magazzino/urls.py`, `templates/magazzino/modifica_record_tabella.html` |
| **Audit Logging** | Logger strutturato con marker `[AUDIT_TABELLE]` e diff campi | `magazzino/views.py`, `logs/django.log` |
| **Gestione Tabelle Completa** | Interfaccia web da `/gestione-tabelle/` con visualizzazione + modifica | `magazzino/views.py`, `templates/magazzino/gestione_tabelle.html` |
| **Fix Visibilità Record Inattivi** | Nuova logica per tbunitamisura mostra inattivi di default | `magazzino/views.py` |
| **Fix CSS Compatibilità** | Rimozione selettore `:has()` non standard, sostituzione con `.alert-warning-special` | `templates/base.html`, `static/js/` |
| **Test Suite Estesa** | Aggiunti 3 nuovi test (modifica record, permessi, visibilità) | `magazzino/tests.py` |

### Suite Test Validata
```
20 test totali - TUTTI VERDI ✅
├── 4 test CodiceArticolo (generazione automatica)
├── 3 test GestioneTabelle (modifica, permessi, visibilità)
├── 13 test Accounts (autenticazione, logout, autorizzazione)
└── (altri test modelli)
```

### Collaudo E2E Completato
Testati su 3 tabelle reali:
- ✅ tbappellativo (7 record)
- ✅ tbmodalitapagamento (8 record)
- ✅ tbcategoriaiva (7 record)

**Risultati**: Lista 200 OK, Form 200 OK, POST 302 Redirect OK, Persistenza DB OK, Audit Log OK

### Breaking Changes
⚠️ **NESSUN breaking change**: Tutte le modifiche sono backward-compatible con versione v1.1

### Come Testare Piano 1 Localmente
```bash
# 1. Aggiorna il codice
git pull

# 2. Applica eventuali migrazioni (normalmente non ce ne sono)
python manage.py migrate

# 3. Esegui test suite
python manage.py test magazzino.tests.GestioneTabelleRecordTests

# 4. Avvia server
python manage.py runserver

# 5. Accedi a /gestione-tabelle/ con admin / admin
# 6. Modifica un record e verifica audit log: grep AUDIT_TABELLE logs/django.log
```

### Known Issues
Nessun known issue riportato.

---

## �📁 STRUTTURA PROGETTO

```
GestioneMagazzinoRicambi Goose/
│
├── config/                    # Configurazione progetto Django
│   ├── settings.py            # Database, app, middleware config
│   ├── urls.py                # Routing URL principale
│   ├── wsgi.py                # Configurazione WSGI
│   └── asgi.py                # Configurazione ASGI
│
├── accounts/                  # App Autenticazione
│   ├── models.py              # ProfiloUtente, LogAccesso
│   ├── views.py               # LoginView, ProfileView, etc.
│   ├── forms.py               # LoginForm, ProfileForm
│   ├── urls.py                # Rotte /accounts/
│   ├── signals.py             # Auto-crea ProfiloUtente
│   ├── admin.py               # Interfaccia admin
│   └── migrations/            # Migrazioni database
│
├── magazzino/                 # App Magazzino
│   ├── models.py              # 16 modelli (11 magazzino + 6 clienti)
│   ├── views.py               # 47 CBV totali
│   ├── forms.py               # Form Django con crispy-forms
│   ├── urls.py                # 40+ URL routes
│   ├── admin.py               # Admin interface
│   ├── backup_manager.py      # Gestione backup DB
│   ├── management/
│   │   └── commands/
│   │       ├── populate_db.py # Dati test magazzino
│   │       ├── create_backup.py
│   │       └── import_tb*.py  # Import tabelle clienti
│   └── migrations/            # Migrazioni database
│
├── templates/                 # Template HTML (40+ totali)
│   ├── base.html              # Template base (navbar, sidebar)
│   ├── accounts/
│   │   ├── login.html
│   │   ├── profile.html
│   │   └── edit_profile.html
│   └── magazzino/
│       ├── dashboard.html
│       ├── categoria_*.html
│       ├── pezzoricambio_*.html
│       ├── fornitore_*.html
│       ├── movimento_*.html
│       ├── giacenza_*.html
│       └── report_*.html
│
├── static/                    # CSS, JavaScript, immagini
│   └── css/, js/, img/
│
├── logs/                      # File log applicazione
│
├── venv/                      # Virtual environment Python
│
├── BACKUP_RECOVERY_GUIDE.md  # Guida completa backup & recovery
├── restore_db_emergency.ps1  # Script PowerShell ripristino emergenza
├── fix_mysql.ps1             # Ripristino MySQL XAMPP corrotto
├── export_db_to_csv.py       # Export modelli → CSV
├── test_db_connection.py     # Verifica connessione MySQL
├── check_system.py           # Verifica dipendenze sistema
├── .pylintrc                 # Configurazione linting Python
```

---

## 📚 RISORSE LEARNING

Questo progetto dimostra:
- Setup & configurazione Django 5.2
- Relazioni modelli ORM & query
- Class-Based Views con mixin
- Gestione form & validazione
- Autenticazione & permessi
- Template inheritance & rendering
- URL routing con namespace
- Design & migrazioni database
- Customizzazione interfaccia admin
- Design responsive Bootstrap
- Handler signal
- Management command

---

## 🚀 DEPLOY

Per il deploy in produzione, consulta [MANUALE_AMMINISTRATORE.md](MANUALE_AMMINISTRATORE.md) sezione "Deploy" che copre:
- Checklist pre-deploy
- Setup Gunicorn + Nginx
- Configurazione SSL/HTTPS
- Ottimizzazione database
- Automazione backup

---

## 🆘 BACKUP & RECOVERY

Il sistema include **3 metodi di ripristino** database per ogni scenario:

### 📊 Metodi Disponibili

| Metodo | Quando Usare | Richiede Login | Complessità |
|--------|--------------|----------------|-------------|
| **Interfaccia Web** | Database OK, interfaccia accessibile | ✅ SI | ⭐ Facile |
| **Management Command** | Database corrotto, Django funzionante | ❌ NO | ⭐⭐ Medio |
| **Script PowerShell** | Emergenza totale, Django non funziona | ❌ NO | ⭐⭐⭐ Avanzato |

### 🌐 Metodo 1: Interfaccia Web (Normale)

```
1. Accedi a http://127.0.0.1:8000/backup/
2. Clicca "Ripristina" sul backup desiderato
3. Digita "RESTORE" per confermare
4. Riavvia server Django
```

### 💻 Metodo 2: Management Command (Emergenza Media)

```bash
# Lista backup disponibili
python manage.py restore_backup --list

# Ripristina backup specifico
python manage.py restore_backup backup_gmr_20251223_120530.sql.gz

# Oppure ripristina il più recente
python manage.py restore_backup --latest
```

### 🚨 Metodo 3: Script PowerShell (Emergenza Critica)

**Quando Django è completamente inaccessibile:**

```powershell
# Lista backup
.\restore_db_emergency.ps1 -ListBackups

# Ripristina il più recente
.\restore_db_emergency.ps1 -Latest

# Ripristina backup specifico
.\restore_db_emergency.ps1 -BackupFile backup_gmr_20251223_120530.sql.gz
```

**📘 Guida Completa**: Vedi [BACKUP_RECOVERY_GUIDE.md](BACKUP_RECOVERY_GUIDE.md) per procedure dettagliate e troubleshooting.

### ✅ Completezza Backup

I backup includono:
- ✅ Struttura completa database (CREATE TABLE)
- ✅ Tutti i dati (INSERT con nomi colonne)
- ✅ Stored procedures e functions
- ✅ Trigger database
- ✅ Eventi schedulati
- ✅ Charset UTF8MB4 corretto
- ✅ Compressione gzip automatica

**Nota**: File media (immagini) NON inclusi - backup manuale di `media/articoli/` consigliato.

---

## 📚 STRUTTURA DOCUMENTAZIONE

| Documento | Scopo | Audience |
|-----------|-------|----------|
| **README.md** (questo file) | Referimento tecnico completo con setup | Developer, IT Staff |
| **GESTIONE_UTENTI.md** | Guida completa al sistema utenti | Admin, Support Staff |
| **MANUALE_AMMINISTRATORE.md** | Procedure amministratore avanzate | System Admin |
| **BACKUP_RECOVERY_GUIDE.md** | **Guida backup & recovery 3 metodi** | **System Admin, DBA** |
| **MEMORIA_TECNICA_SVILUPPO.md** | **Memory centrale sviluppo recente** | **Developer, AI Agents** |
| **AGENTS.md** | **Patterns architettura per AI agents** | **Copilot/AI Development** |

**Nota**: START_HERE.md, QUICK_START.md, PROJECT_STATUS.md sono stati consolidati in questo README.

---

## 🔧 CONVENZIONI SPECIFICHE PROGETTO

### Naming Modelli & Database
- **Nomi italiani**: i nomi dei campi sono in italiano (es. `giacenza_minima`, `codice_scm`, `operatore`)
- **Colonne PK**: Sempre `id_<model_minuscolo>` (es. `id_categoria`, `id_pezzo`)
- **Riferimenti FK**: Usare `db_column` per matching naming legacy (es. `id_categoria_padre`)
- **Campi timestamp**: `creato_il` (auto_now_add), `modificato_il` (auto_now) - naming standard
- **Modelli clienti**: Nomi tabella legacy (es. `TbAppellativo`, `TbCategoriaIVA`) con campi legacy (`idAppellativo`, `idCategoriaIVA`)

### Naming View & URL
- `<Model>ListView` per pagine lista/ricerca
- `<Model>CreateView` per form di creazione
- `<Model>DetailView` per visualizzazione singolo oggetto (dettaglio read-only + link modifica)
- `<Model>UpdateView` per form di modifica
- `<Model>DeleteView` con template di conferma
- **Dashboard views**: Usare `TemplateView` con logica aggregata (es. `DashboardView`)
- **URL routes**: kebab-case italiano (es. `/categorie/`, `/articoli/`)

### Validazione Form
- Usare metodi `clean_<fieldname>()` per validazione specifica campo
- Usare `clean()` per validazione cross-field (es. min ≤ max)
- Widget personalizzati: `MatricolaSelectWidget` aggiunge data attributes per interop JS
- Crispy-forms: sempre usare `{% load crispy_forms_tags %}` + `{{ form|crispy }}`

### Struttura Template
- Tutti ereditano da `base.html` (navbar, sidebar, footer)
- Usare crispy forms: `{% load crispy_forms_tags %}`
- Font Awesome 6.4 per icone (es. `<i class="fas fa-plus"></i>`)
- Bootstrap 5.3 (CDN) per componenti responsive

### Signals & Automazione Dati
- **MovimentoMagazzino** → **Giacenza**: Signal `post_save` aggiorna stock disponibile/impegnata/prenotata
- **PezzoRicambio**: Signal `pre_save` processa immagini
- **CRITICO**: Non aggiornare mai manualmente Giacenza; creare sempre MovimentoMagazzino
- Campi `auto_now_add`: creato_il (timestamp creazione) - NON modificare manualmente
- Campi `auto_now`: modificato_il, ultimo_accesso (timestamp aggiornamento automatico)

### Middleware & Sicurezza
- `NoCacheMiddleware` disabilita caching per utenti autenticati (prevenire perdite info su PC condivisi)
- Protezione CSRF abilitata; tutti i form usano `{% csrf_token %}`
- Hashing Argon2 per password (argon2-cffi)

**Riferimento completo**: [AGENTS.md - Convenzioni Specifiche Progetto](AGENTS.md#-convenzioni-specifiche-progetto)

---

## � RIFERIMENTO RAPIDO: COMANDI AI-AGENT

```bash
# SETUP INIZIALE (eseguire una volta)
mysql -u root < database_creation.sql     # Crea DB da schema
python manage.py migrate                   # Applica migrazioni Django
python manage.py populate_db               # Carica dati test (8 cat, 5 fornitori, 19 articoli)
python manage.py import_tbappellativo      # Importa 7 record appellativi
python manage.py import_tbcategoriaiva     # Importa 7 record categorie IVA
python manage.py import_tbcategorietariffe # Importa 21 record categorie tariffe
python manage.py import_tbtipopagamento    # Importa 23 record tipi pagamento
python manage.py import_tbmodalitapagamento # Importa 8 record modalità pagamento

# SVILUPPO QUOTIDIANO
python manage.py runserver                 # Avvia server porta 8000
python manage.py shell                     # Django shell per debug modelli
python manage.py test                      # Esegui test suite

# TROUBLESHOOTING
python test_db_connection.py               # Verifica connessione MySQL
python manage.py migrate --plan            # Visualizza migrazioni pendenti
python manage.py showmigrations             # Lista migrazioni applicate

# BACKUP & RECOVERY
python manage.py create_backup              # Crea backup compresso
python manage.py restore_backup             # Ripristina da backup (interattivo)
.\restore_db_emergency.ps1                 # Script PowerShell emergenza
```

### Checklista AI Agent: Decisioni Comuni

| Domanda | Risposta | Riferimento |
|---------|----------|-------------|
| Devo permettere edit a questo campo? | Controlla `CanEditMixin` in view CRUD e `può_modificare_dati()` in form | [magazzino/views.py](magazzino/views.py#L50-L61) |
| Come aggiunge stock correttamente? | **Sempre** crea `MovimentoMagazzino`; **mai** modificare `Giacenza` direttamente | [magazzino/models.py](magazzino/models.py#L669-L750) |
| Dove vanno le immagini? | `media/articoli/` auto-gestito da signals; non toccare manualmente | [magazzino/signals.py](magazzino/signals.py) |
| Categoria padre può avere loop? | **NO** - `save()` verifica max 10 livelli di profondità | [magazzino/models.py](magazzino/models.py#L83-L95) |
| Quale DB driver usiamo? | **PyMySQL** (non mysqlclient) - può differire da MySQL standard | [requirements.txt](requirements.txt) |
| Come gestisco validazione cross-field? | Usa `clean()` nel form, non nel modello | [magazzino/forms.py](magazzino/forms.py) |
| Aggiungo una nuova app? | **NO** - tutto in `accounts` + `magazzino`. Creare modello + view + form in queste | [config/settings.py](config/settings.py#L37-L45) |
| Come testo in locale? | `populate_db` carica dati test; accedi con admin / admin | [README.md](#-avvio-rapido-3-comandi) |
| Come gestisco backup database? | **3 metodi**: Web UI (/backup/), management command, script PowerShell emergenza | [BACKUP_RECOVERY_GUIDE.md](BACKUP_RECOVERY_GUIDE.md) |
| Come accedo tabelle clienti? | **Interfaccia web**: /gestione-tabelle/ (solo ADMIN/GESTORE) | [magazzino/views.py](magazzino/views.py#L2009-L2100) |

---

## �🤝 Come Contribuire

Questo è un progetto Django per la gestione di magazzino ricambi. Se desideri contribuire al miglioramento del progetto, segui le linee guida di seguito:

### Come Segnalare Bug

Se trovi un bug, apri una **Issue** con:
1. **Titolo chiaro**: Descrizione breve del problema
2. **Dettagli del bug**: 
   - Passaggi per riprodurre
   - Comportamento osservato
   - Comportamento atteso
3. **Ambiente**: Python version, Django version, SO
4. **Log/Screenshot**: Errori o schermate rilevanti

**Esempio Issue:**
```
Titolo: Errore 500 quando creo movimento con quantità negativa

Descrizione:
- Passaggi: Accedi → Movimenti → Crea nuovo → Tipo SCARICO → Quantità -5 → Salva
- Errore: "ValueError: quantita cannot be negative"
- Atteso: Validazione form con messaggio di errore chiaro
```

### Come Proporre Feature

Per proporre una nuova feature:
1. Apri una **Issue** con label `enhancement`
2. Descrivi il caso d'uso e i benefici
3. Suggerisci l'implementazione (se possibile)
4. Discuti con il team prima di codificare

### Linee Guida Sviluppo

#### 1️⃣ **Naming Convention**
- **Nomi Python**: snake_case italiano (es. `giacenza_disponibile`, `calcola_saldo`)
- **Nomi database**: Colonne PK come `id_<model>` (es. `id_categoria`, `id_pezzo`)
- **URL routes**: kebab-case italiano (es. `/categorie/`, `/articoli/`)
- **Modelli legacy**: Nomenclatura Tb* mantenuta per compatibilità (es. `TbAppellativo`)

#### 2️⃣ **Struttura Codice**
- **View**: CBV con mixin (CanEditMixin, CanViewMixin)
- **Form**: Usare crispy-forms + crispy-bootstrap5
- **Modelli**: Campi italiani, auto_now_add/auto_now per timestamp
- **Permessi**: Sempre verificare ruolo via mixin, non view logic

#### 3️⃣ **Testing**
Prima di fare commit:
```bash
# Verificare sintassi
python manage.py check

# Eseguire test (se esistono)
python manage.py test

# Validazione migrazioni
python manage.py migrate --plan
```

#### 4️⃣ **Migrazioni Database**
```bash
# Se modifichi modelli, crea migrazione
python manage.py makemigrations

# Verifica prima di commit
python manage.py migrate --plan
```

---

## 🧠 Memoria Tecnica Sviluppo

Per mantenere coerenza tra sviluppo, manuali e operativita quotidiana, la memoria tecnica centralizzata e' disponibile in:

- **[MEMORIA_TECNICA_SVILUPPO.md](MEMORIA_TECNICA_SVILUPPO.md)** - Decisioni operative recenti & timeline interventi

Sintesi ultimo aggiornamento (10/05/2026):
- dashboard con nuovi indicatori articoli,
- doppio layout dashboard con scelta persistente per sessione,
- miglioramenti UX/validazione su form "Aggiungi Nuovo Articolo",
- terminologia frontend allineata in italiano lato utente.

#### 5️⃣ **Documentazione**
- Aggiungi docstring alle funzioni complesse
- Documenta workflow critico nei commenti
- Aggiorna README.md se aggiungi feature importante
- Mantieni AGENTS.md aggiornato con patterns

#### 6️⃣ **Sicurezza**
- Valida sempre input server-side
- Usa ORM Django (prevenzione SQL injection)
- Protezione CSRF: `{% csrf_token %}` nei form
- Permessi: **Mai** bypassare mixin di autorizzazione

#### 7️⃣ **Template**
- Ereditare da `base.html`
- Usare Bootstrap 5.3 (classi standard)
- Font Awesome 6.4 per icone
- Responsive: testare su mobile

### Workflow Contribuzione

```
1. Fork il repository
   git clone https://github.com/YOUR_USERNAME/GestioneMagazzinoRicambi.git

2. Crea branch feature
   git checkout -b feature/nome-feature

3. Fai i cambiamenti
   - Modifica codice
   - Crea test (se applicabile)
   - Aggiorna documentazione

4. Commit con messaggio chiaro
   git commit -m "Descrizione concisa della feature"
   git commit -m "Descrizione: 
   - Cosa è stato fatto
   - Perché è necessario
   - Impatto"

5. Push branch
   git push origin feature/nome-feature

6. Crea Pull Request
   - Descrizione della feature
   - Link a issues correlate
   - Testing performed

7. Code Review
   - Attendi revisione del team
   - Risolvi commenti reviewer
```

### Aree di Contribuzione Prioritarie

- [ ] **Unit Tests**: Implementare test coverage per modelli/view critiche
- [ ] **Ottimizzazione Query**: Ridurre N+1 query, aggiungere select_related/prefetch_related
- [ ] **REST API**: Creare API endpoints per integrazione mobile/esterna
- [ ] **Internazionalizzazione**: Supporto multi-lingua (Django i18n)
- [ ] **Performance**: Caching, indexing database, compressione asset
- [ ] **Documentazione**: Ampliare guide per operatori
- [ ] **UX/UI**: Migliorare interfaccia admin

### Code Review Checklist

Prima di approvare una PR, verificare:
- ✅ Codice segue naming convention del progetto
- ✅ Test passano (se creati)
- ✅ Nessuna regressione su feature esistente
- ✅ Documentazione aggiornata
- ✅ Nessun debug code lasciato (print, debugger)
- ✅ Performance accettabili (no N+1 queries)
- ✅ Sicurezza: validazione input, protezione CSRF

### Domande Frequenti Sviluppo

**D: Dove posso salvare immagini?**
A: Signal `pre_save` in PezzoRicambio elabora automaticamente. Salva in `media/articoli/YYYY/MM/DD/`. Non toccare manualmente.

**D: Come aggiorno stock/giacenza?**
A: **Mai** modificare Giacenza direttamente. Crea MovimentoMagazzino; il signal lo aggiorna automaticamente.

**D: Quali ruoli hanno accesso a questa view?**
A: Controlla il mixin della view:
- `CanViewMixin`: Tutti autenticati (solo lettura)
- `CanEditMixin`: Solo ADMIN + GESTORE_MAGAZZINO

**D: Come gestisco nuove categorie non gerarchiche?**
A: Mantieni la self-FK (`categoria_padre`). Se non assegnata, è root. Verifica profondità max 10 nel `save()`.

---

## 📜 Licenza

Questo progetto è proprietario e riservato. Tutti i diritti sono riservati.

**Restrizioni d'uso:**
- ❌ Vietato copiare, modificare, distribuire senza autorizzazione
- ❌ Vietato usare per scopi commerciali senza licenza esplicita
- ❌ Vietato rivelare il codice sorgente a terzi

**Autorizzazioni per contributori:**
- ✅ È consentito contribuire tramite pull request
- ✅ I contributori cedono i diritti al proprietario del progetto
- ✅ Il proprietario può usare il contributo come ritiene opportuno

Per informazioni su licenze alternative o utilizzo commerciale, contattare il proprietario.

**Proprietario**: Matteo Poggi  
**Email**: [contattare via issue tracker]

---

## 💬 Supporto

Hai domande o hai bisogno di aiuto? Ecco come contattarci:

### 📍 Canali di Supporto

| Canale | Uso | Tempo Risposta |
|--------|-----|----------------|
| **GitHub Issues** | Bug report, domande technical | 24-48 ore |
| **Email** | Supporto commerciale, licenze | 48-72 ore |
| **Wiki/Documentazione** | Domande frequenti (risposte immediate) | - |

### ❓ Domande Frequenti (FAQ)

**Q: Come resetto i dati di test?**
A: 
```bash
mysql -u root < database_creation.sql
python manage.py migrate
python manage.py populate_db
```

**Q: Come cambio la password di un utente?**
A: `python manage.py changepassword <username>`

**Q: Posso usare Postgres al posto di MySQL?**
A: Sì, ma richiede:
- Installare `psycopg2`
- Modificare DATABASES in settings.py
- Testare (alcune query potrebbero differire)

**Q: Come aggiungo un nuovo modello?**
A: Vedi [AGENTS.md](AGENTS.md#-checklista-ai-agent-decisioni-comuni) - sezione "Aggiungere una Nuova View CRUD"

**Q: Dove posso trovare la documentazione completa?**
A: Consulta:
- [README.md](README.md) - Setup & architettura
- [AGENTS.md](AGENTS.md) - Patterns & best practices (per AI agents)
- [MANUALE_AMMINISTRATORE.md](MANUALE_AMMINISTRATORE.md) - Procedure admin
- [GESTIONE_UTENTI.md](GESTIONE_UTENTI.md) - Sistema utenti
- [BACKUP_RECOVERY_GUIDE.md](BACKUP_RECOVERY_GUIDE.md) - Backup & recovery

### 🐛 Segnalare un Bug

Se trovi un bug:
1. Verifica se è già segnalato in [Issues](../../issues)
2. Se no, apri una nuova issue con:
   - **Titolo**: Descrizione breve
   - **Dettagli**: Passaggi per riprodurre, comportamento osservato, atteso
   - **Ambiente**: Python, Django, MySQLversion
   - **Log**: Stacktrace o screenshot

### 📧 Contatti Diretti

**Proprietario del Progetto:**
- Nome: Matteo Poggi
- Ruolo: Lead Developer
- GitHub: mpoggi79-cyber

**Note**: Per issues urgenti, preferisci GitHub Issues in modo che la comunità possa beneficiare della soluzione.

---

| Versione | Data | Cambiamenti |
|----------|------|-----------|
| **1.1** | 24 Dic 2025 | **Sistema Backup completo + 10 Tabelle Gestibili (icone specifiche)** |
| **1.0** | 30 Nov 2025 | Release iniziale produzione - tutti 22 template, 22 view, 11 modelli completi |

---

## ✅ CHECKLIST COMPLETAMENTO

- [x] Setup Django 5.2.8 completo
- [x] Schema database MySQL creato
- [x] 11 modelli ORM implementati
- [x] 22 Class-Based View costruite
- [x] 5 form CRUD creati
- [x] 22 template HTML progettati
- [x] Sistema autenticazione (login/logout)
- [x] Sistema permessi basato su ruoli (4 ruoli)
- [x] 77 movimenti dati test creati
- [x] Dashboard con statistiche
- [x] Report (giacenze, movimenti)
- [x] Interfaccia admin customizzata
- [x] Caratteristiche di sicurezza implementate
- [x] Documentazione README completa
- [x] Overview architettura (consolidato in README)
- [x] Guida gestione utenti
- [ ] Unit test (futuro)
- [ ] Ottimizzazione performance (futuro)
- [ ] REST API (futuro)

---

**Creato**: 30 Novembre 2025  
**Status**: ✅ Pronto per Produzione  
**Versione**: 1.1.0  
**Ultimo Aggiornamento**: 4 Maggio 2026 (Aggiunto: Sezione Contributi, Licenza, Supporto)

---

## 🔗 Link Utili

- 📚 **Documentazione Completa**: [AGENTS.md](AGENTS.md) - Patterns architettura per AI agents
- 🛠️ **Guida Amministratore**: [MANUALE_AMMINISTRATORE.md](MANUALE_AMMINISTRATORE.md) - Procedure admin avanzate
- 👥 **Gestione Utenti**: [GESTIONE_UTENTI.md](GESTIONE_UTENTI.md) - Sistema ruoli & autenticazione
- 💾 **Backup & Recovery**: [BACKUP_RECOVERY_GUIDE.md](BACKUP_RECOVERY_GUIDE.md) - 3 metodi ripristino

---

**Per domande, bug report, o contribuzioni**: Vedi sezione [💬 Supporto](#-supporto) sopra.

Per problemi avanzati, consultare [MANUALE_AMMINISTRATORE.md](MANUALE_AMMINISTRATORE.md#troubleshooting).
