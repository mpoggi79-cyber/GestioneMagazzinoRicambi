# Memoria Tecnica Sviluppo

Documento centrale di memoria tecnica interna.

Scopo:
- Conservare in modo strutturato le decisioni e gli interventi effettuati durante lo sviluppo.
- Evitare duplicazioni tra manuali.
- Mantenere traccia operativa delle modifiche con impatto su UX, backend e convenzioni.

Data ultimo aggiornamento: 03/11/2026 (v1.2.0 - Importazione dal Portale SCM)

## Ambito aggiornamento (chat corrente)

### 1. Dashboard - indicatori articoli
- Aggiunte statistiche sugli articoli richieste dal team:
  - numero articoli attivi,
  - numero articoli con foto,
  - numero articoli con codice SCM,
  - numero articoli con codice fornitore,
  - numero articoli non attivi.
- Implementate due varianti di layout dashboard:
  - variante additiva,
  - variante riorganizzata.
- Scelta layout resa persistente per sessione utente.

File principali coinvolti:
- `magazzino/views.py`
- `templates/magazzino/dashboard.html`

### 2. Frontend - terminologia utente in italiano
- Rimosse diciture tecniche poco chiare lato utente (es. uso sigle non spiegate).
- Sostituite con testi comprensibili in italiano:
  - "Riepilogo Generale"
  - "Indicatori Articoli"
  - descrizioni contestuali delle metriche.

File principale coinvolto:
- `templates/magazzino/dashboard.html`

### 3. Form "Aggiungi Nuovo Articolo" - robustezza e UX errori
- Migliorata gestione caso di submit non valido:
  - messaggio esplicito in `form_invalid` lato create,
  - riepilogo errori in alto,
  - scroll automatico al riepilogo,
  - focus sul primo campo non valido,
  - evidenziazione sezione "Classificazione" quando errore categoria.
- Aggiunto fallback server-side per categoria da campo nascosto, per ridurre errori silenziosi nei submit.

File principali coinvolti:
- `magazzino/forms.py`
- `magazzino/views.py`
- `templates/magazzino/pezzoricambio_form.html`

## Decisioni operative confermate

1. I manuali principali vengono allineati con note sintetiche e rimando a questo documento centrale.
2. I file di configurazione workspace (`.vscode/settings.json`, `.vscode/tasks.json`, `.vscode/launch.json`) non vengono usati come changelog narrativo.
3. Le convenzioni lato utente restano in italiano chiaro, evitando sigle non spiegate.

## Regola di manutenzione

Ad ogni intervento significativo:
1. Aggiornare prima questo documento.
2. Riportare solo una sintesi essenziale nei manuali principali.
3. Registrare la timeline sintetica in `/memories/repo/version_history.md`.

---

## PIANO 1 STABILIZZAZIONE (10-11/05/2026)

**Status**: ✅ COMPLETATO - v1.1.1

### Ambito intervento

Consolidamento funzionalita critiche e stabilizzazione interfaccia gestione tabelle.

### Decisioni applicate

#### 1. Modifica Record Reale - Implementazione View Generica
**Descrizione**: Conversione da placeholder (modal fake con alert) a implementazione reale di ModificaRecordTabellaView.

**Cosa è stato fatto**:
- Creazione `ModificaRecordTabellaView` in magazzino/views.py (~linea 2297)
- Whitelist tabelle autorizzate (10 tabelle)
- Generazione form dinamico via `modelform_factory`
- Validazione permessi CanEditMixin
- Redirect post-modifica a lista aggiornata
- Invariante di sicurezza: PK sempre da URL, mai da form

**File**: magazzino/views.py, magazzino/urls.py, templates/magazzino/modifica_record_tabella.html

#### 2. Audit Logging Strutturato
**Descrizione**: Implementazione logging permanente per tracciare modifiche su record di tabelle.

**Cosa è stato fatto**:
- Logger `magazzino.views` con marker `[AUDIT_TABELLE]` per filtro facile
- Campi tracciati: utente, tabella, modello, record_pk, diff (campo: vecchio → nuovo)
- Timestamp auto-generato
- File persistente: logs/django.log
- Normalizzazione valori per audit leggibile

**Pattern**:
```python
logger.info(f"[AUDIT_TABELLE] utente={user.username} tabella={nome_tabella} modello={modello.__name__} record_pk={pk} modifiche={diff_string}")
```

**File**: magazzino/views.py (metodo form_valid ~linea 2365)

#### 3. Fix Visibilità Record Inattivi
**Descrizione**: tbunitamisura non mostrava record inattivi nonostante richiesta. Implementato controllo dinamico.

**Cosa è stato fatto**:
- Logica speciale in `ModificaTabellaView.get_context_data()`
- Se tabella == tbunitamisura: mostra inattivi per default
- Toggle checkbox nel template per nascondere/mostrare
- Pattern ereditato da altri modelli simili (tbprestazioni, modelli_scm, matricole_scm)

**File**: magazzino/views.py (~linea 2280), template modifica_tabella.html (~linea 33)

