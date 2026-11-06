"""
Recupero dei dati di un articolo dal portale ricambi SCM (shop.scmgroup.com).

L'autenticazione (login Microsoft con MFA) viene fatta a mano dall'operatore, dal
pulsante "Accedi al portale SCM" del form articolo o con il comando `scm_login`: la
sessione resta in un profilo browser locale e non vengono mai salvate credenziali.
Prezzi e disponibilità sono visibili solo da autenticati.
"""

import json
import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

URL_BASE_PORTALE = 'https://shop.scmgroup.com/scmwood/it/it/'
URL_LOGIN_PORTALE = URL_BASE_PORTALE + 'login'
DIR_PROFILO_BROWSER = Path(settings.BASE_DIR) / '.scm_browser_profile'
FILE_SESSIONE = DIR_PROFILO_BROWSER / 'sessione_scm.json'

TIMEOUT_NAVIGAZIONE_MS = 30000
TIMEOUT_PAGINA_MS = 15000

# Il profilo Chrome non può essere aperto da due processi insieme
_lock_browser = threading.Lock()

# Stato del login avviato dall'interfaccia web (thread in background)
_lock_stato_login = threading.Lock()
_stato_login = {'in_corso': False, 'esito': None, 'messaggio': ''}

MESSAGGIO_SESSIONE_SCADUTA = (
    'Sessione del portale SCM scaduta. Clicca "Accedi al portale SCM" e fai il login nella finestra di Chrome.'
)


class ErroreSCM(Exception):
    """Errore generico del recupero dati dal portale SCM."""


class SessioneScadutaSCM(ErroreSCM):
    """La sessione del portale non è valida: serve rifare il login con `scm_login`."""


class CodiceNonTrovatoSCM(ErroreSCM):
    """Il codice cercato non esiste nel portale."""


class PortaleNonDisponibileSCM(ErroreSCM):
    """Portale non raggiungibile, browser non avviabile o pagina inattesa."""


@dataclass
class DatiArticoloSCM:
    codice_scm: str
    descrizione: str = ''
    prezzo_listino: Optional[Decimal] = None
    prezzo_acquisto: Optional[Decimal] = None
    disponibilita: Optional[int] = None
    stato_disponibilita: str = ''
    url_immagine: str = ''
    url_pagina: str = ''
    nota: str = ''
    rilevato_il: datetime = field(default_factory=timezone.now)

    def come_dizionario(self):
        """Dizionario serializzabile in JSON (prezzi come stringhe con 2 decimali)."""
        def importo(valore):
            return None if valore is None else f'{valore:.2f}'

        return {
            'codice_scm': self.codice_scm,
            'descrizione': self.descrizione,
            'prezzo_listino': importo(self.prezzo_listino),
            'prezzo_acquisto': importo(self.prezzo_acquisto),
            'disponibilita': self.disponibilita,
            'stato_disponibilita': self.stato_disponibilita,
            'url_immagine': self.url_immagine,
            'url_pagina': self.url_pagina,
            'nota': self.nota,
            'rilevato_il': timezone.localtime(self.rilevato_il).isoformat(timespec='seconds'),
        }


# ============================================================================
# INTERPRETAZIONE DEI DATI GREZZI (nessun accesso a rete o browser)
# ============================================================================

def interpreta_importo(testo):
    """Converte '1.303,68 €' (formato italiano, anche con spazi non separabili) in Decimal."""
    if not testo:
        return None
    pulito = re.sub(r'[^\d,.\-]', '', str(testo))
    if not pulito:
        return None
    if ',' in pulito:
        pulito = pulito.replace('.', '').replace(',', '.')
    try:
        return Decimal(pulito).quantize(Decimal('0.01'))
    except InvalidOperation:
        return None


def interpreta_disponibilita(testo):
    """Da 'Disponibile  6' / 'In arrivo  1' ricava (quantità, stato)."""
    if not testo:
        return None, ''
    normalizzato = re.sub(r'\s+', ' ', str(testo).replace('\xa0', ' ')).strip()
    numero = re.search(r'(\d+)\s*$', normalizzato)
    stato = re.sub(r'\s*\d+\s*$', '', normalizzato).strip()
    if numero:
        quantita = int(numero.group(1))
    elif re.search(r'non disponibil|esaurit', normalizzato, re.IGNORECASE):
        quantita = 0
    else:
        quantita = None
    return quantita, stato


def _scegli_immagine(immagini):
    """Sceglie l'immagine migliore tra quelle del JSON-LD scartando il segnaposto 'missing_product'."""
    valide = [i for i in immagini if i and 'missing_product' not in i]
    if not valide:
        return ''

    def dimensione(url):
        corrispondenza = re.search(r'(\d+)Wx(\d+)H', url)
        return int(corrispondenza.group(1)) if corrispondenza else 0

    migliore = max(valide, key=dimensione)
    return urljoin(URL_BASE_PORTALE, re.sub(r'(?<!:)//+', '/', migliore))


