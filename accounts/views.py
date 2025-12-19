"""
Views per la gestione degli utenti e autenticazione.
"""

from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, UpdateView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from .models import ProfiloUtente, LogAccesso
from .forms import LoginForm, RegisterForm, ProfileForm
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# LOGIN VIEW - Accesso al sistema con logging
# ============================================================================

class LoginView(DjangoLoginView):
    """View personalizzata per il login"""
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Reindirizza alla home dopo login riuscito"""
        return reverse_lazy('magazzino:dashboard')
    
    def post(self, request, *args, **kwargs):
        """Registra il tentativo di login nel log"""
        username = request.POST.get('username')
        
        # Recupera IP address
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        response = super().post(request, *args, **kwargs)
        
        # Log del tentativo di accesso
        if request.user.is_authenticated:
            # Accesso riuscito
            LogAccesso.objects.create(
                user=request.user,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            logger.info(f"✅ Login riuscito per utente: {request.user.username}")
        else:
            # Accesso fallito
            try:
                user = User.objects.get(username=username)
                LogAccesso.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    motivo_fallimento='Password non corretta'
                )
                logger.warning(f"❌ Tentativo di login fallito per: {username}")
            except User.DoesNotExist:
                logger.warning(f"❌ Tentativo di login con utente inesistente: {username}")
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Estrae l'IP address dal request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# ============================================================================
# LOGOUT VIEW
# ============================================================================

class LogoutView(LoginRequiredMixin, DjangoLogoutView):
    """View per il logout"""
    next_page = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"🔐 Logout per utente: {request.user.username}")
        messages.success(request, _('Logout effettuato con successo. Arrivederci!'))
        return super().dispatch(request, *args, **kwargs)


# ============================================================================
# REGISTER VIEW - Registrazione nuovo utente
# ============================================================================

class RegisterView(CreateView):
    """View per la registrazione di nuovi utenti"""
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        """Salva il nuovo utente e mostra messaggio di successo"""
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Registrazione completata! Accedi con le tue credenziali.')
        )
        logger.info(f"✨ Nuovo utente registrato: {form.cleaned_data['username']}")
        return response
    
    def form_invalid(self, form):
        """Gestisce errori di registrazione"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


# ============================================================================
# PROFILE VIEW - Visualizzazione profilo utente
# ============================================================================

class ProfileView(LoginRequiredMixin, TemplateView):
    """View per visualizzare il profilo dell'utente"""
    template_name = 'accounts/profile.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        """Aggiunge dati del profilo al context"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            profilo = user.profilo
        except ProfiloUtente.DoesNotExist:
            profilo = ProfiloUtente.objects.create(user=user)
        
        context['profilo'] = profilo
        context['ultimi_accessi'] = LogAccesso.objects.filter(
            user=user,
            success=True
        ).order_by('-data_accesso')[:5]
        
        return context


# ============================================================================
# EDIT PROFILE VIEW - Modifica profilo utente
# ============================================================================

class EditProfileView(LoginRequiredMixin, TemplateView):
    """View per modificare il profilo utente"""
    template_name = 'accounts/edit_profile.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        """Prepara il form per la modifica"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            profilo = user.profilo
        except ProfiloUtente.DoesNotExist:
            profilo = ProfiloUtente.objects.create(user=user)
        
        if self.request.method == 'POST':
            form = ProfileForm(self.request.POST, instance=user)
        else:
            form = ProfileForm(instance=user)
        
        context['form'] = form
        context['profilo'] = profilo
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Salva i dati modificati"""
        user = request.user
        form = ProfileForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            messages.success(request, _('Profilo aggiornato con successo!'))
            logger.info(f"✏️ Profilo aggiornato per: {user.username}")
            return redirect('accounts:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return render(request, self.template_name, context)


# ============================================================================
# CHANGE PASSWORD VIEW - Cambio password
# ============================================================================

class ChangePasswordView(LoginRequiredMixin, TemplateView):
    """View per il cambio password dell'utente"""
    template_name = 'accounts/change_password.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        """Prepara il context per il template"""
        context = super().get_context_data(**kwargs)
        
        from .forms import ChangePasswordForm
        if self.request.method == 'POST':
            context['form'] = ChangePasswordForm(self.request.POST)
        else:
            context['form'] = ChangePasswordForm()
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Gestisce il cambio password"""
        from .forms import ChangePasswordForm
        from django.contrib.auth import update_session_auth_hash
        
        form = ChangePasswordForm(request.POST)
        user = request.user
        
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password1']
            
            # Verifica che la password attuale sia corretta
            if not user.check_password(old_password):
                messages.error(request, _('La password attuale non è corretta.'))
                context = self.get_context_data(**kwargs)
                context['form'] = form
                return render(request, self.template_name, context)
            
            # Cambia la password
            user.set_password(new_password)
            user.save()
            
            # Mantiene l'utente loggato dopo il cambio password
            update_session_auth_hash(request, user)
            
            messages.success(
                request,
                _('Password modificata con successo!')
            )
            logger.info(f"🔑 Password cambiata per: {user.username}")
            
            return redirect('accounts:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return render(request, self.template_name, context)

