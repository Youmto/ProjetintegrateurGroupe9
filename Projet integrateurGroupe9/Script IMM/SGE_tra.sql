-- =============================================
-- SGE_tra.sql
-- Routines pour les opérations de mise à jour
-- ============================================
DROP FUNCTION annuler_colis(INTEGER);

-- Réceptionner un lot de produits
CREATE OR REPLACE FUNCTION receptionner_lot(
    p_id_bon INTEGER,
    p_reference_lot VARCHAR(50),
    p_id_produit INTEGER,
    p_quantite INTEGER,
    p_date_production DATE,
    p_date_expiration DATE,
    p_id_cellule INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_id_lot INTEGER;
    v_id_colis INTEGER;
BEGIN
    -- Créer le lot
    INSERT INTO LOT(numeroLot, quantiteInitiale, quantiteDisponible, dateProduction, dateExpiration, statut)
    VALUES (p_reference_lot, p_quantite, p_quantite, p_date_production, p_date_expiration, 'actif')
    RETURNING idLot INTO v_id_lot;
    
    -- Créer un colis pour la réception
    v_id_colis := ajouter_colis_reception(p_id_bon, 'REC-' || p_reference_lot, 'recu');
    
    -- Lier le lot au colis
    INSERT INTO CONTENIR(idColis, idLot, quantite)
    VALUES (v_id_colis, v_id_lot, p_quantite);
    
    -- Stocker le lot dans la cellule
    INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite)
    VALUES (v_id_lot, p_id_cellule, CURRENT_DATE, p_quantite);
    
    -- Mettre à jour le statut du bon si c'est le dernier colis
    UPDATE BON_RECEPTION
    SET statut = 'termine'
    WHERE idBon = p_id_bon
    AND NOT EXISTS (
        SELECT 1 FROM RECEVOIR_COLIS rc 
        JOIN COLIS c ON rc.idColis = c.idColis
        WHERE rc.idBon = p_id_bon AND c.statut = 'en_attente'
    );
    
    RETURN v_id_lot;
END;
$$ LANGUAGE plpgsql;

