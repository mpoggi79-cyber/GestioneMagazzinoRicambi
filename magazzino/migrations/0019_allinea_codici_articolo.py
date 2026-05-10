from django.db import migrations, transaction


CODICE_ARTICOLO_PREFIX = 'ART'
CODICE_ARTICOLO_PLACEHOLDER_PREFIX = '__TMP_ART_MIG__'


def genera_codice_articolo(id_articolo):
    return f"{CODICE_ARTICOLO_PREFIX}-{id_articolo:05d}"


def allinea_codici_articolo(apps, schema_editor):
    PezzoRicambio = apps.get_model('magazzino', 'PezzoRicambio')

    with transaction.atomic():
        articoli = list(
            PezzoRicambio.objects.order_by('id_articolo').values_list('id_articolo', flat=True)
        )

        for id_articolo in articoli:
            PezzoRicambio.objects.filter(id_articolo=id_articolo).update(
                codice_interno=f"{CODICE_ARTICOLO_PLACEHOLDER_PREFIX}{id_articolo:05d}"
            )

        for id_articolo in articoli:
            PezzoRicambio.objects.filter(id_articolo=id_articolo).update(
                codice_interno=genera_codice_articolo(id_articolo)
            )


class Migration(migrations.Migration):

    dependencies = [
        ('magazzino', '0018_alter_unitamisura_denominazione_tbprestazioni'),
    ]

    operations = [
        migrations.RunPython(allinea_codici_articolo, migrations.RunPython.noop),
    ]