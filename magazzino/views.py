"""
Views per l'applicazione Gestione Magazzino Ricambi..
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, 
    UpdateView, DeleteView, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, F, Sum, Count
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse, FileResponse, HttpResponse
from django.conf import settings
from datetime import datetime, timedelta
import logging
import secrets
import string

from django.db.models.deletion import ProtectedError
from .forms import (
    CategoriaForm, PezzoRicambioForm, FornitoreForm, 
    MovimentoMagazzinoForm, InventarioForm
)
from .models import (
    Categoria, UnitaMisura, Fornitore, PezzoRicambio, 
    Giacenza, MovimentoMagazzino, Inventario, DettaglioInventario,
    TbTipoPagamento, TbCategoriaIVA, TbContatti
)
from accounts.models import RuoloUtente

logger = logging.getLogger(__name__)


# ============================================================================
# MIXINS PERSONALIZZATI PER I PERMESSI
# ============================================================================

class CanViewMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica se l'utente può visualizzare"""
    login_url = 'accounts:login'
    
    def test_func(self):
        return self.request.user.is_authenticated


class CanEditMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica se l'utente può modificare i dati"""
    login_url = 'accounts:login'
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        try:
            profilo = self.request.user.profilo
            return profilo.può_modificare_dati()
        except:
            return False
    
    def handle_no_permission(self):
        messages.error(
            self.request,
            _('Non hai i permessi necessari per eseguire questa azione.')
        )
        return redirect('magazzino:dashboard')


class SortableListMixin:
    """Mixin per abilitare l'ordinamento nelle liste"""
    sortable_fields = []  # Campi ordinabili, da definire nella view
    default_sort = None   # Campo di ordinamento predefinito
    
    def get_ordering(self):
        """Determina l'ordinamento dalla query string"""
        order = self.request.GET.get('order', self.default_sort)
        
        # Se l'ordinamento è valido, applicalo
        if order:
            # Rimuovi il - per controllo
            field = order.lstrip('-')
            if field in self.sortable_fields:
                return order
        
        return self.default_sort
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_order = self.request.GET.get('order', self.default_sort or '')
        
        # Aggiungi info ordinamento al context
        context['current_order'] = current_order
        context['sortable_fields'] = self.sortable_fields
        
        return context


# ============================================================================
# DASHBOARD - HOME PAGE
# ============================================================================

class DashboardView(CanViewMixin, TemplateView):
    """Dashboard principale con statistiche"""
    template_name = 'magazzino/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiche generali
        context['total_articoli'] = PezzoRicambio.objects.filter(stato_attivo=True).count()
        context['total_fornitori'] = Fornitore.objects.filter(stato_attivo=True).count()
        context['total_categorie'] = Categoria.objects.filter(stato_attivo=True).count()
        
        # Giacenze
        giacenze_total = Giacenza.objects.aggregate(
            total_disponibile=Sum('quantita_disponibile'),
            total_impegnata=Sum('quantita_impegnata')
        )
        context['giacenze'] = giacenze_total
        
        # Articoli sotto soglia
        articoli_sotto_soglia = PezzoRicambio.objects.filter(
            stato_attivo=True,
            giacenza__quantita_disponibile__lt=F('giacenza_minima')
        ).count()
        context['articoli_sotto_soglia'] = articoli_sotto_soglia
        
        # Ultimi movimenti
        context['ultimi_movimenti'] = MovimentoMagazzino.objects.select_related(
            'articolo', 'fornitore'
        ).order_by('-data_movimento')[:10]
        
        # Top 5 utenti per numero di azioni (carichi + fornitori creati)
        from django.contrib.auth.models import User
        from .models import AzioneUtente
        
        # Conta le azioni per ogni utente
        utenti_con_azioni = []
        for user in User.objects.all():
            # Conta azioni registrate con pesi diversi
            azioni = AzioneUtente.objects.filter(username=user.username)
            punti_azioni = 0
            for azione in azioni:
                if azione.tipo_azione == 'IMMAGINE':
                    punti_azioni += 2  # +2 punti per immagini
                else:
                    punti_azioni += 1  # +1 punto per altre azioni
            
            # Conta anche i movimenti IN (per retrocompatibilità con dati esistenti)
            count_carichi = MovimentoMagazzino.objects.filter(
                operatore=user.username,
                tipo_movimento='IN'
            ).count()
            
            total = punti_azioni + count_carichi
            
            if total > 0:
                nome_completo = f"{user.first_name} {user.last_name}".strip() or user.username
                utenti_con_azioni.append({
                    'username': user.username,
                    'operatore': nome_completo,
                    'totale_articoli': total
                })
        
        # Ordina per numero totale e prendi i top 5
        top_operatori = sorted(utenti_con_azioni, key=lambda x: x['totale_articoli'], reverse=True)[:5]
        context['top_operatori'] = top_operatori
        
        # Convertire a JSON per il template
        import json
        context['top_operatori_json'] = json.dumps(top_operatori, default=str)
        
        # Statistiche per ruolo
        try:
            profilo = self.request.user.profilo
            context['ruolo_utente'] = profilo.get_ruolo_display()
        except:
            context['ruolo_utente'] = 'Sconosciuto'
        
        return context


class ResetClassificaView(CanEditMixin, TemplateView):
    """Azzera la classifica degli articoli creati (solo ADMIN/GESTORE)"""
    
    def test_func(self):
        """Solo ADMIN e GESTORE possono azzerare la classifica"""
        if not self.request.user.is_authenticated:
            return False
        try:
            profilo = self.request.user.profilo
            return profilo.è_admin() or profilo.è_gestore_magazzino()
        except:
            return False
    
    def post(self, request, *args, **kwargs):
        try:
            # Elimina tutte le azioni registrate per azzerare la classifica
            from .models import AzioneUtente
            count = AzioneUtente.objects.all().count()
            AzioneUtente.objects.all().delete()
            
            messages.success(
                request,
                f"✅ Classifica azzerata! {count} azioni eliminate."
            )
            logger.warning(
                f"⚠️ Classifica azzerata da {request.user.username}: {count} azioni eliminate"
            )
            
        except Exception as e:
            messages.error(request, f"❌ Errore durante l'azzeramento: {str(e)}")
            logger.error(f"Errore azzeramento classifica: {e}", exc_info=True)
        
        return redirect('magazzino:dashboard')


# ============================================================================
# CATEGORIE - CRUD
# ============================================================================

class CategoriaListView(CanViewMixin, ListView):
    """Lista di tutte le categorie con visualizzazione gerarchica ad albero"""
    model = Categoria
    template_name = 'magazzino/categoria_list.html'
    context_object_name = 'categorie'
    
    def get_queryset(self):
        # Restituisci solo le macrocategorie (livello 0)
        # Le sottocategorie saranno accedute tramite relazione 'sottocategorie'
        queryset = Categoria.objects.filter(categoria_padre__isnull=True).prefetch_related(
            'sottocategorie__sottocategorie'  # Prefetch fino a 3 livelli
        ).order_by('ordine', 'nome_categoria')
        
        # Filtro per ricerca (cerca in tutti i livelli)
        search = self.request.GET.get('search')
        if search:
            # Se c'è una ricerca, mostra tutte le categorie che matchano
            queryset = Categoria.objects.filter(
                Q(nome_categoria__icontains=search) |
                Q(descrizione__icontains=search)
            ).select_related('categoria_padre').order_by('livello', 'ordine', 'nome_categoria')
        
        # Filtro per stato
        stato = self.request.GET.get('stato')
        if stato == 'attivo':
            queryset = queryset.filter(stato_attivo=True)
        elif stato == 'inattivo':
            queryset = queryset.filter(stato_attivo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['stato'] = self.request.GET.get('stato', '')
        # Flag per sapere se siamo in modalità ricerca o tree view
        context['is_search'] = bool(self.request.GET.get('search'))
        return context


class CategoriaCreateView(CanEditMixin, CreateView):
    """Crea una nuova categoria"""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'magazzino/categoria_form.html'
    success_url = reverse_lazy('magazzino:categoria_list')
    
    def get_initial(self):
        """Pre-imposta la categoria padre se passata nella URL"""
        initial = super().get_initial()
        padre_id = self.request.GET.get('padre')
        if padre_id:
            try:
                padre = Categoria.objects.get(pk=padre_id)
                initial['categoria_padre'] = padre
                
                # Pre-popola anche i campi virtuali per le tendine a cascata
                if padre.livello == 0:
                    # Il padre è una macrocategoria -> la nuova sarà livello 1
                    initial['macrocategoria'] = padre
                elif padre.livello == 1:
                    # Il padre è livello 1 -> la nuova sarà livello 2
                    initial['categoria_livello2'] = padre
                    # Imposta anche la macrocategoria (nonno)
                    if padre.categoria_padre:
                        initial['macrocategoria'] = padre.categoria_padre
            except Categoria.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, _('Categoria creata con successo!'))
        logger.info(f"✨ Categoria creata: {form.cleaned_data['nome_categoria']}")
        return super().form_valid(form)