def interpreta_dati_grezzi(grezzi, codice_scm, url_pagina=''):
    """
    Trasforma i testi estratti dalla pagina (vedi _SCRIPT_ESTRAZIONE) in DatiArticoloSCM.

    Il prezzo barrato è il prezzo di listino al cliente; il prezzo finale (dopo
    sconto online 3% e sconto riservato 20%) è il prezzo a noi. Senza sconti
    esposti il prezzo unico vale sia come listino sia come acquisto.
    """
    prezzo_barrato = interpreta_importo(grezzi.get('prezzo_barrato'))
    prezzo_finale = interpreta_importo(grezzi.get('prezzo_finale'))
    prezzo_json_ld = interpreta_importo(grezzi.get('prezzo_json_ld'))

    if prezzo_barrato is not None:
        listino = prezzo_barrato
        acquisto = prezzo_finale
    else:
        listino = prezzo_json_ld if prezzo_json_ld is not None else prezzo_finale
        acquisto = prezzo_finale

    nota = ''
    if listino is None and acquisto is None:
        if not grezzi.get('autenticato'):
            raise SessioneScadutaSCM(
                'Prezzo non presente nella pagina: la sessione del portale SCM potrebbe essere scaduta. '
                'Usa "Accedi al portale SCM" e riprova.'
            )
        nota = 'Il portale non espone un prezzo per questo articolo.'

    quantita, stato = interpreta_disponibilita(grezzi.get('disponibilita'))
    if quantita is None and re.search(r'non disponibil', grezzi.get('testo_principale') or '', re.IGNORECASE):
        quantita, stato = 0, 'Non disponibile'
        nota = 'Articolo attualmente non disponibile sul portale.' + (' ' + nota if nota else '')
    descrizione = re.sub(r'\s+', ' ', (grezzi.get('descrizione') or grezzi.get('nome') or '')).strip()

    return DatiArticoloSCM(
        codice_scm=codice_scm,
        descrizione=descrizione[:200],
        prezzo_listino=listino,
        prezzo_acquisto=acquisto,
        disponibilita=quantita,
        stato_disponibilita=stato[:30],
        url_immagine=_scegli_immagine(grezzi.get('immagini') or []),
        url_pagina=url_pagina,
        nota=nota,
    )


# Eseguito nel browser: restituisce solo testi grezzi, l'interpretazione è in Python
_SCRIPT_ESTRAZIONE = """
() => {
    const testo = (selettore) => {
        const e = document.querySelector(selettore);
        return e ? e.textContent.trim() : '';
    };
    let immagini = [];
    let prezzoJsonLd = '';
    let nomeJsonLd = '';
    for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
        try {
            const dati = JSON.parse(s.textContent);
            if (dati && dati['@type'] === 'Product') {
                nomeJsonLd = dati.name || '';
                immagini = Array.isArray(dati.image) ? dati.image : (dati.image ? [dati.image] : []);
                prezzoJsonLd = dati.offers && dati.offers.price ? String(dati.offers.price) : '';
            }
        } catch (e) {}
    }
    const barrato =  document.querySelector('.product-main-info .discount-price del .amount.price');
    const finale = document.querySelector('.product-main-info .discount-price ins .amount.price')
        || document.querySelector('.product-main-info .amount.price:not(.discount-price-strikethrough)');
    return {
        nome: nomeJsonLd || testo('.product-details.page-title .name'),
        descrizione: testo('.product-main-info .description'),
        prezzo_barrato: barrato ? barrato.textContent : '',
        prezzo_finale: finale ? finale.textContent : '',
        prezzo_json_ld: prezzoJsonLd,
        disponibilita: testo('.stock-status'),
        testo_principale: (document.querySelector('.product-main-info') || {innerText: ''}).innerText.slice(0, 1000),
        immagini: immagini,
        autenticato: document.body.innerText.includes('DISCONNESSIONE'),
    };
}
"""


# ============================================================================
# BROWSER (Playwright con profilo persistente)
# ============================================================================

def _avvia_contesto(playwright, headless):
    """Apre Chrome con il profilo dedicato e ripristina i cookie di sessione salvati."""
    DIR_PROFILO_BROWSER.mkdir(parents=True, exist_ok=True)
    try:
        contesto = playwright.chromium.launch_persistent_context(
            str(DIR_PROFILO_BROWSER / 'chrome'),
            channel='chrome',
            headless=headless,
            locale='it-IT',
        )
    except Exception as errore:
        raise PortaleNonDisponibileSCM(
            f'Impossibile avviare Google Chrome per il portale SCM: {errore}'
        ) from errore

    if FILE_SESSIONE.exists():
        try:
            stato = json.loads(FILE_SESSIONE.read_text(encoding='utf-8'))
            contesto.add_cookies(stato.get('cookies', []))
        except (OSError, ValueError) as errore:
            logger.warning('Sessione SCM salvata non leggibile: %s', errore)
    return contesto


