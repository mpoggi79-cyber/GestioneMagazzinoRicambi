"""
Models per la gestione degli utenti e autenticazione.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class RuoloUtente(models.TextChoices):
    """Ruoli disponibili per gli utenti"""
    ADMIN = 'ADMIN', _('Amministratore')
    GESTORE_MAGAZZINO = 'GESTORE_MAGAZZINO', _('Gestore Magazzino')
    OPERATORE = 'OPERATORE', _('Operatore')
    VISUALIZZATORE = 'VISUALIZZATORE', _('Visualizzatore')


class ProfiloUtente(models.Model):
    """Profilo personalizzato per gli utenti"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name=_('Utente'),
        related_name='profilo'
    )
    
    ruolo = models.CharField(
        max_length=20,
        choices=RuoloUtente.choices,
        default=RuoloUtente.OPERATORE,
        verbose_name=_('Ruolo'),
        help_text=_('Ruolo dell\'utente nel sistema')
    )
    
    dipartimento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Dipartimento'),
        help_text=_('Dipartimento di appartenenza')
    )
    
    numero_dipendente = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('Numero Dipendente')
    )
    
    attivo = models.BooleanField(
        default=True,
        verbose_name=_('Attivo'),
        help_text=_('Utente attivo o disattivato')
    )
    
    ultimo_accesso = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Ultimo Accesso'),
        auto_now=True
    )
    
    data_creazione = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data Creazione')
    )
    
    data_modifica = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Data Modifica')
    )
    
    class Meta:
        verbose_name = _('Profilo Utente')
        verbose_name_plural = _('Profili Utenti')
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_ruolo_display()}"
    
    def è_admin(self):
        """Verifica se l'utente è admin"""
        return self.ruolo == RuoloUtente.ADMIN
    
    def è_gestore_magazzino(self):
        """Verifica se l'utente è gestore magazzino"""
        return self.ruolo == RuoloUtente.GESTORE_MAGAZZINO
    
    def è_operatore(self):
        """Verifica se l'utente è operatore"""
        return self.ruolo == RuoloUtente.OPERATORE
    
    def può_modificare_dati(self):
        """Verifica se può modificare i dati"""
        return self.ruolo in [RuoloUtente.ADMIN, RuoloUtente.GESTORE_MAGAZZINO]
    
    def può_visualizzare_tutti_movimenti(self):
        """Verifica se può visualizzare tutti i movimenti"""
        return self.ruolo in [RuoloUtente.ADMIN, RuoloUtente.GESTORE_MAGAZZINO]


class LogAccesso(models.Model):
    """Log di accesso al sistema"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Utente'),
        related_name='accessi'
    )
    
    data_accesso = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data Accesso')
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name=_('Indirizzo IP'),
        blank=True,
        null=True
    )
    
    user_agent = models.TextField(
        verbose_name=_('User Agent'),
        blank=True,
        null=True,
        help_text=_('Browser e sistema operativo')
    )
    
    success = models.BooleanField(
        default=True,
        verbose_name=_('Accesso Riuscito'),
        help_text=_('Indica se l\'accesso è stato riuscito')
    )
    
    motivo_fallimento = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Motivo Fallimento'),
        help_text=_('Motivo del fallimento dell\'accesso')
    )
    
    class Meta:
        db_table = 'log_accessi'
        verbose_name = _('Log Accesso')
        verbose_name_plural = _('Log Accessi')
        ordering = ['-data_accesso']
        indexes = [
            models.Index(fields=['-data_accesso']),
            models.Index(fields=['user', '-data_accesso']),
        ]
    
    def __str__(self):
        status = "✅ Riuscito" if self.success else "❌ Fallito"
        return f"{self.user.username} - {self.data_accesso.strftime('%d/%m/%Y %H:%M')} - {status}"
