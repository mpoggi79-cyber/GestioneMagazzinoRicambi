# 👥 Sistema di Gestione Utenti - Guida Completa

## 📋 Panoramica

È stato implementato un sistema completo di gestione utenti che permette agli amministratori di:
- ✅ Visualizzare tutti gli utenti del sistema
- ✅ Creare nuovi utenti con ruoli personalizzati
- ✅ Modificare dati e permessi degli utenti
- ✅ Disattivare utenti (senza eliminarli dal database)
- ✅ Resettare le password
- ✅ Monitorare gli accessi e le attività

## 🔐 Livelli di Accesso

### 1. **Amministratore (ADMIN)**
- Accesso completo a tutte le funzionalità
- Può creare, modificare ed eliminare utenti
- Può cambiare i ruoli degli utenti
- Può resettare le password

### 2. **Gestore Magazzino (GESTORE_MAGAZZINO)**
- Può visualizzare tutti gli utenti
- Può vedere i dettagli degli utenti
- NON può creare/modificare utenti

### 3. **Operatore (OPERATORE)**
- Può vedere solo il proprio profilo
- Può cambiare la propria password

### 4. **Visualizzatore (VISUALIZZATORE)**
- Può vedere solo il proprio profilo
- Può cambiare la propria password

## 📍 Come Accedere

### Menu Principale
1. Accedi come **Admin** o **Gestore Magazzino**
2. Vai alla **Sidebar** a sinistra
3. Nella sezione **"Amministrazione"** trovi:
   - 👥 **Gestione Utenti**

### URL Diretti
- Lista utenti: `http://localhost:8000/utenti/`
- Nuovo utente: `http://localhost:8000/utenti/create/`
- Dettaglio utente: `http://localhost:8000/utenti/<id>/`
- Modifica utente: `http://localhost:8000/utenti/<id>/update/`

## 🆕 Funzionalità Implementate

### 1. **Lista Utenti** (`/utenti/`)

**Caratteristiche:**
- Tabella con tutti gli utenti del sistema
- Badge colorati per ruoli e stati
- Statistiche rapide (totale, attivi, admin, inattivi)
- Filtri avanzati:
  - Ricerca per username, nome, email
  - Filtro per ruolo
  - Filtro per stato (attivo/inattivo)
- Paginazione (20 utenti per pagina)

**Azioni disponibili:**
- 👁️ **Visualizza dettagli**
- ✏️ **Modifica** (solo admin)
- 🔑 **Reset password** (solo admin)
- 🚫 **Disattiva** (solo admin, non se stessi)

### 2. **Creazione Nuovo Utente** (`/utenti/create/`)

**Solo ADMIN può creare utenti**

**Campi obbligatori:**
- Username (unico)
- Email (unica)

**Campi opzionali:**
- Nome
- Cognome
- Dipartimento

**Configurazioni:**
- Ruolo (ADMIN, GESTORE_MAGAZZINO, OPERATORE, VISUALIZZATORE)
- Stato attivo/inattivo
- Staff (accesso admin Django)

**Funzionalità speciali:**
- Genera automaticamente una **password temporanea** casuale
- La password viene mostrata SOLO alla creazione
- L'utente deve cambiarla al primo accesso

### 3. **Modifica Utente** (`/utenti/<id>/update/`)

**Solo ADMIN può modificare**

**Modificabile:**
- Dati anagrafici (nome, cognome, email)
- Ruolo
- Dipartimento
- Stato attivo/inattivo
- Permessi staff

**Azioni amministrative:**
- Reset password
- Disattivazione account

### 4. **Dettaglio Utente** (`/utenti/<id>/`)

**Visualizzazione completa:**

**Informazioni Utente:**
- Username, Nome, Cognome, Email
- Ruolo con badge colorato
- Dipartimento
- Stato (attivo/inattivo)
- Permessi (staff, superuser)

**Statistiche Accesso:**
- Data creazione account
- Ultimo accesso
- Numero totale accessi

**Ultimi Accessi:**
- Tabella con data/ora
- Tipo (login/logout)
- Indirizzo IP
- User agent (browser)

**Movimenti Recenti:**
- Ultimi 10 movimenti di magazzino effettuati dall'utente
- Data, tipo, articolo, quantità