class CategoriaUpdateView(CanEditMixin, UpdateView):
    """Modifica una categoria"""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'magazzino/categoria_form.html'
    
    def get_success_url(self):
        return reverse('magazzino:categoria_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Categoria aggiornata con successo!'))
        logger.info(f"✏️ Categoria aggiornata: {form.cleaned_data['nome_categoria']}")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        logger.warning(f"⚠️ Form invalida per categoria: {form.errors}")
        return super().form_invalid(form)


class CategoriaDeleteView(CanEditMixin, DeleteView):
    """Elimina una categoria"""
    model = Categoria
    template_name = 'magazzino/categoria_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('magazzino:categoria_list')
    
    def post(self, request, *args, **kwargs):
        categoria = self.get_object()
        
        # Proteggi la categoria di fallback da eliminazione accidentale
        if categoria.nome_categoria == "Nessuna (da caratterizzare)":
            messages.error(
                request,
                "❌ Non puoi eliminare la categoria 'Nessuna (da caratterizzare)' - è una categoria di sistema necessaria!"
            )
            logger.warning(f"❌ Tentativo di eliminare categoria di fallback: {categoria.nome_categoria}")
            return redirect('magazzino:categoria_list')
        
        # Verifica se ha sottocategorie
        sottocategorie = Categoria.objects.filter(categoria_padre=categoria)
        if sottocategorie.exists():
            sottocategorie_nomi = ', '.join([f'"{c.nome_categoria}"' for c in sottocategorie[:5]])
            if sottocategorie.count() > 5:
                sottocategorie_nomi += f' e altre {sottocategorie.count() - 5}'
            
            messages.error(
                request,
                f'❌ Impossibile eliminare "{categoria.nome_categoria}": contiene {sottocategorie.count()} '
                f'sottocategoria/e ({sottocategorie_nomi}). Elimina prima le sottocategorie o spostale altrove.'
            )
            logger.warning(f"⚠️ Tentativo di eliminare categoria con sottocategorie: {categoria.nome_categoria}")
            return redirect('magazzino:categoria_list')
        
        # Ottieni la categoria di fallback "Nessuna (da caratterizzare)"
        try:
            categoria_fallback = Categoria.objects.get(nome_categoria="Nessuna (da caratterizzare)")
        except Categoria.DoesNotExist:
            messages.error(
                request,
                "❌ Errore: Categoria di fallback 'Nessuna (da caratterizzare)' non trovata. Contatta l'amministratore."
            )
            logger.error("❌ Categoria di fallback non trovata")
            return redirect('magazzino:categoria_list')
        
        # Se la categoria da eliminare ha articoli, riassegnali alla categoria di fallback
        articoli_da_riassegnare = PezzoRicambio.objects.filter(categoria=categoria)
        if articoli_da_riassegnare.exists():
            num_articoli = articoli_da_riassegnare.count()
            articoli_da_riassegnare.update(categoria=categoria_fallback)
            messages.warning(
                request,
                f"⚠️ {num_articoli} articolo/i della categoria '{categoria.nome_categoria}' "
                f"sono stati riassegnati a 'Nessuna (da caratterizzare)' per essere caratterizzati manualmente."
            )
            logger.info(
                f"📋 {num_articoli} articoli riassegnati da '{categoria.nome_categoria}' "
                f"a '{categoria_fallback.nome_categoria}'"
            )
        
        # Procedi con la cancellazione standard
        return super().post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        categoria = self.get_object()
        
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, _('Categoria eliminata con successo!'))
            logger.info(f"🗑️ Categoria eliminata: {categoria.nome_categoria}")
            return result
        except ProtectedError as e:
            # Se c'è ancora un ProtectedError per altri motivi
            messages.error(
                request,
                f"❌ Impossibile eliminare la categoria: è ancora referenziata da altri elementi del sistema."
            )
            logger.error(f"❌ ProtectedError per categoria {categoria.nome_categoria}: {str(e)}")
            return redirect('magazzino:categoria_list')


