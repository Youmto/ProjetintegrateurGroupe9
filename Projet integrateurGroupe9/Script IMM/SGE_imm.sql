-- =============================================
-- SGE_imm.sql
-- Interface Métier / IHM – Vues, Routines et Triggers
-- =============================================

SET search_path TO public;

-- =======================
-- VUES MÉTIER POUR L'IHM
-- =======================

-- Vue : Produits avec disponibilité et type
CREATE OR REPLACE VIEW ihm_vue_produits_disponibles AS
SELECT
    p.idProduit,
    p.reference,
    p.nom,
    p.type,
    COALESCE(SUM(s.quantite), 0) AS quantiteDisponible,
    p.estMaterielEmballage,
    STRING_AGG(DISTINCT c.reference, ', ' ORDER BY c.reference) AS emplacements
FROM 
    PRODUIT p
    LEFT JOIN LOT l ON l.idProduit = p.idProduit
    LEFT JOIN STOCKER s ON s.idLot = l.idLot
    LEFT JOIN CELLULE c ON c.idCellule = s.idCellule
GROUP BY
    p.idProduit, p.reference, p.nom, p.type, p.estMaterielEmballage;

-- Vue : Colis prêts à être expédiés
CREATE OR REPLACE VIEW ihm_vue_colis_prets AS
SELECT
    c.idColis,
    c.reference,
    c.dateCreation,
    c.statut,
    be.reference AS bonExpedition,
    be.dateExpeditionPrevue,
    COUNT(DISTINCT ct.idLot) AS nbLots,
    COALESCE(SUM(ct.quantite), 0) AS quantiteTotale,
    STRING_AGG(DISTINCT p.nom, ', ') AS produits
FROM 
    COLIS c
    JOIN EXPEDIER_COLIS ec ON ec.idColis = c.idColis
    JOIN BON_EXPEDITION be ON be.idBon = ec.idBon
    LEFT JOIN CONTENIR ct ON ct.idColis = c.idColis
    LEFT JOIN LOT l ON l.idLot = ct.idLot
    LEFT JOIN PRODUIT p ON p.idProduit = l.idProduit
WHERE 
    c.statut = 'pret_a_expedier'
GROUP BY
    c.idColis, c.reference, c.dateCreation, c.statut, 
    be.reference, be.dateExpeditionPrevue;

-- Vue : Bons d'expédition en attente ou en cours
CREATE OR REPLACE VIEW ihm_vue_bons_expedition AS
SELECT
    be.idBon,
    be.reference,
    be.dateCreation,
    be.dateExpeditionPrevue,
    be.priorite,
    be.statut,
    COUNT(DISTINCT ec.idColis) AS nbColis,
    COALESCE(SUM(ct.quantite), 0) AS quantiteTotale,
    STRING_AGG(DISTINCT p.nom, ', ') AS produits
FROM 
    BON_EXPEDITION be
    LEFT JOIN EXPEDIER_COLIS ec ON ec.idBon = be.idBon
    LEFT JOIN CONTENIR ct ON ct.idColis = ec.idColis
    LEFT JOIN LOT l ON l.idLot = ct.idLot
    LEFT JOIN PRODUIT p ON p.idProduit = l.idProduit
GROUP BY
    be.idBon, be.reference, be.dateCreation, 
    be.dateExpeditionPrevue, be.priorite, be.statut;

-- Vue : Mouvements récents (30 derniers jours)
CREATE OR REPLACE VIEW ihm_vue_mouvements_recents AS
SELECT
    m.type,
    m.date,
    m.produit,
    m.lot,
    m.quantite,
    m.cellule,
    m.bon,
    m.id_produit
