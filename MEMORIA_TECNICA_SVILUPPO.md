# Memoria Tecnica Sviluppo

Documento centrale di memoria tecnica interna.

Scopo:
- Conservare in modo strutturato le decisioni e gli interventi effettuati durante lo sviluppo.
- Evitare duplicazioni tra manuali.
- Mantenere traccia operativa delle modifiche con impatto su UX, backend e convenzioni.

Data ultimo aggiornamento: 10/05/2026

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