# ============================================================================
# CATEGORIE - OPERAZIONI AVANZATE (Drag & Drop)
# ============================================================================

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
@require_POST
def categoria_move(request):
    """Sposta una categoria via drag & drop"""
    try:
        data = json.loads(request.body)
        categoria_id = data.get('categoria_id')
        nuova_categoria_padre_id = data.get('nuovo_padre_id')  # None = radice
        nuovo_ordine = data.get('nuovo_ordine', 0)
        
        categoria = Categoria.objects.get(pk=categoria_id)
        
        # Verifica che non stia provando a spostare sotto se stessa o un suo discendente
        if nuova_categoria_padre_id:
            nuovo_padre = Categoria.objects.get(pk=nuova_categoria_padre_id)
            
            # Controllo 1: Non spostare sotto se stessa
            if categoria.pk == nuovo_padre.pk:
                return JsonResponse({
                    'success': False,
                    'error': 'Non puoi spostare una categoria sotto se stessa'
                }, status=400)
            
            # Controllo 2: Verifica che nuovo_padre non sia un discendente di categoria
            # (usa un controllo iterativo sicuro invece di ricorsivo)
            current = nuovo_padre
            visited = set()
            is_descendant = False
            max_iterations = 10
            iterations = 0
            
            while current and iterations < max_iterations:
                if current.pk == categoria.pk:
                    is_descendant = True
                    break
                if current.pk in visited:
                    break  # Loop rilevato
                visited.add(current.pk)
                current = current.categoria_padre
                iterations += 1
            
            if is_descendant:
                return JsonResponse({
                    'success': False,
                    'error': 'Non puoi spostare una categoria sotto uno dei suoi discendenti'
                }, status=400)
            
            # Verifica limite 3 livelli
            if nuovo_padre.livello >= 2:
                return JsonResponse({
                    'success': False,
                    'error': 'Massimo 3 livelli di categorie consentiti'
                }, status=400)
            
            categoria.categoria_padre = nuovo_padre
        else:
            categoria.categoria_padre = None
        
        categoria.ordine = nuovo_ordine
        categoria.save()  # Il livello si aggiorna automaticamente nel save()
        
        messages.success(request, f'✅ Categoria "{categoria.nome_categoria}" spostata con successo!')
        logger.info(f"📦 Categoria spostata: {categoria.nome_categoria} -> {categoria.get_breadcrumb()}")
        
        return JsonResponse({
            'success': True,
            'nuovo_breadcrumb': categoria.get_breadcrumb(),
            'nuovo_livello': categoria.livello
        })
        
    except Categoria.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Categoria non trovata'}, status=404)
    except Exception as e:
        logger.error(f"❌ Errore spostamento categoria: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_categorie_figlie(request, parent_id):
    """API per ottenere le categorie figlie di una categoria padre (per dropdown a cascata)"""
    try:
        categorie = Categoria.objects.filter(
            categoria_padre_id=parent_id,
            stato_attivo=True
        ).order_by('ordine', 'nome_categoria').values('id_categoria', 'nome_categoria')
        
        return JsonResponse({
            'success': True,
            'categorie': list(categorie)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# PEZZI DI RICAMBIO / ARTICOLI - CRUD
# ============================================================================

class PezzoRicambioListView(SortableListMixin, CanViewMixin, ListView):
    """Lista di tutti gli articoli"""
    model = PezzoRicambio
    template_name = 'magazzino/articolo_list.html'
    context_object_name = 'articoli'
    paginate_by = 50
    sortable_fields = ['codice_interno', 'descrizione', 'categoria__nome_categoria', 'giacenza__quantita_disponibile', 'prezzo_acquisto', 'stato_disponibilita']
    default_sort = 'descrizione'
    
    def get_queryset(self):
        queryset = PezzoRicambio.objects.select_related(
            'categoria', 'unita_misura', 'giacenza'
        ).order_by(self.get_ordering())
        
        # Filtro per ricerca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(codice_interno__icontains=search) |
                Q(descrizione__icontains=search) |
                Q(codice_fornitore__icontains=search)
            )
        
        # Filtro per categoria (GERARCHICO: include sottocategorie)
        categoria = self.request.GET.get('categoria')
        if categoria:
            try:
                cat = Categoria.objects.get(pk=categoria)
                # Includi la categoria selezionata + tutte le sue sottocategorie
                categoria_ids = [cat.id_categoria] + cat.get_all_children_ids()
                queryset = queryset.filter(categoria_id__in=categoria_ids)
            except Categoria.DoesNotExist:
                pass
        
        # Filtro per stato
        stato = self.request.GET.get('stato')
        if stato:
            queryset = queryset.filter(stato_attivo=stato == 'attivo')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa solo le macrocategorie (livello 0) per il filtro
        context['macrocategorie'] = Categoria.objects.filter(stato_attivo=True, livello=0).order_by('ordine', 'nome_categoria')
        # Mantieni tutte le categorie per retrocompatibilità, se necessario
        context['categorie'] = Categoria.objects.filter(stato_attivo=True).order_by('livello', 'ordine', 'nome_categoria')
        return context


class PezzoRicambioDetailView(CanViewMixin, DetailView):
    """Dettagli di un articolo"""
    model = PezzoRicambio
    template_name = 'magazzino/pezzoricambio_detail.html'
    context_object_name = 'articolo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articolo = self.get_object()
        
        try:
            context['giacenza'] = articolo.giacenza
        except Giacenza.DoesNotExist:
            context['giacenza'] = None
        
        context['ultimi_movimenti'] = articolo.movimenti.select_related(
            'fornitore'
        ).order_by('-data_movimento')[:10]
        
        return context


class PezzoRicambioCreateView(CanEditMixin, CreateView):
    """Crea un nuovo articolo"""
    model = PezzoRicambio
    form_class = PezzoRicambioForm
    template_name = 'magazzino/pezzoricambio_form.html'
    success_url = reverse_lazy('magazzino:articolo_list')
    
    def form_valid(self, form):
        # Assegna la categoria calcolata dal clean()
        if 'categoria' in form.cleaned_data:
            form.instance.categoria = form.cleaned_data['categoria']
        
        # Crea automaticamente la giacenza
        response = super().form_valid(form)
        articolo = self.object
        
        Giacenza.objects.get_or_create(
            articolo=articolo,
            defaults={
                'quantita_disponibile': 0,
                'quantita_impegnata': 0,
                'quantita_prenotata': 0,
            }
        )
        
        # Registra azione per la classifica
        from .models import AzioneUtente
        punti = 1  # Punto base per creazione articolo
        bonus_dettagli = []
        
        # Bonus +2 punti se ha caricato un'immagine
        if articolo.immagine:
            punti += 2
            bonus_dettagli.append('immagine')
            AzioneUtente.objects.create(
                username=self.request.user.username,
                tipo_azione='IMMAGINE',
                dettagli=f"Aggiunta immagine a nuovo articolo: {articolo.codice_interno}"
            )
        
        # Registra creazione articolo
        AzioneUtente.objects.create(
            username=self.request.user.username,
            tipo_azione='ARTICOLO',
            dettagli=f"Creato articolo: {articolo.codice_interno}"
        )
        
        # Messaggio di successo
        if bonus_dettagli:
            messages.success(
                self.request, 
                f'✅ Articolo creato con successo! +{punti} punti (base +1, bonus immagine +2)'
            )
        else:
            messages.success(
                self.request, 
                f'✅ Articolo creato con successo! +1 punto (aggiungi un\'immagine per +2 punti)'
            )
        
        logger.info(f"✨ Articolo creato: {form.cleaned_data['codice_interno']} da {self.request.user.username} (+{punti} punti)")
        return response


class PezzoRicambioUpdateView(CanEditMixin, UpdateView):
    """Modifica un articolo"""
    model = PezzoRicambio
    form_class = PezzoRicambioForm
    template_name = 'magazzino/pezzoricambio_form.html'
    
    def get_success_url(self):
        return reverse('magazzino:articolo_list')
    
    def form_valid(self, form):
        # Salva l'immagine precedente per confronto
        old_instance = PezzoRicambio.objects.get(pk=self.object.pk)
        aveva_immagine = bool(old_instance.immagine)
        
        # Assegna la categoria calcolata dal clean()
        if 'categoria' in form.cleaned_data:
            form.instance.categoria = form.cleaned_data['categoria']
        
        response = super().form_valid(form)
        
        # Verifica se è stata aggiunta un'immagine dove prima non c'era
        ha_immagine_ora = bool(self.object.immagine)
        
        if ha_immagine_ora and not aveva_immagine:
            # Bonus +2 punti per aggiunta immagine in articolo esistente
            from .models import AzioneUtente
            AzioneUtente.objects.create(
                username=self.request.user.username,
                tipo_azione='IMMAGINE',
                dettagli=f"Aggiunta immagine ad articolo esistente: {self.object.codice_interno}"
            )
            messages.success(
                self.request, 
                _('✅ Articolo aggiornato con successo! +2 punti per aggiunta immagine')
            )
            logger.info(f"🖼️ Immagine aggiunta a {self.object.codice_interno} da {self.request.user.username} (+2 punti)")
        else:
            messages.success(self.request, _('Articolo aggiornato con successo!'))
            logger.info(f"Articolo aggiornato: {form.cleaned_data['codice_interno']}")
        
        return response
    
    def form_invalid(self, form):
        logger.warning(f"Form invalida per articolo: {form.errors}")
        return super().form_invalid(form)


class PezzoRicambioDeleteView(CanEditMixin, DeleteView):
    """Elimina un articolo"""
    model = PezzoRicambio
    template_name = 'magazzino/articolo_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('magazzino:articolo_list')
    
    def post(self, request, *args, **kwargs):
        articolo = self.get_object()
        
        # Ottieni i movimenti associati all'articolo
        movimenti_da_eliminare = MovimentoMagazzino.objects.filter(articolo=articolo)
        
        if movimenti_da_eliminare.exists() and not request.POST.get('confirm_delete_with_movements'):
            num_movimenti = movimenti_da_eliminare.count()
            messages.warning(
                request,
                f"⚠️ Questo articolo ha {num_movimenti} movimento/i associato/i. "
                f"Se continui, verranno eliminati anche i movimenti. Confermi?"
            )
            logger.warning(
                f"⚠️ Tentativo di eliminare articolo con {num_movimenti} movimenti: {articolo.codice_interno}"
            )
            return redirect('magazzino:articolo_detail', pk=articolo.pk)
        
        # Se abbiamo movimenti e la conferma è stata data, eliminiamo i movimenti
        if movimenti_da_eliminare.exists() and request.POST.get('confirm_delete_with_movements'):
            num_movimenti = movimenti_da_eliminare.count()
            movimenti_da_eliminare.delete()
            messages.info(
                request,
                f"🗑️ {num_movimenti} movimento/i associato/i all'articolo '{articolo.codice_interno}' sono stati eliminati."
            )
            logger.info(
                f"🗑️ {num_movimenti} movimenti eliminati per cancellazione articolo: {articolo.codice_interno}"
            )
        
        # Procedi con la cancellazione standard
        return super().post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        articolo = self.get_object()
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, _('Articolo eliminato con successo!'))
            logger.info(f"🗑️ Articolo eliminato: {articolo.codice_interno}")
            return result
        except ProtectedError as e:
            # Se c'è ancora un ProtectedError (per altre relazioni), mostra errore
            messages.error(
                request,
                f"❌ Errore: Non è stato possibile eliminare l'articolo. Contatta l'amministratore."
            )
            logger.error(f"❌ ProtectedError inaspettato per articolo {articolo.codice_interno}: {str(e)}")
            return redirect('magazzino:articolo_detail', pk=articolo.pk)


# ============================================================================
# FORNITORI - CRUD
# ============================================================================

class FornitoreListView(SortableListMixin, CanViewMixin, ListView):
    """Lista di tutti i fornitori"""
    model = Fornitore
    template_name = 'magazzino/fornitore_list.html'
    context_object_name = 'fornitori'
    paginate_by = 50
    sortable_fields = ['ragione_sociale', 'citta', 'email', 'tempo_medio_consegna_giorni']
    default_sort = 'ragione_sociale'
    
    def get_queryset(self):
        queryset = Fornitore.objects.order_by(self.get_ordering())
        
        # Filtro per ricerca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(ragione_sociale__icontains=search) |
                Q(email__icontains=search) |
                Q(partita_iva__icontains=search)
            )
        
        # Filtro per stato
        stato = self.request.GET.get('stato')
        if stato:
            queryset = queryset.filter(stato_attivo=stato == 'attivo')
        
        return queryset


