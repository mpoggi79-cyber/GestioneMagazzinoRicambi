# 📊 ANALISI TABELLE ESISTENTI DATABASE

**Data Analisi**: 20 dicembre 2025  
**Database**: MySQL 10.4 via PyMySQL  
**Fonte**: Export da modelli Django esistenti  

---

## 📋 RIEPILOGO TABELLE ESPORTATE

| # | Nome Tabella | Righe | Descrizione |
|---|--------------|-------|-------------|
| 1 | categorie | 24 | Categorie gerarchiche per classificazione ricambi |
| 2 | **tbunitamisura** | **14** | **✅ Unità di misura per articoli (SOSTITUISCE unita_misura)** |
| 3 | fornitori | 7 | Anagrafica fornitori |
| 4 | pezzi_ricambio | N/D | Articoli/ricambi con codici, prezzi, giacenze |
| 5 | giacenze | N/D | Livelli di stock per ogni articolo |
| 6 | movimenti_magazzino | N/D | Storico movimenti (carico/scarico/rettifica) |
| 7 | modelli_macchine_scm | N/D | Modelli macchine SCM |
| 8 | matricole_macchine_scm | N/D | Matricole specifiche macchine |

**⚠️ IMPORTANTE**: La tabella `unita_misura` è stata ELIMINATA e sostituita definitivamente da `tbunitamisura`.

---

## 1️⃣ categorie

**Descrizione**: Classificazione gerarchica ricambi con supporto sottocategorie  
**Nome Tabella**: `categorie`  
**Righe dati**: 24

### 📋 Struttura Colonne

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| id_categoria | INT | Numerico | **PK** | ID univoco categoria |
| nome_categoria | VARCHAR(50) | Testo | - | Nome categoria |
| descrizione | VARCHAR(200) | Testo | NULL | Descrizione tecnica |
| id_categoria_padre | INT | Numerico | **FK** | → categorie (self-referencing per gerarchia) |
| livello | INT | Numerico | - | 0=Macro, 1=Categoria, 2=Sottocategoria |
| ordine | INT | Numerico | - | Ordine visualizzazione |
| stato_attivo | BOOLEAN | VERO/FALSO | - | Categoria attiva |
| creato_il | DATETIME | Data/Ora | - | Timestamp creazione |
| modificato_il | DATETIME | Data/Ora | - | Timestamp ultima modifica |

### 📊 Esempi Dati

**Macrocategorie (livello 0)**:
- ID 16: ACCESSORI PIANI MACCHINE
- ID 15: AUTO
- ID 12: RICAMBI MECCANICI
- ID 13: RICAMBI ELETTRICI
- ID 14: RICAMBI PNEUMATICI
- ID 17: Pompe Del Vuoto
- ID 29: Macchine al Capanno

**Categorie/Sottocategorie (livello 1)**:
- ID 18: Backer (padre: 17 - Pompe Del Vuoto)
- ID 19: Busch (padre: 17 - Pompe Del Vuoto)
- ID 42: Aspirazione (padre: 12 - RICAMBI MECCANICI)
- ID 38: Cuffie (padre: 12 - RICAMBI MECCANICI)
- ID 6: Climatizzazione (padre: 15 - AUTO)

---

## 2️⃣ tbunitamisura ✅ TABELLA ATTIVA

**Descrizione**: Unità di misura per articoli magazzino e prestazioni  
**Nome Tabella**: `tbunitamisura` (db_table='tbUnitaMisura')  
**Modello Django**: `TbUnitaMisura`  
**File CSV**: `tbUnitaMisura.csv`  
**Righe dati**: 14 (include unità per prestazioni: Ore, gg, km)

### 📋 Struttura Colonne

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idUnitaMisura | INT | Numerico | **PK** | ID univoco unità (db_column='idUnitaMisura') |
| Denominazione | VARCHAR(50) | Testo | - | Codice breve (es: Pz, Kg, Ore, gg) |
| DenominazioneStampa | VARCHAR(100) | Testo | NULL | Descrizione estesa per stampa |
| stato_attivo | BOOLEAN | VERO/FALSO | - | Unità attiva (sempre True) |
| creato_il | DATETIME | Data/Ora | auto_now_add | Timestamp creazione |
| modificato_il | DATETIME | Data/Ora | auto_now | Timestamp ultima modifica |

### 📊 Dati Completi (14 unità)

