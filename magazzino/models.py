"""
Models per l'applicazione Gestione Magazzino Ricambi.

Rappresentano tutte le tabelle del database MySQL.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import datetime


# ============================================================================
# 1. CATEGORIE - Classificazione dei ricambi
# ============================================================================

class Categoria(models.Model):
    """Categoria di classificazione per i ricambi con supporto gerarchia"""
    
    id_categoria = models.AutoField(primary_key=True, db_column='id_categoria')
    nome_categoria = models.CharField(
        max_length=50,
        verbose_name=_('Nome Categoria'),
        help_text=_('Inserire il nome della categoria (es. Meccanica, Elettrica)')
    )
    descrizione = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Descrizione'),
        help_text=_('Descrizione tecnica della categoria')
    )
    
    # NUOVO: Gerarchia categorie (self-referencing)
    categoria_padre = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sottocategorie',
        db_column='id_categoria_padre',
        verbose_name=_('Categoria Padre'),
        help_text=_('Categoria superiore nella gerarchia (lasciare vuoto per macrocategoria)')
    )
    
    # Campo calcolato automaticamente per facilitare query
    livello = models.IntegerField(
        default=0,
        editable=False,
        verbose_name=_('Livello'),
        help_text=_('0=Macrocategoria, 1=Categoria, 2=Sottocategoria')
    )
    
    # Per ordinamento personalizzato
    ordine = models.IntegerField(
        default=0,
        verbose_name=_('Ordine'),
        help_text=_('Ordine di visualizzazione (0=primo)')
    )
    
    stato_attivo = models.BooleanField(
        default=True,
        verbose_name=_('Stato Attivo'),
        help_text=_('Categoria attiva o disattivata')
    )
    creato_il = models.DateTimeField(auto_now_add=True, db_column='creato_il')
    modificato_il = models.DateTimeField(auto_now=True, db_column='modificato_il')
    
    class Meta:
        db_table = 'categorie'
        ordering = ['livello', 'ordine', 'nome_categoria']
        indexes = [
            models.Index(fields=['stato_attivo']),
            models.Index(fields=['nome_categoria']),
            models.Index(fields=['categoria_padre']),
            models.Index(fields=['livello']),
        ]
        verbose_name = _('Categoria')
        verbose_name_plural = _('Categorie')
        # Rimuovo unique constraint su nome_categoria per permettere stesso nome in livelli diversi
    
    def save(self, *args, **kwargs):
        """Calcola automaticamente il livello in base alla gerarchia"""
        # Controllo anti-loop infinito
        if self.categoria_padre:
            # Verifica che non stia creando un loop (categoria padre che punta a se stessa)
            visited = set()
            current = self.categoria_padre
            depth = 0
            max_depth = 10  # Protezione contro loop infiniti
            
            while current and depth < max_depth:
                if current.pk == self.pk:
                    from django.core.exceptions import ValidationError
                    raise ValidationError("Errore: creazione di loop circolare rilevata. Una categoria non può essere padre di se stessa.")
                
                if current.pk in visited:
                    from django.core.exceptions import ValidationError
                    raise ValidationError("Errore: loop circolare rilevato nella gerarchia delle categorie.")
                
                visited.add(current.pk)
                current = current.categoria_padre
                depth += 1
            
            if depth >= max_depth:
                from django.core.exceptions import ValidationError
                raise ValidationError("Errore: gerarchia troppo profonda o loop rilevato.")
            
            # Calcola livello in modo sicuro
            self.livello = len(visited)
            
            # Validazione: massimo 3 livelli (0, 1, 2)
            if self.livello > 2:
                from django.core.exceptions import ValidationError
                raise ValidationError("Massimo 3 livelli di categorie consentiti (Macrocategoria > Categoria > Sottocategoria)")
        else:
            self.livello = 0
        super().save(*args, **kwargs)
    
    def get_breadcrumb(self):
        """Restituisce il percorso completo: Motore > Cinghie > Distribuzione"""
        if self.categoria_padre:
            return f"{self.categoria_padre.get_breadcrumb()} > {self.nome_categoria}"
        return self.nome_categoria
    
    def get_breadcrumb_html(self):
        """Restituisce breadcrumb con icone HTML"""
        if self.categoria_padre:
            return f"{self.categoria_padre.get_breadcrumb_html()} <i class='fas fa-chevron-right fa-xs'></i> {self.nome_categoria}"
        return f"<i class='fas fa-folder'></i> {self.nome_categoria}"
    
    def get_all_children(self, _visited=None):
        """Restituisce tutte le sottocategorie ricorsivamente (con protezione anti-loop)"""
        if _visited is None:
            _visited = set()
        
        # Protezione contro loop infiniti
        if self.pk in _visited:
            return []
        
        _visited.add(self.pk)
        
        children = list(self.sottocategorie.filter(stato_attivo=True))
        for child in list(children):
            children.extend(child.get_all_children(_visited=_visited))
        return children
    
    def get_all_children_ids(self):
        """Restituisce tutti gli ID delle sottocategorie (per query)"""
        return [c.id_categoria for c in self.get_all_children()]
    
    def count_articoli(self):
        """Conta articoli in questa categoria e tutte le sottocategorie"""
        from django.db.models import Count
        # Articoli diretti
        count = self.pezzoricambio_set.filter(stato_attivo=True).count()
        # Articoli nelle sottocategorie
        for child in self.sottocategorie.filter(stato_attivo=True):
            count += child.count_articoli()
        return count
    
    def has_children(self):
        """Verifica se ha sottocategorie"""
        return self.sottocategorie.filter(stato_attivo=True).exists()
    
    def get_icon(self):
        """Restituisce icona FontAwesome in base al livello"""
        icons = {
            0: 'fas fa-folder',           # Macrocategoria
            1: 'fas fa-folder-open',      # Categoria
            2: 'fas fa-file-alt',         # Sottocategoria
        }
        return icons.get(self.livello, 'fas fa-folder')
    
    def __str__(self):
        return self.get_breadcrumb()


# ============================================================================
# 2. UNITÀ DI MISURA - Standardizzazione delle unità
# ============================================================================

class UnitaMisura(models.Model):
    """Unità di misura standard per i ricambi"""
    
    id_unita = models.AutoField(primary_key=True, db_column='id_unita')
    codice = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('Codice'),
        help_text=_('Codice univoco (es. pz, kg, mt, lt)')
    )
    descrizione = models.CharField(
        max_length=50,
        verbose_name=_('Descrizione'),
        help_text=_('Descrizione estesa dell\'unità')
    )
    stato_attivo = models.BooleanField(default=True, verbose_name=_('Stato Attivo'))
    
    class Meta:
        db_table = 'unita_misura'
        ordering = ['descrizione']
        indexes = [
            models.Index(fields=['codice']),
            models.Index(fields=['stato_attivo']),
        ]
        verbose_name = _('Unità di Misura')
        verbose_name_plural = _('Unità di Misura')
    
    def __str__(self):
        return f"{self.codice} - {self.descrizione}"


# ============================================================================
# 3. FORNITORI - Anagrafica fornitori
# ============================================================================

class Fornitore(models.Model):
    """Anagrafica dei fornitori dei ricambi"""
    
    id_fornitore = models.AutoField(primary_key=True, db_column='id_fornitore')
    ragione_sociale = models.CharField(
        max_length=100,
        verbose_name=_('Ragione Sociale'),
        help_text=_('Nome dell\'azienda fornitrice')
    )
    indirizzo = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_('Indirizzo')
    )
    citta = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Città')
    )
    cap = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_('CAP')
    )
    provincia = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name=_('Provincia')
    )
    telefono = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_('Telefono')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email')
    )
    partita_iva = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Partita IVA'),
        unique=True
    )
    tempo_medio_consegna_giorni = models.IntegerField(
        default=7,
        verbose_name=_('Tempo Medio Consegna (giorni)'),
        validators=[MinValueValidator(1), MaxValueValidator(365)]
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Note')
    )
    stato_attivo = models.BooleanField(default=True, verbose_name=_('Stato Attivo'))
    creato_il = models.DateTimeField(auto_now_add=True, db_column='creato_il')
    modificato_il = models.DateTimeField(auto_now=True, db_column='modificato_il')
    
    class Meta:
        db_table = 'fornitori'
        ordering = ['ragione_sociale']
        indexes = [
            models.Index(fields=['ragione_sociale']),
            models.Index(fields=['partita_iva']),
            models.Index(fields=['stato_attivo']),
            models.Index(fields=['email']),
        ]
        verbose_name = _('Fornitore')
        verbose_name_plural = _('Fornitori')
    
    def __str__(self):
        return f"{self.ragione_sociale} - {self.citta}"


# ============================================================================
# 3B. MODELLI MACCHINE SCM - Anagrafica modelli
# ============================================================================

class ModelloMacchinaSCM(models.Model):
    """Modelli di macchine SCM"""
    
    id_modello = models.AutoField(primary_key=True, db_column='id_modello')
    nome_modello = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nome Modello'),
        help_text=_('Denominazione del modello di macchina SCM')
    )
    gamma = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Gamma'),
        help_text=_('Famiglia/Gamma di appartenenza del modello')
    )
    stato_attivo = models.BooleanField(default=True, verbose_name=_('Stato Attivo'))
    creato_il = models.DateTimeField(auto_now_add=True, db_column='creato_il')
    modificato_il = models.DateTimeField(auto_now=True, db_column='modificato_il')
    
    class Meta:
        db_table = 'modelli_macchine_scm'
        ordering = ['gamma', 'nome_modello']
        indexes = [
            models.Index(fields=['nome_modello']),
            models.Index(fields=['gamma']),
            models.Index(fields=['stato_attivo']),
        ]
        verbose_name = _('Modello Macchina SCM')
        verbose_name_plural = _('Modelli Macchine SCM')
    
    def __str__(self):
        if self.gamma:
            return f"{self.gamma} - {self.nome_modello}"
        return self.nome_modello


# ============================================================================
# 3C. MATRICOLE MACCHINE SCM - Matricole per modello
# ============================================================================

class MatricolaMacchinaSCM(models.Model):
    """Matricole delle macchine SCM"""
    
    id_matricola = models.AutoField(primary_key=True, db_column='id_matricola')
    modello = models.ForeignKey(
        ModelloMacchinaSCM,
        on_delete=models.PROTECT,
        verbose_name=_('Modello Macchina'),
        db_column='id_modello',
        related_name='matricole'
    )
    matricola_macchina = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Matricola Macchina'),
        help_text=_('Numero di matricola univoco della macchina')
    )
    anno = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Anno'),
        help_text=_('Anno di produzione/installazione'),
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    stato_attivo = models.BooleanField(default=True, verbose_name=_('Stato Attivo'))
    creato_il = models.DateTimeField(auto_now_add=True, db_column='creato_il')
    modificato_il = models.DateTimeField(auto_now=True, db_column='modificato_il')
    
    class Meta:
        db_table = 'matricole_macchine_scm'
        ordering = ['modello', 'matricola_macchina']
        indexes = [
            models.Index(fields=['matricola_macchina']),
            models.Index(fields=['modello']),
            models.Index(fields=['anno']),
            models.Index(fields=['stato_attivo']),
        ]
        verbose_name = _('Matricola Macchina SCM')
        verbose_name_plural = _('Matricole Macchine SCM')
    
    def __str__(self):
        if self.anno:
            return f"{self.matricola_macchina} ({self.anno}) - {self.modello.nome_modello}"
        return f"{self.matricola_macchina} - {self.modello.nome_modello}"


# ============================================================================
# 4. PEZZI DI RICAMBIO (ARTICOLI) - Archivio principale
# ============================================================================

class PezzoRicambio(models.Model):
    """Archivio principale dei ricambi"""
    
    # Scelte per stato disponibilità
    DISPONIBILE = 'DISP'
    ORDINATO = 'ORD'
    ESAURITO = 'ESAU'
    FUORI_PRODUZIONE = 'FP'
    
    STATO_DISPONIBILITA_CHOICES = [
        (DISPONIBILE, _('Disponibile in magazzino')),
        (ORDINATO, _('Ordinato - In arrivo')),
        (ESAURITO, _('Esaurito - Da riordinare')),
        (FUORI_PRODUZIONE, _('Fuori produzione')),
    ]
    
    id_articolo = models.AutoField(primary_key=True, db_column='id_articolo')
    codice_interno = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Codice Interno'),
        help_text=_('Codice interno univoco dell\'articolo')
    )
    codice_scm = models.CharField(
        max_length=11,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}[A-Z]$',
                message=_('Il Codice SCM deve essere formato da 10 cifre seguite da 1 lettera maiuscola (es. 1234567890A)')
            )
        ],
        verbose_name=_('Codice SCM'),
        help_text=_('Codice SCM univoco: 10 cifre + 1 lettera maiuscola (es. 1234567890A)')
    )
    descrizione_scm = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Descrizione Codice SCM'),
        help_text=_('Descrizione del codice SCM')
    )
    modello_scm_old = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Modello Macchina SCM (OLD)'),
        db_column='modello_macchina_scm'
    )
    matricola_scm_old = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Matricola Macchina SCM (OLD)'),
        db_column='matricola_macchina_scm'
    )
    modello_macchina_scm = models.ForeignKey(
        ModelloMacchinaSCM,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Modello Macchina SCM'),
        db_column='id_modello_scm',
        related_name='articoli'
    )
    matricola_macchina_scm = models.ForeignKey(
        MatricolaMacchinaSCM,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Matricola Macchina SCM'),
        db_column='id_matricola_scm',
        related_name='articoli'
    )
    codice_fornitore = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Codice Fornitore')
    )
    descrizione = models.CharField(
        max_length=200,
        verbose_name=_('Descrizione'),
        help_text=_('Descrizione estesa dell\'articolo')
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        verbose_name=_('Categoria'),
        db_column='id_categoria'
    )
    fornitore = models.ForeignKey(
        Fornitore,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('Fornitore Principale'),
        db_column='id_fornitore',
        help_text=_('Fornitore associato al prezzo di acquisto')
    )
    unita_misura = models.ForeignKey(
        UnitaMisura,
        on_delete=models.PROTECT,
        verbose_name=_('Unità di Misura'),
        db_column='id_unita_misura'
    )
    giacenza_minima = models.IntegerField(
        default=5,
        verbose_name=_('Giacenza Minima'),
        validators=[MinValueValidator(0)],
        help_text=_('Soglia minima di riordino')
    )
    giacenza_massima = models.IntegerField(
        default=100,
        verbose_name=_('Giacenza Massima'),
        validators=[MinValueValidator(0)],
        help_text=_('Scorta massima consigliata')
    )
    prezzo_acquisto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Prezzo Acquisto'),
        validators=[MinValueValidator(0)]
    )
    prezzo_acquisto_scm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Prezzo Acquisto SCM'),
        validators=[MinValueValidator(0)]
    )
    stato_disponibilita = models.CharField(
        max_length=4,
        choices=STATO_DISPONIBILITA_CHOICES,
        default=DISPONIBILE,
        verbose_name=_('Stato Disponibilità'),
        help_text=_('Indica la disponibilità fisica dell\'articolo')
    )
    
    # Campi immagine
    immagine = models.ImageField(
        upload_to='articoli/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Immagine Articolo'),
        help_text=_('Carica un\'immagine dell\'articolo (max 5MB, formati: JPG, PNG, WebP)')
    )
    immagine_thumbnail = models.ImageField(
        upload_to='articoli/thumbnails/%Y/%m/',
        blank=True,
        null=True,
        editable=False,
        verbose_name=_('Thumbnail'),
        help_text=_('Miniatura generata automaticamente (300x300px)')
    )
    
    stato_attivo = models.BooleanField(default=True, verbose_name=_('Stato Attivo'))
    creato_il = models.DateTimeField(auto_now_add=True, db_column='creato_il')
    modificato_il = models.DateTimeField(auto_now=True, db_column='modificato_il')
    
    class Meta:
        db_table = 'pezzi_ricambio'
        ordering = ['descrizione']
        indexes = [
            models.Index(fields=['codice_interno']),
            models.Index(fields=['codice_fornitore']),
            models.Index(fields=['categoria']),
            models.Index(fields=['stato_attivo']),
            models.Index(fields=['descrizione']),
        ]
        verbose_name = _('Pezzo di Ricambio')
        verbose_name_plural = _('Pezzi di Ricambio')
    
    def __str__(self):
        return f"{self.codice_interno} - {self.descrizione}"
    
    def è_sotto_soglia(self):
        """Verifica se il pezzo è sotto la giacenza minima"""
        giacenza = self.giacenza_set.first()
        if giacenza:
            return giacenza.quantita_disponibile < self.giacenza_minima
        return True


# ============================================================================
# 5. GIACENZE - Situazione aggiornata dello stock
# ============================================================================

class Giacenza(models.Model):
    """Giacenze attuali degli articoli"""
    
    id_giacenza = models.AutoField(primary_key=True, db_column='id_giacenza')
    articolo = models.OneToOneField(
        PezzoRicambio,
        on_delete=models.CASCADE,
        verbose_name=_('Articolo'),
        db_column='id_articolo',
        related_name='giacenza'
    )
    quantita_disponibile = models.IntegerField(
        default=0,
        verbose_name=_('Quantità Disponibile'),
        validators=[MinValueValidator(0)]
    )
    quantita_impegnata = models.IntegerField(
        default=0,
        verbose_name=_('Quantità Impegnata'),
        validators=[MinValueValidator(0)],
        help_text=_('Quantità impegnata per ordini aperti')
    )
    quantita_prenotata = models.IntegerField(
        default=0,
        verbose_name=_('Quantità Prenotata'),
        validators=[MinValueValidator(0)],
        help_text=_('Quantità prenotata per lavorazioni')
    )
    ultimo_aggiornamento = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Ultimo Aggiornamento'),
        db_column='ultimo_aggiornamento'
    )
    
    class Meta:
        db_table = 'giacenze'
        indexes = [
            models.Index(fields=['articolo']),
        ]
        verbose_name = _('Giacenza')
        verbose_name_plural = _('Giacenze')
    
    def __str__(self):
        return f"{self.articolo.codice_interno} - Disp: {self.quantita_disponibile}"
    
    @property
    def quantita_libera(self):
        """Quantità effettivamente disponibile (disponibile - impegnata - prenotata)"""
        return max(0, self.quantita_disponibile - self.quantita_impegnata - self.quantita_prenotata)


# ============================================================================
# 6. MOVIMENTI DI MAGAZZINO - Registro di tutte le movimentazioni
# ============================================================================

class TipoMovimento(models.TextChoices):
    CARICO = 'CARICO', _('Carico')
    SCARICO = 'SCARICO', _('Scarico')
    RETTIFICA = 'RETTIFICA', _('Rettifica')
    RESO_FORNITORE = 'RESO_FORNITORE', _('Reso a Fornitore')


class MovimentoMagazzino(models.Model):
    """Registro di tutte le movimentazioni di magazzino"""
    
    id_movimento = models.AutoField(primary_key=True, db_column='id_movimento')
    articolo = models.ForeignKey(
        PezzoRicambio,
        on_delete=models.PROTECT,
        verbose_name=_('Articolo'),
        db_column='id_articolo',
        related_name='movimenti'
    )
    data_movimento = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data Movimento'),
        db_column='data_movimento'
    )
    tipo_movimento = models.CharField(
        max_length=20,
        choices=TipoMovimento.choices,
        verbose_name=_('Tipo Movimento'),
        db_column='tipo_movimento'
    )
    quantita = models.IntegerField(
        verbose_name=_('Quantità'),
        validators=[MinValueValidator(1)],
        help_text=_('Quantità movimentata')
    )
    fornitore = models.ForeignKey(
        Fornitore,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Fornitore'),
        db_column='id_fornitore'
    )
    causale = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_('Causale'),
        help_text=_('Motivo del movimento')
    )
    numero_documento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Numero Documento'),
        help_text=_('DDT, Fattura, Ordine, ecc.')
    )
    operatore = models.CharField(
        max_length=50,
        verbose_name=_('Operatore'),
        help_text=_('Username di chi ha registrato il movimento')
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Note')
    )
    creato_il = models.DateTimeField(auto_now_add=True, db_column='creato_il')
    
    class Meta:
        db_table = 'movimenti_magazzino'
        ordering = ['-data_movimento']
        indexes = [
            models.Index(fields=['articolo']),
            models.Index(fields=['data_movimento']),
            models.Index(fields=['tipo_movimento']),
            models.Index(fields=['fornitore']),
            models.Index(fields=['operatore']),
        ]
        verbose_name = _('Movimento Magazzino')
        verbose_name_plural = _('Movimenti Magazzino')
    
    def __str__(self):
        return f"{self.articolo.codice_interno} - {self.tipo_movimento} ({self.data_movimento.strftime('%d/%m/%Y')})"


# ============================================================================
# 7. INVENTARI - Registrazione inventari fisici periodici
# ============================================================================

class StatoInventario(models.TextChoices):
    IN_CORSO = 'IN_CORSO', _('In Corso')
    CHIUSO = 'CHIUSO', _('Chiuso')
    APPROVATO = 'APPROVATO', _('Approvato')


class Inventario(models.Model):
    """Registrazione di inventari fisici"""
    
    id_inventario = models.AutoField(primary_key=True, db_column='id_inventario')
    data_inventario = models.DateField(
        verbose_name=_('Data Inventario'),
        db_column='data_inventario'
    )
    operatore = models.CharField(
        max_length=50,
        verbose_name=_('Operatore'),
        help_text=_('Chi ha effettuato l\'inventario')
    )
    stato = models.CharField(
        max_length=20,
        choices=StatoInventario.choices,
        default=StatoInventario.IN_CORSO,
        verbose_name=_('Stato'),
        db_column='stato'
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Note')
    )
    creato_il = models.DateTimeField(auto_now_add=True, db_column='creato_il')
    modificato_il = models.DateTimeField(auto_now=True, db_column='modificato_il')
    
    class Meta:
        db_table = 'inventari'
        ordering = ['-data_inventario']
        indexes = [
            models.Index(fields=['data_inventario']),
            models.Index(fields=['stato']),
            models.Index(fields=['operatore']),
        ]
        verbose_name = _('Inventario')
        verbose_name_plural = _('Inventari')
    
    def __str__(self):
        return f"Inventario {self.data_inventario.strftime('%d/%m/%Y')} - {self.get_stato_display()}"


# ============================================================================
# 8. DETTAGLIO INVENTARIO - Conteggio articolo per articolo
# ============================================================================

class DettaglioInventario(models.Model):
    """Dettaglio dei conteggi per ogni articolo in un inventario"""
    
    id_dettaglio = models.AutoField(primary_key=True, db_column='id_dettaglio')
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        verbose_name=_('Inventario'),
        db_column='id_inventario',
        related_name='dettagli'
    )
    articolo = models.ForeignKey(
        PezzoRicambio,
        on_delete=models.PROTECT,
        verbose_name=_('Articolo'),
        db_column='id_articolo'
    )
    quantita_rilevata = models.IntegerField(
        verbose_name=_('Quantità Rilevata'),
        db_column='quantita_rilevata',
        validators=[MinValueValidator(0)],
        help_text=_('Quantità conteggiata fisicamente')
    )
    quantita_sistema = models.IntegerField(
        verbose_name=_('Quantità Sistema'),
        db_column='quantita_sistema',
        validators=[MinValueValidator(0)],
        help_text=_('Quantità registrata nel sistema')
    )
    note = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Note'),
        help_text=_('Note su anomalie o discrepanze')
    )
    creato_il = models.DateTimeField(auto_now_add=True, db_column='creato_il')
    
    class Meta:
        db_table = 'dettaglio_inventario'
        ordering = ['articolo']
        indexes = [
            models.Index(fields=['inventario']),
            models.Index(fields=['articolo']),
        ]
        unique_together = ('inventario', 'articolo')
        verbose_name = _('Dettaglio Inventario')
        verbose_name_plural = _('Dettagli Inventario')
    
    def __str__(self):
        return f"{self.articolo.codice_interno} - {self.inventario.data_inventario}"
    
    @property
    def differenza(self):
        """Differenza tra quantità rilevata e quantità sistema"""
        return self.quantita_rilevata - self.quantita_sistema
    
    @property
    def ha_discrepanza(self):
        """Verifica se c'è una discrepanza"""
        return self.differenza != 0