### 5. **Reset Password** (Solo Admin)

**Come funziona:**
1. Admin clicca sul pulsante 🔑 nella lista utenti
2. Si apre un modal di conferma
3. Viene generata una **nuova password casuale** (12 caratteri)
4. La password viene mostrata all'admin (da comunicare all'utente)
5. L'utente deve cambiarla al prossimo login

**Sicurezza:**
- Non si può resettare la propria password (si usa "Cambia Password")
- Password complessa auto-generata
- Log dell'operazione

### 6. **Disattivazione Utente** (Solo Admin)

**Importante:**
- L'utente NON viene eliminato dal database
- Viene solo impostato `is_active = False`
- Tutti i dati storici sono preservati
- L'utente può essere riattivato in futuro

**Protezioni:**
- Non si può disattivare se stessi
- Richiede conferma

### 7. **Cambio Password** (Tutti gli utenti)

**URL:** `/accounts/change-password/`

**Caratteristiche:**
- Form intuitivo con 3 campi
- Toggle show/hide password
- **Indicatore di forza password in tempo reale**
- Verifica corrispondenza password
- Validazione client-side e server-side

**Requisiti password:**
- Minimo 10 caratteri
- Almeno 1 maiuscola
- Almeno 1 minuscola
- Almeno 1 numero
- Almeno 1 carattere speciale

**Sicurezza:**
- Verifica password attuale
- Mantiene la sessione attiva dopo il cambio
- Log dell'operazione

## 🎨 Design e UX

### Badge Colorati per Ruoli
- 🔴 **ADMIN** - Badge rosso
- 🟡 **GESTORE_MAGAZZINO** - Badge giallo/arancione
- 🔵 **OPERATORE** - Badge blu
- ⚫ **VISUALIZZATORE** - Badge grigio

### Badge Stati
- ✅ **Attivo** - Badge verde
- ❌ **Inattivo** - Badge rosso
- ⭐ **Staff** - Badge giallo
- 👑 **Superuser** - Badge rosso

### Statistiche Dashboard
Nella lista utenti, in alto:
- 👥 Totale Utenti
- ✅ Utenti Attivi
- 🛡️ Amministratori
- ❌ Utenti Inattivi

## 🔒 Sicurezza

### Protezioni Implementate
1. **Autenticazione richiesta** per tutte le operazioni
2. **Authorization** basata su ruoli
3. **CSRF Protection** su tutti i form
4. **Password Hashing** (Argon2)
5. **Log di tutte le operazioni** amministrative
6. **Validazione input** lato client e server
7. **Protezione auto-disattivazione** (non puoi disattivare te stesso)

### Log delle Operazioni
Tutte le operazioni critiche vengono loggate:
- ✅ Creazione nuovo utente
- ✏️ Modifica dati utente
- 🔑 Reset password
- 🚫 Disattivazione utente
- 🔐 Cambio password

I log sono disponibili in:
- File `logs/django.log`
- Django admin (`/admin/`)

## 📊 Database

### Modelli Coinvolti

**User** (Django built-in)
- username, email, first_name, last_name
- is_active, is_staff, is_superuser
- last_login, date_joined

**ProfiloUtente** (Custom)
- ruolo (ADMIN, GESTORE_MAGAZZINO, OPERATORE, VISUALIZZATORE)
- dipartimento
- numero_dipendente
- attivo
- date_created, date_modified

**LogAccesso** (Custom)
- user, data_ora, tipo_accesso (LOGIN/LOGOUT)
- ip_address, user_agent
- success, motivo_fallimento

## 🚀 Come Utilizzare

### Scenario 1: Creare un nuovo operatore

1. **Login come Admin**
2. Vai a **Gestione Utenti**
3. Clicca **"Nuovo Utente"**
4. Compila il form:
   - Username: `mario.rossi`
   - Email: `mario.rossi@azienda.it`
   - Nome: `Mario`
   - Cognome: `Rossi`
   - Ruolo: `Operatore`
   - Dipartimento: `Manutenzione`
   - ✅ Utente Attivo
5. Clicca **"Crea Utente"**
6. **COPIA la password temporanea** mostrata
7. Comunica username e password a Mario
8. Mario deve cambiarla al primo login