FROM (
    SELECT
        'Entrée'::TEXT AS type,
        br.dateReceptionPrevue AS date,
        p.nom AS produit,
        l.numeroLot AS lot,
        ct.quantite,
        c.reference AS cellule,
        br.reference AS bon,
        p.idProduit AS id_produit
    FROM 
        BON_RECEPTION br
        JOIN RECEVOIR_COLIS rc ON rc.idBon = br.idBon
        JOIN COLIS co ON co.idColis = rc.idColis
        JOIN CONTENIR ct ON ct.idColis = co.idColis
        JOIN LOT l ON l.idLot = ct.idLot
        JOIN PRODUIT p ON p.idProduit = l.idProduit
        JOIN STOCKER s ON s.idLot = l.idLot
        JOIN CELLULE c ON c.idCellule = s.idCellule
    WHERE 
        br.dateReceptionPrevue >= CURRENT_DATE - INTERVAL '30 days'
    
    UNION ALL
    
    SELECT
        'Sortie'::TEXT AS type,
        be.dateExpeditionPrevue AS date,
        p.nom AS produit,
        l.numeroLot AS lot,
        -ct.quantite AS quantite,
        c.reference AS cellule,
        be.reference AS bon,
        p.idProduit AS id_produit
    FROM 
        BON_EXPEDITION be
        JOIN EXPEDIER_COLIS ec ON ec.idBon = be.idBon
        JOIN COLIS co ON co.idColis = ec.idColis
        JOIN CONTENIR ct ON ct.idColis = co.idColis
        JOIN LOT l ON l.idLot = ct.idLot
        JOIN PRODUIT p ON p.idProduit = l.idProduit
        JOIN STOCKER s ON s.idLot = l.idLot
        JOIN CELLULE c ON c.idCellule = s.idCellule
    WHERE 
        be.dateExpeditionPrevue >= CURRENT_DATE - INTERVAL '30 days'
) m
ORDER BY m.date DESC;

-- =======================
-- FONCTIONS LÉGÈRES POUR L'IHM
-- =======================

-- Obtenir le résumé d'un bon
CREATE OR REPLACE FUNCTION ihm_get_bon_resume(p_id_bon INTEGER)
RETURNS TABLE (
    idBon INTEGER,
    reference TEXT,
    statut TEXT,
    priorite TEXT,
    nbColis INTEGER,
    quantiteTotale INTEGER,
    produits TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        be.idBon,
        be.reference,
        be.statut,
        be.priorite,
        COUNT(DISTINCT ec.idColis),
        COALESCE(SUM(ct.quantite), 0),
        STRING_AGG(DISTINCT p.nom, ', ')
    FROM 
        BON_EXPEDITION be
        LEFT JOIN EXPEDIER_COLIS ec ON be.idBon = ec.idBon
        LEFT JOIN CONTENIR ct ON ec.idColis = ct.idColis
        LEFT JOIN LOT l ON l.idLot = ct.idLot
        LEFT JOIN PRODUIT p ON p.idProduit = l.idProduit
    WHERE 
        be.idBon = p_id_bon
    GROUP BY 
        be.idBon, be.reference, be.statut, be.priorite;
END;
$$ LANGUAGE plpgsql;

-- Produits d'un colis
CREATE OR REPLACE FUNCTION ihm_get_colis_contenu(p_id_colis INTEGER)
RETURNS TABLE (
    idLot INTEGER,
    lot TEXT,
    produit TEXT,
    idProduit INTEGER,
    quantite INTEGER,
    expiration DATE,
    emplacement TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        l.idLot,
        l.numeroLot,
        p.nom,
        p.idProduit,
        ct.quantite,
        l.dateExpiration,
        c.reference
    FROM 
        CONTENIR ct
        JOIN LOT l ON l.idLot = ct.idLot
        JOIN PRODUIT p ON p.idProduit = l.idProduit
        LEFT JOIN STOCKER s ON s.idLot = l.idLot
        LEFT JOIN CELLULE c ON c.idCellule = s.idCellule
    WHERE 
        ct.idColis = p_id_colis;
END;
$$ LANGUAGE plpgsql;

-- =======================
-- TRIGGERS POUR L'IHM
-- =======================

-- Mise à jour auto du statut du bon de réception à "termine"
CREATE OR REPLACE FUNCTION trg_update_statut_bon_reception()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM COLIS c 
        JOIN RECEVOIR_COLIS rc ON rc.idColis = c.idColis 
        WHERE rc.idBon = NEW.idBon AND c.statut != 'recu'
    ) THEN
        UPDATE BON_RECEPTION 
        SET statut = 'termine', dateReceptionReelle = CURRENT_DATE
        WHERE idBon = NEW.idBon;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auto_maj_bon_reception ON RECEVOIR_COLIS;
CREATE TRIGGER trg_auto_maj_bon_reception
AFTER INSERT OR UPDATE ON RECEVOIR_COLIS
FOR EACH ROW
EXECUTE FUNCTION trg_update_statut_bon_reception();

-- =======================
-- FIN DU SCRIPT
-- =======================