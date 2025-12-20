# 📊 ANALISI STRUTTURA TABELLE CSV
**Data analisi**: 20 Dicembre 2025  
**Totale tabelle**: 13  
**Separatore CSV**: `;` (punto e virgola)  
**Encoding**: UTF-8-sig (con BOM)
**Ultima modifica**: Aggiornamento tbUnitaMisura (14 righe), unita_misura ELIMINATA dal database

---

## ⚠️ IMPORTANTE: Tabella tbUnitaMisura

**Status**: ✅ **IMPLEMENTATA NEL DATABASE** (tabella `tbunitamisura`)  
**Modello Django**: `TbUnitaMisura` (magazzino/models.py)  
**Migration**: 0011, 0012, 0013, 0014 applicate  
**Data attivazione**: 20/12/2025  
**Righe attuali**: **14** (include unità per prestazioni E articoli)

La tabella `tbunitamisura` è ora l'UNICA tabella per unità di misura del sistema, sostituendo definitivamente la vecchia `unita_misura` (eliminata dal database).

---

## 1️⃣ tbAppellativo

**Descrizione**: Tipi di appellativo per contatti (Sig., Dott., Prof., etc.)  
**Nome Tabella**: `tbAppellativo`  
**Righe dati**: 7

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idAppellativo | INT | Numerico | **PK** | ID univoco appellativo |
| Descrizione | VARCHAR(50) | Testo | - | Appellativo (es: "Sig.", "Dott.", "Prof.") |

---

## 2️⃣ tbCategoriaIVA

**Descrizione**: Categorie IVA per applicazione aliquote fiscali su prestazioni/servizi  
**Nome Tabella**: `tbCategoriaIVA`  
**Righe dati**: 7

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idCategoriaIVA | INT | Numerico | **PK** | ID univoco categoria IVA |
| NomeCategoria | VARCHAR(100) | Testo | - | Nome categoria (es: "Manodopera", "Ricambi") |
| ValoreIVA | DECIMAL(5,3) | Percentuale | - | Aliquota IVA (es: 0.22 = 22%, 0 = esente) |

---

## 3️⃣ tbCategoriaSpesa

**Descrizione**: Categorie di spesa per contabilità e deducibilità fiscale  
**Nome Tabella**: `tbCategoriaSpesa`  
**Righe dati**: 32

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idCategoriaSpesa | INT | Numerico | **PK** | ID univoco categoria spesa |
| Descrizione | VARCHAR(200) | Testo | - | Descrizione spesa (es: "Fatture Vitto/Alloggio") |
| ValoreDeducibile | DECIMAL(5,2) | Percentuale | - | % deducibile fiscalmente (1=100%, 0.4=40%) |
| PercentualeIVA | DECIMAL(5,3) | Percentuale | - | Aliquota IVA applicata |
| IVAScaricabile | DECIMAL(5,2) | Percentuale | - | % IVA scaricabile |
| Note | TEXT | Testo lungo | NULL | Note aggiuntive |
| Attivo | BOOLEAN | VERO/FALSO | - | Categoria attiva o archiviata |

---

## 4️⃣ tbCategorieTariffe

**Descrizione**: Categorie di tariffe per clienti (assistenza, produzione, etc.)  
**Nome Tabella**: `tbCategorieTariffe`  
**Righe dati**: 22

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idCategorieTariffe | INT | Numerico | **PK** | ID univoco categoria tariffa (usato come idTariffe) |
| CategoriaTariffe | VARCHAR(200) | Testo | - | Nome categoria (es: "Assistenza lunga per cliente generico") |
| IsVisible | BOOLEAN | VERO/FALSO | - | Visibilità tariffa (attiva/nascosta) |

**⚠️ NOTA**: Nella tabella questa PK viene referenziata come `idTariffe` dalle altre tabelle.

---

## 5️⃣ tbClienti ⭐ TABELLA PRINCIPALE

