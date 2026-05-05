#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script di attivazione Virtual Environment - Gestione Magazzino Ricambi
.DESCRIPTION
    Attiva il virtual environment di Python per il progetto Django
.EXAMPLE
    .\activate_venv.ps1
    Attiva il venv e mostra i comandi disponibili
#>

[CmdletBinding()]
param()

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPath = Join-Path $scriptPath "venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  GESTIONE MAGAZZINO RICAMBI - Virtual Environment Activation" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# Controlla se venv esiste
if (-not (Test-Path $activateScript)) {
    Write-Host "[ERRORE] Virtual environment non trovato!" -ForegroundColor Red
    Write-Host "   Percorso atteso: $venvPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Eseguire per ricrearlo:" -ForegroundColor Yellow
    Write-Host "   python -m venv venv --upgrade-deps" -ForegroundColor Green
    Write-Host "   .\venv\Scripts\pip.exe install -r requirements.txt" -ForegroundColor Green
    Write-Host ""
    exit 1
}

# Attiva venv
try {
    & $activateScript
    Write-Host "[OK] Virtual Environment attivato!" -ForegroundColor Green
    Write-Host ""
    
    # Mostra info ambiente
    $pythonVersion = python --version
    Write-Host "[PYTHON] $pythonVersion" -ForegroundColor Cyan
    
    $djangoVersion = python -c "import django; print(f'Django {django.__version__}')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[DJANGO] $djangoVersion" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "Comandi disponibili:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Django:" -ForegroundColor White
    Write-Host "    - python manage.py runserver         -> Avvia server (porta 8000)" -ForegroundColor Gray
    Write-Host "    - python manage.py migrate           -> Applica migrazioni database" -ForegroundColor Gray
    Write-Host "    - python manage.py shell             -> Django shell interattivo" -ForegroundColor Gray
    Write-Host "    - python manage.py test magazzino    -> Esegui test suite" -ForegroundColor Gray
    Write-Host "    - python manage.py populate_db       -> Carica dati di test" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Database:" -ForegroundColor White
    Write-Host "    - python test_db_connection.py       -> Verifica connessione MySQL" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Admin Panel:" -ForegroundColor White
    Write-Host "    - http://localhost:8000/admin/       -> URL (utente: admin / admin)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host ""
}
catch {
    Write-Host "[ERRORE] Impossibile attivare venv:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
