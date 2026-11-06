"""
Apre Chrome sul portale SCM per fare il login a mano (Microsoft + MFA) e salva la sessione.
"""
from django.core.management.base import BaseCommand, CommandError

from magazzino import scm_portale


class Command(BaseCommand):
    help = 'Login manuale al portale ricambi SCM: la sessione viene riusata per recuperare i dati degli articoli'

    def handle(self, *args, **options):
        self.stdout.write(
            'Si apre Chrome sul portale SCM: effettua l\'accesso con il tuo account Microsoft. '
            'La sessione viene salvata appena compare "BENVENUTO ..." (attesa massima 5 minuti).'
        )

        try:
            autenticato = scm_portale.esegui_login_manuale()
        except scm_portale.ErroreSCM as errore:
            raise CommandError(str(errore))

        if not autenticato:
            raise CommandError('Accesso non riconosciuto: la sessione non è stata salvata. Riprova.')
        self.stdout.write(self.style.SUCCESS('Sessione SCM salvata.'))