# ============================================================================
# 9. DOCUMENTI ALLEGATI - Archivio digitale documenti
# ============================================================================

class TipoEntita(models.TextChoices):
    ARTICOLO = 'ARTICOLO', _('Articolo')
    MOVIMENTO = 'MOVIMENTO', _('Movimento')
    FORNITORE = 'FORNITORE', _('Fornitore')


class DocumentoAllegato(models.Model):
    """Archivio digitale di documenti allegati"""
    
    id_documento = models.AutoField(primary_key=True, db_column='id_documento')
    tipo_entita = models.CharField(
        max_length=20,
        choices=TipoEntita.choices,
        verbose_name=_('Tipo Entità'),
        db_column='tipo_entita'
    )
    id_entita = models.IntegerField(
        verbose_name=_('ID Entità'),
        db_column='id_entita',
        help_text=_('ID dell\'articolo, movimento o fornitore')
    )
    tipo_documento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Tipo Documento'),
        help_text=_('Fattura, scheda tecnica, manuale, ecc.')
    )
    nome_file = models.CharField(
        max_length=150,
        verbose_name=_('Nome File'),
        db_column='nome_file'
    )
    percorso_file = models.CharField(
        max_length=250,
        verbose_name=_('Percorso File'),
        db_column='percorso_file'
    )
    data_caricamento = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data Caricamento'),
        db_column='data_caricamento'
    )
    operatore = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Operatore'),
        help_text=_('Username di chi ha caricato il file')
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Note')
    )
    
    class Meta:
        db_table = 'documenti_allegati'
        ordering = ['-data_caricamento']
        indexes = [
            models.Index(fields=['tipo_entita', 'id_entita']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['data_caricamento']),
        ]
        verbose_name = _('Documento Allegato')
        verbose_name_plural = _('Documenti Allegati')
    
    def __str__(self):
        return f"{self.nome_file} ({self.get_tipo_entita_display()})"