**Descrizione**: Anagrafica completa clienti con dati fiscali, indirizzo, tariffe, pagamenti  
**Nome Tabella**: `tbClienti`  
**Righe dati**: 262

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idClienti | INT | Numerico | **PK** | ID univoco cliente |
| Nominativo | VARCHAR(200) | Testo | - | Nome breve/identificativo cliente |
| RagioneSociale | VARCHAR(300) | Testo | NULL | Ragione sociale completa |
| PIVA | VARCHAR(20) | Alfanumerico | NULL | Partita IVA |
| CodiceFiscale | VARCHAR(16) | Alfanumerico | NULL | Codice Fiscale |
| ViaIndirizzo | VARCHAR(200) | Testo | NULL | Via/Indirizzo |
| NumeroIndirizzo | VARCHAR(20) | Testo | NULL | Numero civico |
| ComuneIndirizzo | VARCHAR(100) | Testo | NULL | Comune |
| ProvinciaIndirizzo | CHAR(2) | Sigla | NULL | Provincia (es: RN, MI) |
| NazioneIndirizzo | VARCHAR(100) | Testo | NULL | Nazione |
| CAP | VARCHAR(10) | Numerico | NULL | Codice Avviamento Postale |
| WWW | VARCHAR(200) | URL | NULL | Sito web |
| idCategoriaTariffe | INT | Numerico | **FK** | → tbCategorieTariffe |
| TariffaViaggioForfait | DECIMAL(10,2) | Decimale | NULL | Tariffa forfait viaggio |
| idTipoPagamento | INT | Numerico | **FK** | → tbTipoPagamento |
| Banca | VARCHAR(200) | Testo | NULL | Nome banca |
| IbanCode | VARCHAR(34) | Alfanumerico | NULL | Codice IBAN completo |
| CIN | CHAR(1) | Alfanumerico | NULL | CIN (Check Internal Number) |
| ABI | CHAR(5) | Numerico | NULL | ABI (Associazione Bancaria Italiana) |
| CAB | CHAR(5) | Numerico | NULL | CAB (Codice Avviamento Bancario) |
| ContoCorr | VARCHAR(20) | Numerico | NULL | Numero conto corrente |
| SDI | VARCHAR(7) | Alfanumerico | NULL | Codice Sistema Di Interscambio (fattura elettronica) |
| PEC | VARCHAR(200) | Email | NULL | Posta Elettronica Certificata |
| Note | TEXT | Testo lungo | NULL | Note generali cliente |
| NoteTariffe | TEXT | Testo lungo | NULL | Note specifiche tariffe |
| TxtStampaConsuntivo | TEXT | Testo lungo | NULL | Testo da stampare su consuntivo |
| TxtStampaFatture | TEXT | Testo lungo | NULL | Testo da stampare su fatture |

---

## 6️⃣ tbContatti

**Descrizione**: Contatti (persone) associati a clienti e fornitori  
**Nome Tabella**: `tbContatti`  
**Righe dati**: 299

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idContatto | INT | Numerico | **PK** | ID univoco contatto |
| idCliente | INT | Numerico | **FK** | → tbClienti (NULL se fornitore) |
| idFornitore | INT | Numerico | **FK** | → Fornitore (tabella esistente magazzino) |
| Appellativo | INT | Numerico | **FK** | → tbAppellativo |
| Nome | VARCHAR(100) | Testo | NULL | Nome contatto |
| Cognome | VARCHAR(100) | Testo | NULL | Cognome contatto |
| Ruolo | VARCHAR(100) | Testo | NULL | Ruolo aziendale (es: "Titolare", "Amministrazione") |
| TelefonoAzienda | VARCHAR(50) | Telefono | NULL | Telefono fisso aziendale |
| CellulareAzienda | VARCHAR(50) | Telefono | NULL | Cellulare aziendale |
| emailAzienda | VARCHAR(200) | Email | NULL | Email aziendale |
| CellularePersonale | VARCHAR(50) | Telefono | NULL | Cellulare personale |
| eMailPersonale | VARCHAR(200) | Email | NULL | Email personale |
| Nota | TEXT | Testo lungo | NULL | Note contatto |

---

## 7️⃣ tbDettaglioTariffe

**Descrizione**: Macro-categorie dettaglio tariffe (Manodopera, Rimborso spese, etc.)  
**Nome Tabella**: `tbDettaglioTariffe`  
**Righe dati**: 7

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idDettaglioTariffe | INT | Numerico | **PK** | ID univoco dettaglio tariffa |
| DettaglioTariffa | VARCHAR(100) | Testo | - | Nome categoria (es: "Manodopera", "Ricambi") |
| IVA | DECIMAL(5,3) | Percentuale | - | Aliquota IVA (0.22 = 22%) |

