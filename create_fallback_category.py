#!/usr/bin/env python
"""
Script per creare la categoria di fallback "Nessuna (da caratterizzare)"
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from magazzino.models import Categoria

# Crea la categoria di fallback
categoria, created = Categoria.objects.get_or_create(
    nome_categoria="Nessuna (da caratterizzare)",
    defaults={
        'descrizione': 'Categoria di fallback per articoli orfani - da caratterizzare manualmente'
    }
)

if created:
    print(f"✅ Categoria '{categoria.nome_categoria}' creata con successo (ID: {categoria.id_categoria})")
else:
    print(f"✓ Categoria '{categoria.nome_categoria}' già esiste (ID: {categoria.id_categoria})")
