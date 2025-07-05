-- =============================================
-- SGE_tra.sql
-- Routines transactionnelles & métiers
-- Système de Gestion d’Entrepôt (SGE)
-- =============================================

-- Activer les extensions utiles
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ===============================
-- SEQUENCES PAR DEFAUT
-- ===============================

-- Appliquer les séquences automatiques
ALTER TABLE produit ALTER COLUMN idProduit SET DEFAULT nextval('produit_seq');
ALTER TABLE rapport_exception ALTER COLUMN idRapport SET DEFAULT nextval('rapport_exception_seq');
ALTER TABLE bon_expedition ALTER COLUMN idBon SET DEFAULT nextval('bon_expedition_seq');
ALTER TABLE bon_reception ALTER COLUMN idBon SET DEFAULT nextval('bon_reception_seq');
ALTER TABLE colis ALTER COLUMN idColis SET DEFAULT nextval('colis_seq');
ALTER TABLE lot ALTER COLUMN idLot SET DEFAULT nextval('lot_seq');

-- Unicité rôle-individu dans l'organisation
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'affecter_role' 
        AND constraint_type = 'UNIQUE'
    ) THEN
        ALTER TABLE affecter_role 
        ADD CONSTRAINT unique_individu_role 
        UNIQUE(idIndividu, idOrganisation, idRole);
    END IF;
END $$;

-- ===============================
-- AJOUT D’UN COLIS POUR RÉCEPTION
-- ===============================
CREATE OR REPLACE FUNCTION ajouter_colis_reception(
    p_id_bon dom_id,
    p_reference dom_reference,
    p_statut dom_statut
) RETURNS dom_id AS $$
DECLARE
    new_colis_id dom_id;
BEGIN
    INSERT INTO COLIS(reference, dateCreation, statut)
    VALUES (p_reference, CURRENT_DATE, p_statut)
    RETURNING idColis INTO new_colis_id;

    INSERT INTO RECEVOIR_COLIS(idBon, idColis)
    VALUES (p_id_bon, new_colis_id);

    RETURN new_colis_id;
END;
$$ LANGUAGE plpgsql;

-- ===============================
-- RÉCEPTIONNER UN LOT
-- ===============================
CREATE OR REPLACE FUNCTION receptionner_lot(
    p_id_bon dom_id,
    p_reference_lot dom_reference,
    p_id_produit dom_id,
    p_quantite dom_quantite,
    p_date_production dom_date,
    p_date_expiration dom_date,
    p_id_cellule dom_id
) RETURNS dom_id AS $$
DECLARE
    v_id_lot dom_id;
    v_id_colis dom_id;
BEGIN
    -- Vérifier que le produit existe
    IF NOT EXISTS (SELECT 1 FROM PRODUIT WHERE idProduit = p_id_produit) THEN
        RAISE EXCEPTION 'Produit avec ID % introuvable', p_id_produit;
    END IF;

    -- Vérifier que la cellule existe
    IF NOT EXISTS (SELECT 1 FROM CELLULE WHERE idCellule = p_id_cellule) THEN
        RAISE EXCEPTION 'Cellule avec ID % introuvable', p_id_cellule;
    END IF;

    -- Création du lot
    INSERT INTO LOT(
        numeroLot, 
        quantiteInitiale, 
        quantiteDisponible, 
        dateProduction, 
        dateExpiration, 
        statut, 
        idProduit
    ) VALUES (
        p_reference_lot, 
        p_quantite, 
        p_quantite, 
        p_date_production, 
        p_date_expiration, 
        'actif', 
        p_id_produit
    ) 
    RETURNING idLot INTO v_id_lot;

    -- Création d'un colis
    v_id_colis := ajouter_colis_reception(
        p_id_bon, 
        'REC-' || p_reference_lot, 
        'termine'
    );

    -- Lien entre colis et lot
    INSERT INTO CONTENIR(idColis, idLot, quantite)
    VALUES (v_id_colis, v_id_lot, p_quantite);

    -- Stockage
    INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite)
    VALUES (v_id_lot, p_id_cellule, CURRENT_DATE, p_quantite);

    -- Vérifier si tous les colis sont reçus
    PERFORM 1 FROM RECEVOIR_COLIS rc
    JOIN COLIS c ON rc.idColis = c.idColis
    WHERE rc.idBon = p_id_bon AND c.statut = 'en_attente';

    IF NOT FOUND THEN
        UPDATE BON_RECEPTION SET statut = 'termine' WHERE idBon = p_id_bon;
    END IF;

    RETURN v_id_lot;
END;
$$ LANGUAGE plpgsql;

