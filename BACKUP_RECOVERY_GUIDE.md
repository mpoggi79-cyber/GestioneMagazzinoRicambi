# 🆘 GUIDA RIPRISTINO DATABASE - PROCEDURE EMERGENZA

**Progetto**: Gestione Magazzino Ricambi Goose  
**Data**: 23 dicembre 2025  
**Versione**: 1.0

---

## 🎯 PROBLEMA RISOLTO

**Scenario critico**: Database corrotto → utenti Django inaccessibili → impossibile fare login → impossibile ripristinare dall'interfaccia web.

**Soluzione**: 3 metodi di ripristino con livelli di complessità crescente.

---

## 📊 METODI DI RIPRISTINO (dal più semplice al più complesso)

| Metodo | Quando Usare | Richiede Login | Difficoltà |
|--------|--------------|----------------|------------|
| **1. Interfaccia Web** | Database OK, interfaccia accessibile | ✅ SI | ⭐ Facile |
| **2. Management Command** | Database corrotto, Django funzionante | ❌ NO | ⭐⭐ Medio |
| **3. Script PowerShell** | Emergenza totale, Django non funziona | ❌ NO | ⭐⭐⭐ Avanzato |

---

## 🌐 METODO 1: RIPRISTINO DA INTERFACCIA WEB (Normale)

### Quando Usare
- ✅ Database funzionante
- ✅ Puoi fare login nell'applicazione
- ✅ Vuoi ripristinare una versione precedente

### Procedura

1. **Accedi all'applicazione**
   ```
   http://127.0.0.1:8000/
   Login con utente ADMIN o GESTORE_MAGAZZINO
   ```

2. **Vai alla gestione backup**
   ```
   Menu → Backup → Gestione Backup Database
   URL: http://127.0.0.1:8000/backup/
   ```

3. **Seleziona backup da ripristinare**
   - Clicca sul pulsante ⚠️ "Ripristina" del backup desiderato
   - Leggi attentamente gli avvisi nel modal
   - Digita `RESTORE` nel campo di conferma
   - Clicca "Ripristina Database"

4. **Riavvia il server Django**
   ```powershell
   # Ferma il server (CTRL+C nel terminale)
   # Riavvia
   python manage.py runserver
   ```

5. **Verifica funzionamento**
   - Ricarica la pagina di login
   - Accedi con le credenziali del backup ripristinato

---

## 💻 METODO 2: MANAGEMENT COMMAND (Emergenza Media)

### Quando Usare
- ❌ Database corrotto, non puoi fare login
- ✅ Python/Django ancora funzionanti
- ✅ Hai accesso al terminale

### Procedura

1. **Ferma il server Django** (se in esecuzione)
   ```powershell
   # CTRL+C nel terminale dove gira il server
   ```

2. **Lista backup disponibili**
   ```powershell
   python manage.py restore_backup --list
   ```

   Output esempio:
   ```
   📦 BACKUP DISPONIBILI:

   1. backup_gmr_20251223_120530.sql.gz
      Data: 23/12/2025 12:05:30 | Dimensione: 2.34 MB | Età: 0 giorni fa

   2. backup_gmr_20251222_183015.sql.gz
      Data: 22/12/2025 18:30:15 | Dimensione: 2.31 MB | Età: 1 giorni fa
   ```

3. **Ripristina backup specifico**
   ```powershell
   python manage.py restore_backup backup_gmr_20251223_120530.sql.gz
   ```

   **OPPURE** ripristina il più recente:
   ```powershell
   python manage.py restore_backup --latest
   ```

4. **Conferma operazione**
   ```
   ⚠️  ATTENZIONE - OPERAZIONE CRITICA!

   Stai per ripristinare:
     File: backup_gmr_20251223_120530.sql.gz

   ❌ TUTTI I DATI ATTUALI VERRANNO SOVRASCRITTI!
   ❌ OPERAZIONE IRREVERSIBILE!

   Digita "RESTORE" per confermare: RESTORE
   ```

