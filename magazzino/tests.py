from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import RuoloUtente
from .codici import genera_codice_articolo
from .forms import PezzoRicambioForm
from .models import Categoria, Fornitore, MatricolaMacchinaSCM, ModelloMacchinaSCM, PezzoRicambio, TbAppellativo, UnitaMisura


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
