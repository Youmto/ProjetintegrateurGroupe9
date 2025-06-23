-- =============================================
-- SGE_init.sql
-- Configuration initiale et séquences
-- =============================================

-- Création des séquences pour les IDs auto-générés
CREATE SEQUENCE IF NOT EXISTS organisation_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS individu_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS role_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS produit_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS entrepot_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS cellule_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS lot_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS colis_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS bon_reception_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS bon_expedition_seq START WITH 100;
CREATE SEQUENCE IF NOT EXISTS rapport_seq START WITH 100;

-- Configuration des paramètres par défaut
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_cache_size = '4GB';
SELECT pg_reload_conf();
