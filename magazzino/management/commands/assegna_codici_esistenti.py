"""
Management command per assegnare il codice interno univoco (ART-XXXXX)
agli articoli esistenti allineandolo alla stessa regola dei nuovi record.
Il codice viene derivato dalla chiave primaria (id_articolo) dell'articolo,
garantendo che sia stabile e non generi collisioni con i nuovi inserimenti.

Eseguire UNA SOLA VOLTA dopo l'attivazione del sistema di codici automatici:
    python manage.py assegna_codici_esistenti

Opzioni:
    --dry-run    Mostra cosa verrebbe fatto senza applicare modifiche
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from magazzino.codici import genera_codice_articolo
from magazzino.models import PezzoRicambio
import logging

logger = logging.getLogger(__name__)


CODICE_ARTICOLO_PLACEHOLDER_PREFIX = '__TMP_ART_CMD__'


class Command(BaseCommand):
    help = 'Allinea il codice interno univoco (ART-XXXXX) di tutti gli articoli esistenti'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra le modifiche senza applicarle',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('--- MODALITA\' DRY-RUN: nessuna modifica verrà applicata ---'))

        articoli_da_allineare = []
        for articolo in PezzoRicambio.objects.order_by('id_articolo'):
            nuovo_codice = genera_codice_articolo(articolo.id_articolo)
            if articolo.codice_interno != nuovo_codice:
                articoli_da_allineare.append((articolo.id_articolo, articolo.descrizione, nuovo_codice))

        totale = len(articoli_da_allineare)

        if totale == 0:
            self.stdout.write(self.style.SUCCESS('Tutti gli articoli hanno già un codice interno allineato. Nulla da fare.'))
            return

        self.stdout.write(f'Trovati {totale} articoli da allineare.')

        for id_articolo, descrizione, nuovo_codice in articoli_da_allineare:
            self.stdout.write(f'  id={id_articolo:5d} | "{descrizione[:40]}" → {nuovo_codice}')

        if not dry_run:
            with transaction.atomic():
                for id_articolo, _, _ in articoli_da_allineare:
                    PezzoRicambio.objects.filter(id_articolo=id_articolo).update(
                        codice_interno=f"{CODICE_ARTICOLO_PLACEHOLDER_PREFIX}{id_articolo:05d}"
                    )

                for id_articolo, _, nuovo_codice in articoli_da_allineare:
                    PezzoRicambio.objects.filter(id_articolo=id_articolo).update(
                        codice_interno=nuovo_codice
                    )

        # Riepilogo finale
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'DRY-RUN completato: {totale} articoli verrebbero aggiornati.'
            ))
            self.stdout.write(self.style.WARNING(
                'Esegui senza --dry-run per applicare le modifiche.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Completato: {totale} articoli aggiornati.'
            ))
            logger.info(f'[CODICI] Allineati {totale} codici interni articolo.')
