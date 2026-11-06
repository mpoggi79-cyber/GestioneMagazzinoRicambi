from django.db import migrations

TABELLE = [
    ("tbAppellativo", "tbappellativo"),
    ("tbCategoriaIVA", "tbcategoriaiva"),
    ("tbCategorieTariffe", "tbcategorietariffe"),
    ("tbPrestazioni", "tbprestazioni"),
]


def rinomina_tabelle_minuscolo(apps, schema_editor):
    """Rinomina fisicamente solo se il DB distingue maiuscole/minuscole (es. Linux).

    Su MySQL/MariaDB con lower_case_table_names=1 (Windows/XAMPP) le tabelle sono
    già minuscole e il RENAME fallirebbe, quindi non si fa nulla.
    """
    connessione = schema_editor.connection
    with connessione.cursor() as cursore:
        esistenti = set(connessione.introspection.table_names(cursore))
    for vecchio, nuovo in TABELLE:
        if vecchio in esistenti and nuovo not in esistenti:
            schema_editor.execute(
                "RENAME TABLE %s TO %s"
                % (schema_editor.quote_name(vecchio), schema_editor.quote_name(nuovo))
            )


class Migration(migrations.Migration):

    dependencies = [
        ("magazzino", "0021_pezzoricambio_codice_sostitutivo"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterModelTable(name=nuovo, table=nuovo)
                for _, nuovo in TABELLE
            ],
            database_operations=[
                migrations.RunPython(rinomina_tabelle_minuscolo, migrations.RunPython.noop),
            ],
        ),
    ]
