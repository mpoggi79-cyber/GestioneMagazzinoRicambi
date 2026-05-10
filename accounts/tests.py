from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class FlussoAutenticazioneTests(TestCase):
	def setUp(self):
		self.username = 'utente_test'
		self.password = 'PasswordSicura123!'
		self.user = User.objects.create_user(
			username=self.username,
			password=self.password,
			email='utente_test@example.com',
		)

	def test_login_riuscito_mostra_benvenuto_in_dashboard(self):
		response = self.client.post(
			reverse('accounts:login'),
			{
				'username': self.username,
				'password': self.password,
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, f'Benvenuto, {self.username}! Accesso effettuato con successo.')

	def test_logout_redirect_a_pagina_dedicata(self):
		self.client.force_login(self.user)

		response = self.client.post(reverse('accounts:logout'))

		self.assertRedirects(
			response,
			reverse('accounts:logout_completato'),
			fetch_redirect_response=False,
		)

	def test_pagina_logout_completato_contiene_solo_conferma(self):
		response = self.client.get(reverse('accounts:logout_completato'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Grazie e Arrivederci')
		self.assertContains(response, reverse('accounts:logout_conferma'))
		self.assertContains(response, '>OK<', html=False)

	def test_conferma_logout_richiede_post(self):
		response = self.client.get(reverse('accounts:logout_conferma'))

		self.assertEqual(response.status_code, 405)

	def test_conferma_logout_reindirizza_a_login_con_reset(self):
		response = self.client.post(reverse('accounts:logout_conferma'))

		self.assertRedirects(
			response,
			f"{reverse('accounts:login')}?session_reset=1",
			fetch_redirect_response=False,
		)

	def test_nessun_messaggio_logout_residuo_dopo_nuovo_login(self):
		self.client.force_login(self.user)
		self.client.post(reverse('accounts:logout'))
		self.client.post(reverse('accounts:logout_conferma'))

		response = self.client.post(
			reverse('accounts:login'),
			{
				'username': self.username,
				'password': self.password,
			},
			follow=True,
		)

		self.assertNotContains(response, 'Logout effettuato con successo. Arrivederci!')
		self.assertContains(response, f'Benvenuto, {self.username}! Accesso effettuato con successo.')

	def test_login_e_logout_completato_hanno_header_no_cache(self):
		login_response = self.client.get(reverse('accounts:login'))
		logout_completato_response = self.client.get(reverse('accounts:logout_completato'))

		self.assertIn('no-store', login_response.get('Cache-Control', '').lower())
		self.assertIn('no-store', logout_completato_response.get('Cache-Control', '').lower())
