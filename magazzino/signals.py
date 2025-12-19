"""
Signals per l'elaborazione automatica delle immagini degli articoli.
Gestisce:
- Auto-ridimensionamento immagine principale (max 800x800px)
- Generazione automatica thumbnail (300x300px con crop centrato)
- Conversione in formato JPEG ottimizzato
- Eliminazione file immagini alla cancellazione dell'articolo
"""

import os
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import PezzoRicambio
import logging

logger = logging.getLogger(__name__)


def process_image(image_file, max_size, quality=90, crop=False):
    """
    Processa un'immagine: ridimensiona, converte in JPEG e ottimizza.
    
    Args:
        image_file: File immagine da processare
        max_size: Dimensione massima (larghezza, altezza) in pixel
        quality: Qualità JPEG (0-100)
        crop: Se True, ritaglia al centro per ottenere dimensioni esatte
        
    Returns:
        ContentFile con l'immagine processata
    """
    # Apri l'immagine con Pillow
    img = Image.open(image_file)
    
    # Converti RGBA (PNG con trasparenza) in RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        # Crea uno sfondo bianco
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Ridimensiona l'immagine
    if crop:
        # Crop centrato per thumbnail (dimensioni esatte)
        img = ImageOps.fit(img, max_size, Image.Resampling.LANCZOS)
    else:
        # Ridimensiona mantenendo aspect ratio (per immagine grande)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Salva in formato JPEG ottimizzato
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    return ContentFile(output.read())


@receiver(pre_save, sender=PezzoRicambio)
def process_articolo_image(sender, instance, **kwargs):
    """
    Signal pre-save: processa l'immagine caricata generando:
    - Immagine principale ottimizzata (max 800x800px, qualità 90%)
    - Thumbnail (300x300px cropped, qualità 85%)
    """
    logger.info(f"🎯 Signal chiamato per: {getattr(instance, 'codice_interno', 'NUOVO')}")
    
    # Se non c'è immagine, non fare nulla
    if not instance.immagine:
        logger.info("❌ Nessuna immagine, skip")
        # Se l'immagine è stata rimossa, elimina anche il thumbnail
        if instance.pk:
            try:
                old_instance = PezzoRicambio.objects.get(pk=instance.pk)
                if old_instance.immagine_thumbnail:
                    old_instance.immagine_thumbnail.delete(save=False)
                    instance.immagine_thumbnail = None
            except PezzoRicambio.DoesNotExist:
                pass
        return
    
    logger.info(f"✅ Immagine presente: {instance.immagine.name}")
    
    # Controlla se l'immagine è stata modificata
    try:
        old_instance = PezzoRicambio.objects.get(pk=instance.pk)
        # Se l'immagine non è cambiata, non riprocessare
        if old_instance.immagine == instance.immagine:
            logger.info("⏭️ Immagine non modificata")
            return
        # Elimina le vecchie immagini
        if old_instance.immagine:
            old_instance.immagine.delete(save=False)
        if old_instance.immagine_thumbnail:
            old_instance.immagine_thumbnail.delete(save=False)
    except PezzoRicambio.DoesNotExist:
        # Nuovo record, nessuna immagine da eliminare
        logger.info("🆕 Nuovo articolo con immagine")
        pass
    
    logger.info("🔄 Inizio processing...")
    
    # Salva il file originale in memoria prima di processarlo
    instance.immagine.seek(0)
    image_data = instance.immagine.read()
    instance.immagine.seek(0)
    
    # Processa immagine principale (max 800x800, mantiene aspect ratio)
    large_image = process_image(BytesIO(image_data), (800, 800), quality=90, crop=False)
    
    # Genera nome file per immagine ottimizzata
    original_name = instance.immagine.name
    base_name = os.path.splitext(os.path.basename(original_name))[0]
    large_name = f"{base_name}_large.jpg"
    
    logger.info(f"💾 Salvo large: {large_name}")
    # Salva immagine principale processata
    instance.immagine.save(large_name, large_image, save=False)
    
    # Genera thumbnail (300x300 cropped al centro) usando gli stessi dati
    thumbnail_image = process_image(BytesIO(image_data), (300, 300), quality=85, crop=True)
    
    # Salva thumbnail
    thumbnail_name = f"{base_name}_thumb.jpg"
    logger.info(f"💾 Salvo thumb: {thumbnail_name}")
    instance.immagine_thumbnail.save(thumbnail_name, thumbnail_image, save=False)
    logger.info("✨ Processing completato!")


@receiver(post_delete, sender=PezzoRicambio)
def delete_articolo_images(sender, instance, **kwargs):
    """
    Signal post-delete: elimina fisicamente i file immagini quando l'articolo viene cancellato.
    """
    # Elimina immagine principale
    if instance.immagine:
        if os.path.isfile(instance.immagine.path):
            os.remove(instance.immagine.path)
    
    # Elimina thumbnail
    if instance.immagine_thumbnail:
        if os.path.isfile(instance.immagine_thumbnail.path):
            os.remove(instance.immagine_thumbnail.path)
