"""
Configurazione del pannello admin per l'applicazione Gestione Magazzino Ricambi.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Categoria,
    UnitaMisura,
    Fornitore,
    ModelloMacchinaSCM,
    MatricolaMacchinaSCM,
    PezzoRicambio,
    Giacenza,
    MovimentoMagazzino,
    Inventario,
    DettaglioInventario,
    DocumentoAllegato,
)


# ============================================================================
# CATEGORIA
# ============================================================================

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome_categoria', 'descrizione', 'stato_attivo', 'creato_il')
    list_filter = ('stato_attivo', 'creato_il')
    search_fields = ('nome_categoria', 'descrizione')
    readonly_fields = ('creato_il', 'modificato_il')
    
    fieldsets = (
        (_('Informazioni Generali'), {
            'fields': ('nome_categoria', 'descrizione', 'stato_attivo')
        }),
        (_('Timestamp'), {
            'fields': ('creato_il', 'modificato_il'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# UNITÀ DI MISURA
# ============================================================================

@admin.register(UnitaMisura)
class UnitaMisuraAdmin(admin.ModelAdmin):
    list_display = ('codice', 'descrizione', 'stato_attivo')
    list_filter = ('stato_attivo',)
    search_fields = ('codice', 'descrizione')
    
    fieldsets = (
        (_('Informazioni Generali'), {
            'fields': ('codice', 'descrizione', 'stato_attivo')
        }),
    )


# ============================================================================
# FORNITORE
# ============================================================================

@admin.register(Fornitore)
class FornitoreAdmin(admin.ModelAdmin):
    list_display = ('ragione_sociale', 'citta', 'telefono', 'email', 'stato_attivo')
    list_filter = ('stato_attivo', 'provincia', 'creato_il')
    search_fields = ('ragione_sociale', 'email', 'partita_iva', 'citta')
    readonly_fields = ('creato_il', 'modificato_il')
    
    fieldsets = (
        (_('Dati Generali'), {
            'fields': ('ragione_sociale', 'partita_iva', 'stato_attivo')
        }),
        (_('Indirizzo'), {
            'fields': ('indirizzo', 'citta', 'cap', 'provincia')
        }),
        (_('Contatti'), {
            'fields': ('telefono', 'email')
        }),
        (_('Condizioni Commerciali'), {
            'fields': ('tempo_medio_consegna_giorni', 'note')
        }),
        (_('Timestamp'), {
            'fields': ('creato_il', 'modificato_il'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# MODELLO MACCHINA SCM
# ============================================================================

@admin.register(ModelloMacchinaSCM)
class ModelloMacchinaSCMAdmin(admin.ModelAdmin):
    list_display = ('nome_modello', 'gamma', 'stato_attivo', 'creato_il')
    list_filter = ('stato_attivo', 'gamma', 'creato_il')
    search_fields = ('nome_modello', 'gamma')
    readonly_fields = ('creato_il', 'modificato_il')
    
    fieldsets = (
        (_('Informazioni Generali'), {
            'fields': ('nome_modello', 'gamma', 'stato_attivo')
        }),
        (_('Timestamp'), {
            'fields': ('creato_il', 'modificato_il'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# MATRICOLA MACCHINA SCM
# ============================================================================

@admin.register(MatricolaMacchinaSCM)
class MatricolaMacchinaSCMAdmin(admin.ModelAdmin):
    list_display = ('matricola_macchina', 'modello', 'anno', 'stato_attivo', 'creato_il')
    list_filter = ('stato_attivo', 'modello', 'anno', 'creato_il')
    search_fields = ('matricola_macchina', 'modello__nome_modello')
    readonly_fields = ('creato_il', 'modificato_il')
    
    fieldsets = (
        (_('Informazioni Generali'), {
            'fields': ('modello', 'matricola_macchina', 'anno', 'stato_attivo')
        }),
        (_('Timestamp'), {
            'fields': ('creato_il', 'modificato_il'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# PEZZO DI RICAMBIO (ARTICOLO)
# ============================================================================

@admin.register(PezzoRicambio)
class PezzoRicambioAdmin(admin.ModelAdmin):
    list_display = ('codice_interno', 'descrizione', 'categoria', 'unita_misura', 'stato_attivo')
    list_filter = ('stato_attivo', 'categoria', 'creato_il')
    search_fields = ('codice_interno', 'descrizione', 'codice_fornitore', 'codice_scm')
    readonly_fields = ('creato_il', 'modificato_il')
    
    fieldsets = (
        (_('Codici'), {
            'fields': ('codice_interno', 'codice_scm', 'codice_fornitore', 'codice_alternativo')
        }),
        (_('Descrizione e Classificazione'), {
            'fields': ('descrizione', 'categoria', 'unita_misura')
        }),
        (_('Giacenze'), {
            'fields': ('giacenza_minima', 'giacenza_massima')
        }),
        (_('Prezzi'), {
            'fields': ('prezzo_acquisto', 'prezzo_acquisto_scm')
        }),
        (_('Stato'), {
            'fields': ('stato_attivo',)
        }),
        (_('Timestamp'), {
            'fields': ('creato_il', 'modificato_il'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# GIACENZA
# ============================================================================

@admin.register(Giacenza)
class GiacenzaAdmin(admin.ModelAdmin):
    list_display = ('articolo', 'quantita_disponibile', 'quantita_impegnata', 'quantita_libera', 'ultimo_aggiornamento')
    list_filter = ('ultimo_aggiornamento',)
    search_fields = ('articolo__codice_interno', 'articolo__descrizione')
    readonly_fields = ('ultimo_aggiornamento', 'quantita_libera')
    
    fieldsets = (
        (_('Articolo'), {
            'fields': ('articolo',)
        }),
        (_('Quantità'), {
            'fields': ('quantita_disponibile', 'quantita_impegnata', 'quantita_prenotata', 'quantita_libera')
        }),
        (_('Informazioni'), {
            'fields': ('ultimo_aggiornamento',),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# MOVIMENTO DI MAGAZZINO
# ============================================================================

@admin.register(MovimentoMagazzino)
class MovimentoMagazzinoAdmin(admin.ModelAdmin):
    list_display = ('articolo', 'tipo_movimento', 'quantita', 'operatore', 'data_movimento')
    list_filter = ('tipo_movimento', 'data_movimento', 'operatore')
    search_fields = ('articolo__codice_interno', 'numero_documento', 'operatore')
    readonly_fields = ('data_movimento', 'creato_il')
    
    fieldsets = (
        (_('Articolo e Quantità'), {
            'fields': ('articolo', 'quantita')
        }),
        (_('Tipo Movimento'), {
            'fields': ('tipo_movimento',)
        }),
        (_('Documento'), {
            'fields': ('numero_documento', 'fornitore')
        }),
        (_('Causale'), {
            'fields': ('causale', 'note')
        }),
        (_('Operatore'), {
            'fields': ('operatore',)
        }),
        (_('Timestamp'), {
            'fields': ('data_movimento', 'creato_il'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# INVENTARIO
# ============================================================================

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('data_inventario', 'operatore', 'stato', 'creato_il')
    list_filter = ('stato', 'data_inventario', 'operatore')
    search_fields = ('operatore', 'note')
    readonly_fields = ('creato_il', 'modificato_il')
    
    fieldsets = (
        (_('Informazioni Generali'), {
            'fields': ('data_inventario', 'operatore', 'stato')
        }),
        (_('Note'), {
            'fields': ('note',)
        }),
        (_('Timestamp'), {
            'fields': ('creato_il', 'modificato_il'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# DETTAGLIO INVENTARIO
# ============================================================================

@admin.register(DettaglioInventario)
class DettaglioInventarioAdmin(admin.ModelAdmin):
    list_display = ('inventario', 'articolo', 'quantita_rilevata', 'quantita_sistema', 'differenza', 'ha_discrepanza')
    list_filter = ('inventario__stato', 'inventario__data_inventario')
    search_fields = ('articolo__codice_interno', 'articolo__descrizione')
    readonly_fields = ('differenza', 'creato_il')
    
    fieldsets = (
        (_('Inventario'), {
            'fields': ('inventario',)
        }),
        (_('Articolo'), {
            'fields': ('articolo',)
        }),
        (_('Quantità'), {
            'fields': ('quantita_rilevata', 'quantita_sistema', 'differenza')
        }),
        (_('Note'), {
            'fields': ('note',)
        }),
        (_('Timestamp'), {
            'fields': ('creato_il',),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# DOCUMENTO ALLEGATO
# ============================================================================

@admin.register(DocumentoAllegato)
class DocumentoAllegatoAdmin(admin.ModelAdmin):
    list_display = ('nome_file', 'tipo_entita', 'tipo_documento', 'operatore', 'data_caricamento')
    list_filter = ('tipo_entita', 'tipo_documento', 'data_caricamento')
    search_fields = ('nome_file', 'operatore')
    readonly_fields = ('data_caricamento',)
    
    fieldsets = (
        (_('Entità Correlata'), {
            'fields': ('tipo_entita', 'id_entita')
        }),
        (_('Documento'), {
            'fields': ('tipo_documento', 'nome_file', 'percorso_file')
        }),
        (_('Operatore'), {
            'fields': ('operatore',)
        }),
        (_('Note'), {
            'fields': ('note',)
        }),
        (_('Timestamp'), {
            'fields': ('data_caricamento',),
            'classes': ('collapse',)
        }),
    )