#### 4. Compatibilità CSS - Rimozione :has()
**Descrizione**: Selettore `.alert-warning:has(i.fa-key)` non supportato in IE e vecchi browser.

**Cosa è stato fatto**:
- Rimosso selettore :has() da base.html
- Sostituzione con classe `.alert-warning-special` applicata via JavaScript
- Script controlla se alert contiene i.fa-key o "PASSWORD" e applica classe
- Fallback CSS per styling della classe

**File**: templates/base.html (~linea 252, ~615 script JS)

#### 5. Test Suite - 3 Nuovi Test Aggiunti
**Descrizione**: Espansione test suite per coprire nuovo flusso modifica record.

**Cosa è stato fatto**:
- Classe `GestioneTabelleRecordTests` in magazzino/tests.py (~linea 138)
- Test 1: `test_admin_puo_modificare_record_tabella` - Verifica POST con audit log
- Test 2: `test_operatore_senza_permessi_non_accede_a_modifica_record_tabella` - Blocco non-admin
- Test 3: `test_tbunitamisura_mostra_inattivi_di_default` - Regressione visibilità

**Totale**: 20 test (3 nuovi) → `python manage.py test` risultato: ✅ PASS

### Regola Workspace - Memoria Tecnica Centralizzata

**Decisione operativa**: La memoria tecnica non viene scritta come testo narrativo nei file workspace (`.vscode/*`).
Le note restano consolidate in:
1. AGENTS.md (sezione "Memoria Sviluppo Recente")
2. MEMORIA_TECNICA_SVILUPPO.md (timeline operativa centrale - questo file)
3. `/memories/repo/version_history.md` (storia versioni)

**Conseguenze**:
- Manuali principali (GESTIONE_UTENTI.md, MANUALE_AMMINISTRATORE.md, BACKUP_RECOVERY_GUIDE.md) contengono sintesi + rimando a fonti centrali
- No duplicazioni di contenuto
- Un'unica fonte di verità per decisioni tecniche

### Impatto Test & Qualita

**Status test**: ✅ 20/20 pass
- Nessuna regressione
- Nuovi test verificano flusso modifica record
- Audit logging testato con assertLogs

**Impatto UX**:
- ✅ Modifica record funziona realmente
- ✅ Tracciamento completo operazioni admin
- ✅ Visibilità record inattivi corretta
- ✅ Compatibilità CSS migliorata

### Docstrings & Convenzioni

**Naming**: Tutti i nomi rimangono in italiano (giacenza_disponibile, operatore, calcola_saldo, etc.)

**Commenti**: Inline e docstring in italiano per mantenere coerenza dominio aziendale

### Totale modifiche

| Categoria | Conteggio |
|-----------|-----------|
| File modificati | 6 |
| View nuove | 1 |
| Template nuovi | 1 |
| Test aggiunti | 3 |
| URL pattern nuovi | 1 |
| Linee codice aggiunte | ~280 |
| Bug corretti | 4 |


---

## Importazione articolo dal Portale SCM (02-03/11/2026) - IMPLEMENTATA (fase 1: un codice alla volta)

### Cronologia decisioni
1. 02/11: autenticazione manuale (Playwright + profilo browser), prima fase su un solo codice, prezzi IVA esclusa, storico dei rilevamenti.
2. 02/11: sconti sempre 3% online + 20% riservato; il prezzo barrato è il prezzo al cliente, il finale è il prezzo a noi.
3. 03/11: niente modalità headless (Chrome visibile) per non farsi riconoscere come browser automatico; pause casuali nel futuro import massivo.
4. 03/11: pulsanti piccoli sotto il campo Codice SCM (in affiancamento coprivano il codice) e pulsante **"Accedi al portale SCM"** per fare il login dal form, senza terminale.
5. 03/11: correzione: un articolo senza prezzo ("Articolo attualmente non disponibile") non è una sessione scaduta; si importano i dati disponibili senza toccare i prezzi.

### Analisi portale (shop.scmgroup.com/scmwood/it/it/)
- Piattaforma SAP Commerce (Hybris). Ricerca: `/search?text=<codice>`. Scorciatoia verificata: `/p/<codice_scm>` reindirizza alla pagina prodotto canonica.
- **Senza login** sono visibili descrizione, disponibilita e foto, ma **non i prezzi**: servono l'accesso Microsoft (operatore esterno).
- Pagina articolo (da login): prezzo di listino barrato (no IVA), righe sconto (es. "3% sconto online", "20% discount"), prezzo netto finale, "Disponibile N" o "In arrivo N", immagine. Verifica: 1.680,00 x 0,97 x 0,80 = 1.303,68.
- Il prezzo barrato e il prezzo al cliente; il prezzo finale e il prezzo a noi (sconti sempre 3% online + 20% riservato).
- Alcuni articoli non hanno foto ("NO IMAGE AVAILABLE"): gestire come caso normale.