| ID | Denominazione | DenominazioneStampa | Uso |
|----|---------------|---------------------|-----|
| 1  | Num.    | Num. | Prestazioni numeriche |
| 2  | km      | per Chilometro - per kilometer | Viaggi/distanze |
| 3  | gg      | per Giornata - per Day | Prestazioni giornaliere |
| 4  | Ore     | per Ora o frazione | **Manodopera oraria** |
| 5  | Kg      | Kg | Articoli a peso |
| 7  | Day     | Daily | Giorni (inglese) |
| 8  | Hour    | Hour or fraction | Ore (inglese) |
| 9  | Pz      | Pezzi | **Articoli contati** (da vecchio ID 1) |
| 10 | Lt      | Litri | Liquidi (da vecchio ID 2 "L") |
| 11 | Mt      | Metri | Lunghezze (da vecchio ID 4) |
| 12 | Set     | Set oppure Kit | Kit/Set (da vecchio ID 5) |
| 13 | Coppia  | Coppia | Coppie (da vecchio ID 6) |
| 14 | Conf    | Confezione | Confezioni (da vecchio ID 7) |

### 🔗 Foreign Key

**Referenziata da**:
- `pezzi_ricambio.idUnitaMisura` → Campo `unita_misura` (model field)
- `tbPrestazioni.idUnitaMisura` → FK futura per prestazioni/servizi

### ✅ Migrazione Completata

**Migration 0013**: Mappatura dati vecchi ID → nuovi ID  
**Migration 0014**: Rimozione campo transitorio `id_tb_unita_misura`, eliminazione modello `UnitaMisura`  
**Status**: ✅ ATTIVA - Unica tabella unità di misura del sistema

**⚠️ TABELLA ELIMINATA**: `unita_misura` (7 righe) rimossa dal database il 20/12/2025

---

## ~~2️⃣ unita_misura~~ ❌ TABELLA ELIMINATA

## ~~2️⃣ unita_misura~~ ❌ TABELLA ELIMINATA

**Status**: ❌ **ELIMINATA DAL DATABASE il 20/12/2025**  
**Sostituita da**: `tbunitamisura` (vedi sopra)  
**Motivo eliminazione**: Sostituzione con tabella estesa per supportare unità prestazioni (Ore, gg, km)

~~**Descrizione**: Unità di misura per articoli magazzino~~  
~~**Nome Tabella**: `unita_misura`~~  
~~**Righe dati**: 7~~

### ❌ Vecchia Struttura (ELIMINATA)

| ID | Codice | Descrizione | → Nuovo ID in tbunitamisura |
|----|--------|-------------|------------------------------|
| 1  | Pz     | Pezzi | → **ID 9** |
| 2  | L      | Litri | → **ID 10** (Lt) |
| 3  | Kg     | Chilogrammi | → **ID 5** |
| 4  | Mt     | Metri | → **ID 11** |
| 5  | Set    | Set | → **ID 12** |
| 6  | Coppia | Coppia | → **ID 13** |
| 7  | Conf   | Confezione | → **ID 14** |

**Mapping applicato**: Tutti i record in `pezzi_ricambio` aggiornati automaticamente dalla migration 0013.

---

## 3️⃣ fornitori

**Descrizione**: Anagrafica fornitori con dati fiscali e contatti  
**Nome Tabella**: `fornitori`  
**Righe dati**: 7

### 📋 Struttura Colonne

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| id_fornitore | INT | Numerico | **PK** | ID univoco fornitore |
| ragione_sociale | VARCHAR(200) | Testo | - | Ragione sociale |
| indirizzo | VARCHAR(200) | Testo | NULL | Indirizzo completo |
| citta | VARCHAR(100) | Testo | NULL | Città |
| cap | VARCHAR(10) | Testo | NULL | Codice postale |
| provincia | VARCHAR(2) | Testo | NULL | Sigla provincia |
| telefono | VARCHAR(20) | Testo | NULL | Numero telefono |
| email | VARCHAR(100) | Testo | NULL | Email |
| partita_iva | VARCHAR(20) | Testo | NULL | P.IVA |
| tempo_medio_consegna_giorni | INT | Numerico | - | Tempo consegna medio |
| note | TEXT | Testo lungo | NULL | Note fornitore |
| stato_attivo | BOOLEAN | VERO/FALSO | - | Fornitore attivo |
| creato_il | DATETIME | Data/Ora | - | Timestamp creazione |
| modificato_il | DATETIME | Data/Ora | - | Timestamp ultima modifica |

### 📊 Esempi Dati

| ID | Ragione Sociale | Città | Telefono | Attivo |
|----|----------------|-------|----------|--------|
| 1 | BOSCH Italia S.p.A. | Milano | +39 02 1234 5678 | VERO |
| 4 | BREMBO S.p.A. | Bergamo | +39 035 215 6111 | FALSO |
| 6 | Hiteco | Villa Verucchio | 0541746111 | VERO |
| 999 | Non Specificato | - | - | VERO |
| 1000 | Pneumaticenter | Santarcangelo | +3977888888 | VERO |