class FornitoreDetailView(CanViewMixin, DetailView):
    """Dettagli di un fornitore"""
    model = Fornitore
    template_name = 'magazzino/fornitore_detail.html'
    context_object_name = 'fornitore'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fornitore = self.get_object()
        
        context['articoli'] = PezzoRicambio.objects.filter(
            codice_fornitore__isnull=False,
            stato_attivo=True
        )[:20]
        
        context['ultimi_movimenti'] = MovimentoMagazzino.objects.filter(
            fornitore=fornitore
        ).select_related('articolo').order_by('-data_movimento')[:10]
        
        return context


class FornitoreCreateView(CanEditMixin, CreateView):
    """Crea un nuovo fornitore"""
    model = Fornitore
    form_class = FornitoreForm
    template_name = 'magazzino/fornitore_form.html'
    success_url = reverse_lazy('magazzino:fornitore_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registra l'azione per la classifica
        from .models import AzioneUtente
        AzioneUtente.objects.create(
            username=self.request.user.username,
            tipo_azione='FORNITORE',
            dettagli=f"Creato fornitore: {form.cleaned_data['ragione_sociale']}"
        )
        
        messages.success(self.request, _('Fornitore creato con successo! +1 punto classifica'))
        logger.info(f"✨ Fornitore creato: {form.cleaned_data['ragione_sociale']} da {self.request.user.username}")
        return response


class FornitoreUpdateView(CanEditMixin, UpdateView):
    """Modifica un fornitore"""
    model = Fornitore
    form_class = FornitoreForm
    template_name = 'magazzino/fornitore_form.html'
    
    def get_success_url(self):
        return reverse('magazzino:fornitore_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Fornitore aggiornato con successo!'))
        logger.info(f"✏️ Fornitore aggiornato: {form.cleaned_data['ragione_sociale']}")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        logger.warning(f"⚠️ Form invalida per fornitore: {form.errors}")
        return super().form_invalid(form)


class FornitoreDeleteView(CanEditMixin, DeleteView):
    """Elimina un fornitore, riassegnando i movimenti al fornitore fallback"""
    model = Fornitore
    template_name = 'magazzino/fornitore_confirm_delete.html'
    success_url = reverse_lazy('magazzino:fornitore_list')
    
    def post(self, request, *args, **kwargs):
        """Riassegna movimenti al fornitore fallback prima della cancellazione"""
        fornitore = self.get_object()
        
        # ID fisso del fornitore fallback
        FALLBACK_FORNITORE_ID = 999
        
        # Proteggi il fornitore fallback stesso dalla cancellazione
        if fornitore.id_fornitore == FALLBACK_FORNITORE_ID:
            messages.error(
                request,
                _("⚠️ Non puoi eliminare il fornitore 'Non Specificato'. È un fornitore di sistema.")
            )
            logger.warning(f"❌ Tentativo di eliminare fornitore fallback: {fornitore.ragione_sociale}")
            return redirect('magazzino:fornitore_list')
        
        # Recupera tutti i movimenti che riferenziano questo fornitore
        movimenti_da_riassegnare = MovimentoMagazzino.objects.filter(fornitore=fornitore)
        count_movimenti = movimenti_da_riassegnare.count()
        
        if count_movimenti > 0:
            try:
                # Recupera il fornitore fallback
                fornitore_fallback = Fornitore.objects.get(id_fornitore=FALLBACK_FORNITORE_ID)
                
                # Riassegna tutti i movimenti al fornitore fallback
                movimenti_da_riassegnare.update(fornitore=fornitore_fallback)
                
                logger.info(
                    f"🔄 {count_movimenti} movimento/i riassegnato/i da '{fornitore.ragione_sociale}' "
                    f"a '{fornitore_fallback.ragione_sociale}'"
                )
                
                # Mostra messaggio di avviso all'utente
                messages.warning(
                    request,
                    f"⚠️ {count_movimenti} movimento/i è/sono stato/i riassegnato/i al fornitore "
                    f"'Non Specificato' perché il fornitore '{fornitore.ragione_sociale}' è stato eliminato."
                )
                
            except Fornitore.DoesNotExist:
                messages.error(
                    request,
                    _("Errore: Fornitore fallback non trovato. Contattare l'amministratore.")
                )
                logger.error(f"❌ Fornitore fallback (ID={FALLBACK_FORNITORE_ID}) non trovato nel DB")
                return redirect('magazzino:fornitore_list')
        
        # Procedi con la cancellazione del fornitore
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, _(f'Fornitore "{fornitore.ragione_sociale}" eliminato con successo!'))
            logger.info(f"🗑️ Fornitore eliminato: {fornitore.ragione_sociale}")
            return result
        except Exception as e:
            messages.error(request, _('Errore durante l\'eliminazione del fornitore.'))
            logger.error(f"❌ Errore eliminazione fornitore: {str(e)}")
            return redirect('magazzino:fornitore_list')


# ============================================================================
# MODELLI MACCHINE SCM
# ============================================================================

class ModelloSCMListView(SortableListMixin, CanViewMixin, ListView):
    """Lista di tutti i modelli macchine SCM"""
    model = None  # Definito in get_queryset
    template_name = 'magazzino/modello_scm_list.html'
    context_object_name = 'modelli'
    paginate_by = 50
    sortable_fields = ['nome_modello', 'gamma']
    default_sort = 'nome_modello'
    
    def get_queryset(self):
        from .models import ModelloMacchinaSCM
        queryset = ModelloMacchinaSCM.objects.filter(stato_attivo=True).order_by(self.get_ordering())
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_modello__icontains=search) |
                Q(gamma__icontains=search)
            )
        
        return queryset


class ModelloSCMCreateView(CanEditMixin, CreateView):
    """Crea un nuovo modello macchina SCM"""
    template_name = 'magazzino/modello_scm_form.html'
    success_url = reverse_lazy('magazzino:modello_scm_list')
    fields = ['nome_modello', 'gamma']
    
    def get_queryset(self):
        from .models import ModelloMacchinaSCM
        return ModelloMacchinaSCM.objects.all()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registra l'azione per la classifica
        from .models import AzioneUtente
        AzioneUtente.objects.create(
            username=self.request.user.username,
            tipo_azione='MODELLO_SCM',
            dettagli=f"Creato modello SCM: {form.cleaned_data['nome_modello']}"
        )
        
        messages.success(self.request, _('Modello macchina creato con successo! +1 punto classifica'))
        logger.info(f"✨ Modello SCM creato: {form.cleaned_data['nome_modello']} da {self.request.user.username}")
        return response


