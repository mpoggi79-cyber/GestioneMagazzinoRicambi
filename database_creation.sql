-- ============================================================================
-- GESTIONE MAGAZZINO RICAMBI - CREAZIONE DATABASE E TABELLE
-- Database: GMR
-- Data: 2025-11-30
-- ============================================================================

-- Crea il database se non esiste
CREATE DATABASE IF NOT EXISTS GMR;
USE GMR;

-- ============================================================================
-- 1. TABELLA: CATEGORIE
-- Classificazione logica dei ricambi
-- ============================================================================
CREATE TABLE IF NOT EXISTS categorie (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nome_categoria VARCHAR(50) NOT NULL UNIQUE,
    descrizione VARCHAR(200),
    stato_attivo TINYINT DEFAULT 1,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stato (stato_attivo),
    INDEX idx_nome (nome_categoria)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. TABELLA: UNITÀ DI MISURA
-- Standardizzazione delle unità di misura
-- ============================================================================
CREATE TABLE IF NOT EXISTS unita_misura (
    id_unita INT PRIMARY KEY AUTO_INCREMENT,
    codice VARCHAR(10) NOT NULL UNIQUE,
    descrizione VARCHAR(50) NOT NULL,
    stato_attivo TINYINT DEFAULT 1,
    INDEX idx_codice (codice),
    INDEX idx_stato (stato_attivo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. TABELLA: FORNITORI
-- Anagrafica fornitori
-- ============================================================================
CREATE TABLE IF NOT EXISTS fornitori (
    id_fornitore INT PRIMARY KEY AUTO_INCREMENT,
    ragione_sociale VARCHAR(100) NOT NULL,
    indirizzo VARCHAR(150),
    citta VARCHAR(50),
    cap VARCHAR(10),
    provincia VARCHAR(2),
    telefono VARCHAR(30),
    email VARCHAR(100),
    partita_iva VARCHAR(20),
    tempo_medio_consegna_giorni INT DEFAULT 7,
    note TEXT,
    stato_attivo TINYINT DEFAULT 1,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ragione_sociale (ragione_sociale),
    INDEX idx_partita_iva (partita_iva),
    INDEX idx_stato (stato_attivo),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. TABELLA: PEZZI DI RICAMBIO (ARTICOLI)
-- Anagrafica completa degli articoli a magazzino
-- ============================================================================
CREATE TABLE IF NOT EXISTS pezzi_ricambio (
    id_articolo INT PRIMARY KEY AUTO_INCREMENT,
    codice_interno VARCHAR(50) NOT NULL UNIQUE,
    codice_scm VARCHAR(50),
    codice_fornitore VARCHAR(50),
    codice_alternativo VARCHAR(50),
    descrizione VARCHAR(200) NOT NULL,
    id_categoria INT NOT NULL,
    id_unita_misura INT NOT NULL,
    giacenza_minima INT DEFAULT 5,
    giacenza_massima INT DEFAULT 100,
    prezzo_acquisto DECIMAL(10, 2),
    prezzo_acquisto_scm DECIMAL(10, 2),
    stato_attivo TINYINT DEFAULT 1,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorie(id_categoria) ON DELETE RESTRICT,
    FOREIGN KEY (id_unita_misura) REFERENCES unita_misura(id_unita) ON DELETE RESTRICT,
    INDEX idx_codice_interno (codice_interno),
    INDEX idx_codice_fornitore (codice_fornitore),
    INDEX idx_categoria (id_categoria),
    INDEX idx_stato (stato_attivo),
    INDEX idx_descrizione (descrizione)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. TABELLA: GIACENZE
-- Situazione aggiornata dello stock
-- ============================================================================
CREATE TABLE IF NOT EXISTS giacenze (
    id_giacenza INT PRIMARY KEY AUTO_INCREMENT,
    id_articolo INT NOT NULL UNIQUE,
    quantita_disponibile INT DEFAULT 0,
    quantita_impegnata INT DEFAULT 0,
    quantita_prenotata INT DEFAULT 0,
    ultimo_aggiornamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_articolo) REFERENCES pezzi_ricambio(id_articolo) ON DELETE CASCADE,
    INDEX idx_articolo (id_articolo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 6. TABELLA: MOVIMENTI DI MAGAZZINO
-- Registro completo di tutte le movimentazioni
-- ============================================================================
CREATE TABLE IF NOT EXISTS movimenti_magazzino (
    id_movimento INT PRIMARY KEY AUTO_INCREMENT,
    id_articolo INT NOT NULL,
    data_movimento DATETIME NOT NULL,
    tipo_movimento ENUM('CARICO', 'SCARICO', 'RETTIFICA', 'RESO_FORNITORE') NOT NULL,
    quantita INT NOT NULL,
    id_fornitore INT,
    causale VARCHAR(150),
    numero_documento VARCHAR(50),
    operatore VARCHAR(50),
    note TEXT,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_articolo) REFERENCES pezzi_ricambio(id_articolo) ON DELETE RESTRICT,
    FOREIGN KEY (id_fornitore) REFERENCES fornitori(id_fornitore) ON DELETE SET NULL,
    INDEX idx_articolo (id_articolo),
    INDEX idx_data_movimento (data_movimento),
    INDEX idx_tipo_movimento (tipo_movimento),
    INDEX idx_fornitore (id_fornitore),
    INDEX idx_operatore (operatore)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 7. TABELLA: INVENTARI
-- Registrazione inventari fisici periodici
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventari (
    id_inventario INT PRIMARY KEY AUTO_INCREMENT,
    data_inventario DATE NOT NULL,
    operatore VARCHAR(50) NOT NULL,
    stato ENUM('IN_CORSO', 'CHIUSO', 'APPROVATO') DEFAULT 'IN_CORSO',
    note TEXT,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_data (data_inventario),
    INDEX idx_stato (stato),
    INDEX idx_operatore (operatore)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 8. TABELLA: DETTAGLIO INVENTARIO
-- Conteggio articolo per articolo
-- ============================================================================
CREATE TABLE IF NOT EXISTS dettaglio_inventario (
    id_dettaglio INT PRIMARY KEY AUTO_INCREMENT,
    id_inventario INT NOT NULL,
    id_articolo INT NOT NULL,
    quantita_rilevata INT NOT NULL,
    quantita_sistema INT NOT NULL,
    differenza INT GENERATED ALWAYS AS (quantita_rilevata - quantita_sistema) STORED,
    note VARCHAR(200),
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_inventario) REFERENCES inventari(id_inventario) ON DELETE CASCADE,
    FOREIGN KEY (id_articolo) REFERENCES pezzi_ricambio(id_articolo) ON DELETE RESTRICT,
    INDEX idx_inventario (id_inventario),
    INDEX idx_articolo (id_articolo),
    INDEX idx_differenza (differenza)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 9. TABELLA: DOCUMENTI ALLEGATI
-- Archivio digitale documenti
-- ============================================================================
CREATE TABLE IF NOT EXISTS documenti_allegati (
    id_documento INT PRIMARY KEY AUTO_INCREMENT,
    tipo_entita ENUM('ARTICOLO', 'MOVIMENTO', 'FORNITORE') NOT NULL,
    id_entita INT NOT NULL,
    tipo_documento VARCHAR(50),
    nome_file VARCHAR(150) NOT NULL,
    percorso_file VARCHAR(250) NOT NULL,
    data_caricamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operatore VARCHAR(50),
    note TEXT,
    INDEX idx_entita (tipo_entita, id_entita),
    INDEX idx_tipo_documento (tipo_documento),
    INDEX idx_data (data_caricamento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- DATI DI INIZIALIZZAZIONE
-- ============================================================================

-- Inserire unità di misura standard
INSERT INTO unita_misura (codice, descrizione) VALUES
    ('pz', 'Pezzo'),
    ('cf', 'Confezione'),
    ('mt', 'Metro'),
    ('kg', 'Chilogrammo'),
    ('lt', 'Litro'),
    ('sc', 'Scatola');

-- Inserire categorie di base
INSERT INTO categorie (nome_categoria, descrizione) VALUES
    ('Meccanica', 'Componenti meccanici generici'),
    ('Elettrica', 'Componenti elettrici e elettronici'),
    ('Pneumatica', 'Componenti pneumatici'),
    ('Accessori consumo', 'Accessori di consumo'),
    ('Idraulica', 'Componenti idraulici'),
    ('Cuscinetti', 'Cuscinetti e rotismi'),
    ('Viti e Bulloneria', 'Viti, bulloni e fasteners');

-- ============================================================================
-- FINE SCRIPT DI CREAZIONE
-- ============================================================================
