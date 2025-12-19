"""
Configurazione del pannello admin per la gestione degli utenti.
"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import ProfiloUtente, LogAccesso


# ============================================================================
# PROFILO UTENTE - Inline admin per User
# ============================================================================

class ProfiloUtenteInline(admin.StackedInline):
    """Inline per gestire il profilo utente da User admin"""
    model = ProfiloUtente
    fields = ('ruolo', 'dipartimento', 'numero_dipendente', 'attivo', 'ultimo_accesso', 'data_creazione', 'data_modifica')
    readonly_fields = ('ultimo_accesso', 'data_creazione', 'data_modifica')
    extra = 0


# ============================================================================
# USER ADMIN PERSONALIZZATO - Unregister e re-register
# ============================================================================

# Unregister il User admin di default di Django
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizzato per User con Profilo integrato"""
    inlines = [ProfiloUtenteInline]
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_ruolo', 'is_active', 'last_login')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'profilo__ruolo')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    
    def get_ruolo(self, obj):
        """Visualizza il ruolo dell'utente dalla lista"""
        try:
            return obj.profilo.get_ruolo_display()
        except ProfiloUtente.DoesNotExist:
            return "-"
    get_ruolo.short_description = _('Ruolo')
    get_ruolo.admin_order_field = 'profilo__ruolo'


# ============================================================================
# PROFILO UTENTE
# ============================================================================

@admin.register(ProfiloUtente)
class ProfiloUtenteAdmin(admin.ModelAdmin):
    """Admin per ProfiloUtente"""
    list_display = ('user', 'ruolo', 'dipartimento', 'numero_dipendente', 'attivo', 'ultimo_accesso')
    list_filter = ('ruolo', 'attivo', 'data_creazione')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'numero_dipendente')
    readonly_fields = ('ultimo_accesso', 'data_creazione', 'data_modifica')
    
    fieldsets = (
        (_('Utente'), {
            'fields': ('user',)
        }),
        (_('Informazioni Profilo'), {
            'fields': ('ruolo', 'dipartimento', 'numero_dipendente')
        }),
        (_('Stato'), {
            'fields': ('attivo',)
        }),
        (_('Timestamp'), {
            'fields': ('ultimo_accesso', 'data_creazione', 'data_modifica'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# LOG ACCESSI
# ============================================================================

@admin.register(LogAccesso)
class LogAccessoAdmin(admin.ModelAdmin):
    """Admin per i log di accesso"""
    list_display = ('user', 'data_accesso', 'ip_address', 'success', 'user_agent_short')
    list_filter = ('success', 'data_accesso', 'user')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'data_accesso', 'ip_address', 'user_agent', 'success', 'motivo_fallimento')
    
    fieldsets = (
        (_('Accesso'), {
            'fields': ('user', 'data_accesso', 'ip_address')
        }),
        (_('Stato'), {
            'fields': ('success', 'motivo_fallimento')
        }),
        (_('Dettagli Browser'), {
            'fields': ('user_agent',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Impedisce di aggiungere manualmente log di accesso"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo admin può eliminare i log"""
        return request.user.is_superuser
    
    def user_agent_short(self, obj):
        """Visualizza una versione abbreviata dell'user agent"""
        if obj.user_agent:
            return obj.user_agent[:60] + "..." if len(obj.user_agent) > 60 else obj.user_agent
        return "-"
    user_agent_short.short_description = _('User Agent')
