-- =============================================
-- SGE_init.sql
-- Initialisation des séquences et réglages système
-- Pour le Système de Gestion d’Entrepôt (SGE)
-- =============================================

-- =============================================
-- SECTION 1 : Séquences pour les clés primaires
-- =============================================

CREATE SEQUENCE IF NOT EXISTS organisation_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS individu_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS role_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS produit_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS entrepot_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS cellule_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS lot_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS colis_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS bon_reception_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

CREATE SEQUENCE IF NOT EXISTS bon_expedition_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

-- Redondant : supprimé → seq_bon_reception

-- Rapport exception spécifique (commence à 1)
CREATE SEQUENCE IF NOT EXISTS rapport_exception_seq
    START WITH 1 INCREMENT BY 1 CACHE 10;

-- Rapport générique si besoin d’un identifiant à part
CREATE SEQUENCE IF NOT EXISTS rapport_seq
    START WITH 100 INCREMENT BY 1 CACHE 10;

-- =============================================
-- SECTION 2 : Configuration système PostgreSQL
-- (optionnel selon environnement, nécessite superuser)
-- =============================================

-- Commenter ces lignes si vous n'avez pas les droits SUPERUSER
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_cache_size = '4GB';

-- -- Recharger la configuration
SELECT pg_reload_conf();

-- =============================================
-- FIN DU SCRIPT
-- =============================================
