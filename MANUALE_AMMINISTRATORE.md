# 👨‍💼 MANUALE AMMINISTRATORE - GESTIONE MAGAZZINO RICAMBI

**Versione**: 1.0 | **Data**: 30 Novembre 2025 | **Audience**: System Admin, IT Staff, Support

---

## 📋 INDICE

1. [Accesso e Setup Iniziale](#-accesso-e-setup-iniziale)
2. [Gestione Utenti](#-gestione-utenti)
3. [Gestione Ruoli e Permessi](#-gestione-ruoli-e-permessi)
4. [Database Management](#-database-management)
5. [Backup e Recovery](#-backup-e-recovery)
6. [Troubleshooting](#-troubleshooting)
7. [Sicurezza](#-sicurezza)
8. [Performance & Monitoring](#-performance--monitoring)
9. [Deployment](#-deployment)
10. [Comandi Amministrativi](#-comandi-amministrativi)

---

## 🚀 ACCESSO E SETUP INIZIALE

### Accesso Admin Panel

```bash
# URL
http://localhost:8000/admin/

# Credenziali default (dopo populate_db)
Username: admin
Password: admin
```

### First Time Setup

**STEP 1: Verifica connessione database**
```bash
python test_db_connection.py
```

Output atteso:
```
✅ Django setup completato con successo!
✅ Connessione al database MySQL riuscita!
   Database: GMR
   Host: 127.0.0.1
   User: root
```

**STEP 2: Applica migrazioni**
```bash
python manage.py migrate
```

**STEP 3: Carica dati test (OPZIONALE)**
```bash
python manage.py populate_db
```

**STEP 4: Verifica sistema**
```bash
python manage.py check
```

Output atteso:
```
System check identified no issues (0 silenced).
```

---

## 👥 GESTIONE UTENTI

### Creare Nuovo Utente

**Metodo 1: Via Admin Panel** (Consigliato)

1. Accedi a: http://localhost:8000/admin/
2. **Auth and authorization** → **Users** → **+ Add user**
3. Compila:
   - **Username**: `nuovo_utente`
   - **Password**: Genera automatico (clicca "Generate")
   - **Confirm password**: Copia da sopra
4. Clicca **Save and continue editing**
5. Scorri a **ProfiloUtente** e seleziona **Ruolo**: `GESTORE_MAGAZZINO`
6. Clicca **Save**

**Metodo 2: Via Comando (Django Shell)**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import ProfiloUtente, RuoloUtente

# Crea utente
user = User.objects.create_user(
    username='nuovo_utente',
    email='nuovo@example.com',
    password='Password123!',
    first_name='Nuovo',
    last_name='Utente'
)

# Assegna ruolo (signal auto-crea ProfiloUtente)
profilo = user.profilo
profilo.ruolo = RuoloUtente.GESTORE_MAGAZZINO
profilo.save()

print(f"✅ Utente {user.username} creato con ruolo {profilo.get_ruolo_display()}")
```

### Modificare Utente Esistente

**Via Admin Panel:**
1. **Auth and authorization** → **Users**
2. Clicca su username da modificare
3. Modifica campi desiderati
4. **Salva**

**Via Shell:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='nomeutente')
user.email = 'nuova@email.com'
user.first_name = 'Nuovo Nome'
user.save()

print(f"✅ Utente {user.username} aggiornato")
```

### Disattivare/Attivare Utente

**Via Admin Panel:**
1. **Users** → Seleziona utente
2. Deseleziona checkbox **Active** (per disattivare)
3. **Save**

**Via Shell:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='nomeutente')
user.is_active = False  # Disattiva
user.save()

# Oppure per attivare:
user.is_active = True
user.save()
```

### Resettare Password Utente

**Via Admin Panel:**
1. **Users** → Seleziona utente
2. Clicca **this form** link accanto a password
3. Genera nuova password
4. **Save**

**Via Shell:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='nomeutente')
user.set_password('NuovaPassword123!')
user.save()

print(f"✅ Password resettata per {user.username}")
```

### Eliminare Utente

⚠️ **ATTENZIONE**: Elimina TUTTI i dati associati (movimenti, log accessi)

**Via Admin Panel:**
1. **Users** → Seleziona utente
2. Clicca **Delete** (bottone rosso in basso)
3. Conferma

**Via Shell:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='nomeutente')
username = user.username
user.delete()

print(f"✅ Utente {username} eliminato permanentemente")
```

### Visualizzare Utenti Attivi

**Via Admin Panel:**
1. **Users** → Filter by **Active** checkbox

**Via Shell:**
```python
from django.contrib.auth.models import User
from accounts.models import RuoloUtente

# Tutti gli utenti attivi
active_users = User.objects.filter(is_active=True)

for user in active_users:
    profilo = user.profilo
    print(f"{user.username:15} | {profilo.get_ruolo_display():20} | {user.email}")
```

---

## 🔐 GESTIONE RUOLI E PERMESSI

### I 4 Ruoli Disponibili

| Ruolo | Modello | Permessi | Uso |
|-------|---------|----------|-----|
| **ADMIN** | `RuoloUtente.ADMIN` | ✅ CRUD tutto + Admin panel | Amministratore sistema |
| **GESTORE_MAGAZZINO** | `RuoloUtente.GESTORE_MAGAZZINO` | ✅ CRUD dati + Report | Responsabile magazzino |
| **OPERATORE** | `RuoloUtente.OPERATORE` | ✅ Crea movimenti solamente | Operatore magazzino |
| **VISUALIZZATORE** | `RuoloUtente.VISUALIZZATORE` | 🔍 Leggi solamente | Viewer reports |

### Assegnare Ruolo a Utente

**Via Admin Panel:**
1. **Users** → Seleziona utente
2. Scorri a **ProfiloUtente**
3. **Ruolo**: Seleziona dal dropdown
4. **Save**

**Via Shell:**
```python
from django.contrib.auth.models import User
from accounts.models import RuoloUtente

user = User.objects.get(username='nomeutente')
user.profilo.ruolo = RuoloUtente.OPERATORE
user.profilo.save()

print(f"✅ {user.username} → {user.profilo.get_ruolo_display()}")
```

### Verificare Permessi Utente

**Via Shell:**
```python
from django.contrib.auth.models import User

user = User.objects.get(username='nomeutente')
profilo = user.profilo

print(f"Utente: {user.username}")
print(f"Ruolo: {profilo.get_ruolo_display()}")
print(f"Può modificare dati: {profilo.può_modificare_dati()}")
print(f"Può visualizzare report: {profilo.può_visualizzare_report()}")
print(f"È ADMIN: {profilo.è_admin()}")
```

### Matrice Permessi Dettagliata

```python
# In accounts/models.py ProfiloUtente

può_modificare_dati():
  → ADMIN: True
  → GESTORE_MAGAZZINO: True
  → OPERATORE: False
  → VISUALIZZATORE: False

può_visualizzare_report():
  → ADMIN: True
  → GESTORE_MAGAZZINO: True
  → OPERATORE: False
  → VISUALIZZATORE: True

è_admin():
  → ADMIN: True
  → Tutti gli altri: False
```

---

## 🗄️ DATABASE MANAGEMENT

### Backup Database (MySQL)

**Backup Completo:**
```bash
# Windows PowerShell
mysqldump -u root GMR > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Linux/Mac
mysqldump -u root GMR > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Backup con tabelle specifiche:**
```bash
mysqldump -u root GMR categoria pezzoricambio giacenza > backup_articoli.sql
```

**Backup compresso:**
```bash
mysqldump -u root GMR | gzip > backup_$(Get-Date -Format 'yyyyMMdd').sql.gz
```

### Restore Database

⚠️ **ATTENZIONE**: Questo cancella TUTTI i dati attuali!

```bash
# Drop database e ricrea da backup
mysql -u root -e "DROP DATABASE GMR; CREATE DATABASE GMR;"
mysql -u root GMR < backup_20251130.sql
```

### Verificare Integrità Database

**Esegui Django system checks:**
```bash
python manage.py check
```

**Verifica dati nel database:**
```python
python manage.py shell

from magazzino.models import Categoria, PezzoRicambio, Giacenza
from django.contrib.auth.models import User

print(f"Utenti: {User.objects.count()}")
print(f"Categorie: {Categoria.objects.count()}")
print(f"Articoli: {PezzoRicambio.objects.count()}")
print(f"Giacenze: {Giacenza.objects.count()}")
```

### Export Dati da Django

**Export in JSON:**
```bash
python manage.py dumpdata > dati_complete.json

# Specifici modelli
python manage.py dumpdata magazzino > dati_magazzino.json
python manage.py dumpdata accounts > dati_accounts.json
```

**Export in CSV (custom command):**
```python
# magazzino/management/commands/export_csv.py (da creare se necessario)
# Attualmente non incluso - creare se richiesto per reportistica
```

### Import Dati in Django

```bash
python manage.py loaddata dati_complete.json
```

### Pulizia Database

**Elimina sessioni scadute:**
```bash
python manage.py clearsessions
```

**Elimina log accessi vecchi (> 90 giorni):**
```python
python manage.py shell

from accounts.models import LogAccesso
from datetime import datetime, timedelta

cutoff_date = datetime.now() - timedelta(days=90)
deleted_count, _ = LogAccesso.objects.filter(data_ora__lt=cutoff_date).delete()
print(f"✅ {deleted_count} log accessi vecchi eliminati")
```

---

## 💾 BACKUP E RECOVERY

### Strategia di Backup Consigliata

**Daily Backup (Automatizzato)**
```bash
# Aggiungi a cron job (Linux) o Task Scheduler (Windows)
mysqldump -u root GMR > /backups/gmr_daily_$(date +\%Y\%m\%d).sql
```

**Weekly Full Backup**
```bash
# Domenica alle 2:00 AM
mysqldump -u root --all-databases > /backups/gmr_full_$(date +\%Y\%m\%d).sql
```

**Monthly Archive**
```bash
# Primo del mese - archiviare in storage
tar -czf gmr_monthly_$(date +\%Y\%m).tar.gz /backups/gmr_full_*.sql
```

### Disaster Recovery Plan

**Scenario 1: Database Corrotto**
1. Stoppa applicazione: `CTRL+C` su terminale
2. Ripristina da ultimo backup: `mysql -u root GMR < backup_ultimo.sql`
3. Esegui migrazioni: `python manage.py migrate`
4. Riavvia server: `python manage.py runserver`

**Scenario 2: Dati Cancellati per Errore**
1. Identifica backup pre-cancellazione
2. Ripristina database da quel backup
3. Esporta dati specifici: `python manage.py dumpdata`
4. Importa selettivamente nel DB corrente

**Scenario 3: Hard Drive Failure**
1. Ripristina ambiente Python (venv)
2. Reinstalla dipendenze: `pip install -r requirements.txt`
3. Ricrea database da schema: `mysql -u root < database_creation.sql`
4. Carichi backup dati: `mysql -u root GMR < backup_completo.sql`
5. Migra schema Django: `python manage.py migrate`

---

## 🆘 TROUBLESHOOTING

### Problemi Comuni

#### Errore: "Database connection refused"
```
Causa: MySQL non avviato o credenziali sbagliate
Soluzione:
1. Avvia XAMPP → MySQL START
2. Verifica config/settings.py per credenziali
3. Testa: python test_db_connection.py
```

#### Errore: "Port 8000 already in use"
```
Causa: Altro processo usa porta 8000
Soluzione:
# Usa porta diversa
python manage.py runserver 8001

# O uccidi processo su porta 8000
netstat -ano | findstr :8000  # Trova PID
taskkill /PID <PID> /F        # Uccidi processo
```

#### Errore: "ModuleNotFoundError: No module named 'X'"
```
Causa: Dipendenza non installata
Soluzione:
pip install -r requirements.txt
# O installa specifica dipendenza:
pip install django==5.2.8
pip install mysqlclient==2.2.0
```

#### Errore: "PermissionDenied" su view CRUD
```
Causa: Utente non ha ruolo appropriato
Soluzione:
1. Verifica ruolo utente: Admin panel → Users → ProfiloUtente
2. Assegna ruolo ADMIN o GESTORE_MAGAZZINO
3. Utente deve fare logout/login per refresh permessi
```

#### Errore: "TemplateDoesNotExist"
```
Causa: Template file mancante in templates/
Soluzione:
# Verifica che tutti 22 template siano presenti
ls templates/magazzino/  # Deve mostrare 19 file
ls templates/accounts/   # Deve mostrare 3 file

# Se mancano, ricrea da backup o README.md template list
```

#### Errore: "Migrations conflitto"
```
Causa: Conflitto in migrazione Django
Soluzione:
python manage.py migrate --fake-initial  # Force
python manage.py migrate                 # Poi vero
```

### Debug Commands

**Verifica salute applicazione:**
```bash
python manage.py check
python manage.py check --deploy  # Per produzione
```

**Vedi state migrazioni:**
```bash
python manage.py showmigrations
python manage.py showmigrations accounts
python manage.py showmigrations magazzino
```

**Accedi shell Django per debug:**
```bash
python manage.py shell

# Esegui query di debug
from magazzino.models import PezzoRicambio
articoli = PezzoRicambio.objects.all()
print(f"Articoli nel DB: {articoli.count()}")

# Verifica permessi
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
print(f"Admin permission: {user.profilo.è_admin()}")
```

---

## 🔒 SICUREZZA

### Password Policy

**Requisiti Password:**
- Minimo 8 caratteri
- Lettere + numeri
- Almeno un carattere speciale consigliato
- Niente password comuni (1000+ blacklist)

**Password Hashing:**
- Algoritmo: Argon2 (più sicuro di PBKDF2)
- Salt: Generato automaticamente per ogni password
- Iterazioni: 4 (default di Argon2)

### Audit Logging

**Visualizza Log Accessi:**
```bash
# Via Admin Panel: Auth and authorization → Log accessi

# Via Shell:
from accounts.models import LogAccesso
import json

# Accessi falliti (ultimi 7 giorni)
from datetime import datetime, timedelta
last_week = datetime.now() - timedelta(days=7)
failed = LogAccesso.objects.filter(successo=False, data_ora__gte=last_week)

for log in failed:
    print(f"{log.user.username} | {log.data_ora} | IP: {log.indirizzo_ip} | FAILED")

# Accessi per utente
user_logs = LogAccesso.objects.filter(user__username='admin')
print(f"Admin login attempts: {user_logs.count()}")
```

### Session Security

**Configurazioni applicate (settings.py):**
```python
SESSION_COOKIE_HTTPONLY = True      # JS non può accedere cookie
SESSION_COOKIE_SAMESITE = 'Strict'  # Protezione CSRF aggiuntiva
SESSION_COOKIE_SECURE = False       # True in produzione (HTTPS)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

**Per PRODUZIONE, aggiungere:**
```python
DEBUG = False
ALLOWED_HOSTS = ['tuodominio.it']
SESSION_COOKIE_SECURE = True        # Richiede HTTPS
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000      # 1 anno
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Protezioni CSRF

**Attive su tutti i form HTML:**
```html
<form method="post">
    {% csrf_token %}  <!-- Incluso in base.html -->
    ...
</form>
```

### SQL Injection Prevention

**Django ORM previene automaticamente:**
```python
# SICURO - Django ORM escapa parametri
articoli = PezzoRicambio.objects.filter(codice_interno__contains=user_input)

# PERICOLOSO - Non fare mai!
# query = f"SELECT * FROM magazzino_pezzoricambio WHERE codice='{user_input}'"
```

---

## 📊 PERFORMANCE & MONITORING

### Monitorare Usage

**Dashboard attuale (in app):**
- Numero articoli: magazzino/dashboard
- Numero movimenti ultimi 30gg: report_movimenti
- Giacenze critiche: report_giacenze

**Via Shell - Statistiche Dettagliate:**
```python
from magazzino.models import MovimentoMagazzino, Giacenza, PezzoRicambio
from datetime import datetime, timedelta

# Movimenti ultimi 30 giorni
last_month = datetime.now() - timedelta(days=30)
movimenti_mese = MovimentoMagazzino.objects.filter(data__gte=last_month).count()
print(f"Movimenti ultimi 30gg: {movimenti_mese}")

# Articoli sotto soglia minima
sotto_soglia = Giacenza.objects.filter(
    quantita_disponibile__lt=models.F('giacenza_minima')
)
print(f"Articoli sotto soglia: {sotto_soglia.count()}")

# Top 5 articoli più movimentati
from django.db.models import Count
top_articoli = PezzoRicambio.objects.annotate(
    num_movimenti=Count('movimentomagazzino')
).order_by('-num_movimenti')[:5]

for articolo in top_articoli:
    print(f"{articolo.codice_interno:15} → {articolo.num_movimenti} movimenti")
```

### Ottimizzazioni

**Database Queries:**
```python
# Usa select_related per ForeignKey
articoli = PezzoRicambio.objects.select_related('categoria', 'fornitore').all()

# Usa prefetch_related per ManyToMany/reverse FK
articoli = PezzoRicambio.objects.prefetch_related('giacenza_set').all()

# Limita fields se non servono tutti
articoli = PezzoRicambio.objects.only('codice_interno', 'descrizione')
```

**Caching (Future - Not Implemented):**
```python
# Aggiungere in settings.py quando necessario
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# In view
from django.views.decorators.cache import cache_page
@cache_page(60 * 15)  # Cache 15 minuti
def report_giacenze(request):
    ...
```

---

## 🚢 DEPLOYMENT

### Pre-Deployment Checklist

```
☐ DEBUG = False in settings.py
☐ SECRET_KEY in environment variable
☐ ALLOWED_HOSTS configurato
☐ Database backup fatto
☐ Static files collectati: python manage.py collectstatic
☐ Migazioni applicate: python manage.py migrate
☐ Superuser creato
☐ Email settings configurate (se usato)
☐ HTTPS certificato installato
☐ Firewall configurato (port 80, 443)
```

### Production Server Setup (Gunicorn + Nginx)

**Installa Gunicorn:**
```bash
pip install gunicorn
```

**Crea startup script (deploy.sh):**
```bash
#!/bin/bash
cd /path/to/GestioneMagazzinoRicambi\ Goose
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
```

**Nginx configuration (esempio):**
```nginx
server {
    listen 80;
    server_name tuodominio.it www.tuodominio.it;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/static/;
    }
}
```

**SSL/HTTPS (Let's Encrypt):**
```bash
# Installa certbot
sudo apt-get install certbot python3-certbot-nginx

# Genera certificato
sudo certbot certonly --nginx -d tuodominio.it

# Auto-renew
sudo certbot renew --dry-run
```

### Database in Produzione

**Backup automatico (cron):**
```bash
# Crontab entry (every day at 2 AM)
0 2 * * * mysqldump -u root -p$MYSQL_PASS GMR > /backups/gmr_$(date +\%Y\%m\%d).sql
```

**Replication setup (per alta disponibilità):**
- Configura MySQL master-slave se richiesto
- Backup primario e secondario

---

## 🛠️ COMANDI AMMINISTRATIVI

### Django Management Commands

```bash
# UTENTI
python manage.py createsuperuser          # Crea admin
python manage.py changepassword username  # Cambia password
python manage.py migrate                  # Applica migrazioni
python manage.py makemigrations           # Crea migrazione

# DATABASE
python manage.py dumpdata > backup.json   # Esporta dati
python manage.py loaddata backup.json     # Importa dati
python manage.py sqlsequencereset app     # Reset sequence

# TESTING
python manage.py test magazzino           # Run tests
python manage.py test accounts

# UTILITY
python manage.py shell                    # Django shell
python manage.py check                    # Verifica errori
python manage.py check --deploy           # Verifica produzione
python manage.py showmigrations            # Mostra stato migrazioni
python manage.py clearsessions            # Elimina sessioni scadute
python manage.py collectstatic            # Copia file static

# CUSTOM
python manage.py populate_db              # Carica dati test
```

### MySQL Commands (Utility)

```bash
# Connessione
mysql -u root -p                          # Entra con password prompt
mysql -u root < schema.sql                # Carica schema

# Backup/Restore
mysqldump -u root GMR > backup.sql        # Backup
mysql -u root GMR < backup.sql            # Restore

# Management
SHOW DATABASES;                           # Lista DB
USE GMR;                                  # Seleziona DB
SHOW TABLES;                              # Lista tabelle
DESC tabella;                             # Struttura tabella
```

### Systemd Service File (Linux/Produzione)

**File: `/etc/systemd/system/gmr.service`**
```ini
[Unit]
Description=Gestione Magazzino Ricambi Goose
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/admin/GestioneMagazzinoRicambi\ Goose
Environment="PATH=/home/admin/GestioneMagazzinoRicambi\ Goose/venv/bin"
ExecStart=/home/admin/GestioneMagazzinoRicambi\ Goose/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/run/gmr.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Enablement:**
```bash
sudo systemctl enable gmr
sudo systemctl start gmr
sudo systemctl status gmr
```

---

## 📞 SUPPORTO E CONTATTI

**Per problemi contattare:**
- Email: admin@gestionemagazzino.it
- Interno: Ext. 123

**Documentazione online:**
- Django: https://docs.djangoproject.com
- MySQL: https://dev.mysql.com/doc/
- Bootstrap: https://getbootstrap.com/docs

---

**Documento creato**: 30 Novembre 2025  
**Ultimo update**: 30 Novembre 2025  
**Versione**: 1.0 - Production Ready
