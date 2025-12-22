# ============================================================================
# Script di Ripristino MySQL per XAMPP
# ============================================================================

Write-Host "=== RIPRISTINO MySQL XAMPP ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verifica che XAMPP sia installato
if (-not (Test-Path "C:\xampp\mysql")) {
    Write-Host "ERRORE: XAMPP non trovato in C:\xampp" -ForegroundColor Red
    exit 1
}

# 2. Ferma MySQL se in esecuzione
Write-Host "1. Fermando processi MySQL..." -ForegroundColor Yellow
Get-Process mysqld -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 3. Backup cartella data attuale
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "C:\xampp\mysql\data_backup_$timestamp"
Write-Host "2. Creando backup in: $backupPath" -ForegroundColor Yellow
Copy-Item -Path "C:\xampp\mysql\data" -Destination $backupPath -Recurse -Force

# 4. Rimuovi cartella data corrotta
Write-Host "3. Rimuovendo cartella data corrotta..." -ForegroundColor Yellow
Remove-Item -Path "C:\xampp\mysql\data" -Recurse -Force

# 5. Copia backup pulito
Write-Host "4. Ripristinando backup pulito XAMPP..." -ForegroundColor Yellow
Copy-Item -Path "C:\xampp\mysql\backup" -Destination "C:\xampp\mysql\data" -Recurse -Force

# 6. Copia database utente se esisteva
$userDB = Join-Path $backupPath "magazzino_ricambi"
if (Test-Path $userDB) {
    Write-Host "5. Recuperando database magazzino_ricambi..." -ForegroundColor Yellow
    Copy-Item -Path $userDB -Destination "C:\xampp\mysql\data" -Recurse -Force
} else {
    Write-Host "5. Database magazzino_ricambi non trovato (sarà ricreato)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== COMPLETATO ===" -ForegroundColor Green
Write-Host ""
Write-Host "PROSSIMI PASSI:" -ForegroundColor Cyan
Write-Host "1. Avvia MySQL dal pannello XAMPP"
Write-Host "2. Esegui: mysql -u root < database_creation.sql"
Write-Host "3. Esegui: python manage.py migrate"
Write-Host "4. Esegui: python manage.py populate_db"
Write-Host ""
Write-Host "Backup salvato in: $backupPath" -ForegroundColor Gray