class ModelloSCMUpdateView(CanEditMixin, UpdateView):
    """Modifica un modello macchina SCM"""
    template_name = 'magazzino/modello_scm_form.html'
    success_url = reverse_lazy('magazzino:modello_scm_list')
    fields = ['nome_modello', 'gamma', 'stato_attivo']
    
    def get_queryset(self):
        from .models import ModelloMacchinaSCM
        return ModelloMacchinaSCM.objects.all()
    
    def form_valid(self, form):
        messages.success(self.request, _('Modello macchina aggiornato con successo!'))
        return super().form_valid(form)


class ModelloSCMDeleteView(CanEditMixin, DeleteView):
    """Elimina un modello macchina SCM"""
    template_name = 'magazzino/modello_scm_confirm_delete.html'
    success_url = reverse_lazy('magazzino:modello_scm_list')
    
    def get_queryset(self):
        from .models import ModelloMacchinaSCM
        return ModelloMacchinaSCM.objects.all()
    
    def post(self, request, *args, **kwargs):
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, _('Modello macchina eliminato con successo!'))
            return result
        except ProtectedError:
            messages.error(
                request,
                _('Impossibile eliminare: ci sono matricole associate a questo modello.')
            )
            return redirect('magazzino:modello_scm_list')


# ============================================================================
# MATRICOLE MACCHINE SCM
# ============================================================================

class MatricolaSCMListView(SortableListMixin, CanViewMixin, ListView):
    """Lista di tutte le matricole macchine SCM"""
    model = None
    template_name = 'magazzino/matricola_scm_list.html'
    context_object_name = 'matricole'
    paginate_by = 50
    sortable_fields = ['modello__nome_modello', 'matricola_macchina', 'anno']
    default_sort = 'modello__nome_modello'
    
    def get_queryset(self):
        from .models import MatricolaMacchinaSCM
        queryset = MatricolaMacchinaSCM.objects.select_related('modello').filter(
            stato_attivo=True
        ).order_by(self.get_ordering())
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(matricola_macchina__icontains=search) |
                Q(modello__nome_modello__icontains=search)
            )
        
        modello_id = self.request.GET.get('modello')
        if modello_id:
            queryset = queryset.filter(modello_id=modello_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        from .models import ModelloMacchinaSCM
        context = super().get_context_data(**kwargs)
        context['modelli'] = ModelloMacchinaSCM.objects.filter(stato_attivo=True).order_by('nome_modello')
        return context


class MatricolaSCMCreateView(CanEditMixin, CreateView):
    """Crea una nuova matricola macchina SCM"""
    template_name = 'magazzino/matricola_scm_form.html'
    success_url = reverse_lazy('magazzino:matricola_scm_list')
    fields = ['modello', 'matricola_macchina', 'anno']
    
    def get_queryset(self):
        from .models import MatricolaMacchinaSCM
        return MatricolaMacchinaSCM.objects.all()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registra l'azione per la classifica
        from .models import AzioneUtente
        AzioneUtente.objects.create(
            username=self.request.user.username,
            tipo_azione='MATRICOLA_SCM',
            dettagli=f"Creata matricola SCM: {form.cleaned_data['matricola_macchina']}"
        )
        
        messages.success(self.request, _('Matricola macchina creata con successo! +1 punto classifica'))
        logger.info(f"✨ Matricola SCM creata: {form.cleaned_data['matricola_macchina']} da {self.request.user.username}")
        return response


class MatricolaSCMUpdateView(CanEditMixin, UpdateView):
    """Modifica una matricola macchina SCM"""
    template_name = 'magazzino/matricola_scm_form.html'
    success_url = reverse_lazy('magazzino:matricola_scm_list')
    fields = ['modello', 'matricola_macchina', 'anno', 'stato_attivo']
    
    def get_queryset(self):
        from .models import MatricolaMacchinaSCM
        return MatricolaMacchinaSCM.objects.all()
    
    def form_valid(self, form):
        messages.success(self.request, _('Matricola macchina aggiornata con successo!'))
        return super().form_valid(form)


class MatricolaSCMDeleteView(CanEditMixin, DeleteView):
    """Elimina una matricola macchina SCM"""
    template_name = 'magazzino/matricola_scm_confirm_delete.html'
    success_url = reverse_lazy('magazzino:matricola_scm_list')
    
    def get_queryset(self):
        from .models import MatricolaMacchinaSCM
        return MatricolaMacchinaSCM.objects.all()
    
    def post(self, request, *args, **kwargs):
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(request, _('Matricola macchina eliminata con successo!'))
            return result
        except ProtectedError:
            messages.error(
                request,
                _('Impossibile eliminare: ci sono articoli associati a questa matricola.')
            )
            return redirect('magazzino:matricola_scm_list')


# ============================================================================
# MOVIMENTI DI MAGAZZINO
# ============================================================================

class MovimentoListView(SortableListMixin, CanViewMixin, ListView):
    """Lista di tutti i movimenti"""
    model = MovimentoMagazzino
    template_name = 'magazzino/movimento_list.html'
    context_object_name = 'movimenti'
    paginate_by = 50
    sortable_fields = ['data_movimento', 'articolo__codice_interno', 'tipo_movimento', 'quantita', 'fornitore__ragione_sociale']
    default_sort = '-data_movimento'
    
    def get_queryset(self):
        queryset = MovimentoMagazzino.objects.select_related(
            'articolo', 'fornitore'
        ).order_by(self.get_ordering())
        
        # Filtro per tipo movimento
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_movimento=tipo)
        
        # Filtro per data
        data_da = self.request.GET.get('data_da')
        if data_da:
            queryset = queryset.filter(data_movimento__gte=data_da)
        
        data_a = self.request.GET.get('data_a')
        if data_a:
            queryset = queryset.filter(data_movimento__lte=data_a)
        
        return queryset


class MovimentoDetailView(CanViewMixin, DetailView):
    """Dettagli di un movimento"""
    model = MovimentoMagazzino
    template_name = 'magazzino/movimento_detail.html'
    context_object_name = 'movimento'


class MovimentoCreateView(CanEditMixin, CreateView):
    """Registra un nuovo movimento di magazzino"""
    model = MovimentoMagazzino
    form_class = MovimentoMagazzinoForm
    template_name = 'magazzino/movimento_form.html'
    success_url = reverse_lazy('magazzino:movimento_list')
    
    def get_initial(self):
        """Precompila l'articolo e fornitore se viene passato come parametro GET"""
        initial = super().get_initial()
        articolo_id = self.request.GET.get('articolo')
        if articolo_id:
            try:
                articolo = PezzoRicambio.objects.get(id_articolo=articolo_id)
                initial['articolo'] = articolo
                # Precompila anche il fornitore se presente
                if articolo.fornitore:
                    initial['fornitore'] = articolo.fornitore
            except PezzoRicambio.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        movimento = form.save(commit=False)
        movimento.operatore = self.request.user.username
        movimento.save()
        
        # Registra azione se è un CARICO (IN)
        if movimento.tipo_movimento == 'CARICO':
            from .models import AzioneUtente
            AzioneUtente.objects.create(
                username=self.request.user.username,
                tipo_azione='CARICO',
                dettagli=f"Carico articolo: {movimento.articolo.codice_interno}"
            )
        
        # Aggiorna la giacenza
        articolo = movimento.articolo
        giacenza = articolo.giacenza
        
        if movimento.tipo_movimento == 'CARICO':
            giacenza.quantita_disponibile += movimento.quantita
        elif movimento.tipo_movimento in ['SCARICO', 'RESO_FORNITORE']:
            giacenza.quantita_disponibile = max(0, giacenza.quantita_disponibile - movimento.quantita)
        elif movimento.tipo_movimento == 'RETTIFICA':
            # Per rettifiche, il valore inserito è la nuova quantità
            giacenza.quantita_disponibile = movimento.quantita
        
        giacenza.save()
        
        messages.success(self.request, _('Movimento registrato con successo!'))
        logger.info(f"📦 Movimento registrato: {movimento.tipo_movimento} - {articolo.codice_interno}")
        return super().form_valid(form)


# ============================================================================
# GIACENZE
# ============================================================================

