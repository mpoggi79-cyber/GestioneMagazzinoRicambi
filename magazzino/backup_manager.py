"""
Utility per la gestione dei backup del database MySQL.
"""

import os
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class BackupManager:
    """Gestione backup del database"""
    
    def __init__(self):
        """Inizializza il manager con le configurazioni dal database"""
        from .models import Configurazione
        
        # Carica configurazioni dal database o usa default
        self.backup_dir = Path(
            Configurazione.get_value('backup_dir', str(settings.BASE_DIR / 'backups'))
        )
        self.retention_days = Configurazione.get_value('backup_retention_days', 30)
        self.mysql_bin_path = Configurazione.get_value('mysql_bin_path', r'C:\xampp\mysql\bin')
        
        # Crea directory backup se non esiste
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Credenziali database da settings
        db_settings = settings.DATABASES['default']
        self.db_name = db_settings['NAME']
        self.db_user = db_settings['USER']
        self.db_password = db_settings['PASSWORD']
        self.db_host = db_settings.get('HOST', 'localhost')
        self.db_port = db_settings.get('PORT', '3306')
    
    def create_backup(self):
        """
        Crea un nuovo backup compresso del database.
        
        Returns:
            tuple: (success: bool, filepath: Path, message: str)
        """
        try:
            # Nome file con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_{self.db_name}_{timestamp}.sql'
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"Creazione backup: {backup_filename}")
            
            # Percorso mysqldump dal database o settings
            mysqldump_exe = os.path.join(self.mysql_bin_path, 'mysqldump.exe')
            
            # Comando mysqldump
            cmd = [
                mysqldump_exe,
                f'--user={self.db_user}',
                f'--password={self.db_password}',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--add-drop-table',
                '--extended-insert',
                self.db_name
            ]
            
            # Esegui mysqldump
            with open(backup_path, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode != 0:
                error_msg = result.stderr
                logger.error(f"Errore mysqldump: {error_msg}")
                return False, None, f"Errore durante il backup: {error_msg}"
            
            # Comprimi con gzip
            compressed_path = backup_path.with_suffix('.sql.gz')
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Rimuovi file non compresso
            backup_path.unlink()
            
            # Dimensione file
            size_mb = compressed_path.stat().st_size / (1024 * 1024)
            
            logger.info(f"Backup creato: {compressed_path.name} ({size_mb:.2f} MB)")
            
            return True, compressed_path, f"Backup creato con successo ({size_mb:.2f} MB)"
            
        except FileNotFoundError:
            error_msg = "mysqldump non trovato. Assicurati che MySQL sia installato e nel PATH."
            logger.error(error_msg)
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Errore durante il backup: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, None, error_msg
    
    def list_backups(self):
        """
        Lista tutti i backup disponibili.
        
        Returns:
            list: Lista di dict con info sui backup
        """
        backups = []
        
        # Pattern più flessibile per catturare tutti i backup
        for backup_file in sorted(self.backup_dir.glob('backup_*.sql.gz'), reverse=True):
            try:
                # Estrai timestamp dal nome (backup_GMR_20251205_235438.sql.gz)
                parts = backup_file.stem.replace('.sql', '').split('_')
                # Cerca gli ultimi due elementi che sembrano data e ora
                date_str = None
                time_str = None
                
                for i in range(len(parts) - 1, 0, -1):
                    if len(parts[i]) == 6 and parts[i].isdigit():  # HHMMSS
                        time_str = parts[i]
                        if i > 0 and len(parts[i-1]) == 8 and parts[i-1].isdigit():  # YYYYMMDD
                            date_str = parts[i-1]
                            break
                
                if date_str and time_str:
                    timestamp = datetime.strptime(f"{date_str}_{time_str}", '%Y%m%d_%H%M%S')
                else:
                    timestamp = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                # Info file
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                
                backups.append({
                    'filename': backup_file.name,
                    'filepath': backup_file,
                    'timestamp': timestamp,
                    'size_mb': size_mb,
                    'age_days': (datetime.now() - timestamp).days
                })
                
            except Exception as e:
                logger.warning(f"Errore lettura backup {backup_file}: {e}")
        
        return backups
    
    def delete_backup(self, filename):
        """
        Elimina un backup specifico.
        
        Args:
            filename: Nome del file da eliminare
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            backup_path = self.backup_dir / filename
            
            if not backup_path.exists():
                return False, "File non trovato"
            
            # Verifica che sia un file di backup valido
            if not backup_path.name.startswith('backup_') or not backup_path.suffix == '.gz':
                return False, "File non valido"
            
            backup_path.unlink()
            logger.info(f"Backup eliminato: {filename}")
            
            return True, "Backup eliminato con successo"
            
        except Exception as e:
            error_msg = f"Errore durante l'eliminazione: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def cleanup_old_backups(self):
        """
        Elimina backup più vecchi di retention_days.
        
        Returns:
            tuple: (count: int, message: str)
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            removed_count = 0
            
            for backup in self.list_backups():
                if backup['timestamp'] < cutoff_date:
                    success, _ = self.delete_backup(backup['filename'])
                    if success:
                        removed_count += 1
            
            logger.info(f"Pulizia completata: {removed_count} backup eliminati")
            
            return removed_count, f"{removed_count} backup obsoleti eliminati"
            
        except Exception as e:
            error_msg = f"Errore durante la pulizia: {str(e)}"
            logger.error(error_msg)
            return 0, error_msg
    
    def restore_backup(self, filename):
        """
        Ripristina un backup (DA USARE CON CAUTELA!).
        
        Args:
            filename: Nome del file di backup
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            backup_path = self.backup_dir / filename
            
            if not backup_path.exists():
                return False, "File di backup non trovato"
            
            logger.warning(f"[WARNING] RESTORE backup: {filename}")
            
            # Percorso mysql dal database o settings
            mysql_exe = os.path.join(self.mysql_bin_path, 'mysql.exe')
            
            # Decomprimi temporaneamente
            sql_path = backup_path.with_suffix('')
            with gzip.open(backup_path, 'rb') as f_in:
                with open(sql_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Comando mysql restore
            cmd = [
                mysql_exe,
                f'--user={self.db_user}',
                f'--password={self.db_password}',
                f'--host={self.db_host}',
                f'--port={self.db_port}',
                self.db_name
            ]
            
            with open(sql_path, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # Rimuovi file decompresso
            sql_path.unlink()
            
            if result.returncode != 0:
                error_msg = result.stderr
                logger.error(f"Errore restore: {error_msg}")
                return False, f"Errore durante il ripristino: {error_msg}"
            
            logger.info(f"Backup ripristinato: {filename}")
            
            return True, "Database ripristinato con successo"
            
        except Exception as e:
            error_msg = f"Errore durante il ripristino: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