-- Préparer une expédition
CREATE OR REPLACE FUNCTION preparer_expedition(
    p_id_bon INTEGER,
    p_id_produit INTEGER,
    p_quantite INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_id_colis INTEGER;
    v_quantite_restante INTEGER := p_quantite;
    v_lot RECORD;
BEGIN
    -- Créer un nouveau colis
    INSERT INTO COLIS(reference, dateCreation, statut)
    VALUES ('EXP-' || nextval('colis_seq'), CURRENT_DATE, 'en_preparation')
    RETURNING idColis INTO v_id_colis;
    
    -- Lier le colis au bon d'expédition
    INSERT INTO EXPEDIER_COLIS(idBon, idColis)
    VALUES (p_id_bon, v_id_colis);
    
    -- Trouver les lots disponibles (FIFO par date d'expiration)
    FOR v_lot IN 
        SELECT l.idLot, l.quantiteDisponible
        FROM LOT l
        WHERE l.idProduit = p_id_produit AND l.quantiteDisponible > 0
        ORDER BY COALESCE(l.dateExpiration, '9999-12-31')
    LOOP
        IF v_quantite_restante <= 0 THEN
            EXIT;
        END IF;
        
        IF v_lot.quantiteDisponible >= v_quantite_restante THEN
            -- Prendre toute la quantité nécessaire de ce lot
            INSERT INTO CONTENIR(idColis, idLot, quantite)
            VALUES (v_id_colis, v_lot.idLot, v_quantite_restante);
            
            UPDATE LOT
            SET quantiteDisponible = quantiteDisponible - v_quantite_restante
            WHERE idLot = v_lot.idLot;
            
            -- Retirer du stockage
            UPDATE STOCKER
            SET quantite = quantite - v_quantite_restante
            WHERE idLot = v_lot.idLot;
            
            v_quantite_restante := 0;
        ELSE
            -- Prendre tout ce qu'il reste dans ce lot
            INSERT INTO CONTENIR(idColis, idLot, quantite)
            VALUES (v_id_colis, v_lot.idLot, v_lot.quantiteDisponible);
            
            UPDATE LOT
            SET quantiteDisponible = 0
            WHERE idLot = v_lot.idLot;
            
            -- Retirer du stockage
            UPDATE STOCKER
            SET quantite = quantite - v_lot.quantiteDisponible
            WHERE idLot = v_lot.idLot;
            
            v_quantite_restante := v_quantite_restante - v_lot.quantiteDisponible;
        END IF;
    END LOOP;
    
    -- Si on n'a pas pu trouver assez de stock
    IF v_quantite_restante > 0 THEN
        -- Annuler l'opération
        DELETE FROM CONTENIR WHERE idColis = v_id_colis;
        DELETE FROM EXPEDIER_COLIS WHERE idColis = v_id_colis;
        DELETE FROM COLIS WHERE idColis = v_id_colis;
        
        -- Générer un rapport d'exception
        INSERT INTO RAPPORT_EXCEPTION(typeRapport, dateGeneration, description, idBonExpedition)
        VALUES ('rupture_stock', CURRENT_DATE, 
                'Stock insuffisant pour le produit ' || p_id_produit || 
                '. Quantité manquante: ' || v_quantite_restante, 
                p_id_bon);
        
        RAISE EXCEPTION 'Stock insuffisant pour le produit %. Quantité manquante: %', 
              p_id_produit, v_quantite_restante;
    ELSE
        -- Marquer le colis comme prêt à expédier
        UPDATE COLIS
        SET statut = 'pret_a_expedier'
        WHERE idColis = v_id_colis;
        
        -- Mettre à jour le statut du bon si complet
        UPDATE BON_EXPEDITION
        SET statut = 'pret_a_expedier'
        WHERE idBon = p_id_bon
        AND NOT EXISTS (
            SELECT 1 FROM PRODUIT p
            JOIN INVENTAIRE i ON p.idProduit = i.idProduit
            WHERE i.quantiteDisponible < (
                SELECT SUM(be.quantite)
                FROM BON_EXPEDITION be
                JOIN EXPEDIER_COLIS ec ON be.idBon = ec.idBon
                JOIN COLIS c ON ec.idColis = c.idColis
                JOIN CONTENIR ct ON c.idColis = ct.idColis
                JOIN LOT l ON ct.idLot = l.idLot
                WHERE be.idBon = p_id_bon AND l.idProduit = p.idProduit
            )
        );
    END IF;
    
    RETURN v_id_colis;
END;
$$ LANGUAGE plpgsql;

-- Déplacer un lot d'une cellule à une autre
CREATE OR REPLACE FUNCTION deplacer_lot(
    p_id_lot INTEGER,
    p_id_cellule_source INTEGER,
    p_id_cellule_destination INTEGER,
    p_quantite INTEGER,
    p_id_responsable INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_quantite_disponible INTEGER;
BEGIN
    -- Vérifier la quantité disponible
    SELECT quantite INTO v_quantite_disponible
    FROM STOCKER
    WHERE idLot = p_id_lot AND idCellule = p_id_cellule_source;
    
    IF v_quantite_disponible < p_quantite THEN
        RAISE EXCEPTION 'Quantité insuffisante dans la cellule source';
    END IF;
    
    -- Réduire la quantité dans la cellule source
    UPDATE STOCKER
    SET quantite = quantite - p_quantite
    WHERE idLot = p_id_lot AND idCellule = p_id_cellule_source;
    
    -- Si la quantité devient 0, supprimer la ligne
    DELETE FROM STOCKER
    WHERE idLot = p_id_lot AND idCellule = p_id_cellule_source AND quantite = 0;
    
    -- Ajouter à la cellule destination (ou mettre à jour si existe déjà)
    INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite)
    VALUES (p_id_lot, p_id_cellule_destination, CURRENT_DATE, p_quantite)
    ON CONFLICT (idLot, idCellule) 
    DO UPDATE SET quantite = STOCKER.quantite + p_quantite;
    
    -- Enregistrer le mouvement dans un rapport
    INSERT INTO RAPPORT_EXCEPTION(
        typeRapport, 
        dateGeneration, 
        description
    )
    VALUES (
        'mouvement_stock',
        CURRENT_DATE,
        'Déplacement de ' || p_quantite || ' unités du lot ' || 
        (SELECT numeroLot FROM LOT WHERE idLot = p_id_lot) || 
        ' de la cellule ' || (SELECT reference FROM CELLULE WHERE idCellule = p_id_cellule_source) || 
        ' vers la cellule ' || (SELECT reference FROM CELLULE WHERE idCellule = p_id_cellule_destination)
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Mettre à jour l'inventaire après inventaire physique
CREATE OR REPLACE FUNCTION ajuster_inventaire(
    p_id_lot INTEGER,
    p_id_cellule INTEGER,
    p_nouvelle_quantite INTEGER,
    p_id_responsable INTEGER,
    p_commentaire TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_quantite_actuelle INTEGER;
    v_id_produit INTEGER;
    v_difference INTEGER;
BEGIN
    -- Obtenir la quantité actuelle
    SELECT COALESCE(quantite, 0) INTO v_quantite_actuelle
    FROM STOCKER
    WHERE idLot = p_id_lot AND idCellule = p_id_cellule;
    
    -- Calculer la différence
    v_difference := p_nouvelle_quantite - v_quantite_actuelle;
    
    -- Obtenir l'ID du produit
    SELECT idProduit INTO v_id_produit FROM LOT WHERE idLot = p_id_lot;
    
    -- Mettre à jour le stockage
    IF p_nouvelle_quantite <= 0 THEN
        DELETE FROM STOCKER
        WHERE idLot = p_id_lot AND idCellule = p_id_cellule;
    ELSE
        INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite)
        VALUES (p_id_lot, p_id_cellule, CURRENT_DATE, p_nouvelle_quantite)
        ON CONFLICT (idLot, idCellule) 
        DO UPDATE SET quantite = p_nouvelle_quantite;
    END IF;
    
    -- Mettre à jour le lot
    UPDATE LOT
    SET quantiteDisponible = quantiteDisponible + v_difference
    WHERE idLot = p_id_lot;
    
    -- Enregistrer l'ajustement
    INSERT INTO RAPPORT_EXCEPTION(
        typeRapport, 
        dateGeneration, 
        description,
        idBonReception,
        idBonExpedition
    )
    VALUES (
        'inventaire_physique',
        CURRENT_DATE,
        'Ajustement de stock: ' || v_difference || ' unités pour le lot ' || 
        (SELECT numeroLot FROM LOT WHERE idLot = p_id_lot) || 
        ' dans la cellule ' || (SELECT reference FROM CELLULE WHERE idCellule = p_id_cellule) ||
        '. Commentaire: ' || p_commentaire,
        NULL,
        NULL
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

--valider reception du produit

CREATE OR REPLACE FUNCTION valider_reception(p_id_bon INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE BON_RECEPTION
    SET statut = 'termine'
    WHERE idBon = p_id_bon;
END;
$$ LANGUAGE plpgsql;

--Annuler un colis 

CREATE OR REPLACE FUNCTION annuler_colis(p_id_colis INTEGER)
RETURNS VOID AS $$
DECLARE
    v_lot RECORD;
BEGIN
    -- Réinjecter les quantités dans les lots
    FOR v_lot IN 
        SELECT idLot, quantite FROM CONTENIR WHERE idColis = p_id_colis
    LOOP
        UPDATE LOT
        SET quantiteDisponible = quantiteDisponible + v_lot.quantite
        WHERE idLot = v_lot.idLot;
    END LOOP;

    -- Supprimer les liens
    DELETE FROM CONTENIR WHERE idColis = p_id_colis;
    DELETE FROM EXPEDIER_COLIS WHERE idColis = p_id_colis;

    -- Marquer le colis comme annulé
    UPDATE COLIS
    SET statut = 'annule'
    WHERE idColis = p_id_colis;
END;
$$ LANGUAGE plpgsql;
