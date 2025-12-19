"""
URL configuration for Gestione Magazzino Ricambi.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Accounts app - autenticazione
    path('accounts/', include('accounts.urls')),
    
    # Magazzino app - con namespace sulla root
    path('', include('magazzino.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizzazione admin
admin.site.site_header = "Gestione Magazzino Ricambi"
admin.site.site_title = "Admin GMR"
admin.site.index_title = "Benvenuto nell'admin di Gestione Magazzino Ricambi"
