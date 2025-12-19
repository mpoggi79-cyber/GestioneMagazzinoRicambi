# 🏭 Gestione Magazzino Ricambi Goose

**Status**: ✅ v1.0 PRODUCTION READY | Django 5.2.8 | MySQL 10.4 | Bootstrap 5.3  
**Completamento**: 22 view | 11 modelli | 22 template | 4 ruoli utente | 77 movimenti test

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
# Accedere: http://localhost:8000 → admin/admin
```

**Per primo avvio più dettagliato**, vedi sezione "Setup Passo-Passo" sotto.

---

## 🚀 FASTEST START (3 COMMANDS)

```bash
# 1. Create database (MySQL must run: XAMPP → MySQL START)
mysql -u root < database_creation.sql

# 2. Setup Django
python manage.py migrate
python manage.py populate_db

# 3. Run server
python manage.py runserver
# Then: http://localhost:8000 → admin/admin
```

---

## ✅ STATO APPLICAZIONE

| Componente | Stato | Dettagli |
|-----------|-------|---------|
| **Backend Django 5.2.8** | ✅ Completo | 22 CBV, 11 modelli ORM, 5 form |
| **Database MySQL 10.4** | ✅ Operativo | 77 movimenti test, 19 articoli, 8 categorie, 5 fornitori |
| **Frontend Bootstrap 5.3** | ✅ Completo | 22 template HTML responsive, Font Awesome 6.4 |
| **Autenticazione** | ✅ Funzionante | Login/logout, 4 ruoli, ProfiloUtente, LogAccesso |
| **Permessi** | ✅ Implementati | CanEditMixin, CanViewMixin, controlli basati su ruolo |
| **CRUD Operazioni** | ✅ Testate | Categoria, PezzoRicambio, Fornitore, MovimentoMagazzino, Giacenza, Inventario |
| **Report & Statistiche** | ✅ Funzionanti | Dashboard, report_giacenze, report_movimenti |
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

### 4️⃣ Caricare Dati di Test (OPZIONALE ma CONSIGLIATO)

```bash
python manage.py populate_db
```

Crea:
- **8 categorie** (Motori, Trasmissioni, Componenti Meccanici, Idraulica, Pneumatica, Controllo, Connettori, Varia)
- **7 unità di misura** (pz, kg, l, h, m, mm, W)
- **5 fornitori** (MotorTech, HydraulicSys, ElectroComponents, FastSupply, QualityParts)
- **19 articoli** con giacenze associate
- **77 movimenti** ultimi 30 giorni (CARICO/SCARICO/RETTIFICA/RESO)
- **4 utenti test**:
  - `admin` / `admin` (ADMIN - Accesso completo)
  - `gestore` / `gestore` (GESTORE_MAGAZZINO - CRUD + Report)
  - `operatore` / `operatore` (OPERATORE - Solo creazione movimenti)
  - `visualizzatore` / `visualizzatore` (VISUALIZZATORE - Solo lettura)

### 5️⃣ Avviare Server di Sviluppo

```bash
python manage.py runserver
```

Accedere: **http://localhost:8000** con credenziali `admin` / `admin`

---

## 📊 MODELLI DATI (11 TOTALI)

### Dominio Magazzino (9 modelli)

```
Categoria
├── nome_categoria: CharField(max_length=100, unique=True)
├── descrizione: TextField(blank=True)
└── ordine: PositiveIntegerField(default=0)

UnitaMisura
├── codice: CharField(max_length=10, unique=True)
└── descrizione: CharField(max_length=100)

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
├── codice_alternativo: CharField(max_length=50, blank=True)
├── descrizione: TextField()
├── categoria: ForeignKey(Categoria)
├── unita_misura: ForeignKey(UnitaMisura)
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

/movimenti/                    → MovimentoListView
/movimenti/create/             → MovimentoCreateView
/movimenti/<id>/               → MovimentoDetailView

/giacenze/                     → GiacenzaListView
/giacenze/<id>/                → GiacenzaDetailView

/report/giacenze/              → ReportGiacenzeView
/report/movimenti/             → ReportMovimentiView
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
└── magazzino/
    ├── dashboard.html (dashboard statistiche)
    ├── categoria_list.html, categoria_form.html, categoria_confirm_delete.html (3)
    ├── pezzoricambio_list.html, pezzoricambio_form.html, pezzoricambio_detail.html, pezzoricambio_confirm_delete.html (4)
    ├── fornitore_list.html, fornitore_form.html, fornitore_detail.html, fornitore_confirm_delete.html (4)
    ├── movimento_list.html, movimento_form.html, movimento_detail.html (3)
    ├── giacenza_list.html, giacenza_detail.html (2)
    ├── report_giacenze.html (report giacenze)
    └── report_movimenti.html (report movimenti 30gg)
```

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
| "TemplateDoesNotExist" | File template mancante | Verificare che tutti i 22 template esistano in templates/ |
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
│   ├── models.py              # 9 modelli magazzino
│   ├── views.py               # 22 view CRUD
│   ├── forms.py               # 5 form CRUD
│   ├── urls.py                # Rotte /magazzino/
│   ├── admin.py               # Interfaccia admin
│   ├── management/
│   │   └── commands/
│   │       └── populate_db.py # Management command dati test
│   └── migrations/            # Migrazioni database
│
├── templates/                 # Template HTML (22 file)
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
├── README.md                  # Questo file
├── GESTIONE_UTENTI.md         # Guida gestione utenti
├── MANUALE_AMMINISTRATORE.md  # Procedure amministratore
├── .github/copilot-instructions.md  # Guida AI agents
├── database_creation.sql      # Schema MySQL
├── test_db_connection.py      # Script test connessione
├── check_system.py            # Script controllo sistema
├── requirements.txt           # Dipendenze Python
├── manage.py                  # Django CLI
└── init_database.py           # Legacy - usare manage.py populate_db
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

## 📚 STRUTTURA DOCUMENTAZIONE

| Documento | Scopo | Audience |
|-----------|-------|----------|
| **README.md** (questo file) | Referimento tecnico completo con setup | Developer, IT Staff |
| **GESTIONE_UTENTI.md** | Guida completa al sistema utenti | Admin, Support Staff |
| **MANUALE_AMMINISTRATORE.md** | Procedure amministratore avanzate | System Admin |
| **.github/copilot-instructions.md** | Guida per AI agents nello sviluppo | AI/Copilot |

**Nota**: START_HERE.md, QUICK_START.md, PROJECT_STATUS.md sono stati consolidati in questo README.

---

## ✨ CRONOLOGIA VERSIONI

| Versione | Data | Cambiamenti |
|----------|------|-----------|
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
**Versione**: 1.0.0  
**Ultimo Aggiornamento**: 14 Dicembre 2025

Per domande o problemi, consultare [MANUALE_AMMINISTRATORE.md](MANUALE_AMMINISTRATORE.md) sezione "Troubleshooting".