class GiacenzaListView(SortableListMixin, CanViewMixin, ListView):
    """Lista di tutte le giacenze"""
    model = Giacenza
    template_name = 'magazzino/giacenza_list.html'
    context_object_name = 'giacenze'
    paginate_by = 50
    sortable_fields = ['articolo__codice_interno', 'articolo__descrizione', 'quantita_disponibile', 'quantita_libera', 'quantita_impegnata']
    default_sort = '-quantita_disponibile'
    
    def get_queryset(self):
        queryset = Giacenza.objects.select_related(
            'articolo', 'articolo__categoria'
        ).order_by(self.get_ordering())
        
        # Filtro per ricerca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                articolo__codice_interno__icontains=search
            )
        
        # Filtro per soglia
        soglia = self.request.GET.get('soglia')
        if soglia == 'sotto':
            queryset = queryset.filter(
                quantita_disponibile__lt=F('articolo__giacenza_minima')
            )
        elif soglia == 'sopra':
            queryset = queryset.filter(
                quantita_disponibile__gt=F('articolo__giacenza_massima')
            )
        
        return queryset


class GiacenzaDetailView(CanViewMixin, DetailView):
    """Dettagli di una giacenza"""
    model = Giacenza
    template_name = 'magazzino/giacenza_detail.html'
    context_object_name = 'giacenza'


# ============================================================================
# REPORT E STATISTICHE
# ============================================================================

class GiacenzeReportView(CanViewMixin, TemplateView):
    """Report delle giacenze"""
    template_name = 'magazzino/report_giacenze.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Articoli sotto soglia
        context['sotto_soglia'] = Giacenza.objects.filter(
            quantita_disponibile__lt=F('articolo__giacenza_minima'),
            articolo__stato_attivo=True
        ).select_related('articolo', 'articolo__categoria').order_by('quantita_disponibile')
        
        # Articoli sopra soglia
        context['sopra_soglia'] = Giacenza.objects.filter(
            quantita_disponibile__gt=F('articolo__giacenza_massima'),
            articolo__stato_attivo=True
        ).select_related('articolo', 'articolo__categoria').order_by('-quantita_disponibile')
        
        # Statistiche totali
        context['statistiche'] = Giacenza.objects.aggregate(
            total_articoli=Count('articolo'),
            total_disponibile=Sum('quantita_disponibile'),
            total_impegnata=Sum('quantita_impegnata'),
            total_prenotata=Sum('quantita_prenotata'),
        )
        
        return context


class MovimentiReportView(CanViewMixin, TemplateView):
    """Report dei movimenti"""
    template_name = 'magazzino/report_movimenti.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ultimi 30 giorni
        data_inizio = datetime.now() - timedelta(days=30)
        
        context['movimenti_ultimi_30_giorni'] = MovimentoMagazzino.objects.filter(
            data_movimento__gte=data_inizio
        ).select_related('articolo', 'fornitore').order_by('-data_movimento')
        
        # Statistiche per tipo movimento
        context['statistiche_tipo'] = MovimentoMagazzino.objects.filter(
            data_movimento__gte=data_inizio
        ).values('tipo_movimento').annotate(
            count=Count('id_movimento'),
            quantita_totale=Sum('quantita')
        )
        
        # Statistiche per operatore
        context['statistiche_operatore'] = MovimentoMagazzino.objects.filter(
            data_movimento__gte=data_inizio
        ).values('operatore').annotate(
            count=Count('id_movimento')
        ).order_by('-count')[:10]
        
        return context


# ============================================================================
# GESTIONE UTENTI
# ============================================================================

class UtenteListView(CanViewMixin, ListView):
    """Lista di tutti gli utenti del sistema"""
    model = User
    template_name = 'magazzino/utente_list.html'
    context_object_name = 'utenti'
    paginate_by = 20
    
    def test_func(self):
        """Solo ADMIN e GESTORE_MAGAZZINO possono visualizzare"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.ruolo in [
                RuoloUtente.ADMIN,
                RuoloUtente.GESTORE_MAGAZZINO
            ]
        except:
            return False
    
    def get_queryset(self):
        queryset = User.objects.all().select_related('profilo').order_by('username')
        
        # Filtro per ricerca
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Filtro per ruolo
        ruolo = self.request.GET.get('ruolo', '')
        if ruolo:
            queryset = queryset.filter(profilo__ruolo=ruolo)
        
        # Filtro per stato
        stato = self.request.GET.get('stato', '')
        if stato == 'attivo':
            queryset = queryset.filter(is_active=True)
        elif stato == 'inattivo':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ruoli'] = RuoloUtente.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['ruolo_filtro'] = self.request.GET.get('ruolo', '')
        context['stato_filtro'] = self.request.GET.get('stato', '')
        
        # Statistiche utenti
        context['total_utenti'] = User.objects.count()
        context['utenti_attivi'] = User.objects.filter(is_active=True).count()
        context['utenti_admin'] = User.objects.filter(
            profilo__ruolo=RuoloUtente.ADMIN
        ).count()
        
        return context


class UtenteDetailView(CanViewMixin, DetailView):
    """Dettaglio di un utente"""
    model = User
    template_name = 'magazzino/utente_detail.html'
    context_object_name = 'utente_obj'
    
    def test_func(self):
        """Admin e Gestore possono vedere tutti, altri solo se stessi"""
        if not self.request.user.is_authenticated:
            return False
        try:
            # Admin e gestore vedono tutti
            if self.request.user.profilo.ruolo in [
                RuoloUtente.ADMIN,
                RuoloUtente.GESTORE_MAGAZZINO
            ]:
                return True
            # Altri vedono solo se stessi
            return self.get_object() == self.request.user
        except:
            return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        utente = self.object
        
        # Ultimi accessi
        from accounts.models import LogAccesso
        context['ultimi_accessi'] = LogAccesso.objects.filter(
            user=utente
        ).order_by('-data_accesso')[:10]
        
        # Movimenti effettuati
        context['movimenti_recenti'] = MovimentoMagazzino.objects.filter(
            operatore=utente.username
        ).select_related('articolo').order_by('-data_movimento')[:10]
        
        return context


class UtenteCreateView(CanEditMixin, CreateView):
    """Crea nuovo utente"""
    model = User
    template_name = 'magazzino/utente_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
    success_url = reverse_lazy('magazzino:utente_list')
    
    def test_func(self):
        """Solo ADMIN può creare utenti"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def form_valid(self, form):
        # Salva l'utente
        user = form.save(commit=False)
        
        # Imposta una password temporanea
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
        user.set_password(temp_password)
        user.save()
        
        # Aggiorna il profilo se specificato
        ruolo = self.request.POST.get('ruolo', RuoloUtente.OPERATORE)
        dipartimento = self.request.POST.get('dipartimento', '')
        
        profilo = user.profilo
        profilo.ruolo = ruolo
        profilo.dipartimento = dipartimento
        profilo.save()
        
        messages.warning(
            self.request,
            f"⚠️ IMPORTANTE! Utente '{user.username}' creato con successo!\n\n"
            f"🔑 PASSWORD TEMPORANEA: {temp_password}\n\n"
            f"⚡ COPIA SUBITO QUESTA PASSWORD! Non sarà più visualizzabile."
        )
        
        logger.info(f"Utente {user.username} creato da {self.request.user.username}")
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ruoli'] = RuoloUtente.choices
        context['is_create'] = True
        return context


class UtenteUpdateView(CanEditMixin, UpdateView):
    """Modifica dati utente"""
    model = User
    template_name = 'magazzino/utente_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
    success_url = reverse_lazy('magazzino:utente_list')
    
    def test_func(self):
        """Solo ADMIN può modificare utenti"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Aggiorna anche il profilo
        ruolo = self.request.POST.get('ruolo')
        dipartimento = self.request.POST.get('dipartimento', '')
        
        if ruolo:
            profilo = self.object.profilo
            profilo.ruolo = ruolo
            profilo.dipartimento = dipartimento
            profilo.save()
        
        messages.success(
            self.request,
            f"Utente '{self.object.username}' aggiornato con successo!"
        )
        
        logger.info(f"Utente {self.object.username} modificato da {self.request.user.username}")
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ruoli'] = RuoloUtente.choices
        context['is_create'] = False
        return context


class UtenteDeleteView(CanEditMixin, DeleteView):
    """Disattiva un utente (non elimina dal DB)"""
    model = User
    template_name = 'magazzino/utente_confirm_delete.html'
    success_url = reverse_lazy('magazzino:utente_list')
    
    def test_func(self):
        """Solo ADMIN può disattivare utenti"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def delete(self, request, *args, **kwargs):
        """Disattiva invece di eliminare"""
        self.object = self.get_object()
        
        # Non permettere di disattivare se stesso
        if self.object == request.user:
            messages.error(request, "Non puoi disattivare il tuo stesso account!")
            return redirect(self.success_url)
        
        # Disattiva l'utente
        self.object.is_active = False
        self.object.save()
        
        messages.success(
            request,
            f"Utente '{self.object.username}' disattivato con successo!"
        )
        
        logger.warning(
            f"Utente {self.object.username} disattivato da {request.user.username}"
        )
        
        return redirect(self.success_url)