5. **Attendi completamento**
   ```
   🔄 Ripristino in corso...
   ✅ Database ripristinato con successo
   💡 Riavvia il server Django per applicare le modifiche.
   ```

6. **Riavvia server**
   ```powershell
   python manage.py runserver
   ```

### Opzioni Avanzate

```powershell
# Salta conferma interattiva (PERICOLOSO! Solo per script automatici)
python manage.py restore_backup --latest --force
```

---

## 🚨 METODO 3: SCRIPT POWERSHELL STANDALONE (Emergenza Critica)

### Quando Usare
- ❌ Database completamente corrotto
- ❌ Django non si avvia
- ❌ Python dà errori critici
- ✅ Hai solo accesso a PowerShell e MySQL

### Prerequisiti
- ✅ XAMPP MySQL deve essere in esecuzione
- ✅ File backup nella cartella `backups/`

### Procedura

1. **Apri PowerShell come Amministratore**
   ```powershell
   # Click destro su PowerShell → Esegui come amministratore
   ```

2. **Vai alla cartella del progetto**
   ```powershell
   cd "D:\SVILUPPO MATTEO\Progetti\GestioneMagazzinoRicambi Goose"
   ```

3. **Lista backup disponibili**
   ```powershell
   .\restore_db_emergency.ps1 -ListBackups
   ```

   Output esempio:
   ```
   =====================================
     RIPRISTINO DATABASE EMERGENZA
   =====================================

   [BACKUP DISPONIBILI]

   1. backup_gmr_20251223_120530.sql.gz
      Data: 23/12/2025 12:05:30
      Dimensione: 2.34 MB | Età: 0 giorni fa

   2. backup_gmr_20251222_183015.sql.gz
      Data: 22/12/2025 18:30:15
      Dimensione: 2.31 MB | Età: 1 giorni fa
   ```

4. **Ripristina backup specifico**
   ```powershell
   .\restore_db_emergency.ps1 -BackupFile backup_gmr_20251223_120530.sql.gz
   ```

   **OPPURE** ripristina il più recente:
   ```powershell
   .\restore_db_emergency.ps1 -Latest
   ```

5. **Conferma operazione**
   ```
   ========================================
     ATTENZIONE - OPERAZIONE CRITICA!
   ========================================

   Stai per ripristinare:
     Database: gmr
     File    : backup_gmr_20251223_120530.sql.gz
     Data    : 23/12/2025 12:05:30

   [WARNING] TUTTI I DATI ATTUALI VERRANNO SOVRASCRITTI!
   [WARNING] OPERAZIONE IRREVERSIBILE!

   Digita 'RESTORE' per confermare: RESTORE
   ```

6. **Attendi completamento**
   ```
   [RESTORE] Avvio ripristino...

   [1/4] Decompressione backup...
         [OK] File decompresso: C:\Temp\xyz123.sql

   [2/4] Verifica connessione MySQL...
         [OK] MySQL attivo

   [3/4] Importazione dati in database 'gmr'...
         (Questo potrebbe richiedere alcuni minuti...)
         [OK] Dati importati con successo

   [4/4] Pulizia file temporanei...
         [OK] File temporaneo rimosso

   ========================================
     RIPRISTINO COMPLETATO CON SUCCESSO!
   ========================================

   [NEXT STEPS]
   1. Riavvia il server Django se è in esecuzione
   2. Verifica accesso all'applicazione web
   3. Controlla i log per eventuali errori
   ```

7. **Riavvia Django**
   ```powershell
   # In un nuovo terminale PowerShell
   cd "D:\SVILUPPO MATTEO\Progetti\GestioneMagazzinoRicambi Goose"
   & "venv\Scripts\Activate.ps1"
   python manage.py runserver
   ```

### Opzioni Script PowerShell

