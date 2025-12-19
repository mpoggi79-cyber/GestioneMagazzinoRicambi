"""
Signals per la gestione automatica dei profili utenti.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProfiloUtente


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automaticamente un ProfiloUtente quando viene creato un nuovo User.
    """
    if created:
        ProfiloUtente.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva il profilo quando l'User viene salvato.
    """
    if hasattr(instance, 'profilo'):
        instance.profilo.save()