---

## 8️⃣ tbModalitaPagamento

**Descrizione**: Modalità di pagamento (Assegno, Bonifico, Contanti, etc.)  
**Nome Tabella**: `tbModalitaPagamento`  
**Righe dati**: 8

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idModalitaPagamento | INT | Numerico | **PK** | ID univoco modalità pagamento |
| Nome | VARCHAR(100) | Testo | - | Descrizione modalità (es: "Bonifico bancario") |

---

## 9️⃣ tbPrestazioni

**Descrizione**: Prestazioni/servizi erogabili con tariffe e categorie  
**Nome Tabella**: `tbPrestazioni`  
**Righe dati**: 142

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idPrestazione | INT | Numerico | **PK** | ID univoco prestazione |
| Denominazione | VARCHAR(200) | Testo | - | Descrizione prestazione (es: "Manodopera ordinaria") |
| idUnitaMisura | INT | Numerico | **FK** | → tbUnitaMisura |
| PrezzoUnitario | DECIMAL(10,2) | Decimale | - | Prezzo unitario |
| idCategorieTariffe | INT | Numerico | **FK** | → tbCategorieTariffe |
| idCategoriaIVA | INT | Numerico | **FK** | → tbCategoriaIVA |
| VisualizzaPreventivo | BOOLEAN | VERO/FALSO | - | Mostra in preventivo |
| OrdineStampa | INT | Numerico | NULL | Ordine visualizzazione stampa |

---

## 🔟 tbRiferimentoSpesa

**Descrizione**: Riferimenti/categorie per classificazione spese  
**Nome Tabella**: `tbRiferimentoSpesa`  
**Righe dati**: 21

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idRiferimentoSpesa | INT | Numerico | **PK** | ID univoco riferimento spesa |
| Descrizione | VARCHAR(200) | Testo | - | Descrizione categoria (es: "Vitto/Alloggio", "Auto") |

---

## 1️⃣1️⃣ tbStatoDocumenti

**Descrizione**: Stati workflow documenti (fatture, preventivi)  
**Nome Tabella**: `tbStatoDocumenti`  
**Righe dati**: 7

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idStatoDocumenti | INT | Numerico | **PK** | ID univoco stato documento |
| DenominazioneStato | VARCHAR(100) | Testo | - | Nome stato (es: "Da completare", "Inviato") |
| Ordinamento | INT | Numerico | - | Ordine visualizzazione stati |

---

## 1️⃣2️⃣ tbTipoPagamento

**Descrizione**: Tipi di pagamento con scadenze (Bonifico 30gg, 60gg, RI.BA., etc.)  
**Nome Tabella**: `tbTipoPagamento`  
**Righe dati**: 24

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idTipoPagamento | INT | Numerico | **PK** | ID univoco tipo pagamento |
| descrizione | VARCHAR(200) | Testo | - | Descrizione (es: "Bonifico 30 gg D.F.") |
| DataRifScad | VARCHAR(50) | Testo | - | Riferimento scadenza (DF=data fattura, FM=fine mese) |
| GiorniDataRif | INT | Numerico | - | Giorni da aggiungere per scadenza |
| GiornoAddebito | INT | Numerico | - | Giorno specifico addebito (0=nessuno) |

---

## 1️⃣3️⃣ tbUnitaMisura ✅ ATTIVA NEL DATABASE

**Descrizione**: Unità di misura per prestazioni/servizi E articoli magazzino  
**Nome Tabella**: `tbUnitaMisura` (database: `tbunitamisura`)  
**Modello Django**: `TbUnitaMisura`  
**File CSV**: `tbUnitaMisura.csv`  
**Righe dati CSV**: 14 (include 6 unità per articoli + 8 unità per prestazioni)

