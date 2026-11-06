from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from accounts.models import RuoloUtente
from . import scm_portale
from .codici import genera_codice_articolo
from .forms import PezzoRicambioForm
from .models import (
	Categoria, Fornitore, MatricolaMacchinaSCM, ModelloMacchinaSCM, PezzoRicambio,
	StoricoDatiSCM, TbAppellativo, UnitaMisura,
)


class CodiceArticoloAutomaticoTests(TestCase):
	def setUp(self):
		self.categoria = Categoria.objects.create(nome_categoria='Categoria Test')
		self.unita_misura = UnitaMisura.objects.create(denominazione='PZ')

	def dati_form_articolo(self, **overrides):
		dati = {
			'descrizione': 'Articolo test SCM',
			'unita_misura': self.unita_misura.pk,
			'stato_disponibilita': PezzoRicambio.DISPONIBILE,
			'stato_attivo': 'on',
			'giacenza_minima': '',
			'giacenza_massima': '',
			'macrocategoria': self.categoria.pk,
			'categoria_livello2': '',
			'sottocategoria': '',
			'categoria': '',
			'codice_scm': '',
		}
		dati.update(overrides)
		return dati

	def crea_articolo(self, descrizione):
		return PezzoRicambio.objects.create(
			descrizione=descrizione,
			categoria=self.categoria,
			unita_misura=self.unita_misura,
		)

	def test_nuovo_articolo_usa_codice_basato_su_id_reale(self):
		articolo = self.crea_articolo('Articolo 1')

		self.assertEqual(articolo.codice_interno, genera_codice_articolo(articolo.id_articolo))

	def test_nuovo_articolo_non_riusa_codice_del_record_eliminato(self):
		primo = self.crea_articolo('Articolo 1')
		secondo = self.crea_articolo('Articolo 2')
		secondo_id = secondo.id_articolo
		secondo.delete()

		nuovo = self.crea_articolo('Articolo 3')

		self.assertNotEqual(nuovo.codice_interno, genera_codice_articolo(secondo_id))
		self.assertEqual(nuovo.codice_interno, genera_codice_articolo(nuovo.id_articolo))

	def test_form_mostra_codice_automatico_in_sola_lettura(self):
		form = PezzoRicambioForm()
		campo = form.fields['codice_interno']

		self.assertFalse(campo.required)
		self.assertTrue(campo.disabled)
		self.assertEqual(
			campo.widget.attrs.get('placeholder'),
			'Generato automaticamente al salvataggio',
		)

	def test_form_richiede_categoria_e_mantiene_default_giacenze(self):
		form = PezzoRicambioForm(data={
			'descrizione': 'Articolo senza categoria esplicita',
			'unita_misura': self.unita_misura.pk,
			'stato_disponibilita': PezzoRicambio.DISPONIBILE,
			'stato_attivo': 'on',
			'giacenza_minima': '',
			'giacenza_massima': '',
			'macrocategoria': '',
			'categoria_livello2': '',
			'sottocategoria': '',
			'categoria': '',
		})

		self.assertFalse(form.is_valid())
		self.assertIn('macrocategoria', form.errors)

		form = PezzoRicambioForm(data={
			'descrizione': 'Articolo con categoria esplicita',
			'unita_misura': self.unita_misura.pk,
			'stato_disponibilita': PezzoRicambio.DISPONIBILE,
			'stato_attivo': 'on',
			'giacenza_minima': '',
			'giacenza_massima': '',
			'macrocategoria': self.categoria.pk,
			'categoria_livello2': '',
			'sottocategoria': '',
			'categoria': '',
		})

		self.assertTrue(form.is_valid(), form.errors)
		articolo = form.save()

		self.assertEqual(articolo.categoria, self.categoria)
		self.assertEqual(articolo.giacenza_minima, 5)
		self.assertEqual(articolo.giacenza_massima, 100)

	def test_codice_scm_facoltativo_non_blocca_salvataggio(self):
		form = PezzoRicambioForm(data=self.dati_form_articolo(codice_scm=''))

		self.assertTrue(form.is_valid(), form.errors)

	def test_codice_scm_11_alfanumerici_accetta_e_converte_maiuscolo(self):
		form = PezzoRicambioForm(data=self.dati_form_articolo(codice_scm='07l0320061b'))

		self.assertTrue(form.is_valid(), form.errors)
		articolo = form.save()
		self.assertEqual(articolo.codice_scm, '07L0320061B')

	def test_codice_scm_rifiuta_lunghezza_diversa_da_11(self):
		form = PezzoRicambioForm(data=self.dati_form_articolo(codice_scm='07L0320061'))

		self.assertFalse(form.is_valid())
		self.assertIn('codice_scm', form.errors)

	def test_codice_scm_rifiuta_caratteri_non_alfanumerici(self):
		form = PezzoRicambioForm(data=self.dati_form_articolo(codice_scm='07L03200-1B'))

		self.assertFalse(form.is_valid())
		self.assertIn('codice_scm', form.errors)

	def test_codice_scm_duplicato_blocca_inserimento_anche_se_input_minuscolo(self):
		articolo_esistente = self.crea_articolo('Articolo con SCM esistente')
		articolo_esistente.codice_scm = '07L0320061B'
		articolo_esistente.save()

		form = PezzoRicambioForm(data=self.dati_form_articolo(
			descrizione='Articolo duplicato',
			codice_scm='07l0320061b',
		))

		self.assertFalse(form.is_valid())
		self.assertIn('codice_scm', form.errors)

	def test_codice_sostitutivo_facoltativo_e_salvato(self):
		nuovo = self.crea_articolo('Articolo B')
		form = PezzoRicambioForm(data=self.dati_form_articolo(
			descrizione='Articolo A',
			codice_sostitutivo=nuovo.pk,
		))

		self.assertTrue(form.is_valid(), form.errors)
		vecchio = form.save()
		self.assertEqual(vecchio.codice_sostitutivo, nuovo)
		self.assertIn(vecchio, nuovo.sostituisce.all())

	def test_codice_sostitutivo_non_puo_essere_l_articolo_stesso(self):
		articolo = self.crea_articolo('Articolo A')
		form = PezzoRicambioForm(
			data=self.dati_form_articolo(descrizione='Articolo A', codice_sostitutivo=articolo.pk),
			instance=articolo,
		)

		self.assertFalse(form.is_valid())
		self.assertIn('codice_sostitutivo', form.errors)

	def test_codice_sostitutivo_rifiuta_cicli(self):
		a = self.crea_articolo('Articolo A')
		b = self.crea_articolo('Articolo B')
		a.codice_sostitutivo = b
		a.save()
		form = PezzoRicambioForm(
			data=self.dati_form_articolo(descrizione='Articolo B', codice_sostitutivo=a.pk),
			instance=b,
		)

		self.assertFalse(form.is_valid())
		self.assertIn('codice_sostitutivo', form.errors)


