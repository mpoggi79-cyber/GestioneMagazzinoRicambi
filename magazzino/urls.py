"""
URL configuration per l'app magazzino.
"""

from django.urls import path
from . import views

app_name = 'magazzino'

urlpatterns = [
    # Home / Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('reset-classifica/', views.ResetClassificaView.as_view(), name='reset_classifica'),
    
    # CATEGORIE
    path('categorie/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorie/create/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorie/<int:pk>/update/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorie/<int:pk>/delete/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),
    
    # Categorie - Operazioni avanzate
    path('categorie/move/', views.categoria_move, name='categoria_move'),
    path('api/categorie/<int:parent_id>/figlie/', views.get_categorie_figlie, name='api_categorie_figlie'),
    
    # API AJAX - Dati in tempo reale
    path('api/articolo/<int:articolo_id>/giacenza/', views.get_articolo_giacenza, name='api_articolo_giacenza'),
    path('api/articolo/<int:articolo_id>/fornitore/', views.get_articolo_fornitore, name='api_articolo_fornitore'),
    
    # ARTICOLI / PEZZI DI RICAMBIO
    path('articoli/', views.PezzoRicambioListView.as_view(), name='articolo_list'),
    path('articoli/create/', views.PezzoRicambioCreateView.as_view(), name='articolo_create'),
    path('articoli/<int:pk>/', views.PezzoRicambioDetailView.as_view(), name='articolo_detail'),
    path('articoli/<int:pk>/update/', views.PezzoRicambioUpdateView.as_view(), name='articolo_update'),
    path('articoli/<int:pk>/delete/', views.PezzoRicambioDeleteView.as_view(), name='articolo_delete'),
    
    # FORNITORI
    path('fornitori/', views.FornitoreListView.as_view(), name='fornitore_list'),
    path('fornitori/create/', views.FornitoreCreateView.as_view(), name='fornitore_create'),
    path('fornitori/<int:pk>/', views.FornitoreDetailView.as_view(), name='fornitore_detail'),
    path('fornitori/<int:pk>/update/', views.FornitoreUpdateView.as_view(), name='fornitore_update'),
    path('fornitori/<int:pk>/delete/', views.FornitoreDeleteView.as_view(), name='fornitore_delete'),
    
    # MODELLI MACCHINE SCM
    path('modelli-scm/', views.ModelloSCMListView.as_view(), name='modello_scm_list'),
    path('modelli-scm/create/', views.ModelloSCMCreateView.as_view(), name='modello_scm_create'),
    path('modelli-scm/<int:pk>/update/', views.ModelloSCMUpdateView.as_view(), name='modello_scm_update'),
    path('modelli-scm/<int:pk>/delete/', views.ModelloSCMDeleteView.as_view(), name='modello_scm_delete'),
    
    # MATRICOLE MACCHINE SCM
    path('matricole-scm/', views.MatricolaSCMListView.as_view(), name='matricola_scm_list'),
    path('matricole-scm/create/', views.MatricolaSCMCreateView.as_view(), name='matricola_scm_create'),
    path('matricole-scm/<int:pk>/update/', views.MatricolaSCMUpdateView.as_view(), name='matricola_scm_update'),
    path('matricole-scm/<int:pk>/delete/', views.MatricolaSCMDeleteView.as_view(), name='matricola_scm_delete'),
    
    # MOVIMENTI DI MAGAZZINO
    path('movimenti/', views.MovimentoListView.as_view(), name='movimento_list'),
    path('movimenti/create/', views.MovimentoCreateView.as_view(), name='movimento_create'),
    path('movimenti/<int:pk>/', views.MovimentoDetailView.as_view(), name='movimento_detail'),
    
    # GIACENZE
    path('giacenze/', views.GiacenzaListView.as_view(), name='giacenza_list'),
    path('giacenze/<int:pk>/', views.GiacenzaDetailView.as_view(), name='giacenza_detail'),
    
    # REPORT E STATISTICHE
    path('report/giacenze/', views.GiacenzeReportView.as_view(), name='report_giacenze'),
    path('report/movimenti/', views.MovimentiReportView.as_view(), name='report_movimenti'),
    
    # GESTIONE UTENTI
    path('utenti/', views.UtenteListView.as_view(), name='utente_list'),
    path('utenti/<int:pk>/', views.UtenteDetailView.as_view(), name='utente_detail'),
    path('utenti/create/', views.UtenteCreateView.as_view(), name='utente_create'),
    path('utenti/<int:pk>/update/', views.UtenteUpdateView.as_view(), name='utente_update'),
    path('utenti/<int:pk>/delete/', views.UtenteDeleteView.as_view(), name='utente_delete'),
    path('utenti/<int:pk>/reset-password/', views.UtenteResetPasswordView.as_view(), name='utente_reset_password'),
    
    # GESTIONE BACKUP
    path('backup/', views.BackupListView.as_view(), name='backup_list'),
    path('backup/create/', views.BackupCreateView.as_view(), name='backup_create'),
    path('backup/download/<str:filename>/', views.BackupDownloadView.as_view(), name='backup_download'),
    path('backup/delete/<str:filename>/', views.BackupDeleteView.as_view(), name='backup_delete'),
    path('backup/cleanup/', views.BackupCleanupView.as_view(), name='backup_cleanup'),
    path('backup/restore/<str:filename>/', views.BackupRestoreView.as_view(), name='backup_restore'),
    path('backup/settings/', views.BackupSettingsView.as_view(), name='backup_settings'),
]
