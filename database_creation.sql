-- ============================================================================
-- GESTIONE MAGAZZINO RICAMBI - CREAZIONE DATABASE
-- Database: GMR
-- ============================================================================
-- Questo script crea SOLO il database vuoto.
-- Tabelle e colonne sono gestite esclusivamente dalle migrazioni Django:
--
--     mysql -u root < database_creation.sql
--     python manage.py migrate
--
-- NON creare tabelle a mano: le migrazioni fallirebbero con "table already exists".
-- ============================================================================

CREATE DATABASE IF NOT EXISTS GMR
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