### 📋 Struttura Colonne

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idUnitaMisura | INT | Numerico | **PK** | ID univoco unità misura (case-sensitive: idUnitaMisura) |
| Denominazione | VARCHAR(50) | Testo | - | Nome unità breve (es: "Ore", "Pz", "km") |
| DenominazioneStampa | VARCHAR(100) | Testo | NULL | Testo descrittivo esteso per stampa |
| stato_attivo | BOOLEAN | VERO/FALSO | - | Unità attiva (default: VERO) |
| creato_il | DATETIME | Data/Ora | auto_now_add | Timestamp creazione record |
| modificato_il | DATETIME | Data/Ora | auto_now | Timestamp ultima modifica |

### 📊 Dati Completi (14 unità)

| ID | Denominazione | DenominazioneStampa | Categoria | Note |
|----|---------------|---------------------|-----------|------|
| 1  | Num.    | Num.                                 | Prestazione     | Forfait/Numero |
| 2  | km      | per Chilometro - per kilometer       | Prestazione     | Viaggi/distanze |
| 3  | gg      | per Giornata - per Day | Prestazione | Giornate lavoro |
| 4  | **Ore** | per Ora o frazione                   | **Prestazione** | **Manodopera oraria** |
| 5  | Kg      | Kg                                   | Articolo | Peso |
| 7  | Day     | Daily                                | Prestazione | Giorni (EN) |
| 8  | Hour    | Hour or fraction | Prestazione       | Ore (EN) |
| 9  | **Pz**  | Pezzi                                | **Articolo** | **Articoli contati** (da vecchio ID 1) |
| 10 | Lt      | Litri                                | Articolo | Liquidi (da vecchio ID 2 "L") |
| 11 | Mt      | Metri                                | Articolo | Lunghezze (da vecchio ID 4) |
| 12 | Set     | Set oppure Kit                       | Articolo | Kit (da vecchio ID 5) |
| 13 | Coppia  | Coppia                               | Articolo | Coppie (da vecchio ID 6) |
| 14 | Conf    | Confezione                           | Articolo | Confezioni (da vecchio ID 7) |

### 🔗 Foreign Key - Referenziata da:

1. **pezzi_ricambio.idUnitaMisura** (magazzino esistente)  
   - Campo modello: `unita_misura`  
   - db_column: `idUnitaMisura`  
   - Usa ID: 5, 9, 10, 11, 12, 13, 14

2. **tbPrestazioni.idUnitaMisura** (da implementare)  
   - Usa principalmente ID: 1, 2, 3, 4, 7, 8

### ✅ Implementazione Completata

**Migrations applicate**:
- `0011_alter_unitamisura_options_tbunitamisura.py` - Creazione tabella tbunitamisura
- `0012_pezzoricambio_tb_unita_misura_and_more.py` - Aggiunta campo transitorio
- `0013_mappa_unita_misura_vecchie_a_nuove.py` - Mappatura dati vecchi→nuovi ID
- `0014_usa_solo_tbunitamisura.py` - Rimozione campo transitorio, eliminazione UnitaMisura

**Status**: ✅ ATTIVA - Unica tabella unità misura del sistema dal 20/12/2025

---

# 🔗 MAPPA FOREIGN KEYS

## ✅ Relazioni Confermate

| Tabella Origine | Colonna FK | → Tabella Destinazione | Colonna PK |
|----------------|------------|----------------------|------------|
| **tbClienti** | idCategoriaTariffe | → tbCategorieTariffe | idCategorieTariffe |
| **tbClienti** | idTipoPagamento | → tbTipoPagamento | idTipoPagamento |
| **tbContatti** | idCliente | → tbClienti | idClienti |
| **tbContatti** | idFornitore | → Fornitore (magazzino) | id_fornitore |
| **tbContatti** | Appellativo | → tbAppellativo | idAppellativo |
| **tbPrestazioni** | idUnitaMisura | → tbUnitaMisura | idUnitaMisura |
| **tbPrestazioni** | idCategorieTariffe | → tbCategorieTariffe | idCategorieTariffe |
| **tbPrestazioni** | idCategoriaIVA | → tbCategoriaIVA | idCategoriaIVA |
| **pezzi_ricambio** | idUnitaMisura | → tbUnitaMisura | idUnitaMisura |

---

## ✅ TUTTI I PROBLEMI RISOLTI