**⚠️ FORNITORE SPECIALE**: ID 999 "Non Specificato" è un fornitore di fallback - NON ELIMINARE.

---

## 4️⃣ pezzi_ricambio

**Descrizione**: Articoli/ricambi con codici, prezzi, giacenze  
**Nome Tabella**: `pezzi_ricambio`  
**Righe dati**: Da verificare

### 📋 Struttura Colonne (Schema)

| Colonna | Tipo | FK | Descrizione |
|---------|------|-----|-------------|
| id_pezzo | INT | **PK** | ID univoco articolo |
| codice_articolo | VARCHAR | - | Codice articolo |
| codice_scm | VARCHAR | NULL | Codice SCM |
| descrizione | VARCHAR | - | Descrizione articolo |
| id_categoria | INT | **FK** | → categorie |
| id_unita_misura | INT | **FK** | → unita_misura |
| id_fornitore | INT | **FK** | → fornitori |
| prezzo_acquisto | DECIMAL | - | Prezzo di acquisto |
| prezzo_vendita | DECIMAL | - | Prezzo di vendita |
| immagine | VARCHAR | NULL | Path immagine principale |
| thumbnail | VARCHAR | NULL | Path thumbnail |
| stato_attivo | BOOLEAN | - | Articolo attivo |
| creato_il | DATETIME | - | Timestamp creazione |
| modificato_il | DATETIME | - | Timestamp ultima modifica |

**⚠️ NOTA**: Questa tabella ha FK a `unita_misura` che verrà sostituita da `tbUnitaMisura`.

---

## 5️⃣ giacenze

**Descrizione**: Livelli di stock per ogni articolo  
**Nome Tabella**: `giacenze`  
**Relazione**: 1:1 con `pezzi_ricambio`

### 📋 Struttura Colonne (Schema)

| Colonna | Tipo | FK | Descrizione |
|---------|------|-----|-------------|
| id_pezzo | INT | **PK/FK** | → pezzi_ricambio |
| quantita_disponibile | DECIMAL | - | Quantità disponibile |
| quantita_impegnata | DECIMAL | - | Quantità impegnata |
| quantita_prenotata | DECIMAL | - | Quantità prenotata |
| giacenza_minima | DECIMAL | - | Soglia minima |
| giacenza_massima | DECIMAL | - | Soglia massima |
| ultimo_aggiornamento | DATETIME | - | Timestamp aggiornamento |

---

## 6️⃣ movimenti_magazzino

**Descrizione**: Storico movimenti magazzino (carico/scarico/rettifica/reso)  
**Nome Tabella**: `movimenti_magazzino`

### 📋 Struttura Colonne (Schema)

| Colonna | Tipo | FK | Descrizione |
|---------|------|-----|-------------|
| id_movimento | INT | **PK** | ID univoco movimento |
| id_pezzo | INT | **FK** | → pezzi_ricambio |
| tipo_movimento | VARCHAR | - | CARICO/SCARICO/RETTIFICA/RESO |
| quantita | DECIMAL | - | Quantità movimentata |
| operatore | VARCHAR | - | Username operatore |
| data_movimento | DATETIME | - | Data movimento |
| note | TEXT | NULL | Note movimento |
| creato_il | DATETIME | - | Timestamp creazione |

**⚠️ DESIGN IMMUTABILE**: I movimenti NON si modificano mai, solo creazione.

---

## 7️⃣ modelli_macchine_scm

**Descrizione**: Modelli macchine SCM (per associazione ricambi)  
**Nome Tabella**: `modelli_macchine_scm`

### 📋 Struttura Colonne (Schema)

| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| id_modello | INT | **PK** ID univoco modello |
| codice_modello | VARCHAR | Codice modello SCM |
| nome_modello | VARCHAR | Nome modello |
| stato_attivo | BOOLEAN | Modello attivo |

---

## 8️⃣ matricole_macchine_scm

**Descrizione**: Matricole specifiche macchine SCM  
**Nome Tabella**: `matricole_macchine_scm`

### 📋 Struttura Colonne (Schema)

| Colonna | Tipo | FK | Descrizione |
|---------|------|-----|-------------|
| id_matricola | INT | **PK** | ID univoco matricola |
| id_modello | INT | **FK** | → modelli_macchine_scm |
| matricola | VARCHAR | - | Numero matricola |
| anno_produzione | INT | NULL | Anno produzione |
| stato_attivo | BOOLEAN | - | Matricola attiva |

---

## 🔗 MAPPA FOREIGN KEY