### Scenario 2: Disattivare un utente che ha lasciato l'azienda

1. **Login come Admin**
2. Vai a **Gestione Utenti**
3. Cerca l'utente nella lista
4. Clicca sul pulsante **🚫 Disattiva**
5. Conferma l'operazione
6. L'utente non potrà più accedere
7. I suoi dati storici rimangono nel sistema

### Scenario 3: Reset password dimenticata

1. **Login come Admin**
2. Vai a **Gestione Utenti**
3. Trova l'utente
4. Clicca sul pulsante **🔑** (Reset Password)
5. Conferma nel modal
6. **COPIA la nuova password** generata
7. Comunica la password all'utente via canale sicuro
8. L'utente deve cambiarla al prossimo login

### Scenario 4: Cambiare la propria password

1. **Login** con le tue credenziali
2. Clicca sul tuo nome in alto a destra
3. Seleziona **"Cambia Password"**
4. Inserisci:
   - Password attuale
   - Nuova password (segui i requisiti)
   - Conferma nuova password
5. Controlla l'indicatore di forza password
6. Clicca **"Cambia Password"**
7. Continuerai ad essere loggato con la nuova password

## 🛠️ File Modificati/Creati

### Views
- `magazzino/views.py` - Aggiunte 6 nuove views per gestione utenti
- `accounts/views.py` - Aggiunta ChangePasswordView

### URLs
- `magazzino/urls.py` - Aggiunti 6 nuovi URL patterns
- `accounts/urls.py` - Modificato URL cambio password

### Forms
- `accounts/forms.py` - Aggiunto UserManagementForm

### Templates
```
templates/
├── magazzino/
│   ├── utente_list.html          # Lista utenti con filtri
│   ├── utente_form.html          # Crea/Modifica utente
│   ├── utente_detail.html        # Dettaglio utente
│   └── utente_confirm_delete.html # Conferma disattivazione
└── accounts/
    └── change_password.html       # Cambio password migliorato
```

### Base Template
- `templates/base.html` - Aggiunto link "Gestione Utenti" nella sidebar

## 📝 Miglioramenti Futuri (Opzionali)

- [ ] Export lista utenti in CSV/Excel
- [ ] Import massivo utenti da file
- [ ] Gruppi utenti personalizzati
- [ ] Permessi granulari per singolo articolo/categoria
- [ ] Dashboard statistiche accessi
- [ ] Notifiche email per reset password
- [ ] 2FA (autenticazione a due fattori)
- [ ] Audit trail completo (chi ha fatto cosa e quando)
- [ ] Sessioni attive (vedi dove un utente è loggato)
- [ ] Blocco account dopo N tentativi falliti

## ❓ FAQ

**Q: Dove trovo la gestione utenti?**
A: Nel menu a sinistra, sezione "Amministrazione" → "Gestione Utenti" (solo per Admin e Gestore)

**Q: Come creo un nuovo utente?**
A: Solo gli Admin possono creare utenti. Vai in Gestione Utenti → "Nuovo Utente"

**Q: La password temporanea dove la trovo?**
A: Viene mostrata SOLO dopo la creazione dell'utente. Copiala subito!

**Q: Posso recuperare una password persa?**
A: Solo gli Admin possono fare "Reset Password" che genera una nuova password casuale.

**Q: Cosa succede se disattivo un utente?**
A: Il suo account viene disabilitato ma tutti i dati storici rimangono. Può essere riattivato.

**Q: Posso cambiare il mio ruolo?**
A: No, solo un Admin può modificare i ruoli degli utenti.

**Q: Perché non vedo il pulsante "Gestione Utenti"?**
A: Solo Admin e Gestore Magazzino possono accedere a quella sezione.

## 🎯 Conclusione

Il sistema di gestione utenti è ora completo e professionale! Permette una gestione sicura, tracciata e user-friendly degli utenti del sistema magazzino.

Per qualsiasi problema o domanda, controlla i log in `logs/django.log` o contatta lo sviluppatore.

---

**Ultima modifica:** 5 Dicembre 2025
**Versione:** 1.0
**Sviluppatore:** Sistema GMR - Gestione Magazzino Ricambi
