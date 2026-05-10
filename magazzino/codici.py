import uuid


CODICE_ARTICOLO_PREFIX = 'ART'
CODICE_ARTICOLO_PLACEHOLDER_PREFIX = '__TMP_ART__'


def genera_codice_articolo(id_articolo):
    """Restituisce il codice articolo canonico a partire dall'id reale."""
    return f"{CODICE_ARTICOLO_PREFIX}-{id_articolo:05d}"


def genera_placeholder_codice_articolo():
    """Restituisce un valore tecnico temporaneo univoco per il primo salvataggio."""
    return f"{CODICE_ARTICOLO_PLACEHOLDER_PREFIX}{uuid.uuid4().hex[:16].upper()}"