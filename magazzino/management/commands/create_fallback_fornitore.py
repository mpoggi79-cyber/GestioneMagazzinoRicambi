"""
Comando Django per creare il fornitore fallback "Non Specificato"
Uso: python manage.py create_fallback_fornitore
"""
from django.core.management.base import BaseCommand
from magazzino.models import Fornitore


class Command(BaseCommand):
    help = 'Crea il fornitore fallback "Non Specificato"'

    def handle(self, *args, **options):
        fornitore, created = Fornitore.objects.get_or_create(
            id_fornitore=999,
            defaults={
                'ragione_sociale': 'Non Specificato',
                'telefono': '',
                'email': '',
                'indirizzo': '',
                'cap': '',
                'citta': '',
                'provincia': '',
                'partita_iva': '',
                'note': 'Fornitore generico usato quando si elimina un fornitore con movimenti associati. NON ELIMINARE.',
                'tempo_medio_consegna_giorni': 0,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Fornitore fallback creato: {fornitore.ragione_sociale} (ID: {fornitore.id_fornitore})"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Fornitore fallback gia' esistente: {fornitore.ragione_sociale} (ID: {fornitore.id_fornitore})"
            ))