def _salva_sessione(contesto):
    """Salva i cookie (compresi quelli di sessione, persi alla chiusura del browser)."""
    DIR_PROFILO_BROWSER.mkdir(parents=True, exist_ok=True)
    FILE_SESSIONE.write_text(json.dumps(contesto.storage_state()), encoding='utf-8')


def esegui_login_manuale(timeout_secondi=300):
    """
    Apre Chrome visibile sul login del portale e attende che l'operatore completi
    l'accesso (Microsoft + MFA). Salva la sessione e ritorna True se l'accesso è riuscito.
    """
    import time

    from playwright.sync_api import Error as ErrorePlaywright
    from playwright.sync_api import sync_playwright

    with _lock_browser, sync_playwright() as playwright:
        contesto = _avvia_contesto(playwright, headless=False)
        try:
            pagina = contesto.pages[0] if contesto.pages else contesto.new_page()
            pagina.goto(URL_LOGIN_PORTALE, timeout=TIMEOUT_NAVIGAZIONE_MS)
            scadenza = time.monotonic() + timeout_secondi
            while time.monotonic() < scadenza:
                for scheda in list(contesto.pages):
                    try:
                        if scheda.url.startswith(URL_BASE_PORTALE) and 'DISCONNESSIONE' in scheda.inner_text('body'):
                            _salva_sessione(contesto)
                            return True
                    except ErrorePlaywright:
                        # Scheda in navigazione o chiusa dall'operatore
                        continue
                if not contesto.pages:
                    return False
                time.sleep(2)
            return False
        finally:
            contesto.close()


def avvia_login_in_background():
    """
    Avvia in un thread il login manuale (Chrome visibile sul PC dove gira il server).
    Ritorna False se un login è già in corso.
    """
    with _lock_stato_login:
        if _stato_login['in_corso']:
            return False
        _stato_login.update(in_corso=True, esito=None, messaggio='')

    def lavoro():
        esito, messaggio = False, ''
        try:
            esito = esegui_login_manuale()
            if not esito:
                messaggio = 'Accesso non completato: riprova.'
        except ErroreSCM as errore:
            messaggio = str(errore)
        except Exception as errore:
            logger.exception('Login SCM fallito')
            messaggio = f'Errore imprevisto durante il login: {errore}'
        with _lock_stato_login:
            _stato_login.update(in_corso=False, esito=esito, messaggio=messaggio)

    threading.Thread(target=lavoro, name='scm-login', daemon=True).start()
    return True


def stato_login():
    """Stato dell'ultimo login avviato dall'interfaccia: in_corso, esito (None/True/False), messaggio."""
    with _lock_stato_login:
        return dict(_stato_login)


def cerca_codice(codice_scm):
    """
    Cerca un codice SCM nel portale e ne restituisce i dati.

    Solleva SessioneScadutaSCM, CodiceNonTrovatoSCM o PortaleNonDisponibileSCM.
    """
    from playwright.sync_api import Error as ErrorePlaywright
    from playwright.sync_api import sync_playwright

    codice_scm = (codice_scm or '').strip().upper()
    if not re.fullmatch(r'[A-Z0-9]{11}', codice_scm):
        raise CodiceNonTrovatoSCM('Il codice SCM deve contenere esattamente 11 caratteri alfanumerici.')

    if not _lock_browser.acquire(blocking=False):
        if _stato_login['in_corso']:
            raise PortaleNonDisponibileSCM('Accesso al portale SCM in corso: completa il login nella finestra di Chrome.')
        raise PortaleNonDisponibileSCM('Un altro recupero dal portale SCM è già in corso: riprova tra qualche secondo.')
    try:
        with sync_playwright() as playwright:
            contesto = _avvia_contesto(playwright, headless=False)
            try:
                pagina = contesto.new_page()
                try:
                    risposta = pagina.goto(
                        f'{URL_BASE_PORTALE}p/{codice_scm}',
                        timeout=TIMEOUT_NAVIGAZIONE_MS,
                        wait_until='domcontentloaded',
                    )
                    if 'login.microsoftonline.com' in pagina.url or '/login' in pagina.url:
                        raise SessioneScadutaSCM(MESSAGGIO_SESSIONE_SCADUTA)
                    if risposta is not None and risposta.status == 404:
                        raise CodiceNonTrovatoSCM(f'Il codice {codice_scm} non è presente nel portale SCM.')
                    pagina.wait_for_selector('.product-main-info', timeout=TIMEOUT_PAGINA_MS)
                    grezzi = pagina.evaluate(_SCRIPT_ESTRAZIONE)
                    url_pagina = pagina.url
                except ErrorePlaywright as errore:
                    raise PortaleNonDisponibileSCM(f'Portale SCM non raggiungibile o pagina inattesa: {errore}') from errore

                if not grezzi.get('autenticato'):
                    raise SessioneScadutaSCM(MESSAGGIO_SESSIONE_SCADUTA)
                dati = interpreta_dati_grezzi(grezzi, codice_scm, url_pagina)
                _salva_sessione(contesto)
                return dati
            finally:
                contesto.close()
    finally:
        _lock_browser.release()