-- ===============================
-- PRÉPARER UNE EXPÉDITION
-- ===============================
CREATE OR REPLACE FUNCTION preparer_expedition(
    p_id_bon dom_id,
    p_id_produit dom_id,
    p_quantite dom_quantite
) RETURNS dom_id AS $$
DECLARE
    v_id_colis dom_id;
    v_quantite_restante dom_quantite := p_quantite;
    v_lot RECORD;
BEGIN
    -- Vérifie que le bon d’expédition existe
    IF NOT EXISTS (
        SELECT 1 FROM BON_EXPEDITION WHERE idBon = p_id_bon
    ) THEN
        RAISE EXCEPTION 'Bon d''expédition avec ID % introuvable', p_id_bon;
    END IF;

    -- Vérifie que le produit existe
    IF NOT EXISTS (
        SELECT 1 FROM PRODUIT WHERE idProduit = p_id_produit
    ) THEN
        RAISE EXCEPTION 'Produit avec ID % introuvable', p_id_produit;
    END IF;

    -- Création du colis
    INSERT INTO COLIS(reference, dateCreation, statut)
    VALUES (
        'EXP-' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISS'),
        CURRENT_DATE,
        'en_preparation'
    )
    RETURNING idColis INTO v_id_colis;

    -- Lier au bon
    INSERT INTO EXPEDIER_COLIS(idBon, idColis)
    VALUES (p_id_bon, v_id_colis);

    -- Boucle FIFO sur les lots disponibles
    FOR v_lot IN
        SELECT idLot, quantiteDisponible
        FROM LOT
        WHERE idProduit = p_id_produit AND quantiteDisponible > 0
        ORDER BY COALESCE(dateExpiration, CURRENT_DATE + INTERVAL '1000 days')
    LOOP
        EXIT WHEN v_quantite_restante <= 0;

        IF v_lot.quantiteDisponible >= v_quantite_restante THEN
            INSERT INTO CONTENIR(idColis, idLot, quantite)
            VALUES (v_id_colis, v_lot.idLot, v_quantite_restante);

            UPDATE LOT
            SET quantiteDisponible = quantiteDisponible - v_quantite_restante
            WHERE idLot = v_lot.idLot;

            UPDATE STOCKER
            SET quantite = quantite - v_quantite_restante
            WHERE idLot = v_lot.idLot;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Stocker non trouvé pour lot %, impossible de décrémenter.', v_lot.idLot;
            END IF;

            v_quantite_restante := 0;

        ELSE
            INSERT INTO CONTENIR(idColis, idLot, quantite)
            VALUES (v_id_colis, v_lot.idLot, v_lot.quantiteDisponible);

            UPDATE LOT
            SET quantiteDisponible = 0
            WHERE idLot = v_lot.idLot;

            UPDATE STOCKER
            SET quantite = quantite - v_lot.quantiteDisponible
            WHERE idLot = v_lot.idLot;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Stocker non trouvé pour lot %, impossible de décrémenter.', v_lot.idLot;
            END IF;

            v_quantite_restante := v_quantite_restante - v_lot.quantiteDisponible;
        END IF;
    END LOOP;

    -- Stock insuffisant → rollback logique
    IF v_quantite_restante > 0 THEN
        DELETE FROM CONTENIR WHERE idColis = v_id_colis;
        DELETE FROM EXPEDIER_COLIS WHERE idColis = v_id_colis;
        DELETE FROM COLIS WHERE idColis = v_id_colis;

        INSERT INTO RAPPORT_EXCEPTION(
            typeRapport, dateGeneration, description, idBonExpedition
        ) VALUES (
            'rupture_stock',
            CURRENT_DATE,
            'Stock insuffisant pour produit ' || p_id_produit || ', manque: ' || v_quantite_restante,
            p_id_bon
        );

        RAISE EXCEPTION 'Stock insuffisant pour produit %, manque: %',
            p_id_produit, v_quantite_restante;
    END IF;

    -- Marquer le colis comme prêt
    UPDATE COLIS
    SET statut = 'pret_a_expedier'
    WHERE idColis = v_id_colis
      AND statut = 'en_preparation';

    -- Vérifier si le bon est maintenant complet
    UPDATE BON_EXPEDITION
    SET statut = 'pret_a_expedier'
    WHERE idBon = p_id_bon
      AND NOT EXISTS (
        SELECT 1
        FROM COMPOSER_EXPEDITION ce
        LEFT JOIN (
            SELECT
                l.idProduit,
                SUM(ct.quantite) AS qte_affectee
            FROM EXPEDIER_COLIS ec
            JOIN COLIS c ON ec.idColis = c.idColis
            JOIN CONTENIR ct ON c.idColis = ct.idColis
            JOIN LOT l ON ct.idLot = l.idLot
            WHERE ec.idBon = p_id_bon
            GROUP BY l.idProduit
        ) affect ON ce.idProduit = affect.idProduit
        WHERE ce.idBon = p_id_bon
          AND (affect.qte_affectee IS NULL OR affect.qte_affectee < ce.quantite)
    );

    RETURN v_id_colis;