class UtenteResetPasswordView(CanEditMixin, DetailView):
    """Reset password utente (solo admin)"""
    model = User
    template_name = 'magazzino/utente_reset_password.html'
    
    def test_func(self):
        """Solo ADMIN può resettare password"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Non permettere di resettare la propria password
        if user == request.user:
            messages.error(request, "Usa 'Cambia Password' per modificare la tua password!")
            return redirect('magazzino:utente_list')
        
        # Genera nuova password
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        new_password = ''.join(secrets.choice(alphabet) for i in range(12))
        user.set_password(new_password)
        user.save()
        
        messages.warning(
            request,
            f"⚠️ IMPORTANTE! Password resettata per '{user.username}'!\n\n"
            f"🔑 NUOVA PASSWORD: {new_password}\n\n"
            f"⚡ COPIA SUBITO QUESTA PASSWORD! Non sarà più visualizzabile."
        )
        
        logger.warning(
            f"Password resettata per {user.username} da {request.user.username}"
        )
        
        return redirect('magazzino:utente_list')


# ============================================================================
# GESTIONE BACKUP DATABASE
# ============================================================================

class BackupListView(CanEditMixin, TemplateView):
    """Lista e gestione dei backup del database"""
    template_name = 'magazzino/backup_list.html'
    
    def test_func(self):
        """Solo ADMIN può gestire i backup"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from .backup_manager import BackupManager
        backup_mgr = BackupManager()
        
        # Lista backup esistenti
        context['backups'] = backup_mgr.list_backups()
        context['backup_dir'] = backup_mgr.backup_dir
        context['retention_days'] = backup_mgr.retention_days
        
        # Statistiche
        if context['backups']:
            total_size = sum(b['size_mb'] for b in context['backups'])
            context['total_size_mb'] = total_size
            context['backup_count'] = len(context['backups'])
            context['oldest_backup'] = context['backups'][-1] if context['backups'] else None
            context['newest_backup'] = context['backups'][0] if context['backups'] else None
        else:
            context['total_size_mb'] = 0
            context['backup_count'] = 0
        
        return context


