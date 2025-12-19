"""
Forms per l'applicazione Gestione Magazzino Ricambi.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.files.base import ContentFile
import os
import requests
from .models import (
    Categoria, PezzoRicambio, Fornitore, 
    MovimentoMagazzino, Inventario, DettaglioInventario,
    ModelloMacchinaSCM, MatricolaMacchinaSCM
)


# ============================================================================
# WIDGET PERSONALIZZATO PER SELECT CON DATA ATTRIBUTES
# ============================================================================

class MatricolaSelectWidget(forms.Select):
    """Widget personalizzato per le matricole che aggiunge data-modello-id"""
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            try:
                # Converti value in intero se necessario
                value_id = int(value.value) if hasattr(value, 'value') else int(value)
                matricola = MatricolaMacchinaSCM.objects.select_related('modello').get(pk=value_id)
                option['attrs']['data-modello-id'] = str(matricola.modello.id_modello)
            except (MatricolaMacchinaSCM.DoesNotExist, AttributeError, ValueError, TypeError):
                pass
        return option


# ============================================================================
# BACKUP SETTINGS FORM
# ============================================================================

class BackupSettingsForm(forms.Form):
    """Form per configurare le impostazioni di backup"""
    
    backup_dir = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': r'D:\Backups\Database',
        }),
        label=_('Cartella di Backup'),
        help_text=_('Percorso assoluto dove salvare i backup (es. D:\\Backups\\Database)'),
        required=True,
    )
    
    retention_days = forms.IntegerField(
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '365',
        }),
        label=_('Giorni di Conservazione'),
        help_text=_('Numero di giorni per cui conservare i backup prima della pulizia automatica'),
        initial=30,
    )
    
    mysql_bin_path = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': r'C:\xampp\mysql\bin',
        }),
        label=_('Percorso MySQL/MariaDB'),
        help_text=_('Cartella contenente mysqldump.exe e mysql.exe (es. C:\\xampp\\mysql\\bin)'),
        required=True,
    )
    
    def clean_backup_dir(self):
        """Valida che la cartella di backup sia accessibile"""
        backup_dir = self.cleaned_data.get('backup_dir')
        
        if not backup_dir:
            raise forms.ValidationError(_('Il percorso di backup è obbligatorio'))
        
        # Crea la cartella se non esiste
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except Exception as e:
            raise forms.ValidationError(_(f'Impossibile creare/accedere alla cartella: {str(e)}'))
        
        # Verifica permessi di scrittura
        if not os.access(backup_dir, os.W_OK):
            raise forms.ValidationError(_('Nessun permesso di scrittura sulla cartella'))
        
        return backup_dir
    
    def clean_mysql_bin_path(self):
        """Valida che mysqldump.exe esista nel percorso specificato"""
        mysql_path = self.cleaned_data.get('mysql_bin_path')
        
        if not mysql_path:
            raise forms.ValidationError(_('Il percorso MySQL è obbligatorio'))
        
        mysqldump_exe = os.path.join(mysql_path, 'mysqldump.exe')
        mysql_exe = os.path.join(mysql_path, 'mysql.exe')
        
        if not os.path.exists(mysqldump_exe):
            raise forms.ValidationError(_(f'mysqldump.exe non trovato in: {mysql_path}'))
        
        if not os.path.exists(mysql_exe):
            raise forms.ValidationError(_(f'mysql.exe non trovato in: {mysql_path}'))
        
        return mysql_path


# ============================================================================
# CATEGORIA FORM
# ============================================================================

class CategoriaForm(forms.ModelForm):
    """Form per la creazione/modifica di categorie con gerarchia"""
    
    # Campi virtuali per selezione gerarchica
    macrocategoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(livello=0, stato_attivo=True).order_by('ordine', 'nome_categoria'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label=_('Macrocategoria (Livello 1)'),
        empty_label=_('--- Nessuna (sarà Macrocategoria) ---'),
    )
    
    categoria_livello2 = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(livello=1, stato_attivo=True).order_by('ordine', 'nome_categoria'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label=_('Categoria Livello 2'),
        empty_label=_('--- Nessuna ---'),
    )
    
    nome_categoria = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Nome categoria'),
            'autofocus': True,
        }),
        label=_('Nome Categoria'),
        help_text=_('Inserire il nome della categoria (es. Meccanica, Elettrica)'),
    )
    
    categoria_padre = forms.ModelChoiceField(
        queryset=Categoria.objects.none(),  # Popolato in __init__
        required=False,
        widget=forms.HiddenInput(),  # Nascosto, valorizzato da JS
        label=_('Categoria Padre'),
        help_text=_('Seleziona la categoria superiore (lascia vuoto per macrocategoria di livello 1)'),
        empty_label=_('--- Nessuna (Macrocategoria) ---'),
    )
    
    ordine = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
        }),
        label=_('Ordine Visualizzazione'),
        help_text=_('Numero per ordinare le categorie (0 = prima)'),
    )
    
    descrizione = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Descrizione della categoria'),
            'rows': 3,
        }),
        label=_('Descrizione'),
    )
    
    stato_attivo = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label=_('Categoria Attiva'),
    )
    
    class Meta:
        model = Categoria
        fields = ('nome_categoria', 'categoria_padre', 'ordine', 'descrizione', 'stato_attivo')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Popola le categorie padre (solo quelle che non causerebbero loop)
        if self.instance and self.instance.pk:
            # In modifica: escludi se stessa e i suoi discendenti
            excluded_ids = [self.instance.pk] + self.instance.get_all_children_ids()
            # Mostra solo categorie di livello 0 e 1 (max 2 livelli sotto)
            self.fields['categoria_padre'].queryset = Categoria.objects.filter(
                stato_attivo=True,
                livello__lt=2
            ).exclude(pk__in=excluded_ids).order_by('livello', 'ordine', 'nome_categoria')
            
            # Pre-popola i campi virtuali in base alla categoria_padre attuale
            if self.instance.categoria_padre:
                if self.instance.categoria_padre.livello == 0:
                    # Padre è macrocategoria -> questa è livello 2
                    self.initial['macrocategoria'] = self.instance.categoria_padre
                elif self.instance.categoria_padre.livello == 1:
                    # Padre è livello 2 -> questa è livello 3
                    self.initial['categoria_livello2'] = self.instance.categoria_padre
                    if self.instance.categoria_padre.categoria_padre:
                        self.initial['macrocategoria'] = self.instance.categoria_padre.categoria_padre
                        # Popola queryset livello 2
                        self.fields['categoria_livello2'].queryset = Categoria.objects.filter(
                            categoria_padre=self.instance.categoria_padre.categoria_padre,
                            stato_attivo=True
                        ).exclude(pk__in=excluded_ids).order_by('ordine', 'nome_categoria')
        else:
            # In creazione: mostra tutte fino a livello 1
            self.fields['categoria_padre'].queryset = Categoria.objects.filter(
                stato_attivo=True,
                livello__lt=2
            ).order_by('livello', 'ordine', 'nome_categoria')
            
            # Se c'è un valore iniziale per macrocategoria (da get_initial della vista)
            # popola il queryset di categoria_livello2
            if 'macrocategoria' in self.initial and self.initial['macrocategoria']:
                macro = self.initial['macrocategoria']
                # Se macro è un oggetto Categoria, usa il suo pk
                macro_id = macro.pk if hasattr(macro, 'pk') else macro
                self.fields['categoria_livello2'].queryset = Categoria.objects.filter(
                    categoria_padre_id=macro_id,
                    stato_attivo=True,
                    livello=1
                ).order_by('ordine', 'nome_categoria')
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Determina categoria_padre dai campi virtuali
        macrocategoria = cleaned_data.get('macrocategoria')
        categoria_livello2 = cleaned_data.get('categoria_livello2')
        
        # Priorità: categoria_livello2 > macrocategoria > None
        if categoria_livello2:
            cleaned_data['categoria_padre'] = categoria_livello2
        elif macrocategoria:
            cleaned_data['categoria_padre'] = macrocategoria
        else:
            cleaned_data['categoria_padre'] = None
        
        categoria_padre = cleaned_data.get('categoria_padre')
        
        # Validazione: non più di 3 livelli
        if categoria_padre and categoria_padre.livello >= 2:
            raise forms.ValidationError(_('Non puoi creare più di 3 livelli di categorie'))
        
        return cleaned_data


# ============================================================================
# PEZZO DI RICAMBIO FORM
# ============================================================================

class PezzoRicambioForm(forms.ModelForm):
    """Form per la creazione/modifica di articoli con dropdown categorie a cascata"""
    
    # Campi virtuali per selezione gerarchica categorie
    macrocategoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(livello=0, stato_attivo=True).order_by('ordine', 'nome_categoria'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Macrocategoria (Livello 1)'),
        empty_label=_('--- Seleziona macrocategoria ---'),
    )
    
    categoria_livello2 = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(livello=1, stato_attivo=True).order_by('ordine', 'nome_categoria'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Categoria (Livello 2)'),
        empty_label=_('--- Prima seleziona macrocategoria ---'),
    )
    
    sottocategoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(livello=2, stato_attivo=True).order_by('ordine', 'nome_categoria'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Sottocategoria (Livello 3) - Opzionale'),
        empty_label=_('--- Nessuna (usa categoria sopra) ---'),
    )
    
    # Campo virtuale per upload da URL
    immagine_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://esempio.com/immagine.jpg',
        }),
        label=_('URL Immagine'),
        help_text=_('In alternativa al caricamento file, inserisci l\'URL di un\'immagine da scaricare'),
    )
    
    class Meta:
        model = PezzoRicambio
        fields = (
            'codice_interno', 'codice_scm', 'descrizione_scm', 
            'modello_macchina_scm', 'matricola_macchina_scm', 'codice_fornitore',
            'descrizione', 'categoria', 'fornitore', 'unita_misura', 'giacenza_minima',
            'giacenza_massima', 'prezzo_acquisto', 'prezzo_acquisto_scm', 
            'stato_disponibilita', 'immagine', 'stato_attivo'
        )
        widgets = {
            'matricola_macchina_scm': MatricolaSelectWidget(attrs={'class': 'form-select'}),
            'categoria': forms.HiddenInput(),  # Campo nascosto, valorizzato da JS
            'immagine': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se in modifica, pre-popola i dropdown gerarchici
        if self.instance and self.instance.pk and self.instance.categoria:
            cat = self.instance.categoria
            
            if cat.livello == 0:
                # Articolo direttamente in macrocategoria
                self.fields['macrocategoria'].initial = cat
            elif cat.livello == 1:
                # Articolo in categoria di livello 2
                self.fields['macrocategoria'].initial = cat.categoria_padre
                self.fields['categoria_livello2'].initial = cat
                self.fields['categoria_livello2'].queryset = Categoria.objects.filter(
                    categoria_padre=cat.categoria_padre, stato_attivo=True
                ).order_by('ordine', 'nome_categoria')
            elif cat.livello == 2:
                # Articolo in sottocategoria
                self.fields['macrocategoria'].initial = cat.categoria_padre.categoria_padre
                self.fields['categoria_livello2'].initial = cat.categoria_padre
                self.fields['sottocategoria'].initial = cat
                
                self.fields['categoria_livello2'].queryset = Categoria.objects.filter(
                    categoria_padre=cat.categoria_padre.categoria_padre, stato_attivo=True
                ).order_by('ordine', 'nome_categoria')
                
                self.fields['sottocategoria'].queryset = Categoria.objects.filter(
                    categoria_padre=cat.categoria_padre, stato_attivo=True
                ).order_by('ordine', 'nome_categoria')
        
        # Codice interno
        self.fields['codice_interno'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Codice interno univoco'),
            'autofocus': True,
        })
        self.fields['codice_interno'].label = _('Codice Interno')
        self.fields['codice_interno'].help_text = _('Identificativo univoco dell\'articolo')
        
        # Codici alternativi
        self.fields['codice_scm'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Es. 1234567890A'),
            'maxlength': '11',
            'pattern': r'\d{10}[A-Z]',
        })
        self.fields['codice_scm'].required = False
        self.fields['codice_scm'].help_text = _('10 cifre + 1 lettera maiuscola (es. 1234567890A)')
        
        self.fields['codice_fornitore'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Codice'),
        })
        self.fields['codice_fornitore'].required = False
        
        # Campi SCM aggiuntivi
        self.fields['descrizione_scm'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Descrizione'),
        })
        self.fields['descrizione_scm'].required = False
        
        self.fields['modello_macchina_scm'].widget.attrs.update({
            'class': 'form-select',
        })
        self.fields['modello_macchina_scm'].required = False
        self.fields['modello_macchina_scm'].label = _('Modello Macchina')
        
        # matricola_macchina_scm usa già MatricolaSelectWidget dal Meta.widgets
        self.fields['matricola_macchina_scm'].required = False
        self.fields['matricola_macchina_scm'].label = _('Matricola Macchina')
        
        # Descrizione
        self.fields['descrizione'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Descrizione estesa dell\'articolo'),
            'rows': 3,
        })
        
        # Categoria nascosta (valorizzata da JS) - opzionale
        self.fields['categoria'].required = False
        # Popola il queryset per permettere la validazione di qualsiasi categoria attiva
        self.fields['categoria'].queryset = Categoria.objects.filter(
            stato_attivo=True
        ).order_by('livello', 'ordine', 'nome_categoria')
        
        # Fornitore e unità di misura
        self.fields['fornitore'].widget.attrs.update({
            'class': 'form-select',
        })
        self.fields['fornitore'].required = False
        self.fields['fornitore'].label = _('Fornitore Principale')
        self.fields['fornitore'].help_text = _('Fornitore associato al prezzo di acquisto')
        
        self.fields['unita_misura'].widget.attrs.update({
            'class': 'form-select',
        })
        
        # Giacenze
        for field in ['giacenza_minima', 'giacenza_massima']:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'type': 'number',
                'min': '0',
            })
        
        # Prezzi
        for field in ['prezzo_acquisto', 'prezzo_acquisto_scm']:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'type': 'number',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
            })
            self.fields[field].required = False
        
        # Stato disponibilità
        self.fields['stato_disponibilita'].widget.attrs.update({
            'class': 'form-select',
        })
        self.fields['stato_disponibilita'].label = _('Stato Disponibilità')
        self.fields['stato_disponibilita'].help_text = _('Indica se l\'articolo è presente fisicamente in magazzino')
        
        # Stato attivo
        self.fields['stato_attivo'].widget.attrs.update({
            'class': 'form-check-input',
        })
    
    def clean(self):
        """Valida e imposta la categoria finale dai dropdown a cascata"""
        cleaned_data = super().clean()
        
        # Determina quale categoria usare (priorità: sottocategoria > categoria_livello2 > macrocategoria)
        sottocategoria = cleaned_data.get('sottocategoria')
        categoria_livello2 = cleaned_data.get('categoria_livello2')
        macrocategoria = cleaned_data.get('macrocategoria')
        
        if sottocategoria:
            cleaned_data['categoria'] = sottocategoria
        elif categoria_livello2:
            cleaned_data['categoria'] = categoria_livello2
        elif macrocategoria:
            cleaned_data['categoria'] = macrocategoria
        else:
            # Categoria opzionale - non sollevare errore
            cleaned_data['categoria'] = None
        
        # Gestione upload immagine da URL
        immagine_url = cleaned_data.get('immagine_url')
        immagine_file = cleaned_data.get('immagine')
        
        # Solo se c'è un URL E non c'è già un file caricato
        if immagine_url and not immagine_file:
            try:
                # Download immagine dall'URL
                response = requests.get(immagine_url, timeout=15, stream=True)
                response.raise_for_status()
                
                # Verifica che sia un'immagine
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    raise forms.ValidationError({
                        'immagine_url': _('L\'URL non punta a un\'immagine valida (Content-Type: {})').format(content_type)
                    })
                
                # Verifica dimensione (max 10MB per sicurezza)
                content_length = int(response.headers.get('Content-Length', 0))
                if content_length > 10 * 1024 * 1024:  # 10MB
                    raise forms.ValidationError({
                        'immagine_url': _('L\'immagine è troppo grande (max 10MB)')
                    })
                
                # Estrai nome file dall'URL o usa default
                filename = immagine_url.split('/')[-1].split('?')[0] or 'immagine_download.jpg'
                # Assicurati che abbia un'estensione
                if '.' not in filename:
                    # Prova a dedurre l'estensione dal Content-Type
                    ext_map = {
                        'image/jpeg': '.jpg',
                        'image/png': '.png',
                        'image/webp': '.webp',
                        'image/gif': '.gif'
                    }
                    filename += ext_map.get(content_type, '.jpg')
                
                # Crea ContentFile dall'immagine scaricata
                image_content = ContentFile(response.content, name=filename)
                cleaned_data['immagine'] = image_content
                
            except requests.RequestException as e:
                raise forms.ValidationError({
                    'immagine_url': _('Errore nel download dell\'immagine: {}').format(str(e))
                })
        
        # Validazione Codice SCM: formato 10 cifre + 1 lettera maiuscola
        codice_scm = cleaned_data.get('codice_scm')
        if codice_scm:
            # Rimuovi eventuali spazi
            codice_scm = codice_scm.strip()
            cleaned_data['codice_scm'] = codice_scm
            
            # Validazione formato: 10 cifre + 1 lettera maiuscola
            import re
            if not re.match(r'^\d{10}[A-Z]$', codice_scm):
                raise forms.ValidationError({
                    'codice_scm': _('Il Codice SCM deve essere formato da 10 cifre seguite da 1 lettera maiuscola (es. 1234567890A)')
                })
            
            # Verifica univocità (escludendo l'istanza corrente in modifica)
            qs = PezzoRicambio.objects.filter(codice_scm=codice_scm)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError({
                    'codice_scm': _('Esiste già un articolo con questo Codice SCM')
                })
        
        return cleaned_data


# ============================================================================
# FORNITORE FORM
# ============================================================================

class FornitoreForm(forms.ModelForm):
    """Form per la creazione/modifica di fornitori"""
    
    class Meta:
        model = Fornitore
        fields = (
            'ragione_sociale', 'indirizzo', 'citta', 'cap', 'provincia',
            'telefono', 'email', 'partita_iva', 'tempo_medio_consegna_giorni',
            'note', 'stato_attivo'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ragione sociale
        self.fields['ragione_sociale'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Nome dell\'azienda'),
            'autofocus': True,
        })
        
        # Indirizzo
        self.fields['indirizzo'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Via, numero, civico'),
        })
        self.fields['indirizzo'].required = False
        
        # Città
        self.fields['citta'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Città'),
        })
        self.fields['citta'].required = False
        
        # CAP
        self.fields['cap'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('CAP'),
        })
        self.fields['cap'].required = False
        
        # Provincia
        self.fields['provincia'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Provincia (es. MI, TO)'),
            'maxlength': '2',
        })
        self.fields['provincia'].required = False
        
        # Telefono
        self.fields['telefono'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Numero di telefono'),
            'type': 'tel',
        })
        self.fields['telefono'].required = False
        
        # Email
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Email'),
            'type': 'email',
        })
        self.fields['email'].required = False
        
        # Partita IVA
        self.fields['partita_iva'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Partita IVA'),
        })
        self.fields['partita_iva'].required = False
        
        # Tempo consegna
        self.fields['tempo_medio_consegna_giorni'].widget.attrs.update({
            'class': 'form-control',
            'type': 'number',
            'min': '1',
            'max': '365',
        })
        
        # Note
        self.fields['note'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Note aggiuntive'),
            'rows': 3,
        })
        self.fields['note'].required = False
        
        # Stato
        self.fields['stato_attivo'].widget.attrs.update({
            'class': 'form-check-input',
        })


# ============================================================================
# MOVIMENTO MAGAZZINO FORM
# ============================================================================

class MovimentoMagazzinoForm(forms.ModelForm):
    """Form per la registrazione di movimenti"""
    
    class Meta:
        model = MovimentoMagazzino
        fields = (
            'articolo', 'tipo_movimento', 'quantita', 'fornitore',
            'causale', 'numero_documento', 'note'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Articolo
        self.fields['articolo'].widget.attrs.update({
            'class': 'form-select',
        })
        self.fields['articolo'].label = _('Articolo')
        
        # Tipo movimento
        self.fields['tipo_movimento'].widget.attrs.update({
            'class': 'form-select',
        })
        self.fields['tipo_movimento'].label = _('Tipo Movimento')
        
        # Quantità
        self.fields['quantita'].widget.attrs.update({
            'class': 'form-control',
            'type': 'number',
            'min': '1',
            'placeholder': _('Quantità'),
        })
        self.fields['quantita'].label = _('Quantità')
        
        # Fornitore (opzionale)
        self.fields['fornitore'].widget.attrs.update({
            'class': 'form-select',
        })
        self.fields['fornitore'].required = False
        
        # Causale
        self.fields['causale'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Motivo del movimento'),
        })
        self.fields['causale'].required = False
        
        # Numero documento
        self.fields['numero_documento'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('DDT, Fattura, Ordine, ecc.'),
        })
        self.fields['numero_documento'].required = False
        
        # Note
        self.fields['note'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Note aggiuntive'),
            'rows': 3,
        })
        self.fields['note'].required = False
    
    def clean(self):
        """Validazione cross-field per controllo stock in scarico"""
        cleaned_data = super().clean()
        articolo = cleaned_data.get('articolo')
        tipo_movimento = cleaned_data.get('tipo_movimento')
        quantita = cleaned_data.get('quantita')
        
        if articolo and tipo_movimento and quantita:
            # Controlla che gli SCARICHI non superino la disponibilità
            if tipo_movimento in ['SCARICO', 'RESO_FORNITORE']:
                try:
                    giacenza = articolo.giacenza
                    disponibile = giacenza.quantita_disponibile if giacenza else 0
                    
                    if quantita > disponibile:
                        raise forms.ValidationError(
                            _('❌ Quantità insufficiente! Disponibile: %(disponibile)d %(unita)s, Richiesto: %(richiesto)d %(unita)s'),
                            code='insufficient_stock',
                            params={
                                'disponibile': disponibile,
                                'richiesto': quantita,
                                'unita': articolo.unita_misura.codice if articolo.unita_misura else 'pz'
                            }
                        )
                except AttributeError:
                    # Se articolo non ha giacenza, non permettere scarico
                    raise forms.ValidationError(
                        _('❌ Impossibile effettuare uno scarico: articolo senza giacenza registrata'),
                        code='no_giacenza'
                    )
        
        return cleaned_data


# ============================================================================
# INVENTARIO FORM
# ============================================================================

class InventarioForm(forms.ModelForm):
    """Form per la creazione di inventari"""
    
    class Meta:
        model = Inventario
        fields = ('data_inventario', 'operatore', 'stato', 'note')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Data
        self.fields['data_inventario'].widget.attrs.update({
            'class': 'form-control',
            'type': 'date',
        })
        
        # Operatore
        self.fields['operatore'].widget.attrs.update({
            'class': 'form-control',
        })
        
        # Stato
        self.fields['stato'].widget.attrs.update({
            'class': 'form-select',
        })
        
        # Note
        self.fields['note'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
        })
        self.fields['note'].required = False


# ============================================================================
# DETTAGLIO INVENTARIO FORM
# ============================================================================

class DettaglioInventarioForm(forms.ModelForm):
    """Form per l'inserimento dettagli inventario"""
    
    class Meta:
        model = DettaglioInventario
        fields = ('articolo', 'quantita_rilevata', 'note')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Articolo
        self.fields['articolo'].widget.attrs.update({
            'class': 'form-select',
        })
        
        # Quantità rilevata
        self.fields['quantita_rilevata'].widget.attrs.update({
            'class': 'form-control',
            'type': 'number',
            'min': '0',
        })
        
        # Note
        self.fields['note'].widget.attrs.update({
            'class': 'form-control',
            'rows': 2,
        })
        self.fields['note'].required = False