END;
$$ LANGUAGE plpgsql;


-- ===============================
-- ANNULER UN COLIS
-- ===============================
DROP FUNCTION annuler_colis(integer)

CREATE OR REPLACE FUNCTION annuler_colis(p_id_colis INTEGER) 
RETURNS VOID AS $$
DECLARE
    r RECORD;
BEGIN
    -- Vérifier que le colis existe
    IF NOT EXISTS (SELECT 1 FROM COLIS WHERE idColis = p_id_colis) THEN
        RAISE EXCEPTION 'Colis avec ID % introuvable', p_id_colis;
    END IF;

    -- Restaurer les quantités des lots
    FOR r IN 
        SELECT idLot, quantite 
        FROM CONTENIR 
        WHERE idColis = p_id_colis
    LOOP
        UPDATE LOT 
        SET quantiteDisponible = quantiteDisponible + r.quantite 
        WHERE idLot = r.idLot;
    END LOOP;

    -- Supprimer les liaisons
    DELETE FROM CONTENIR WHERE idColis = p_id_colis;
    DELETE FROM EXPEDIER_COLIS WHERE idColis = p_id_colis;

    -- Mettre à jour le statut
    UPDATE COLIS 
    SET statut = 'annule' 
    WHERE idColis = p_id_colis;
END;
$$ LANGUAGE plpgsql;

-- ===============================
-- DÉPLACER UN LOT
-- ===============================
CREATE OR REPLACE FUNCTION deplacer_lot(
    p_id_lot INTEGER,
    p_cellule_source INTEGER,
    p_cellule_dest INTEGER,
    p_quantite INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    q_source INTEGER;
BEGIN
    -- Vérifier que le lot existe
    IF NOT EXISTS (SELECT 1 FROM LOT WHERE idLot = p_id_lot) THEN
        RAISE EXCEPTION 'Lot avec ID % introuvable', p_id_lot;
    END IF;

    -- Vérifier que les cellules existent
    IF NOT EXISTS (SELECT 1 FROM CELLULE WHERE idCellule = p_cellule_source) THEN
        RAISE EXCEPTION 'Cellule source avec ID % introuvable', p_cellule_source;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM CELLULE WHERE idCellule = p_cellule_dest) THEN
        RAISE EXCEPTION 'Cellule destination avec ID % introuvable', p_cellule_dest;
    END IF;

    -- Vérifier la quantité disponible
    SELECT quantite INTO q_source 
    FROM STOCKER 
    WHERE idLot = p_id_lot AND idCellule = p_cellule_source;

    IF q_source IS NULL OR q_source < p_quantite THEN
        RAISE EXCEPTION 'Quantité insuffisante dans la cellule source';
    END IF;

    -- Mise à jour des cellules
    UPDATE STOCKER 
    SET quantite = quantite - p_quantite 
    WHERE idLot = p_id_lot AND idCellule = p_cellule_source;

    -- Supprimer si quantité = 0
    DELETE FROM STOCKER 
    WHERE idLot = p_id_lot AND idCellule = p_cellule_source AND quantite = 0;

    -- Ajouter à la destination
    INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite)
    VALUES (p_id_lot, p_cellule_dest, CURRENT_DATE, p_quantite)
    ON CONFLICT (idLot, idCellule) 
    DO UPDATE SET quantite = STOCKER.quantite + EXCLUDED.quantite;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ===============================
