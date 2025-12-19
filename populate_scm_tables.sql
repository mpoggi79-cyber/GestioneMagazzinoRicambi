-- Popolamento tabelle modelli e matricole SCM con dati di esempio

-- 1. Inserisci modelli macchina SCM
INSERT INTO `modelli_macchine_scm` (`nome_modello`, `gamma`, `stato_attivo`) VALUES
('RD100NT TVN', NULL, 1),
('RD110NT TVN PR', NULL, 1),
('RECORD 240', NULL, 1),
('ACCORD 40', NULL, 1),
('ACCORD 40FX', NULL, 1);

-- 2. Inserisci matricole macchine SCM
INSERT INTO `matricole_macchine_scm` (`id_modello`, `matricola_macchina`, `anno`, `stato_attivo`, `creato_il`, `modificato_il`) VALUES
-- Matricole per RD100NT TVN (id_modello = 1)
(1, 'AA1/000681', 2018, 1, NOW(6), NOW(6)),
(1, 'AA1/001250', 2019, 1, NOW(6), NOW(6)),
(1, 'AA1/014696', 2020, 1, NOW(6), NOW(6)),
(1, 'AA10012345', 2021, 1, NOW(6), NOW(6)),
-- Matricole per RD110NT TVN PR (id_modello = 2)
(2, 'AA2/000127', 2019, 1, NOW(6), NOW(6)),
(2, 'AA2/001458', 2020, 1, NOW(6), NOW(6)),
-- Matricole per RECORD 240 (id_modello = 3)
(3, 'AA1/002150', 2017, 1, NOW(6), NOW(6)),
(3, 'AA1/003200', 2018, 1, NOW(6), NOW(6)),
-- Matricole per ACCORD 40 (id_modello = 4)
(4, 'ACL/001/21', 2021, 1, NOW(6), NOW(6)),
(4, 'ACL/002/22', 2022, 1, NOW(6), NOW(6)),
-- Matricole per ACCORD 40FX (id_modello = 5)
(5, 'ACL/003/23', 2023, 1, NOW(6), NOW(6)),
(5, 'ACL/004/24', 2024, 1, NOW(6), NOW(6));
