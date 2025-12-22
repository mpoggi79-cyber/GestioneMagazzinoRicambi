"""
Management command per ripristinare un backup del database da terminale.

Uso emergenza quando l'interfaccia web non è accessibile:
    python manage.py restore_backup <filename>
    python manage.py restore_backup --list
    python manage.py restore_backup --latest
"""

from django.core.management.base import BaseCommand, CommandError
from magazzino.backup_manager import BackupManager
from pathlib import Path
import sys


class Command(BaseCommand):
    help = 'Ripristina un backup del database (USO EMERGENZA)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            nargs='?',
            type=str,
            help='Nome del file di backup da ripristinare'
        )
        
        parser.add_argument(
            '--list',
            action='store_true',
            help='Lista tutti i backup disponibili'
        )
        
        parser.add_argument(
            '--latest',
            action='store_true',
            help='Ripristina il backup più recente'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Salta la conferma interattiva (PERICOLOSO!)'
        )
    
    def handle(self, *args, **options):
        backup_mgr = BackupManager()
        
        # Lista backup disponibili
        if options['list']:
            self.stdout.write(self.style.SUCCESS('\n📦 BACKUP DISPONIBILI:\n'))
            backups = backup_mgr.list_backups()
            
            if not backups:
                self.stdout.write(self.style.WARNING('Nessun backup trovato.'))
                return
            
            for i, backup in enumerate(backups, 1):
                timestamp = backup['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
                size = f"{backup['size_mb']:.2f} MB"
                age = f"{backup['age_days']} giorni fa"
                
                self.stdout.write(
                    f"{i}. {backup['filename']}\n"
                    f"   Data: {timestamp} | Dimensione: {size} | Età: {age}\n"
                )
            
            return
        
        # Determina quale backup ripristinare
        filename = None
        
        if options['latest']:
            backups = backup_mgr.list_backups()
            if not backups:
                raise CommandError('Nessun backup disponibile.')
            filename = backups[0]['filename']
            self.stdout.write(f"Ripristino backup più recente: {filename}")
        elif options['filename']:
            filename = options['filename']
        else:
            raise CommandError(
                'Specifica un filename o usa --list per vedere i backup disponibili, '
                'oppure --latest per ripristinare il più recente.'
            )
        
        # Conferma operazione (se non --force)
        if not options['force']:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  ATTENZIONE - OPERAZIONE CRITICA!\n'
                f'\nStai per ripristinare:\n'
                f'  File: {filename}\n'
                f'\n❌ TUTTI I DATI ATTUALI VERRANNO SOVRASCRITTI!\n'
                f'❌ OPERAZIONE IRREVERSIBILE!\n'
            ))
            
            confirm = input('\nDigita "RESTORE" per confermare: ')
            
            if confirm != 'RESTORE':
                self.stdout.write(self.style.ERROR('Operazione annullata.'))
                return
        
        # Esegui ripristino
        self.stdout.write(self.style.WARNING('\n🔄 Ripristino in corso...'))
        
        success, message = backup_mgr.restore_backup(filename)
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'\n✅ {message}'))
            self.stdout.write(self.style.SUCCESS('\n💡 Riavvia il server Django per applicare le modifiche.'))
        else:
            raise CommandError(f'Errore durante il ripristino: {message}')