-- AJUSTER L’INVENTAIRE PHYSIQUE
-- ===============================
CREATE OR REPLACE FUNCTION ajuster_inventaire(
    p_id_lot INTEGER,
    p_id_cellule INTEGER,
    p_nouvelle_quantite INTEGER,
    p_commentaire TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    q_actuelle INTEGER;
    diff INTEGER;
BEGIN
    -- Vérifier que le lot existe
    IF NOT EXISTS (SELECT 1 FROM LOT WHERE idLot = p_id_lot) THEN
        RAISE EXCEPTION 'Lot avec ID % introuvable', p_id_lot;
    END IF;

    -- Vérifier que la cellule existe
    IF NOT EXISTS (SELECT 1 FROM CELLULE WHERE idCellule = p_id_cellule) THEN
        RAISE EXCEPTION 'Cellule avec ID % introuvable', p_id_cellule;
    END IF;

    -- Calculer la différence
    SELECT COALESCE(quantite, 0) INTO q_actuelle 
    FROM STOCKER 
    WHERE idLot = p_id_lot AND idCellule = p_id_cellule;

    diff := p_nouvelle_quantite - q_actuelle;

    -- Mise à jour du stockage
    IF p_nouvelle_quantite <= 0 THEN
        DELETE FROM STOCKER 
        WHERE idLot = p_id_lot AND idCellule = p_id_cellule;
    ELSE
        INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite)
        VALUES (p_id_lot, p_id_cellule, CURRENT_DATE, p_nouvelle_quantite)
        ON CONFLICT (idLot, idCellule) 
        DO UPDATE SET quantite = EXCLUDED.quantite;
    END IF;

    -- Mise à jour du lot
    UPDATE LOT 
    SET quantiteDisponible = quantiteDisponible + diff 
    WHERE idLot = p_id_lot;

    -- Création d'un rapport d'ajustement
    INSERT INTO RAPPORT_EXCEPTION(
        typeRapport, 
        dateGeneration, 
        description
    ) VALUES (
        'ajustement', 
        CURRENT_DATE, 
        'Ajustement de ' || diff || ' unités sur le lot ' || p_id_lot || 
        ' (commentaire: ' || p_commentaire || ')'
    );

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS preparer_colis(INTEGER, INTEGER, INTEGER);


--preparer_colis
CREATE OR REPLACE FUNCTION preparer_colis(
    p_idBonExp INTEGER,
    p_idProduit INTEGER,
    p_quantite INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_idColis INTEGER;
    v_referenceColis TEXT;
    v_quantite_restante INTEGER := p_quantite;
    v_lot RECORD;
    v_stock_disponible INTEGER;
BEGIN
    SELECT COALESCE(SUM(quantiteDisponible), 0)
    INTO v_stock_disponible
    FROM LOT
    WHERE idProduit = p_idProduit;

    IF v_stock_disponible < p_quantite THEN
        RAISE EXCEPTION 'Stock insuffisant : demandé %, disponible %', p_quantite, v_stock_disponible;
    END IF;

    v_referenceColis := 'COL-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || LPAD(NEXTVAL('colis_seq')::TEXT, 4, '0');

    INSERT INTO COLIS(reference, dateCreation, statut)
    VALUES (v_referenceColis, CURRENT_DATE, 'en_preparation')
    RETURNING idColis INTO v_idColis;

    INSERT INTO EXPEDIER_COLIS(idBon, idColis)
    VALUES (p_idBonExp, v_idColis);

    FOR v_lot IN
        SELECT idLot, quantiteDisponible
        FROM LOT
        WHERE idProduit = p_idProduit AND quantiteDisponible > 0
        ORDER BY COALESCE(dateExpiration, CURRENT_DATE + INTERVAL '9999 days')
    LOOP
        EXIT WHEN v_quantite_restante <= 0;

        IF v_lot.quantiteDisponible >= v_quantite_restante THEN
            INSERT INTO CONTENIR(idColis, idLot, quantite)
            VALUES (v_idColis, v_lot.idLot, v_quantite_restante);

            UPDATE LOT
            SET quantiteDisponible = quantiteDisponible - v_quantite_restante
            WHERE idLot = v_lot.idLot;

            v_quantite_restante := 0;
        ELSE
            INSERT INTO CONTENIR(idColis, idLot, quantite)
            VALUES (v_idColis, v_lot.idLot, v_lot.quantiteDisponible);

            UPDATE LOT
            SET quantiteDisponible = 0
            WHERE idLot = v_lot.idLot;

            v_quantite_restante := v_quantite_restante - v_lot.quantiteDisponible;
        END IF;
    END LOOP;

    IF v_quantite_restante > 0 THEN
        RAISE EXCEPTION 'Erreur : quantité restante après traitement > 0';
    END IF;

    UPDATE COLIS
    SET statut = 'pret_a_expedier'
    WHERE idColis = v_idColis;

    RETURN v_idColis;
END;
$$ LANGUAGE plpgsql;

-- Séquence pour idProduit si elle n'existe pas
CREATE SEQUENCE IF NOT EXISTS produit_seq
    START WITH 1
    INCREMENT BY 1
    CACHE 10;
ALTER TABLE PRODUIT
ALTER COLUMN idProduit SET DEFAULT nextval('produit_seq');

