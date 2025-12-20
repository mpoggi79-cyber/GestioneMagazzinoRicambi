# 📊 ANALISI STRUTTURA TABELLE CSV
**Data analisi**: 20 Dicembre 2025  
**Totale tabelle**: 13  
**Separatore CSV**: `;` (punto e virgola)  
**Ultima modifica**: Aggiunta tbUnitaMisura, eliminata tbDettaglioCategorieTariffe

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

## 2️⃣ tbCategoriaDettaglio

**Descrizione**: Categorie di dettaglio per tariffe (Manodopera, Rimborso spese, Ricambi)  
**Nome Tabella**: `tbCategoriaDettaglio`  
**Righe dati**: 7

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idCategoriaDettaglio | INT | Numerico | **PK** | ID univoco categoria dettaglio |
| NomeCategoria | VARCHAR(100) | Testo | - | Nome categoria (es: "Manodopera", "Ricambi") |
| IVA | DECIMAL(5,3) | Percentuale | - | Aliquota IVA (es: 0.22 = 22%, 0 = esente) |

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
| idCategoriaDettaglio | INT | Numerico | **FK** | → tbCategoriaDettaglio |
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

## 1️⃣3️⃣ tbUnitaMisura ✅ NUOVA

**Descrizione**: Unità di misura per prestazioni/servizi  
**Nome Tabella**: `tbUnitaMisura`  
**Righe dati**: 8

| Colonna | Tipo | Formato | Chiave | Descrizione |
|---------|------|---------|--------|-------------|
| idUnitaMisura | INT | Numerico | **PK** | ID univoco unità misura |
| Denominazione | VARCHAR(50) | Testo | - | Nome unità (es: "Ore", "gg", "km") |
| DenominazioneStampa | VARCHAR(100) | Testo | NULL | Testo descrittivo per stampa (es: "per Ora o frazione") |

**Valori presenti**:
- 1: Num. (Numero/Forfait)
- 2: km (per Chilometro)
- 3: gg (per Giornata)
- 4: Ore (per Ora o frazione)
- 5: Kg (Kilogrammi)
- 7: Day (Daily - inglese)
- 8: Hour (Hour or fraction - inglese)

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
| **tbPrestazioni** | idCategoriaDettaglio | → tbCategoriaDettaglio | idCategoriaDettaglio |

---

## ✅ TUTTI I PROBLEMI RISOLTI

### 1. **Naming Inconsistente PK in tbCategorieTariffe**
**Problema**: La PK si chiama `idCategorieTariffe` ma in alcune referenze storiche era chiamata `idTariffe`  
**Azione**: ✅ RISOLTO - tbPrestazioni ora usa correttamente `idCategorieTariffe`

### 2. **tbContatti.Appellativo**
**Problema**: Contiene valori INT (0-7) ma non era FK formale  
**Azione**: ✅ RISOLTO - Ora è FK formale a tbAppellativo

---

# 📋 RIEPILOGO MODIFICHE

## ✅ Problemi Risolti

1. **tbUnitaMisura CREATA** - Aggiunta con 8 unità di misura
2. **tbDettaglioCategorieTariffe ELIMINATA** - Era duplicato di tbPrestazioni
3. **tbPrestazioni.idCategoriaProdotto RISOLTO** - Ora usa correttamente `idCategorieTariffe`
4. **tbContatti.Appellativo** - Impostato come FK formale a tbAppellativo

---

# 🎯 PROSSIMI STEP

1. ✅ **tbUnitaMisura** - Creata e popolata
2. ✅ **tbPrestazioni** - FK corrette (idCategorieTariffe + idCategoriaDettaglio + idUnitaMisura)
3. ✅ **tbDettaglioCategorieTariffe** - Eliminata (duplicato)
4. ✅ **tbContatti.Appellativo** - Impostato come FK formale a tbAppellativo
5. 🏗️ **Generare modelli Django** - Struttura confermata e completa, pronta per codice

---

**Fine analisi aggiornata** - Struttura confermata e pronta per generazione modelli Django 🚀