### Decisioni
- Autenticazione **manuale** dal browser (MFA inclusa), mai credenziali nel codice o nel DB. Sessione salvata in profilo browser locale `.scm_browser_profile/` (ignorato da git).
- Prima fase: importazione di **un solo codice** (dal form articolo). L'importazione da elenco codici viene dopo.
- Prezzi **IVA esclusa**: prezzo cliente (listino SCM) e prezzo nostro (scontato).
- Si "congela" il momento del rilevamento: data/ora di acquisizione di prezzo e disponibilita.
- L'importazione precompila il form e non salva da sola; riservata a `CanEditMixin`.

### Modello dati (migrazione `0023_dati_scm_storico`, applicata al DB reale dopo backup; tutti i campi facoltativi)
- `PezzoRicambio.prezzo_listino_scm`: prezzo barrato = prezzo al cliente, no IVA
- `PezzoRicambio.prezzo_acquisto_scm` (esistente): prezzo finale dopo 3% sconto online + 20% riservato = prezzo a noi, no IVA
- `PezzoRicambio.disponibilita_scm` + `stato_disponibilita_scm` (il portale usa "Disponibile N" e "In arrivo N")
- `PezzoRicambio.dati_scm_aggiornati_il`: data/ora del rilevamento (campo nascosto valorizzato dal pulsante)
- `StoricoDatiSCM` (tabella `storico_dati_scm`, append-only): rilevazioni congelate con listino, acquisto, disponibilita, stato, operatore. Una riga per ogni nuovo `dati_scm_aggiornati_il` salvato (salvare due volte lo stesso rilevamento non duplica).
- Evoluzione futura: prezzi multi-fornitore.

### Componenti
- `magazzino/scm_portale.py`: `cerca_codice(codice_scm)` apre Chrome (Playwright, `channel='chrome'`, nessun download browser) in modalita **visibile** (niente headless, scelta per non farsi riconoscere come browser automatico: durante il recupero compare una finestra Chrome che si chiude da sola) con il profilo `.scm_browser_profile/` e i cookie salvati in `sessione_scm.json` (i cookie di sessione non sopravvivono alla chiusura del browser). Estrae testi grezzi in JS; l'interpretazione (`interpreta_dati_grezzi`) e Python puro e testata senza portale. Pagina aperta: `/p/<codice>` (404 = codice non trovato; mancanza di prezzo/"DISCONNESSIONE" = sessione scaduta). Un lock impedisce due recuperi contemporanei.
- `python manage.py scm_login` (alternativa da terminale) e pulsante **"Accedi al portale SCM"** nel form articolo (`AvviaLoginSCMView`, `POST/GET /articoli/scm/login/`): apre Chrome visibile sul PC dove gira il server, il login Microsoft/MFA lo fa l'operatore a mano con il proprio account; al termine il recupero riparte da solo. Il login viene registrato nel log con l'utente (`[SCM_PORTALE]`). La sessione si salva appena compare "DISCONNESSIONE" (attesa max 5 minuti). Da rifare quando la sessione scade.
- Articoli senza prezzo sul portale (es. "Articolo attualmente non disponibile"): si importano comunque descrizione, foto e stato "Non disponibile"; i prezzi esistenti non vengono toccati e non si crea una riga di storico. Non e un errore di sessione.
- `RecuperaDatiSCMView` (`POST /articoli/scm/recupera/`, solo `CanEditMixin`, risposte JSON 200/401/403/404/503) e pulsante "Recupera da SCM" nel form articolo: precompila descrizione SCM, descrizione (se vuota), prezzi, disponibilita e `immagine_url`; non salva da solo. La foto del portale (pubblica) viene scaricata dal server al salvataggio solo se l'articolo non ha gia una foto; le immagini "missing_product" sono ignorate.
- Dettaglio articolo: nuovi campi SCM e tabella "Storico Prezzi e Disponibilita SCM". Admin: `StoricoDatiSCMAdmin` in sola lettura.
- Test: `PortaleSCMInterpretazioneTests`, `RecuperaDatiSCMTests` (portale simulato con mock). Totale suite progetto: 37 test.
- Dipendenze: `playwright==1.64.1` (+ greenlet, pyee, typing_extensions) in `requirements.txt`; Google Chrome deve essere installato.
- Sicurezza: `.gitignore` esclude `.scm_browser_profile/` e `Portale Ricambi SCM/Info url e accesso.md` (può contenere credenziali). La sessione del portale dura poco (anche meno di un'ora): è normale dover rifare il login. La sessione è una sola per PC; nel log `[SCM_PORTALE]` resta lo username Django di chi ha avviato login/recupero.
- Limiti noti: il browser si apre sul PC del server (uso locale); un solo recupero alla volta (lock sul profilo Chrome); selettori basati sull'HTML attuale del portale (se SCM cambia il sito vanno aggiornati in `_SCRIPT_ESTRAZIONE`).

### Prossimi passi
- Importazione massiva da elenco di codici (comando e/o pagina) riusando `cerca_codice`, con **pause casuali** tra un codice e l'altro e un limite di codici per esecuzione (decisione 03/11/2026, per non sembrare un robot al portale).
- Eventuali ulteriori dati dal "Piu dettagli" della scheda articolo (per ora non richiesti).
