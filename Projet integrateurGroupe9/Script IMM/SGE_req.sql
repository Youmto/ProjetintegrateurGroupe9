-- =============================================
-- SGE_req.sql
-- Routines pour les requêtes fréquentes
-- =============================================

-- Obtenir l'inventaire d'un produit spécifique
CREATE OR REPLACE FUNCTION obtenir_inventaire_produit(
    p_id_produit INTEGER
) RETURNS TABLE (
    idProduit INTEGER,
    reference VARCHAR(50),
    nom VARCHAR(100),
    quantite_disponible INTEGER,
    emplacements TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.idProduit,
        p.reference,
        p.nom,
        COALESCE(SUM(s.quantite), 0)::INTEGER AS quantite_disponible,
        STRING_AGG(DISTINCT c.reference, ', ') AS emplacements
    FROM PRODUIT p
    LEFT JOIN LOT l ON p.idProduit = l.idProduit
    LEFT JOIN STOCKER s ON l.idLot = s.idLot
    LEFT JOIN CELLULE c ON s.idCellule = c.idCellule
    WHERE p.idProduit = p_id_produit
    GROUP BY p.idProduit, p.reference, p.nom;
END;
$$ LANGUAGE plpgsql;

-- Trouver les produits en rupture de stock
CREATE OR REPLACE FUNCTION produits_en_rupture()
RETURNS TABLE (
    idProduit INTEGER,
    reference VARCHAR(50),
    nom VARCHAR(100),
    quantite_disponible INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.idProduit,
        p.reference,
        p.nom,
        COALESCE(SUM(i.quantiteDisponible), 0)::INTEGER AS quantite_disponible
    FROM PRODUIT p
    LEFT JOIN INVENTAIRE i ON p.idProduit = i.idProduit
    GROUP BY p.idProduit, p.reference, p.nom
    HAVING COALESCE(SUM(i.quantiteDisponible), 0) = 0;
END;
$$ LANGUAGE plpgsql;

-- Lister les colis prêts pour l'expédition
CREATE OR REPLACE FUNCTION colis_pret_expedition()
RETURNS TABLE (
    idColis INTEGER,
    reference VARCHAR(50),
    date_creation DATE,
    bon_expedition VARCHAR(50),
    date_expedition_prevue DATE,
    nb_lots INTEGER,
    quantite_totale INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.idColis,
        c.reference,
        c.dateCreation,
        be.reference,
        be.dateExpeditionPrevue,
        COUNT(ct.idLot)::INTEGER,
        SUM(ct.quantite)::INTEGER
    FROM COLIS c
    JOIN EXPEDIER_COLIS ec ON c.idColis = ec.idColis
    JOIN BON_EXPEDITION be ON ec.idBon = be.idBon
    LEFT JOIN CONTENIR ct ON c.idColis = ct.idColis
    WHERE c.statut = 'pret_a_expedier'
    GROUP BY c.idColis, c.reference, c.dateCreation, be.reference, be.dateExpeditionPrevue;
END;
$$ LANGUAGE plpgsql;

-- Trouver les produits expirant bientôt
CREATE OR REPLACE FUNCTION produits_expirant_bientot(
    p_jours_avant INTEGER
) RETURNS TABLE (
    idProduit INTEGER,
    reference VARCHAR(50),
    nom VARCHAR(100),
    date_expiration DATE,
    jours_restants INTEGER,
    quantite_disponible INTEGER,
    emplacement VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.idProduit,
        p.reference,
        p.nom,
        l.dateExpiration,
        (l.dateExpiration - CURRENT_DATE)::INTEGER,
        s.quantite,
        c.reference
    FROM PRODUIT p
    JOIN LOT l ON p.idProduit = l.idProduit
    JOIN STOCKER s ON l.idLot = s.idLot
    JOIN CELLULE c ON s.idCellule = c.idCellule
    WHERE l.dateExpiration IS NOT NULL
    AND l.dateExpiration BETWEEN CURRENT_DATE AND (CURRENT_DATE + p_jours_avant * INTERVAL '1 day')
    ORDER BY l.dateExpiration;
END;
$$ LANGUAGE plpgsql;

-- Calculer l'occupation des cellules
CREATE OR REPLACE FUNCTION occupation_cellules()
RETURNS TABLE (
    idCellule INTEGER,
    reference VARCHAR(50),
    entrepot VARCHAR(100),
    volume_utilise FLOAT,
    volume_maximal FLOAT,
    pourcentage_occupation FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.idCellule,
        c.reference,
        e.nom,
        COALESCE(SUM(p.volume * s.quantite), 0)::FLOAT,
        c.volumeMaximal,
        (COALESCE(SUM(p.volume * s.quantite), 0) / c.volumeMaximal * 100)::FLOAT
    FROM CELLULE c
    JOIN COMPOSER_ENTREPOT ce ON c.idCellule = ce.idCellule
    JOIN ENTREPOT e ON ce.idEntrepot = e.idEntrepot
    LEFT JOIN STOCKER s ON c.idCellule = s.idCellule
    LEFT JOIN LOT l ON s.idLot = l.idLot
    LEFT JOIN PRODUIT_MATERIEL p ON l.idProduit = p.idProduit
    GROUP BY c.idCellule, c.reference, e.nom, c.volumeMaximal
    ORDER BY e.nom, c.reference;
END;
$$ LANGUAGE plpgsql;
-- Historique des réceptions et expéditions d’un produit
CREATE OR REPLACE FUNCTION mouvements_produit(p_id_produit INTEGER)
RETURNS TABLE (
    type_mouvement TEXT,
    reference_bon VARCHAR(50),
    date_mouvement DATE,
    quantite INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'réception',
        br.reference,
        br.dateCreation,
        SUM(ct.quantite)
    FROM BON_RECEPTION br
    JOIN RECEVOIR_COLIS rc ON br.idBon = rc.idBon
    JOIN COLIS c ON rc.idColis = c.idColis
    JOIN CONTENIR ct ON c.idColis = ct.idColis
    JOIN LOT l ON ct.idLot = l.idLot
    WHERE l.idProduit = p_id_produit
    GROUP BY br.reference, br.dateCreation

    UNION ALL

    SELECT 
        'expédition',
        be.reference,
        be.dateCreation,
        SUM(ct.quantite)
    FROM BON_EXPEDITION be
    JOIN EXPEDIER_COLIS ec ON be.idBon = ec.idBon
    JOIN COLIS c ON ec.idColis = c.idColis
    JOIN CONTENIR ct ON c.idColis = ct.idColis
    JOIN LOT l ON ct.idLot = l.idLot
    WHERE l.idProduit = p_id_produit
    GROUP BY be.reference, be.dateCreation;
END;
$$ LANGUAGE plpgsql;

-- Prodiut par entrepot

CREATE OR REPLACE FUNCTION produits_par_entrepot(p_id_entrepot INTEGER)
RETURNS TABLE (
    produit_ref VARCHAR(50),
    nom_produit VARCHAR(100),
    quantite_totale INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.reference,
        p.nom,
        SUM(s.quantite)
    FROM STOCKER s
    JOIN LOT l ON s.idLot = l.idLot
    JOIN PRODUIT p ON l.idProduit = p.idProduit
    JOIN CELLULE c ON s.idCellule = c.idCellule
    JOIN COMPOSER_ENTREPOT ce ON c.idCellule = ce.idCellule
    WHERE ce.idEntrepot = p_id_entrepot
    GROUP BY p.reference, p.nom;
END;
$$ LANGUAGE plpgsql;

-- Produit jamais stocker
CREATE OR REPLACE FUNCTION produits_jamais_stockes()
RETURNS TABLE (
    idProduit INTEGER,
    reference VARCHAR(50),
    nom VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.idProduit, p.reference, p.nom
    FROM PRODUIT p
    LEFT JOIN LOT l ON p.idProduit = l.idProduit
    LEFT JOIN STOCKER s ON l.idLot = s.idLot
    WHERE s.idLot IS NULL;
END;
$$ LANGUAGE plpgsql;

--Emplacement vide disponible 

CREATE OR REPLACE FUNCTION cellules_vides()
RETURNS TABLE (
    idCellule INTEGER,
    reference VARCHAR(50),
    entrepot VARCHAR(100),
    volume_maximal FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.idCellule, c.reference, e.nom, c.volumeMaximal
    FROM CELLULE c
    JOIN COMPOSER_ENTREPOT ce ON c.idCellule = ce.idCellule
    JOIN ENTREPOT e ON ce.idEntrepot = e.idEntrepot
    LEFT JOIN STOCKER s ON c.idCellule = s.idCellule
    WHERE s.idLot IS NULL;
END;
$$ LANGUAGE plpgsql;
