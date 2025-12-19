"""
Management command per popolare il database con dati di test.
Crea categorie, fornitori, articoli, giacenze e movimenti realistici.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
import logging

from magazzino.models import (
    Categoria, UnitaMisura, Fornitore, PezzoRicambio,
    Giacenza, MovimentoMagazzino
)
from django.contrib.auth.models import User
from accounts.models import ProfiloUtente, RuoloUtente

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Popola il database con dati di test realistici'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Inizio popolazione database...'))
        
        # Verifica se i dati esistono già
        if PezzoRicambio.objects.count() > 0:
            self.stdout.write(self.style.WARNING('⚠️ Database già popolato. Saltando...'))
            return

        # 1. Crea categorie
        self.stdout.write('📁 Creazione categorie...')
        categorie = self._create_categorie()

        # 2. Crea unità di misura
        self.stdout.write('📏 Creazione unità di misura...')
        unita_misura = self._create_unita_misura()

        # 3. Crea fornitori
        self.stdout.write('🏭 Creazione fornitori...')
        fornitori = self._create_fornitori()

        # 4. Crea articoli
        self.stdout.write('📦 Creazione articoli...')
        articoli = self._create_articoli(categorie, unita_misura)

        # 5. Crea giacenze
        self.stdout.write('📊 Creazione giacenze...')
        self._create_giacenze(articoli)

        # 6. Crea movimenti
        self.stdout.write('🔄 Creazione movimenti...')
        self._create_movimenti(articoli, fornitori)

        # 7. Crea utenti di test
        self.stdout.write('👥 Creazione utenti di test...')
        self._create_test_users()

        self.stdout.write(self.style.SUCCESS('✅ Database popolato con successo!'))
        self.stdout.write('\n📋 Dati creati:')
        self.stdout.write(f'   - {Categoria.objects.count()} categorie')
        self.stdout.write(f'   - {UnitaMisura.objects.count()} unità di misura')
        self.stdout.write(f'   - {Fornitore.objects.count()} fornitori')
        self.stdout.write(f'   - {PezzoRicambio.objects.count()} articoli')
        self.stdout.write(f'   - {Giacenza.objects.count()} giacenze')
        self.stdout.write(f'   - {MovimentoMagazzino.objects.count()} movimenti')

    def _create_categorie(self):
        """Crea categorie di ricambi"""
        categorie_data = [
            ('Motore', 'Parti motore e componenti'),
            ('Trasmissione', 'Sistemi di trasmissione'),
            ('Sospensioni', 'Sospensioni e ammortizzatori'),
            ('Freni', 'Sistemi frenanti'),
            ('Elettrica', 'Componenti elettrici'),
            ('Climatizzazione', 'Sistema di raffreddamento'),
            ('Filtri', 'Filtri e manutenzione'),
            ('Lubrificanti', 'Oli e lubrificanti'),
        ]
        
        categorie = []
        for nome, descrizione in categorie_data:
            cat, _ = Categoria.objects.get_or_create(
                nome_categoria=nome,
                defaults={'descrizione': descrizione, 'stato_attivo': True}
            )
            categorie.append(cat)
        
        return categorie

    def _create_unita_misura(self):
        """Crea unità di misura standard"""
        unita_data = [
            ('Pz', 'Pezzi'),
            ('L', 'Litri'),
            ('Kg', 'Chilogrammi'),
            ('Mt', 'Metri'),
            ('Set', 'Set'),
            ('Coppia', 'Coppia'),
            ('Conf', 'Confezione'),
        ]
        
        unita = []
        for codice, descrizione in unita_data:
            um, _ = UnitaMisura.objects.get_or_create(
                codice=codice,
                defaults={'descrizione': descrizione, 'stato_attivo': True}
            )
            unita.append(um)
        
        return unita

    def _create_fornitori(self):
        """Crea fornitori di ricambi"""
        fornitori_data = [
            {
                'ragione_sociale': 'BOSCH Italia S.p.A.',
                'partita_iva': '00000000100',
                'indirizzo': 'Via Roma 100, Milano',
                'telefono': '+39 02 1234 5678',
                'email': 'ordini@bosch.it',
            },
            {
                'ragione_sociale': 'MAGNETI MARELLI S.p.A.',
                'partita_iva': '00000000200',
                'indirizzo': 'Via Verdi 50, Torino',
                'telefono': '+39 011 234 5678',
                'email': 'info@magnetimarelli.it',
            },
            {
                'ragione_sociale': 'PIRELLI S.p.A.',
                'partita_iva': '00000000300',
                'indirizzo': 'Viale Piero e Alberto Pirelli 25, Milano',
                'telefono': '+39 02 6442 1111',
                'email': 'ordini@pirelli.it',
            },
            {
                'ragione_sociale': 'BREMBO S.p.A.',
                'partita_iva': '00000000400',
                'indirizzo': 'Via Brembo 25, Bergamo',
                'telefono': '+39 035 215 6111',
                'email': 'vendite@brembo.it',
            },
            {
                'ragione_sociale': 'CONTINENTAL AG',
                'partita_iva': '00000000500',
                'indirizzo': 'Via Europa 1, Bologna',
                'telefono': '+39 051 542 5000',
                'email': 'info@continental.com',
            },
        ]
        
        fornitori = []
        for data in fornitori_data:
            fornitore, _ = Fornitore.objects.get_or_create(
                partita_iva=data['partita_iva'],
                defaults={**data, 'stato_attivo': True}
            )
            fornitori.append(fornitore)
        
        return fornitori

    def _create_articoli(self, categorie, unita_misura):
        """Crea articoli di ricambio"""
        articoli_data = [
            # Categoria Motore (idx 0)
            ('Filtro Olio', 'Filtro olio motore', 0, 0, 25.50, 5, 15),
            ('Candela Accensione', 'Set 4 candele NGK', 0, 4, 45.00, 3, 10),
            ('Cinghia Distribuzione', 'Cinghia distribuzione 122 denti', 0, 0, 85.00, 2, 8),
            
            # Categoria Trasmissione (idx 1)
            ('Olio Cambio', 'Olio cambio automatico', 1, 1, 22.00, 5, 20),
            ('Cuscinetto Ruota', 'Cuscinetto ruota anteriore', 1, 0, 65.00, 4, 12),
            
            # Categoria Sospensioni (idx 2)
            ('Ammortizzatore Ant', 'Ammortizzatore anteriore sx/dx', 2, 5, 120.00, 3, 8),
            ('Molla Spirale', 'Molla spirale sospensione', 2, 0, 35.00, 6, 15),
            
            # Categoria Freni (idx 3)
            ('Pastiglie Freno', 'Pastiglie freno anteriori', 3, 5, 55.00, 4, 12),
            ('Disco Freno', 'Disco freno ventilato', 3, 0, 95.00, 2, 6),
            ('Liquido Freni', 'Liquido freni DOT 4', 3, 1, 18.00, 5, 15),
            
            # Categoria Elettrica (idx 4)
            ('Batteria Auto', 'Batteria 12V 70Ah', 4, 0, 150.00, 3, 8),
            ('Alternatore', 'Alternatore 120A', 4, 0, 220.00, 2, 5),
            ('Motorino Avviamento', 'Motorino avviamento', 4, 0, 180.00, 2, 6),
            
            # Categoria Climatizzazione (idx 5)
            ('Compressore Clima', 'Compressore aria condizionata', 5, 0, 380.00, 1, 3),
            ('Filtro Abitacolo', 'Filtro abitacolo auto', 5, 0, 28.00, 5, 15),
            
            # Categoria Filtri (idx 6)
            ('Filtro Aria', 'Filtro aria motore', 6, 0, 20.00, 8, 20),
            ('Filtro Gasolio', 'Filtro gasolio motore', 6, 0, 32.00, 6, 15),
            
            # Categoria Lubrificanti (idx 7)
            ('Olio 5W30', 'Olio motore 5W30', 7, 1, 15.00, 10, 30),
            ('Grasso Lubrificante', 'Grasso lubrificante universale', 7, 2, 12.00, 8, 25),
        ]
        
        articoli = []
        for idx, (nome, descr, cat_idx, um_idx, prezzo, min_stock, max_stock) in enumerate(articoli_data):
            articolo, _ = PezzoRicambio.objects.get_or_create(
                codice_interno=f"RIC-{idx+1:04d}",
                defaults={
                    'descrizione': descr,
                    'categoria': categorie[cat_idx],
                    'unita_misura': unita_misura[um_idx],
                    'prezzo_acquisto': prezzo,
                    'giacenza_minima': min_stock,
                    'giacenza_massima': max_stock,
                    'stato_attivo': True,
                }
            )
            articoli.append(articolo)
        
        return articoli

    def _create_giacenze(self, articoli):
        """Crea giacenze per gli articoli"""
        for articolo in articoli:
            # Giacenza casuale tra minima e massima
            quantita = random.randint(
                articolo.giacenza_minima,
                articolo.giacenza_massima
            )
            
            Giacenza.objects.get_or_create(
                articolo=articolo,
                defaults={
                    'quantita_disponibile': quantita,
                    'quantita_impegnata': random.randint(0, max(0, quantita - 2)),
                    'quantita_prenotata': 0,
                }
            )

    def _create_movimenti(self, articoli, fornitori):
        """Crea movimenti di magazzino"""
        today = timezone.now()
        
        for articolo in articoli:
            # Crea 3-5 movimenti per articolo negli ultimi 30 giorni
            num_movimenti = random.randint(3, 5)
            
            for _ in range(num_movimenti):
                # Data casuale negli ultimi 30 giorni
                giorni_fa = random.randint(0, 30)
                data = today - timedelta(days=giorni_fa)
                
                # Tipo movimento casuale
                tipo = random.choice(['CARICO', 'SCARICO', 'RETTIFICA'])
                
                # Quantità casuale
                if tipo == 'CARICO':
                    quantita = random.randint(5, 25)
                    fornitore = random.choice(fornitori)
                    numero_doc = f"OA{random.randint(1000, 9999)}"
                elif tipo == 'SCARICO':
                    quantita = random.randint(1, 10)
                    fornitore = None
                    numero_doc = f"VD{random.randint(1000, 9999)}"
                else:  # RETTIFICA
                    quantita = random.randint(-5, 5)
                    fornitore = None
                    numero_doc = f"RET{random.randint(1000, 9999)}"
                
                MovimentoMagazzino.objects.create(
                    articolo=articolo,
                    tipo_movimento=tipo,
                    quantita=quantita,
                    fornitore=fornitore,
                    numero_documento=numero_doc,
                    data_movimento=data,
                    operatore='admin',
                    note=f'Movimento di test - {tipo}'
                )

    def _create_test_users(self):
        """Crea utenti di test con diversi ruoli"""
        users_data = [
            ('gestore', 'Gestore', 'Magazzino', 'gestore@test.com', RuoloUtente.GESTORE_MAGAZZINO),
            ('operatore', 'Operatore', 'Magazzino', 'operatore@test.com', RuoloUtente.OPERATORE),
            ('visualizzatore', 'Visualizzatore', 'Sistema', 'vis@test.com', RuoloUtente.VISUALIZZATORE),
        ]
        
        for username, first_name, last_name, email, ruolo in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            )
            
            # Crea o aggiorna profilo
            profilo, _ = ProfiloUtente.objects.get_or_create(
                user=user,
                defaults={
                    'ruolo': ruolo,
                    'dipartimento': 'Magazzino',
                    'numero_dipendente': f"EMP{random.randint(1000, 9999)}",
                    'attivo': True,
                }
            )
            
            if created:
                self.stdout.write(f"   Utente {username} creato ({ruolo})")

