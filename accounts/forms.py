"""
Forms per la gestione degli utenti e autenticazione.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


# ============================================================================
# LOGIN FORM
# ============================================================================

class LoginForm(AuthenticationForm):
    """Form personalizzato per il login"""
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nome utente'),
            'autofocus': True,
            'autocomplete': 'username',
        }),
        label=_('Nome utente'),
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password'),
            'autocomplete': 'current-password',
        }),
        label=_('Password'),
    )
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


# ============================================================================
# REGISTER FORM
# ============================================================================

class RegisterForm(UserCreationForm):
    """Form personalizzato per la registrazione"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email'),
        }),
        label=_('Email'),
        help_text=_('Richiesto. Inserisci un indirizzo email valido.'),
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nome'),
        }),
        label=_('Nome'),
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Cognome'),
        }),
        label=_('Cognome'),
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nome utente'),
            'autofocus': True,
        }),
        label=_('Nome utente'),
        help_text=_('Obbligatorio. Massimo 150 caratteri. Solo lettere, numeri e @/./+/-/_'),
    )
    
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password'),
            'autocomplete': 'new-password',
        }),
        help_text=_('La password deve contenere almeno 10 caratteri, lettere, numeri e caratteri speciali.'),
    )
    
    password2 = forms.CharField(
        label=_('Conferma Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Conferma Password'),
            'autocomplete': 'new-password',
        }),
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        """Verifica che l'email sia unica"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Un utente con questo indirizzo email esiste già.'))
        return email
    
    def clean_username(self):
        """Verifica che lo username sia unico"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Un utente con questo nome utente esiste già.'))
        return username
    
    def clean_password2(self):
        """Verifica che le password corrispondano"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Le password non corrispondono.'))
        
        return password2
    
    def save(self, commit=True):
        """Salva l'utente con la password hash"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        
        return user


# ============================================================================
# PROFILE FORM
# ============================================================================

class ProfileForm(forms.ModelForm):
    """Form per la modifica del profilo utente"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        }),
        label=_('Email'),
        help_text=_('La email non può essere modificata qui. Contatta un amministratore.'),
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nome'),
        }),
        label=_('Nome'),
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Cognome'),
        }),
        label=_('Cognome'),
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True


# ============================================================================
# CHANGE PASSWORD FORM
# ============================================================================

class ChangePasswordForm(forms.Form):
    """Form personalizzato per il cambio password"""
    
    old_password = forms.CharField(
        label=_('Password Attuale'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Inserisci la tua password attuale'),
            'autocomplete': 'current-password',
        }),
    )
    
    new_password1 = forms.CharField(
        label=_('Nuova Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Inserisci la nuova password'),
            'autocomplete': 'new-password',
        }),
        help_text=_('Almeno 10 caratteri con numeri e caratteri speciali.'),
    )
    
    new_password2 = forms.CharField(
        label=_('Conferma Nuova Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Conferma la nuova password'),
            'autocomplete': 'new-password',
        }),
    )
    
    def clean_new_password2(self):
        """Verifica che le nuove password corrispondano"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Le password non corrispondono.'))
        
        return password2


# ============================================================================
# USER MANAGEMENT FORM (ADMIN)
# ============================================================================

class UserManagementForm(forms.ModelForm):
    """Form per la gestione degli utenti da parte dell'amministratore"""
    
    ruolo = forms.ChoiceField(
        choices=[],  # Popolato in __init__
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label=_('Ruolo'),
        required=True,
    )
    
    dipartimento = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Dipartimento'),
        }),
        label=_('Dipartimento'),
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nome utente'),
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Email'),
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nome'),
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Cognome'),
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'username': _('Nome utente'),
            'email': _('Email'),
            'first_name': _('Nome'),
            'last_name': _('Cognome'),
            'is_active': _('Attivo'),
            'is_staff': _('Staff (accesso admin)'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Popola le scelte per il ruolo
        from .models import RuoloUtente, ProfiloUtente
        self.fields['ruolo'].choices = RuoloUtente.choices
        
        # Se è un update, imposta il ruolo corrente
        if self.instance and self.instance.pk:
            try:
                self.fields['ruolo'].initial = self.instance.profilo.ruolo
                self.fields['dipartimento'].initial = self.instance.profilo.dipartimento
            except ProfiloUtente.DoesNotExist:
                pass

