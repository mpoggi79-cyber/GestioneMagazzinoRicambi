# Guida Toolset di Sviluppo

Progetto: Gestione Magazzino Ricambi Goose
Stack: Django 5.2, MySQL 10.4, Python 3.14
Data: 9 maggio 2026

## Obiettivo
Questa guida definisce un set pratico di strumenti per sviluppo, debug, test, database e documentazione, con esempi diretti di utilizzo.

## Toolset consigliati

### 1. Sviluppo Django quotidiano
Strumenti:
- Python + Pylance
- Django extension
- Black formatter
- Ruff
- GitLens

Necessita: avviare il progetto
Comando:
```powershell
python manage.py runserver
```

Necessita: creare e applicare migrazioni
Comandi:
```powershell
python manage.py makemigrations
python manage.py migrate
```

Necessita: verificare stato migrazioni
Comando:
```powershell
python manage.py showmigrations
```

Necessita: formattare codice Python
Comando:
```powershell
black .
```

Necessita: controllare problemi lint
Comando:
```powershell
ruff check .
```

Necessita: correggere automaticamente warning correggibili
Comando:
```powershell
ruff check . --fix
```

## 2. Debug e analisi problemi
Strumenti:
- Debugger Python
- Error Lens
- MySQL client

Necessita: entrare in debug rapido lato server
Comando:
```powershell
python manage.py runserver
```
Poi usare breakpoint in VS Code e avviare debug con F5.

Necessita: shell Django per ispezione dati
Comando:
```powershell
python manage.py shell
```

Esempio in shell:
```python
from magazzino.models import MovimentoMagazzino, PezzoRicambio
MovimentoMagazzino.objects.count()
PezzoRicambio.objects.first()
```

Necessita: controllare connessione DB
Comando:
```powershell
python test_db_connection.py
```

## 3. Test e quality gate
Strumenti:
- Test Explorer
- SonarLint
- Ruff
- Black

Necessita: eseguire tutti i test
Comando:
```powershell
python manage.py test
```

Necessita: test solo app magazzino
Comando:
```powershell
python manage.py test magazzino
```

Necessita: test verbosi
Comando:
```powershell
python manage.py test -v 2
```

Workflow consigliato prima di commit:
1. `black .`
2. `ruff check . --fix`
3. `python manage.py test`

## 4. Database e backup
Strumenti:
- MySQL Client
- SQLTools
- SQL formatter

Necessita: creare backup applicativo
Comando:
```powershell
python manage.py create_backup
```

Necessita: ripristino da backup
Comando:
```powershell
python manage.py restore_backup
```

Necessita: reset DB completo da schema (attenzione: distruttivo)
Comando:
```powershell
mysql -u root < database_creation.sql
```

Necessita: ricaricare dati demo
Comando:
```powershell
python manage.py populate_db
```

## 5. Documentazione e API
Strumenti:
- Markdown All in One
- Markdown Preview
- Thunder Client
- YAML

Necessita: anteprima documento markdown
Comando/azione:
- Apri file `.md`
- `Ctrl+K`, poi `V`

Necessita: test endpoint HTTP veloce da terminale
Comando:
```powershell
curl http://127.0.0.1:8000/
```

Necessita: test endpoint con metodo POST
Comando:
```powershell
curl -X POST http://127.0.0.1:8000/login/
```

## Uso rapido con task già presenti nel workspace
Puoi lanciare rapidamente:
- Django: Runserver
- Django: Migrate
- Django: Populate DB
- Django: Test
- Django: Shell

---

## Memoria Tecnica e Workspace

Per tracciare lo sviluppo in modo ordinato:

1. Usa il documento centrale di memoria tecnica:
- [MEMORIA_TECNICA_SVILUPPO.md](MEMORIA_TECNICA_SVILUPPO.md)

2. Mantieni i file di configurazione workspace puliti (senza changelog narrativo):
- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/launch.json`

3. Riporta nei manuali solo sintesi operative, evitando duplicazioni.

Percorso: Terminal > Run Task

## Configurazione applicata in questa implementazione
Sono state applicate impostazioni conservative in `.vscode/settings.json` per:
- type checking base con Pylance
- formatter Python predefinito Black
- mantenimento del comportamento attuale senza format on save globale

## Profilo operativo consigliato
Per questa codebase:
1. Avvio: `python manage.py runserver`
2. Sviluppo: Black + Ruff durante la modifica
3. Verifica: `python manage.py test`
4. Backup periodico: `python manage.py create_backup`
5. Prima del push: black, ruff, test

## Troubleshooting essenziale
Necessita: modulo non trovato
Comandi:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Necessita: migrazioni incoerenti
Comandi:
```powershell
python manage.py migrate --plan
python manage.py showmigrations
```

Necessita: porta 8000 occupata
Comando:
```powershell
python manage.py runserver 8001
```
