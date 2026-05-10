# Memoria Tecnica Sviluppo

Documento centrale di memoria tecnica interna.

Scopo:
- Conservare in modo strutturato le decisioni e gli interventi effettuati durante lo sviluppo.
- Evitare duplicazioni tra manuali.
- Mantenere traccia operativa delle modifiche con impatto su UX, backend e convenzioni.

Data ultimo aggiornamento: 11/05/2026 (Piano 1 Stabilizzazione)

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

## Ambito aggiornamento (analisi frontend e piano redesign)

### 1. Esito analisi frontend (stato attuale)
- Frontend funzionale e coerente sui flussi di dominio, con base Bootstrap 5.3 e struttura template ampia.
- Styling e script molto distribuiti nei template, con frammentazione elevata e manutenibilita ridotta.
- Identita visiva presente ma poco distintiva (impostazione corporate standard).

Criticita rilevate:
- Incoerenza componenti Bootstrap 5 in pagine gestione tabelle (attributi e markup legacy).
- Presenza di selettore CSS non standard nel layout base.
- Funzionalita frontend con placeholder e TODO non completati nella modifica tabella.
- Elevato uso di stile inline e bassa centralizzazione CSS e JS.

File frontend chiave analizzati:
- templates/base.html
- templates/magazzino/dashboard.html
- templates/magazzino/pezzoricambio_form.html
- templates/magazzino/giacenza_list.html
- templates/magazzino/categoria_list.html
- templates/magazzino/modifica_tabella.html
- templates/magazzino/backup_list.html
- templates/accounts/login.html
- templates/accounts/logout_conferma.html
- templates/accounts/edit_profile.html

### 2. Piano operativo redesign frontend
Obiettivo:
- Rendere il frontend piu distintivo, coerente e manutenibile, senza regressioni sui flussi operativi principali.

Direzione estetica proposta:
- Approccio industriale-editoriale: chiaro, tecnico, professionale, con gerarchia visuale netta.
- Tipografia non generica (display + testo), colore dominante controllato con accento unico.
- Motion limitata ma significativa (ingresso pagina, reveal KPI, feedback azioni).

Fase 0 (allineamento):
- Definizione priorita UX per ruoli: admin, gestore, operatore.
- Blueprint visuale sintetico e perimetro pagine core.

Fase 1 (stabilizzazione tecnica):
- Correzione incoerenze Bootstrap 5 nelle pagine gestione tabelle.
- Rimozione selettori CSS non supportati e pulizia regole fragili.
- Allineamento asset branding e static (favicon e riferimenti).
- Rimozione placeholder JS non produttivi (alert e TODO) nelle funzionalita critiche.

Fase 2 (fondazione design system):
- Centralizzazione stile e script comuni in asset statici.
- Definizione token UI: colori, spaziature, raggi, ombre, tipografia, stati.
- Introduzione componenti riusabili: card KPI, header pagina, filtri, tabelle compatte, sezioni form.
- Regole responsive coerenti per desktop e mobile.

Fase 3 (refactor pagine core):
- Shell applicativa (base), dashboard, form articolo, liste operative, autenticazione e profilo.
- Riduzione progressiva CSS inline e normalizzazione pattern visuali.

Fase 4 (QA e rilascio):
- Verifica responsive, accessibilita, consistenza visuale e regressioni funzionali.
- Ottimizzazione payload frontend e pulizia duplicazioni.

### 3. Priorita e criteri di accettazione
Priorita:
- P0: bug e incoerenze tecniche, componenti legacy.
- P1: design system e refactor pagine ad alta frequenza.
- P2: rifiniture avanzate e ottimizzazioni secondarie.

Criteri di accettazione:
- Nessuna sintassi legacy incompatibile nelle pagine migrate.
- Riduzione significativa di stili inline nelle pagine core.
- Coerenza visiva trasversale tra dashboard, form, liste e autenticazione.
- UX mobile usabile senza perdita funzionale.
- Nessuna regressione sui flussi principali (login, CRUD articoli, movimenti, backup).

Stima indicativa:
- 10-14 giorni lavorativi con rilascio progressivo per blocchi.

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
