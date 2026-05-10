from django.test import TestCase

from .codici import genera_codice_articolo
from .forms import PezzoRicambioForm
from .models import Categoria, PezzoRicambio, UnitaMisura


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