class BackupCreateView(CanEditMixin, TemplateView):
    """Crea un nuovo backup"""
    
    def test_func(self):
        """Solo ADMIN può creare backup"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def post(self, request, *args, **kwargs):
        from .backup_manager import BackupManager
        backup_mgr = BackupManager()
        
        success, filepath, message = backup_mgr.create_backup()
        
        if success:
            messages.success(request, f"✅ {message}")
            logger.info(f"Backup creato da {request.user.username}: {filepath.name}")
        else:
            messages.error(request, f"❌ {message}")
            logger.error(f"Errore creazione backup da {request.user.username}: {message}")
        
        return redirect('magazzino:backup_list')


class BackupDownloadView(CanEditMixin, TemplateView):
    """Download di un backup"""
    
    def test_func(self):
        """Solo ADMIN può scaricare backup"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def get(self, request, *args, **kwargs):
        filename = kwargs.get('filename')
        
        from .backup_manager import BackupManager
        backup_mgr = BackupManager()
        
        backup_path = backup_mgr.backup_dir / filename
        
        # Verifica esistenza e validità
        if not backup_path.exists():
            messages.error(request, "File di backup non trovato")
            return redirect('magazzino:backup_list')
        
        if not backup_path.name.startswith('backup_'):
            messages.error(request, "File non valido")
            return redirect('magazzino:backup_list')
        
        # Log download
        logger.info(f"Download backup {filename} da {request.user.username}")
        
        # Serve file
        response = FileResponse(
            open(backup_path, 'rb'),
            content_type='application/gzip'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


class BackupDeleteView(CanEditMixin, TemplateView):
    """Elimina un backup"""
    
    def test_func(self):
        """Solo ADMIN può eliminare backup"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def post(self, request, *args, **kwargs):
        filename = kwargs.get('filename')
        
        from .backup_manager import BackupManager
        backup_mgr = BackupManager()
        
        success, message = backup_mgr.delete_backup(filename)
        
        if success:
            messages.success(request, f"✅ {message}")
            logger.info(f"Backup eliminato da {request.user.username}: {filename}")
        else:
            messages.error(request, f"❌ {message}")
        
        return redirect('magazzino:backup_list')


class BackupCleanupView(CanEditMixin, TemplateView):
    """Pulizia backup obsoleti"""
    
    def test_func(self):
        """Solo ADMIN può pulire backup"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def post(self, request, *args, **kwargs):
        from .backup_manager import BackupManager
        backup_mgr = BackupManager()
        
        count, message = backup_mgr.cleanup_old_backups()
        
        if count > 0:
            messages.success(request, f"🗑️ {message}")
            logger.info(f"Pulizia backup da {request.user.username}: {count} file eliminati")
        else:
            messages.info(request, "Nessun backup obsoleto da eliminare")
        
        return redirect('magazzino:backup_list')


class BackupRestoreView(CanEditMixin, TemplateView):
    """Ripristina un backup"""
    
    def test_func(self):
        """Solo ADMIN può ripristinare backup"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def post(self, request, *args, **kwargs):
        filename = kwargs.get('filename')
        
        # Verifica conferma
        confirm = request.POST.get('confirm')
        if confirm != 'RESTORE':
            messages.error(request, "❌ Conferma non valida. Devi digitare 'RESTORE' per confermare.")
            return redirect('magazzino:backup_list')
        
        from .backup_manager import BackupManager
        backup_mgr = BackupManager()
        
        success, message = backup_mgr.restore_backup(filename)
        
        if success:
            messages.success(request, f"✅ {message}")
            logger.warning(f"⚠️ RESTORE eseguito da {request.user.username}: {filename}")
        else:
            messages.error(request, f"❌ {message}")
        
        return redirect('magazzino:backup_list')


class BackupSettingsView(CanEditMixin, FormView):
    """Configurazione impostazioni backup"""
    template_name = 'magazzino/backup_settings.html'
    form_class = None  # Sarà importato dinamicamente
    
    def test_func(self):
        """Solo ADMIN può modificare settings"""
        if not self.request.user.is_authenticated:
            return False
        try:
            return self.request.user.profilo.è_admin()
        except:
            return False
    
    def get_form_class(self):
        from .forms import BackupSettingsForm
        return BackupSettingsForm
    
    def get_initial(self):
        """Carica impostazioni correnti dal database"""
        from .models import Configurazione
        
        return {
            'backup_dir': Configurazione.get_value('backup_dir', str(settings.BASE_DIR / 'backups')),
            'retention_days': Configurazione.get_value('backup_retention_days', 30),
            'mysql_bin_path': Configurazione.get_value('mysql_bin_path', r'C:\xampp\mysql\bin'),
        }
    
    def form_valid(self, form):
        """Salva le nuove impostazioni nel database"""
        from .models import Configurazione
        
        try:
            username = self.request.user.username
            
            # Salva ciascuna configurazione nel database
            Configurazione.set_value(
                'backup_dir',
                form.cleaned_data['backup_dir'],
                tipo_dato='string',
                descrizione='Cartella di destinazione per i backup del database',
                username=username
            )
            
            Configurazione.set_value(
                'backup_retention_days',
                form.cleaned_data['retention_days'],
                tipo_dato='integer',
                descrizione='Giorni di conservazione dei backup prima della pulizia automatica',
                username=username
            )
            
            Configurazione.set_value(
                'mysql_bin_path',
                form.cleaned_data['mysql_bin_path'],
                tipo_dato='string',
                descrizione='Percorso della cartella bin di MySQL/MariaDB',
                username=username
            )
            
            messages.success(
                self.request, 
                "✅ Impostazioni salvate con successo! Le modifiche sono attive immediatamente."
            )
            logger.info(f"Impostazioni backup aggiornate da {username}")
            
        except Exception as e:
            messages.error(self.request, f"❌ Errore salvataggio impostazioni: {str(e)}")
            logger.error(f"Errore salvataggio backup config: {e}", exc_info=True)
            return self.form_invalid(form)
        
        return redirect('magazzino:backup_list')


# ============================================================================
# AJAX - API ENDPOINTS
# ============================================================================

def get_articolo_giacenza(request, articolo_id):
    """
    Endpoint AJAX che ritorna le giacenze di un articolo in formato JSON.
    Usato per visualizzare in tempo reale le quantità disponibili nel form movimento.
    
    Args:
        articolo_id: ID dell'articolo (id_articolo)
    
    Returns:
        JSON: {
            disponibile: int,
            impegnata: int,
            prenotata: int,
            descrizione: str,
            unita_misura: str
        }
    """
    # Verifica che l'utente sia autenticato
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Non autenticato'
        }, status=401)
    
    try:
        # Recupera l'articolo
        articolo = PezzoRicambio.objects.select_related('giacenza', 'unita_misura').get(
            id_articolo=articolo_id
        )
        
        # Recupera la giacenza (o crea un placeholder se non esiste)
        giacenza = articolo.giacenza if hasattr(articolo, 'giacenza') else None
        
        if giacenza:
            data = {
                'success': True,
                'disponibile': giacenza.quantita_disponibile or 0,
                'impegnata': giacenza.quantita_impegnata or 0,
                'prenotata': giacenza.quantita_prenotata or 0,
                'descrizione': articolo.descrizione,
                'unita_misura': articolo.unita_misura.denominazione if articolo.unita_misura else 'N/D'
            }
        else:
            data = {
                'success': True,
                'disponibile': 0,
                'impegnata': 0,
                'prenotata': 0,
                'descrizione': articolo.descrizione,
                'unita_misura': articolo.unita_misura.denominazione if articolo.unita_misura else 'N/D'
            }
        
        return JsonResponse(data)
    
    except PezzoRicambio.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Articolo non trovato'
        }, status=404)
    except Exception as e:
        logger.error(f"Errore in get_articolo_giacenza: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Errore server: ' + str(e)
        }, status=500)


def get_articolo_fornitore(request, articolo_id):
    """
    Endpoint AJAX che ritorna il fornitore predefinito di un articolo.
    Usato per autocompilare il campo fornitore quando si seleziona un articolo.
    
    Args:
        articolo_id: ID dell'articolo (id_articolo)
    
    Returns:
        JSON: {
            success: bool,
            fornitore_id: int or None,
            fornitore_nome: str or None
        }
    """
    # Verifica che l'utente sia autenticato
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Non autenticato'
        }, status=401)
    
    try:
        articolo = PezzoRicambio.objects.select_related('fornitore').get(
            id_articolo=articolo_id
        )
        
        if articolo.fornitore:
            data = {
                'success': True,
                'fornitore_id': articolo.fornitore.id_fornitore,
                'fornitore_nome': articolo.fornitore.ragione_sociale
            }
        else:
            data = {
                'success': True,
                'fornitore_id': None,
                'fornitore_nome': None
            }
        
        return JsonResponse(data)
    
    except PezzoRicambio.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Articolo non trovato'
        }, status=404)
    except Exception as e:
        logger.error(f"Errore in get_articolo_fornitore: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Errore server: ' + str(e)
        }, status=500)


# ============================================================================
# GESTIONE TABELLE DATABASE
# ============================================================================

class GestioneTabelleView(CanEditMixin, TemplateView):
    """Vista per la gestione delle tabelle del database"""
    template_name = 'magazzino/gestione_tabelle.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lista delle tabelle modificabili (solo quelle sicure)
        tabelle_modificabili = [
            {
                'nome': 'tbunitamisura',
                'descrizione': 'Unità di Misura',
                'modello': 'UnitaMisura',
                'url_modifica': reverse('magazzino:modifica_tabella', kwargs={'nome_tabella': 'tbunitamisura'})
            },
            {
                'nome': 'tbtipopagamento',
                'descrizione': 'Tipo Pagamento',
                'modello': 'TbTipoPagamento',
                'url_modifica': reverse('magazzino:modifica_tabella', kwargs={'nome_tabella': 'tbtipopagamento'})
            },
            {
                'nome': 'tbcategoriaiva',
                'descrizione': 'Categoria IVA',
                'modello': 'TbCategoriaIVA',
                'url_modifica': reverse('magazzino:modifica_tabella', kwargs={'nome_tabella': 'tbcategoriaiva'})
            },
            {
                'nome': 'tbcontatti',
                'descrizione': 'Contatti',
                'modello': 'TbContatti',
                'url_modifica': reverse('magazzino:modifica_tabella', kwargs={'nome_tabella': 'tbcontatti'})
            },
            # Aggiungere altre tabelle qui in futuro
        ]
        
        context['tabelle_modificabili'] = tabelle_modificabili
        return context


class ModificaTabellaView(CanEditMixin, TemplateView):
    """Vista per modificare i record di una tabella specifica"""
    template_name = 'magazzino/modifica_tabella.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nome_tabella = kwargs.get('nome_tabella')
        
        # Solo tabelle autorizzate
        tabelle_permesse = {
            'tbunitamisura': {
                'modello': UnitaMisura,
                'descrizione': 'Unità di Misura',
                'campi': ['id_unita_misura', 'denominazione', 'denominazione_stampa', 'stato_attivo']
            },
            'tbtipopagamento': {
                'modello': TbTipoPagamento,
                'descrizione': 'Tipo Pagamento',
                'campi': ['id_tipo_pagamento', 'descrizione', 'data_rif_scad', 'giorni_data_rif', 'giorno_addebito']
            },
            'tbcategoriaiva': {
                'modello': TbCategoriaIVA,
                'descrizione': 'Categoria IVA',
                'campi': ['id_categoria_iva', 'nome_categoria', 'valore_iva']
            },
            'tbcontatti': {
                'modello': TbContatti,
                'descrizione': 'Contatti',
                'campi': ['id_contatto', 'id_cliente', 'nome', 'cognome', 'ruolo', 'email_azienda', 'telefono_azienda']
            }
        }
        
        if nome_tabella not in tabelle_permesse:
            raise Http404("Tabella non autorizzata")
        
        config = tabelle_permesse[nome_tabella]
        modello = config['modello']
        
        # Ottieni tutti i record e converti in lista di dizionari
        records = []
        if nome_tabella == 'tbcontatti':
            # Per contatti, ordina prima quelli con cognome/nome popolati
            queryset = modello.objects.extra(
                select={'has_name': "CASE WHEN cognome != '' AND nome != '' THEN 1 ELSE 0 END"}
            ).extra(
                order_by=['-has_name', 'cognome', 'nome']
            )
        else:
            queryset = modello.objects.all()
            
        for record in queryset:
            valori_campi = []
            for campo in config['campi']:
                valore = getattr(record, campo)
                # Formatta date
                if campo in ['creato_il', 'modificato_il'] and valore:
                    valore = valore.strftime('%d/%m/%Y %H:%M')
                # Formatta booleani
                elif campo == 'stato_attivo':
                    valore = 'Attivo' if valore else 'Disattivo'
                # Gestisci valori None per campi FK
                elif valore is None:
                    valore = ''
                valori_campi.append(valore)
            
            records.append({
                'pk': record.pk,
                'valori': valori_campi
            })
        
        context.update({
            'nome_tabella': nome_tabella,
            'descrizione_tabella': config['descrizione'],
            'campi': config['campi'],
            'records': records,
        })
        
        return context