class LayoutModificaArticoloTests(TestCase):
	def setUp(self):
		self.utente_admin = User.objects.create_user(username='admin_articolo', password='PasswordSicura123!')
		self.utente_admin.profilo.ruolo = RuoloUtente.ADMIN
		self.utente_admin.profilo.save()

		self.categoria = Categoria.objects.create(nome_categoria='Categoria Layout')
		self.unita_misura = UnitaMisura.objects.create(denominazione='PZ LAYOUT')
		self.fornitore = Fornitore.objects.create(ragione_sociale='Fornitore Layout')
		self.modello_scm = ModelloMacchinaSCM.objects.create(nome_modello='Scm Test 100')
		self.matricola_scm = MatricolaMacchinaSCM.objects.create(
			modello=self.modello_scm,
			matricola_macchina='MATR-LAYOUT-001',
		)
		self.articolo = PezzoRicambio.objects.create(
			descrizione='Articolo layout',
			categoria=self.categoria,
			unita_misura=self.unita_misura,
			fornitore=self.fornitore,
			modello_macchina_scm=self.modello_scm,
			matricola_macchina_scm=self.matricola_scm,
			codice_scm='07L0320061B',
			codice_fornitore='FORN-001',
		)

	def test_pagina_modifica_articolo_mostra_tre_gruppi_e_meta_identificativo(self):
		self.client.force_login(self.utente_admin)
		response = self.client.get(reverse('magazzino:articolo_update', kwargs={'pk': self.articolo.pk}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Identificativo')
		self.assertContains(response, self.articolo.codice_interno)
		self.assertContains(response, 'Modifica Articolo')
		self.assertContains(response, 'Dati SCM')
		self.assertContains(response, 'Dati Fornitore')
		self.assertContains(response, 'Dati Articolo')
		self.assertContains(response, 'Classificazione articolo')
		self.assertNotContains(response, f'Modifica Articolo: {self.articolo.codice_interno}', html=False)
		self.assertNotContains(response, 'name="codice_interno"', html=False)

	def test_dettaglio_articolo_collega_al_codice_sostitutivo_e_viceversa(self):
		nuovo = PezzoRicambio.objects.create(
			descrizione='Articolo nuovo',
			categoria=self.categoria,
			unita_misura=self.unita_misura,
			codice_scm='07L0320062C',
		)
		self.articolo.codice_sostitutivo = nuovo
		self.articolo.save()
		self.client.force_login(self.utente_admin)

		risposta_vecchio = self.client.get(reverse('magazzino:articolo_detail', kwargs={'pk': self.articolo.pk}))
		risposta_nuovo = self.client.get(reverse('magazzino:articolo_detail', kwargs={'pk': nuovo.pk}))

		self.assertContains(
			risposta_vecchio,
			f'href="{reverse("magazzino:articolo_detail", kwargs={"pk": nuovo.pk})}"',
		)
		self.assertContains(
			risposta_nuovo,
			f'href="{reverse("magazzino:articolo_detail", kwargs={"pk": self.articolo.pk})}"',
		)

	def test_admin_django_articolo_carica(self):
		self.utente_admin.is_staff = True
		self.utente_admin.is_superuser = True
		self.utente_admin.save()
		self.client.force_login(self.utente_admin)

		response = self.client.get(f'/admin/magazzino/pezzoricambio/{self.articolo.pk}/change/')

		self.assertEqual(response.status_code, 200)


class GestioneTabelleRecordTests(TestCase):
	def setUp(self):
		self.utente_admin = User.objects.create_user(username='admin_tabella', password='PasswordSicura123!')
		self.utente_admin.profilo.ruolo = RuoloUtente.ADMIN
		self.utente_admin.profilo.save()

		self.utente_operatore = User.objects.create_user(username='operatore_tabella', password='PasswordSicura123!')
		self.utente_operatore.profilo.ruolo = RuoloUtente.OPERATORE
		self.utente_operatore.profilo.save()

		self.record_appellativo = TbAppellativo.objects.create(descrizione='Sig.')
		self.unita_attiva = UnitaMisura.objects.create(denominazione='PZ TEST', stato_attivo=True)
		self.unita_inattiva = UnitaMisura.objects.create(denominazione='KM TEST OFF', stato_attivo=False)

	def test_lista_tabella_contiene_link_modifica_record(self):
		self.client.force_login(self.utente_admin)
		response = self.client.get(reverse('magazzino:modifica_tabella', kwargs={'nome_tabella': 'tbappellativo'}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(
			response,
			reverse(
				'magazzino:modifica_record_tabella',
				kwargs={'nome_tabella': 'tbappellativo', 'pk': self.record_appellativo.pk},
			),
		)

	def test_admin_puo_modificare_record_tabella(self):
		self.client.force_login(self.utente_admin)
		url = reverse(
			'magazzino:modifica_record_tabella',
			kwargs={'nome_tabella': 'tbappellativo', 'pk': self.record_appellativo.pk},
		)

		with self.assertLogs('magazzino.views', level='INFO') as logs_catturati:
			response = self.client.post(url, {'descrizione': 'Dott.'}, follow=True)

		self.record_appellativo.refresh_from_db()
		self.assertEqual(self.record_appellativo.descrizione, 'Dott.')
		self.assertTrue(any('[AUDIT_TABELLE]' in messaggio for messaggio in logs_catturati.output))
		self.assertTrue(any('tabella=tbappellativo' in messaggio for messaggio in logs_catturati.output))
		self.assertRedirects(
			response,
			reverse('magazzino:modifica_tabella', kwargs={'nome_tabella': 'tbappellativo'}),
		)

	def test_operatore_senza_permessi_non_accede_a_modifica_record_tabella(self):
		self.client.force_login(self.utente_operatore)
		url = reverse(
			'magazzino:modifica_record_tabella',
			kwargs={'nome_tabella': 'tbappellativo', 'pk': self.record_appellativo.pk},
		)

		response = self.client.get(url)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, reverse('magazzino:dashboard'))

	def test_tbunitamisura_mostra_inattivi_di_default(self):
		self.client.force_login(self.utente_admin)
		response = self.client.get(reverse('magazzino:modifica_tabella', kwargs={'nome_tabella': 'tbunitamisura'}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.unita_attiva.denominazione)
		self.assertContains(response, self.unita_inattiva.denominazione)
		self.assertContains(response, 'Mostra solo attivi')


class PortaleSCMInterpretazioneTests(SimpleTestCase):
	def test_importo_formato_italiano(self):
		self.assertEqual(scm_portale.interpreta_importo('1.303,68\xa0€'), Decimal('1303.68'))
		self.assertEqual(scm_portale.interpreta_importo('2707.0'), Decimal('2707.00'))
		self.assertIsNone(scm_portale.interpreta_importo(''))

	def test_disponibilita(self):
		self.assertEqual(scm_portale.interpreta_disponibilita('Disponibile \xa06'), (6, 'Disponibile'))
		self.assertEqual(scm_portale.interpreta_disponibilita('In arrivo  1'), (1, 'In arrivo'))
		self.assertEqual(scm_portale.interpreta_disponibilita('Non disponibile'), (0, 'Non disponibile'))
		self.assertEqual(scm_portale.interpreta_disponibilita(''), (None, ''))

	def test_dati_con_sconti(self):
		grezzi = {
			'nome': 'MORSETTO',
			'descrizione': 'MORSETTO',
			'prezzo_barrato': '1.680,00\xa0€',
			'prezzo_finale': '1.303,68\xa0€',
			'prezzo_json_ld': '1680.0',
			'disponibilita': 'Disponibile \xa06',
			'immagini': [
				'https://shop.scmgroup.com//medias/convert-96Wx96H-2737230165e-1.jpg?context=a',
				'https://shop.scmgroup.com//medias/convert-1200Wx1200H-2737230165e-1.jpg?context=b',
			],
			'autenticato': True,
		}
		dati = scm_portale.interpreta_dati_grezzi(grezzi, '2737230165E')

		self.assertEqual(dati.prezzo_listino, Decimal('1680.00'))
		self.assertEqual(dati.prezzo_acquisto, Decimal('1303.68'))
		self.assertEqual(dati.disponibilita, 6)
		self.assertEqual(dati.stato_disponibilita, 'Disponibile')
		self.assertEqual(
			dati.url_immagine,
			'https://shop.scmgroup.com/medias/convert-1200Wx1200H-2737230165e-1.jpg?context=b',
		)

	def test_immagine_segnaposto_ignorata_e_listino_da_json_ld(self):
		grezzi = {
			'nome': 'MORSETTO H=145',
			'descrizione': '',
			'prezzo_barrato': '',
			'prezzo_finale': '2.100,64\xa0€',
			'prezzo_json_ld': '2707.0',
			'disponibilita': 'In arrivo  1',
			'immagini': ['https://shop.scmgroup.com/_ui/theme/images/missing_product_EN_300x300.jpg'],
		}
		dati = scm_portale.interpreta_dati_grezzi(grezzi, '29L0194302H')

		self.assertEqual(dati.descrizione, 'MORSETTO H=145')
		self.assertEqual(dati.prezzo_listino, Decimal('2707.00'))
		self.assertEqual(dati.prezzo_acquisto, Decimal('2100.64'))
		self.assertEqual(dati.url_immagine, '')

	def test_senza_prezzi_segnala_sessione_scaduta(self):
		with self.assertRaises(scm_portale.SessioneScadutaSCM):
			scm_portale.interpreta_dati_grezzi({'nome': 'X', 'disponibilita': 'Disponibile 3'}, '2737230165E')

	def test_articolo_autenticato_senza_prezzo_non_e_sessione_scaduta(self):
		grezzi = {
			'nome': 'AZIONAMENTO BRUSHLESS',
			'descrizione': 'AZIONAMENTO BRUSHLESS',
			'disponibilita': '',
			'testo_principale': 'AZIONAMENTO BRUSHLESS Articolo attualmente non disponibile',
			'autenticato': True,
		}
		dati = scm_portale.interpreta_dati_grezzi(grezzi, '0001310282E')

		self.assertIsNone(dati.prezzo_listino)
		self.assertIsNone(dati.prezzo_acquisto)
		self.assertEqual((dati.disponibilita, dati.stato_disponibilita), (0, 'Non disponibile'))
		self.assertIn('non disponibile', dati.nota)


class RecuperaDatiSCMTests(TestCase):
	def setUp(self):
		self.utente_admin = User.objects.create_user(username='admin_scm', password='PasswordSicura123!')
		self.utente_admin.profilo.ruolo = RuoloUtente.ADMIN
		self.utente_admin.profilo.save()
		self.utente_operatore = User.objects.create_user(username='operatore_scm', password='PasswordSicura123!')
		self.utente_operatore.profilo.ruolo = RuoloUtente.OPERATORE
		self.utente_operatore.profilo.save()
		self.url = reverse('magazzino:articolo_scm_recupera')
		self.categoria = Categoria.objects.create(nome_categoria='Categoria SCM')
		self.unita_misura = UnitaMisura.objects.create(denominazione='PZ SCM')

	def _dati(self):
		return scm_portale.DatiArticoloSCM(
			codice_scm='2737230165E',
			descrizione='MORSETTO',
			prezzo_listino=Decimal('1680.00'),
			prezzo_acquisto=Decimal('1303.68'),
			disponibilita=6,
			stato_disponibilita='Disponibile',
		)

	def test_recupero_riuscito(self):
		self.client.force_login(self.utente_admin)
		with mock.patch.object(scm_portale, 'cerca_codice', return_value=self._dati()):
			risposta = self.client.post(self.url, {'codice_scm': '2737230165e'})

		self.assertEqual(risposta.status_code, 200)
		corpo = risposta.json()
		self.assertTrue(corpo['ok'])
		self.assertEqual(corpo['dati']['prezzo_listino'], '1680.00')
		self.assertEqual(corpo['dati']['prezzo_acquisto'], '1303.68')
		self.assertEqual(corpo['dati']['disponibilita'], 6)

	def test_errori_del_portale_sono_mappati(self):
		self.client.force_login(self.utente_admin)
		casi = [
			(scm_portale.SessioneScadutaSCM('scaduta'), 401),
			(scm_portale.CodiceNonTrovatoSCM('assente'), 404),
			(scm_portale.PortaleNonDisponibileSCM('giu'), 503),
		]
		for errore, stato in casi:
			with mock.patch.object(scm_portale, 'cerca_codice', side_effect=errore):
				risposta = self.client.post(self.url, {'codice_scm': '2737230165E'})
			self.assertEqual(risposta.status_code, stato)
			self.assertFalse(risposta.json()['ok'])

	def test_login_da_interfaccia_solo_per_chi_puo_modificare(self):
		url_login = reverse('magazzino:articolo_scm_login')

		self.client.force_login(self.utente_operatore)
		with mock.patch.object(scm_portale, 'avvia_login_in_background') as finto:
			self.assertEqual(self.client.post(url_login).status_code, 403)
		finto.assert_not_called()

		self.client.force_login(self.utente_admin)
		with mock.patch.object(scm_portale, 'avvia_login_in_background', return_value=True) as finto:
			risposta = self.client.post(url_login)
		self.assertEqual(risposta.json(), {'ok': True, 'avviato': True})
		finto.assert_called_once()

		with mock.patch.object(
			scm_portale, 'stato_login', return_value={'in_corso': False, 'esito': True, 'messaggio': ''}
		):
			stato = self.client.get(url_login).json()
		self.assertTrue(stato['esito'])
		self.assertFalse(stato['in_corso'])

	def test_operatore_senza_permessi_riceve_403(self):
		self.client.force_login(self.utente_operatore)
		with mock.patch.object(scm_portale, 'cerca_codice') as finto:
			risposta = self.client.post(self.url, {'codice_scm': '2737230165E'})

		self.assertEqual(risposta.status_code, 403)
		finto.assert_not_called()

	def test_salvataggio_con_rilevamento_registra_storico_una_sola_volta(self):
		self.client.force_login(self.utente_admin)
		articolo = PezzoRicambio.objects.create(
			descrizione='Morsetto', categoria=self.categoria, unita_misura=self.unita_misura,
			codice_scm='2737230165E',
		)
		url = reverse('magazzino:articolo_update', kwargs={'pk': articolo.pk})
		dati = {
			'descrizione': 'Morsetto',
			'categoria': self.categoria.pk,
			'unita_misura': self.unita_misura.pk,
			'codice_scm': '2737230165E',
			'stato_disponibilita': PezzoRicambio.DISPONIBILE,
			'stato_attivo': 'on',
			'prezzo_listino_scm': '1680.00',
			'prezzo_acquisto_scm': '1303.68',
			'disponibilita_scm': '6',
			'stato_disponibilita_scm': 'Disponibile',
			'dati_scm_aggiornati_il': '2026-11-02T23:30:00+01:00',
		}

		self.assertEqual(self.client.post(url, dati).status_code, 302)
		self.assertEqual(self.client.post(url, dati).status_code, 302)

		articolo.refresh_from_db()
		self.assertEqual(articolo.prezzo_listino_scm, Decimal('1680.00'))
		self.assertEqual(articolo.prezzo_acquisto_scm, Decimal('1303.68'))
		self.assertEqual(articolo.disponibilita_scm, 6)
		storico = StoricoDatiSCM.objects.filter(articolo=articolo)
		self.assertEqual(storico.count(), 1)
		self.assertEqual(storico.first().prezzo_acquisto, Decimal('1303.68'))
		self.assertEqual(storico.first().operatore, 'admin_scm')

		dati.update({'prezzo_acquisto_scm': '1250.00', 'dati_scm_aggiornati_il': '2027-02-02T10:00:00+01:00'})
		self.client.post(url, dati)
		self.assertEqual(StoricoDatiSCM.objects.filter(articolo=articolo).count(), 2)

		risposta_dettaglio = self.client.get(reverse('magazzino:articolo_detail', kwargs={'pk': articolo.pk}))
		self.assertContains(risposta_dettaglio, 'Storico Prezzi e Disponibilità SCM')
		self.assertContains(risposta_dettaglio, '1303,68')