# ============================================================================
# CONFIGURAZIONI APPLICAZIONE
# ============================================================================

class Configurazione(models.Model):
    """
    Configurazioni dell'applicazione salvate nel database.
    Permette di modificare impostazioni senza riavviare il server.
    """
    
    chiave = models.CharField(
        max_length=100,
        unique=True,
        primary_key=True,
        verbose_name=_('Chiave'),
        help_text=_('Nome univoco della configurazione')
    )
    valore = models.TextField(
        verbose_name=_('Valore'),
        help_text=_('Valore della configurazione')
    )
    tipo_dato = models.CharField(
        max_length=20,
        choices=[
            ('string', 'Stringa'),
            ('integer', 'Numero Intero'),
            ('boolean', 'Booleano'),
            ('json', 'JSON'),
        ],
        default='string',
        verbose_name=_('Tipo Dato')
    )
    descrizione = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Descrizione')
    )
    modificato_il = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Modificato il')
    )
    modificato_da = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_('Modificato da')
    )
    
    class Meta:
        db_table = 'configurazioni'
        ordering = ['chiave']
        verbose_name = _('Configurazione')
        verbose_name_plural = _('Configurazioni')
    
    def __str__(self):
        return f"{self.chiave} = {self.valore}"
    
    @classmethod
    def get_value(cls, chiave, default=None):
        """
        Recupera un valore di configurazione.
        
        Args:
            chiave: Nome della configurazione
            default: Valore di default se non trovata
            
        Returns:
            Il valore convertito nel tipo appropriato
        """
        try:
            config = cls.objects.get(chiave=chiave)
            
            if config.tipo_dato == 'integer':
                return int(config.valore)
            elif config.tipo_dato == 'boolean':
                return config.valore.lower() in ('true', '1', 'yes', 'si', 'sì')
            elif config.tipo_dato == 'json':
                import json
                return json.loads(config.valore)
            else:
                return config.valore
                
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, chiave, valore, tipo_dato='string', descrizione=None, username=None):
        """
        Imposta un valore di configurazione.
        
        Args:
            chiave: Nome della configurazione
            valore: Valore da impostare
            tipo_dato: Tipo del dato (string, integer, boolean, json)
            descrizione: Descrizione opzionale
            username: Username di chi modifica
        """
        import json
        
        # Converti valore in stringa
        if tipo_dato == 'json':
            valore_str = json.dumps(valore)
        elif tipo_dato == 'boolean':
            valore_str = 'true' if valore else 'false'
        else:
            valore_str = str(valore)
        
        config, created = cls.objects.update_or_create(
            chiave=chiave,
            defaults={
                'valore': valore_str,
                'tipo_dato': tipo_dato,
                'descrizione': descrizione,
                'modificato_da': username,
            }
        )
        return config


