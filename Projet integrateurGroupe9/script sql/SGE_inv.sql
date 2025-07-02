-- =============================================
-- SGE_inv.sql - VERSION COMPLETE PRO
-- Invariants, vues, triggers et fonctions metier
-- Pour le SGE (Systeme de Gestion d'Entrepot)
-- =============================================

SET client_encoding = 'UTF8';
SET search_path = public;

-- =============================================
-- VUES METIER
-- =============================================

-- Vue inventaire global
drop view vue_inventaire_global;
CREATE OR REPLACE VIEW vue_inventaire_global AS
SELECT
    p.idProduit,
    p.reference,
    p.nom,
    p.type,

    -- Calcul dynamique de la quantité totale via STOCKER → LOT → PRODUIT
    COALESCE(SUM(s.quantite), 0) AS quantite_totale,

    -- Nombre d'entrepôts (organisation) différents dans lesquels le produit est stocké
    COUNT(DISTINCT e.idEntrepot) AS nb_emplacements,

    -- Prochaine date d’expiration parmi tous les lots valides
    MIN(l.dateExpiration) FILTER (WHERE l.dateExpiration > CURRENT_DATE) AS prochaine_expiration

FROM PRODUIT p
LEFT JOIN LOT l ON p.idProduit = l.idProduit
LEFT JOIN STOCKER s ON s.idLot = l.idLot
LEFT JOIN COMPOSER_ENTREPOT ce ON ce.idCellule = s.idCellule
LEFT JOIN ENTREPOT e ON ce.idEntrepot = e.idEntrepot

GROUP BY p.idProduit, p.reference, p.nom, p.type;


-- Vue emplacements avec taux d'occupation
DROP VIEW IF EXISTS vue_emplacements_occupes;

CREATE OR REPLACE VIEW vue_emplacements_occupes AS
SELECT
    c.idCellule AS idCellule,
    c.reference AS reference,
    e.idEntrepot AS idEntrepot,
    e.nom AS nom_entrepot,
    c.capacite_max AS capacite_max,
    c.volumeMaximal AS volumeMaximal,
    c.statut AS statut,

    COUNT(DISTINCT s.idLot) AS nb_lots,

    -- Quantité totale réelle stockée
    COALESCE(SUM(s.quantite), 0) AS quantite_totale,

    -- Volume utilisé (optionnel)
    ROUND(SUM(
        CASE
            WHEN p.type = 'materiel' THEN COALESCE(pm.volume, 0) * COALESCE(s.quantite, 0)
            ELSE 0
        END
    )::NUMERIC, 2) AS volume_utilise,

    -- Volume restant estimé
    ROUND(GREATEST(
        c.volumeMaximal - SUM(
            CASE
                WHEN p.type = 'materiel' THEN COALESCE(pm.volume, 0) * COALESCE(s.quantite, 0)
                ELSE 0
            END
        ), 0
    )::NUMERIC, 2) AS volume_restant,

    -- ✅ Taux d'occupation basé sur QUANTITÉ / CAPACITÉ_MAX
    ROUND(LEAST(
        CASE
            WHEN c.capacite_max > 0 THEN
                COALESCE(SUM(s.quantite), 0)::NUMERIC / c.capacite_max * 100
            ELSE 0
        END, 100
    )::NUMERIC, 2) AS taux_occupation

FROM
    CELLULE c
    JOIN COMPOSER_ENTREPOT ce ON ce.idCellule = c.idCellule
    JOIN ENTREPOT e ON ce.idEntrepot = e.idEntrepot
    LEFT JOIN STOCKER s ON s.idCellule = c.idCellule
    LEFT JOIN LOT l ON s.idLot = l.idLot
    LEFT JOIN PRODUIT p ON l.idProduit = p.idProduit
    LEFT JOIN PRODUIT_MATERIEL pm ON pm.idProduit = p.idProduit

GROUP BY
    c.idCellule,
    c.reference,
    e.idEntrepot,
    e.nom,
    c.capacite_max,
    c.volumeMaximal,
    c.statut;

-- Vue de tous les colis et leur etat
CREATE OR REPLACE VIEW vue_colis_etat AS
SELECT
    c.idColis,
    c.reference,
    c.dateCreation,
    c.statut,
    be.reference AS bon_expedition,
    br.reference AS bon_reception,
    COUNT(DISTINCT ct.idLot) AS nb_lots,
    COALESCE(SUM(ct.quantite), 0) AS quantite_totale
FROM COLIS c
LEFT JOIN CONTENIR ct ON c.idColis = ct.idColis
LEFT JOIN EXPEDIER_COLIS ec ON c.idColis = ec.idColis
LEFT JOIN BON_EXPEDITION be ON ec.idBon = be.idBon
LEFT JOIN RECEVOIR_COLIS rc ON c.idColis = rc.idColis
LEFT JOIN BON_RECEPTION br ON rc.idBon = br.idBon
GROUP BY c.idColis, c.reference, c.dateCreation, c.statut, be.reference, br.reference;

-- Vue produits expirant bientot
CREATE OR REPLACE FUNCTION produits_expirant_bientot(p_jours_avant INTEGER)
RETURNS TABLE (
    idProduit dom_id,
    reference dom_reference,
    nom dom_nom,
    date_expiration DATE,
    jours_restants INTEGER,
    quantite_disponible INTEGER,
    emplacement dom_reference
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.idProduit,
        p.reference,
        p.nom,
        l.dateExpiration::DATE,
        (l.dateExpiration - CURRENT_DATE)::INTEGER,
        COALESCE(s.quantite, 0),
        c.reference
    FROM PRODUIT p
    JOIN LOT l ON l.idProduit = p.idProduit
    JOIN STOCKER s ON s.idLot = l.idLot
    JOIN CELLULE c ON c.idCellule = s.idCellule
    WHERE l.dateExpiration IS NOT NULL
    AND l.dateExpiration BETWEEN CURRENT_DATE AND CURRENT_DATE + p_jours_avant * INTERVAL '1 day'
    ORDER BY l.dateExpiration;
END;
$$;
-- Vue mouvements de produits
CREATE OR REPLACE FUNCTION mouvements_produit(p_idProduit INTEGER)
RETURNS TABLE(
    date_mouvement DATE,
    type TEXT,
    quantite INTEGER,
    numero_lot TEXT,
    cellule TEXT,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        CURRENT_DATE,
        'reception',
        s.quantite,
        l.numeroLot,
        c.reference,
        'Réception en cellule'
    FROM STOCKER s
    JOIN LOT l ON s.idLot = l.idLot
    JOIN CELLULE c ON s.idCellule = c.idCellule
    WHERE l.idProduit = p_idProduit;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- TRIGGERS DE COHERENCE METIER
-- =============================================

-- Quantité lot
CREATE OR REPLACE FUNCTION trg_check_quantite_lot() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantiteDisponible < 0 THEN
        RAISE EXCEPTION 'Quantité disponible ne peut être négative';
    END IF;
    IF NEW.quantiteDisponible > NEW.quantiteInitiale THEN
        RAISE EXCEPTION 'Quantité disponible dépasse la quantité initiale';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_quantite_lot
BEFORE INSERT OR UPDATE ON LOT
FOR EACH ROW EXECUTE FUNCTION trg_check_quantite_lot();

-- Contrôle des dates
CREATE OR REPLACE FUNCTION trg_check_dates_expedition()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.dateExpeditionPrevue < NEW.dateCreation THEN
        RAISE EXCEPTION 'Date prévue < date création';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_dates_expedition
BEFORE INSERT OR UPDATE ON BON_EXPEDITION
FOR EACH ROW EXECUTE FUNCTION trg_check_dates_expedition();

-- =============================================
-- FONCTIONS D'APPLICATION
-- =============================================

-- Annuler un colis
CREATE OR REPLACE FUNCTION annuler_colis(p_idColis INT) RETURNS VOID AS $$
BEGIN
    DELETE FROM CONTENIR WHERE idColis = p_idColis;
    DELETE FROM EXPEDIER_COLIS WHERE idColis = p_idColis;
    DELETE FROM UTILISER_EMBALLAGE WHERE idColis = p_idColis;
    DELETE FROM COLIS WHERE idColis = p_idColis;
END;
$$ LANGUAGE plpgsql;

-- Générer un numéro automatique de bon
ALTER TABLE BON_EXPEDITION ALTER COLUMN idBon SET DEFAULT nextval('bon_expedition_seq');
ALTER TABLE BON_RECEPTION ALTER COLUMN idBon SET DEFAULT nextval('bon_reception_seq');

-- Générer un numéro de colis
CREATE SEQUENCE IF NOT EXISTS colis_seq START 1;
ALTER TABLE COLIS ALTER COLUMN idColis SET DEFAULT nextval('colis_seq');
-- Création de la séquence pour les identifiants de BON_EXPEDITION
CREATE SEQUENCE IF NOT EXISTS bon_expedition_seq
START WITH 1
INCREMENT BY 1
CACHE 10;

-- Appliquer cette séquence à la colonne idBon 
ALTER TABLE bon_expedition
ALTER COLUMN idBon SET DEFAULT nextval('bon_expedition_seq');

-- Création de la séquence pour les identifiants de BON_RECEPTION
CREATE SEQUENCE IF NOT EXISTS bon_reception_seq
START WITH 1
INCREMENT BY 1
CACHE 10;

--Création de la séquence pour la cellule
CREATE SEQUENCE cellule_seq;
ALTER TABLE cellule
ALTER COLUMN idcellule SET DEFAULT nextval('cellule_seq');
-- Appliquer cette séquence à la colonne idBon 
ALTER TABLE bon_reception
ALTER COLUMN idBon SET DEFAULT nextval('bon_reception_seq');

-- =============================================
-- FIN DU SCRIPT SGE_inv.sql
-- =============================================
