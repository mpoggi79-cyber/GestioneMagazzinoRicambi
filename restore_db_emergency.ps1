# ============================================================================
# SCRIPT EMERGENZA: Ripristino Database senza Django
# ============================================================================
# USO: Quando il database è completamente corrotto e non puoi accedere
#      all'applicazione Django per fare ripristino dall'interfaccia web.
#
# ESECUZIONE: .\restore_db_emergency.ps1
# ============================================================================

param(
    [string]$BackupFile = "",
    [switch]$ListBackups = $false,
    [switch]$Latest = $false,
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

# Configurazione
$PROJECT_ROOT = $PSScriptRoot
$BACKUP_DIR = Join-Path $PROJECT_ROOT "backups"
$MYSQL_BIN = "C:\xampp\mysql\bin"
$DB_NAME = "gmr"  # Nome database da settings.py
$DB_USER = "root"
$DB_PASSWORD = ""  # Password vuota di default XAMPP

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "  RIPRISTINO DATABASE EMERGENZA" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Verifica che MySQL esista
if (-not (Test-Path (Join-Path $MYSQL_BIN "mysql.exe"))) {
    Write-Host "`n[ERROR] MySQL non trovato in: $MYSQL_BIN" -ForegroundColor Red
    Write-Host "Modifica la variabile `$MYSQL_BIN nello script se MySQL è altrove.`n" -ForegroundColor Yellow
    exit 1
}

# Verifica cartella backup
if (-not (Test-Path $BACKUP_DIR)) {
    Write-Host "`n[ERROR] Cartella backup non trovata: $BACKUP_DIR" -ForegroundColor Red
    exit 1
}

# ============================================================================
# FUNZIONE: Lista backup disponibili
# ============================================================================
function Get-Backups {
    $backups = Get-ChildItem -Path $BACKUP_DIR -Filter "backup_*.sql.gz" | 
        Sort-Object LastWriteTime -Descending
    
    if ($backups.Count -eq 0) {
        Write-Host "`n[WARNING] Nessun backup trovato in: $BACKUP_DIR" -ForegroundColor Yellow
        return @()
    }
    
    return $backups
}

# ============================================================================
# COMANDO: --ListBackups
# ============================================================================
if ($ListBackups) {
    Write-Host "`n[BACKUP DISPONIBILI]`n" -ForegroundColor Green
    
    $backups = Get-Backups
    if ($backups.Count -eq 0) { exit 0 }
    
    $i = 1
    foreach ($backup in $backups) {
        $sizeMB = [math]::Round($backup.Length / 1MB, 2)
        $age = (Get-Date) - $backup.LastWriteTime
        $ageDays = [math]::Floor($age.TotalDays)
        
        Write-Host "$i. $($backup.Name)" -ForegroundColor Cyan
        Write-Host "   Data: $($backup.LastWriteTime.ToString('dd/MM/yyyy HH:mm:ss'))" -ForegroundColor Gray
        Write-Host "   Dimensione: $sizeMB MB | Età: $ageDays giorni fa`n" -ForegroundColor Gray
        $i++
    }
    
    Write-Host "[INFO] Per ripristinare: .\restore_db_emergency.ps1 -BackupFile <filename>`n" -ForegroundColor Yellow
    exit 0
}

# ============================================================================
# DETERMINA FILE DA RIPRISTINARE
# ============================================================================
$selectedBackup = $null

if ($Latest) {
    $backups = Get-Backups
    if ($backups.Count -eq 0) { exit 1 }
    
    $selectedBackup = $backups[0]
    Write-Host "`n[INFO] Backup più recente selezionato: $($selectedBackup.Name)" -ForegroundColor Cyan
}
elseif ($BackupFile -ne "") {
    $selectedBackup = Get-Item (Join-Path $BACKUP_DIR $BackupFile) -ErrorAction SilentlyContinue
    
    if ($null -eq $selectedBackup) {
        Write-Host "`n[ERROR] File non trovato: $BackupFile" -ForegroundColor Red
        Write-Host "Usa -ListBackups per vedere i backup disponibili.`n" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "`n[ERROR] Specifica un file di backup!" -ForegroundColor Red
    Write-Host "`nOpzioni:" -ForegroundColor Yellow
    Write-Host "  -ListBackups           : Elenca tutti i backup" -ForegroundColor Gray
    Write-Host "  -Latest                : Ripristina il più recente" -ForegroundColor Gray
    Write-Host "  -BackupFile <filename> : Ripristina file specifico`n" -ForegroundColor Gray
    exit 1
}

# ============================================================================
# CONFERMA OPERAZIONE
# ============================================================================
if (-not $Force) {
    Write-Host "`n" -NoNewline
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ATTENZIONE - OPERAZIONE CRITICA!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "`nStai per ripristinare:" -ForegroundColor Yellow
    Write-Host "  Database: $DB_NAME" -ForegroundColor White
    Write-Host "  File    : $($selectedBackup.Name)" -ForegroundColor White
    Write-Host "  Data    : $($selectedBackup.LastWriteTime.ToString('dd/MM/yyyy HH:mm:ss'))" -ForegroundColor White
    Write-Host "`n[WARNING] TUTTI I DATI ATTUALI VERRANNO SOVRASCRITTI!" -ForegroundColor Red
    Write-Host "[WARNING] OPERAZIONE IRREVERSIBILE!`n" -ForegroundColor Red
    
    $confirmation = Read-Host "Digita 'RESTORE' per confermare"
    
    if ($confirmation -ne "RESTORE") {
        Write-Host "`n[CANCELLED] Operazione annullata.`n" -ForegroundColor Yellow
        exit 0
    }
}

# ============================================================================
# ESEGUI RIPRISTINO
# ============================================================================
Write-Host "`n[RESTORE] Avvio ripristino...`n" -ForegroundColor Cyan

try {
    # Step 1: Decomprimi file temporaneo
    Write-Host "[1/4] Decompressione backup..." -ForegroundColor Yellow
    
    $tempSqlFile = [System.IO.Path]::GetTempFileName() + ".sql"
    
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $gzipStream = New-Object System.IO.FileStream($selectedBackup.FullName, [System.IO.FileMode]::Open)
    $outputStream = New-Object System.IO.FileStream($tempSqlFile, [System.IO.FileMode]::Create)
    $gzipDecompressor = New-Object System.IO.Compression.GZipStream($gzipStream, [System.IO.Compression.CompressionMode]::Decompress)
    
    $gzipDecompressor.CopyTo($outputStream)
    
    $outputStream.Close()
    $gzipDecompressor.Close()
    $gzipStream.Close()
    
    Write-Host "      [OK] File decompresso: $tempSqlFile" -ForegroundColor Green
    
    # Step 2: Verifica connessione MySQL
    Write-Host "[2/4] Verifica connessione MySQL..." -ForegroundColor Yellow
    
    $mysqlExe = Join-Path $MYSQL_BIN "mysql.exe"
    $testCmd = "SELECT 'OK' as status;"
    
    # Esegui test connessione MySQL (il risultato non viene utilizzato, solo il codice di uscita)
    & $mysqlExe --user=$DB_USER --password=$DB_PASSWORD -e $testCmd 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        throw "MySQL non risponde. Verifica che XAMPP sia avviato."
    }
    
    Write-Host "      [OK] MySQL attivo" -ForegroundColor Green
    
    # Step 3: Importa SQL
    Write-Host "[3/4] Importazione dati in database '$DB_NAME'..." -ForegroundColor Yellow
    Write-Host "      (Questo potrebbe richiedere alcuni minuti...)" -ForegroundColor Gray
    
    $importResult = Get-Content $tempSqlFile | & $mysqlExe --user=$DB_USER --password=$DB_PASSWORD $DB_NAME 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante l'importazione:`n$importResult"
    }
    
    Write-Host "      [OK] Dati importati con successo" -ForegroundColor Green
    
    # Step 4: Pulizia file temporaneo
    Write-Host "[4/4] Pulizia file temporanei..." -ForegroundColor Yellow
    Remove-Item $tempSqlFile -Force
    Write-Host "      [OK] File temporaneo rimosso" -ForegroundColor Green
    
    # SUCCESSO
    Write-Host "`n" -NoNewline
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  RIPRISTINO COMPLETATO CON SUCCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`n[NEXT STEPS]" -ForegroundColor Cyan
    Write-Host "1. Riavvia il server Django se è in esecuzione" -ForegroundColor White
    Write-Host "2. Verifica accesso all'applicazione web" -ForegroundColor White
    Write-Host "3. Controlla i log per eventuali errori`n" -ForegroundColor White
}
catch {
    Write-Host "`n[ERROR] Ripristino fallito!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`n[TROUBLESHOOTING]" -ForegroundColor Yellow
    Write-Host "- Verifica che MySQL sia in esecuzione (XAMPP)" -ForegroundColor Gray
    Write-Host "- Verifica le credenziali database in settings.py" -ForegroundColor Gray
    Write-Host "- Controlla i log di MySQL per dettagli`n" -ForegroundColor Gray
    exit 1
}
