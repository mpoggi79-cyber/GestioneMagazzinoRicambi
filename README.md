# 🏭 Gestione Magazzino Ricambi Goose By Matteo

**Status**: ✅ v1.1 CLIENTI MODULE - FASE 1 + BACKUP SYSTEM | Django 5.2.8 | MySQL 10.4 | Bootstrap 5.3  
**Completamento**: 47 view totali | 16 modelli | 40 template | 4 ruoli | **+10 tabelle gestibili** | **Sistema Backup**

---

## 📑 Indice Contenuti

1. [Avvio Rapido](#-avvio-rapido-3-comandi)
2. [Stato Applicazione](#-stato-applicazione)
3. [Setup Passo-Passo](#-setup-passo-passo)
4. [Modelli Dati](#-modelli-dati-16-totali)
5. [View & URL](#-view--url-22-class-based-view)
6. [Permessi](#-permessi-basati-su-ruolo)
7. [Template](#-template-22-totali)
8. [Gestione Tabelle](#%EF%B8%8F-sistema-gestione-tabelle-clienti)
9. [Sicurezza](#-implementazione-sicurezza)
10. [Dati Test](#-dati-di-test-populate_dbpy)
11. [Comandi Utili](#%EF%B8%8F-comandi-utili)
12. [Troubleshooting](#-troubleshooting)
13. [Struttura Progetto](#-struttura-progetto)
14. [Backup & Recovery](#-backup--recovery)
15. [Come Contribuire](#-come-contribuire)
16. [Licenza](#-licenza)
17. [Supporto](#-supporto)

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
| **Frontend Bootstrap 5.3** | ✅ Completo | 40 template HTML responsive, Font Awesome 6.4 |
| **Modulo Clienti - Fase 1** | ✅ **COMPLETATA** | **6 tabelle gestibili: tbAppellativo (7), tbCategoriaIVA (7), tbCategorieTariffe (21), tbTipoPagamento (23), tbModalitaPagamento (8), tbContatti (0)** |
| **Sistema Backup Database** | ✅ **COMPLETATO** | **3 metodi ripristino: Web, Management Command, PowerShell emergenza** |
| **Sistema Gestione Tabelle** | ✅ **IMPLEMENTATO** | **Interfaccia web per visualizzare/modificare tabelle clienti** |
| **Autenticazione** | ✅ Funzionante | Login/logout, 4 ruoli, ProfiloUtente, LogAccesso |
| **Permessi** | ✅ Implementati | CanEditMixin, CanViewMixin, controlli basati su ruolo |
| **CRUD Operazioni** | ✅ Testate | Categoria, PezzoRicambio, Fornitore, MovimentoMagazzino, Giacenza, Inventario |
| **Report & Statistiche** | ✅ Funzionanti | Dashboard, report_giacenze, report_movimenti |
| **Sistema Backup Database** | ✅ **3 Metodi Ripristino** | **Web UI, Management Command, Script PowerShell emergenza** |
| **Sistema Gestione Tabelle** | ✅ **Interfaccia Web** | **Visualizzazione/modifica tabelle clienti (ADMIN/GESTORE)** |
| **Sicurezza** | ✅ Implementata | Protezione CSRF, hashing Argon2, session security |
| **Deploy** | ✅ Pronto | Pronto per produzione con Gunicorn + Nginx |

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

**URL**: `/gestione-tabelle/` (solo ADMIN/GESTORE)  
**Funzionalità**: Interfaccia web per visualizzare e modificare tabelle clienti senza SQL

#### 🗂️ Tabelle Gestibili (10 totali)

| Tabella | Descrizione | Record | Icona | Filtro Stato |
|---------|-------------|--------|-------|-------------|
| `tbappellativo` | Appellativi | 7 | 👤 | ❌ |
| `tbunitamisura` | Unità di Misura | 14 | ⚖️ | ✅ |
| `tbtipopagamento` | Tipo Pagamento | 23 | 🏪 | ❌ |
| `tbprestazioni` | Prestazioni | 0 | 🔧 | ✅ |
| `tbcategorietariffe` | Categorie Tariffe | 21 | 🏷️ | ✅ |
| `tbcategoriaiva` | Categoria IVA | 7 | 🧮 | ❌ |
| `tbcontatti` | Contatti | 0 | 📇 | ❌ |
| `modelli_macchine_scm` | Modelli Macchine SCM | 0 | ⚙️ | ✅ |
| `matricole_macchine_scm` | Matricole Macchine SCM | 0 | 📊 | ✅ |
| `tbmodalitapagamento` | Modalità Pagamento | 8 | 💳 | ❌ |

**Legenda**:
- **Record**: Numero di record attualmente nel database
- **Icona**: Icona visualizzata nella card della tabella
- **Filtro Stato**: ✅ = disponibile filtro show_inactive, ❌ = tabella semplice

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

## 🔒 IMPLEMENTAZIONE SICUREZZA

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

| Problema | Causa | Soluzione |
|----------|-------|----------|
| "Connessione database rifiutata" | MySQL non in esecuzione | Avviare XAMPP → START su MySQL |
| "Porta 8000 già in uso" | Un altro processo usa la porta 8000 | Eseguire su porta diversa: `manage.py runserver 8001` |
| "ModuleNotFoundError" | Dipendenza mancante | `pip install -r requirements.txt` |
| "TemplateDoesNotExist" | File template mancante | Verificare che i template esistano in templates/ |
| "Permission Denied su CRUD" | Ruolo utente non permette operazione | Controllare ProfiloUtente.ruolo nel panel admin |
| "Login fallisce con password corretta" | Dati test non caricati | Eseguire `python manage.py populate_db` |

---

## 📁 STRUTTURA PROGETTO

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
| **.github/copilot-instructions.md** | Guida per AI agents nello sviluppo | AI/Copilot |

**Nota**: START_HERE.md, QUICK_START.md, PROJECT_STATUS.md sono stati consolidati in questo README.

---

## 🤝 Come Contribuire

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