### 1. **tbUnitaMisura - IMPLEMENTATA ✅**
**Problema**: Mancava nel database magazzino, usava vecchia tabella `unita_misura` con solo 7 unità  
**Azione**: ✅ **COMPLETATO** - Creata `tbunitamisura` con 14 unità (prestazioni + articoli)  
**Status**: Migrations 0011-0014 applicate, vecchia tabella `unita_misura` ELIMINATA

### 2. **Naming Inconsistente PK in tbCategorieTariffe**
**Problema**: La PK si chiama `idCategorieTariffe` ma in alcune referenze storiche era chiamata `idTariffe`  
**Azione**: ✅ RISOLTO - tbPrestazioni ora usa correttamente `idCategorieTariffe`

### 3. **tbContatti.Appellativo**
**Problema**: Contiene valori INT (0-7) ma non era FK formale  
**Azione**: ✅ RISOLTO - Ora è FK formale a tbAppellativo

---

# 📋 RIEPILOGO MODIFICHE

## ✅ Problemi Risolti

1. **tbUnitaMisura IMPLEMENTATA ✅** - Creata con **14 unità** (prestazioni + articoli), vecchia `unita_misura` ELIMINATA dal database
2. **tbDettaglioCategorieTariffe ELIMINATA** - Era duplicato di tbPrestazioni
3. **tbPrestazioni.idCategoriaProdotto RISOLTO** - Ora usa correttamente `idCategorieTariffe`
4. **tbContatti.Appellativo** - Impostato come FK formale a tbAppellativo
5. **tbCategoriaDettaglio RINOMINATA** - Ora `tbCategoriaIVA` con campo `ValoreIVA` per aliquote

---

# 📂 STATUS FILE CSV

## Tabelle da Implementare (11 rimanenti)

| # | File CSV                 | Righe   | Priorità | Dipendenze |
|---|--------------------------|---------|----------|------------|
| 1 | tbAppellativo.csv        | 7       | Alta     | Nessuna |
| 2 | tbCategoriaIVA.csv       | 7       | Alta     | Nessuna |
| 3 | tbCategoriaSpesa.csv     | 32      | Media    | Nessuna |
| 4 | tbCategorieTariffe.csv   | 22      | Alta     | Nessuna |
| 5 | **tbClienti.csv**        | **262** | **🔥 MASSIMA** | tbCategorieTariffe, tbTipoPagamento |
| 6 | tbContatti.csv           | 299     | Alta     | tbClienti, fornitori, tbAppellativo |
| 7 | tbModalitaPagamento.csv  | 8       | Bassa    | Nessuna |
| 8 | **tbPrestazioni.csv**    | **142** | **🔥 MASSIMA** | tbUnitaMisura ✅, tbCategorieTariffe, tbCategoriaIVA |
| 9 | tbRiferimentoSpesa.csv   | 21      | Bassa    | Nessuna |
| 10 | tbStatoDocumenti.csv    | 7       | Media    | Nessuna |
| 11 | tbTipoPagamento.csv     | 24     | Alta      | Nessuna |

## ✅ Tabelle Implementate (1)

| # | Tabella | Righe DB | Data Implementazione | Migration |
|---|---------|----------|----------------------|-----------|
| 1 | **tbUnitaMisura** | **14** | **20/12/2025** | **0011-0014** |

---

# 🎯 PROSSIMI STEP CONSIGLIATI

### Ordine Implementazione Suggerito:

1. **Fase 1 - Tabelle Base** (nessuna dipendenza):
   - ✅ tbUnitaMisura (COMPLETATA)
   - tbAppellativo
   - tbCategoriaIVA
   - tbCategorieTariffe
   - tbTipoPagamento
   - tbModalitaPagamento

2. **Fase 2 - Tabelle Principali** (dipendono da Fase 1):
   - **tbClienti** (dipende: tbCategorieTariffe, tbTipoPagamento)
   - **tbPrestazioni** (dipende: tbUnitaMisura ✅, tbCategorieTariffe, tbCategoriaIVA)

3. **Fase 3 - Tabelle Secondarie**:
   - tbContatti (dipende: tbClienti, fornitori, tbAppellativo)
   - tbCategoriaSpesa
   - tbRiferimentoSpesa
   - tbStatoDocumenti

---

**Fine analisi aggiornata** - Struttura confermata e pronta per generazione modelli Django 🚀