```powershell
# Salta conferma (PERICOLOSO! Solo per automazione)
.\restore_db_emergency.ps1 -Latest -Force

# Ripristina file specifico senza conferma
.\restore_db_emergency.ps1 -BackupFile <filename> -Force
```

---

## 🛠️ PERSONALIZZAZIONE SCRIPT POWERSHELL

Se MySQL non è in `C:\xampp\mysql\bin`, modifica lo script:

```powershell
# Apri: restore_db_emergency.ps1
# Riga 18-19: Modifica questi percorsi

$MYSQL_BIN = "C:\xampp\mysql\bin"  # ← Cambia qui se MySQL è altrove
$DB_NAME = "gmr"                   # ← Nome database (da settings.py)
```

---

## ❓ TROUBLESHOOTING

### Errore: "MySQL non trovato"
```powershell
[ERROR] MySQL non trovato in: C:\xampp\mysql\bin
```
**Soluzione**: Modifica `$MYSQL_BIN` nello script `restore_db_emergency.ps1`

### Errore: "MySQL non risponde"
```powershell
MySQL non risponde. Verifica che XAMPP sia avviato.
```
**Soluzione**: 
1. Apri XAMPP Control Panel
2. Clicca "Start" su MySQL
3. Riprova il ripristino

### Errore: "File non trovato"
```powershell
[ERROR] File non trovato: backup_xyz.sql.gz
```
**Soluzione**: 
1. Verifica che il file sia in `backups/`
2. Usa `-ListBackups` per vedere i file disponibili
3. Copia/incolla il nome esatto del file

### Errore: "Permission denied"
```powershell
Remove-Item: Access to the path is denied
```
**Soluzione**: Esegui PowerShell come **Amministratore**

---

## 📋 CHECKLIST POST-RIPRISTINO

Dopo ogni ripristino, verifica:

- [ ] Server Django si avvia senza errori
- [ ] Puoi accedere con utente admin/admin
- [ ] Dashboard mostra dati corretti
- [ ] Articoli e giacenze visibili
- [ ] Movimenti magazzino presenti
- [ ] Immagini articoli caricate

---

## 🔒 SICUREZZA BACKUP

### Cosa Include il Backup
✅ Tutte le tabelle database  
✅ Struttura completa (CREATE TABLE)  
✅ Tutti i dati (INSERT)  
✅ Stored procedures e trigger  
✅ Eventi schedulati  
✅ Charset e collation corretti  

### Cosa NON Include
❌ File media (immagini articoli in `media/articoli/`)  
❌ File di log (`logs/`)  
❌ Impostazioni Django (`config/settings.py`)  
❌ Virtual environment (`venv/`)  

**IMPORTANTE**: Per backup completo, copia anche manualmente:
- `media/articoli/` → Immagini articoli
- `logs/` → Log applicazione (opzionale)

---

## 📅 BEST PRACTICES

### Frequenza Backup Consigliata
- **Automatico giornaliero**: Ore 23:00 (quando nessuno lavora)
- **Manuale pre-operazioni critiche**: Prima di migration, aggiornamenti, modifiche strutturali
- **Retention**: 30 giorni (modifica in Impostazioni)

### Test Ripristino
Testa il ripristino **almeno 1 volta al mese** per verificare che i backup siano funzionanti:
1. Crea backup test
2. Ripristinalo in ambiente di sviluppo
3. Verifica integrità dati

### Storage Backup
- **Locale**: `backups/` (incluso nel progetto)
- **Remoto consigliato**: Google Drive, Dropbox, NAS aziendale
- **Rotazione**: Elimina backup > 30 giorni automaticamente

---

## 📞 CONTATTI EMERGENZA

In caso di problemi critici non risolvibili:
1. Verifica log in `logs/django.log`
2. Controlla log MySQL in `C:\xampp\mysql\data\mysql_error.log`
3. Contatta supporto tecnico

---

**Fine Guida** - Aggiornato: 23/12/2025 🚀