# ============================================================================
# AZIONI UTENTI (per tracciare creazioni)
# ============================================================================

class AzioneUtente(models.Model):
    """
    Traccia le azioni degli utenti per la classifica.
    """
    
    TIPO_AZIONE_CHOICES = [
        ('CARICO', 'Carico Magazzino'),
        ('FORNITORE', 'Nuovo Fornitore'),
        ('ARTICOLO', 'Nuovo Articolo'),
        ('IMMAGINE', 'Aggiunta Immagine'),
    ]
    
    username = models.CharField(
        max_length=150,
        verbose_name=_('Username')
    )
    tipo_azione = models.CharField(
        max_length=20,
        choices=TIPO_AZIONE_CHOICES,
        verbose_name=_('Tipo Azione')
    )
    data_azione = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data Azione')
    )
    dettagli = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Dettagli')
    )
    
    class Meta:
        db_table = 'azioni_utenti'
        ordering = ['-data_azione']
        indexes = [
            models.Index(fields=['username', 'tipo_azione']),
            models.Index(fields=['data_azione']),
        ]
        verbose_name = _('Azione Utente')
        verbose_name_plural = _('Azioni Utenti')
    
    def __str__(self):
        return f"{self.username} - {self.get_tipo_azione_display()} ({self.data_azione.strftime('%d/%m/%Y')})"