| Tabella Origine | Colonna FK | Tabella Destinazione | Colonna Target |
|-----------------|------------|---------------------|----------------|
| **categorie** | id_categoria_padre | categorie | id_categoria |
| **pezzi_ricambio** | id_categoria | categorie | id_categoria |
| **pezzi_ricambio** | id_unita_misura | unita_misura | id_unita |
| **pezzi_ricambio** | id_fornitore | fornitori | id_fornitore |
| **giacenze** | id_pezzo | pezzi_ricambio | id_pezzo |
| **movimenti_magazzino** | id_pezzo | pezzi_ricambio | id_pezzo |
| **matricole_macchine_scm** | id_modello | modelli_macchine_scm | id_modello |

---

## ⚠️ OPERAZIONE PIANIFICATA: SOSTITUZIONE unita_misura

### Tabella Attuale: `unita_misura`

| ID | Codice | Descrizione |
|----|--------|-------------|
| 1 | Pz | Pezzi |
| 2 | L | Litri |
| 3 | Kg | Chilogrammi |
| 4 | Mt | Metri |
| 5 | Set | Set |
| 6 | Coppia | Coppia |
| 7 | Conf | Confezione |

### Nuova Tabella: `tbUnitaMisura`

| ID | Denominazione | DenominazioneStampa |
|----|---------------|---------------------|
| 1 | Num. | Num. |
| 2 | km | per Chilometro - per kilometer |
| 3 | gg | per Giornata - per Day |
| 4 | Ore | per Ora o frazione |
| 5 | Kg | Kg |
| 7 | Day | Daily |
| 8 | Hour | Hour or fraction |
| 9 | Pz | Pezzi |
| 10 | Lt | Litri |
| 11 | Mt | Metri |
| 12 | Set | Set oppure Kit |
| 13 | Coppia | Coppia |
| 14 | Conf | Confezione |

### ⚠️ MAPPING ID MODIFICATI

**ATTENZIONE**: Gli ID sono cambiati! Confronto:

| Vecchio (unita_misura) | Nuovo (tbUnitaMisura) | Descrizione |
|------------------------|----------------------|-------------|
| ID 1: Pz | ID 9: Pz | Pezzi ✅ |
| ID 2: L | ID 10: Lt | Litri ✅ |
| ID 3: Kg | ID 5: Kg | Chilogrammi ✅ |
| ID 4: Mt | ID 11: Mt | Metri ✅ |
| ID 5: Set | ID 12: Set | Set ✅ |
| ID 6: Coppia | ID 13: Coppia | Coppia ✅ |
| ID 7: Conf | ID 14: Conf | Confezione ✅ |

**NUOVE UNITÀ IN tbUnitaMisura**:
- ID 1: Num. (Numero/Forfait)
- ID 2: km (Chilometro)
- ID 3: gg (Giornata)
- ID 4: Ore (Ore)
- ID 7: Day (Giornata inglese)
- ID 8: Hour (Ora inglese)

### 🔧 AZIONI NECESSARIE

1. 🏗️ Creare tabella `tbUnitaMisura` da CSV (14 righe)
2. ⚠️ Aggiornare FK in `pezzi_ricambio`:
   - Articoli con `id_unita_misura = 1` (Pz) → cambiare a `9`
   - Articoli con `id_unita_misura = 2` (L) → cambiare a `10`
   - Articoli con `id_unita_misura = 3` (Kg) → cambiare a `5`
   - Articoli con `id_unita_misura = 4` (Mt) → cambiare a `11`
   - Articoli con `id_unita_misura = 5` (Set) → cambiare a `12`
   - Articoli con `id_unita_misura = 6` (Coppia) → cambiare a `13`
   - Articoli con `id_unita_misura = 7` (Conf) → cambiare a `14`
3. ⏳ Mantenere temporaneamente `unita_misura` per compatibilità
4. 🏗️ Aggiornare modelli Django per usare `tbUnitaMisura`
5. ✅ Testare inserimento nuovi articoli con nuove unità

**NOTA UTENTE**: "Modificherò io gli articoli a mano" - OK, l'aggiornamento FK sarà manuale.

---

## 🎯 PROSSIMI STEP

1. ✅ Analisi tabelle esistenti completata
2. 🏗️ Creare script per importare `tbUnitaMisura` da CSV
3. ⚠️ Aggiornare manualmente FK in `pezzi_ricambio`
4. 🏗️ Aggiornare modello Django `UnitaMisura` con nuova struttura
5. 🏗️ Creare migration Django per sostituzione tabella
6. 🏗️ Integrare con tabelle clienti (13 tabelle CSV analizzate in ANALISI_TABELLE_CSV.md)

---

**Fine analisi** - Tabelle esistenti documentate e pronte per integrazione con modulo clienti 🚀
