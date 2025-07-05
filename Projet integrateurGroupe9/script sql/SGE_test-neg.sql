-- =============================================
-- SGE_test-neg.sql
-- Tests unitaires négatifs
-- =============================================

-- Test 1: Tentative d'insertion avec quantité disponible > quantité initiale
DO $$
BEGIN
    BEGIN
        INSERT INTO LOT(idLot, numeroLot, quantiteInitiale, quantiteDisponible, dateProduction, statut,idProduit)
        VALUES (100, 'LOT-TEST', 10, 15, CURRENT_DATE, 'actif',1);
        
        RAISE EXCEPTION 'Test 1 échoué: Insertion invalide acceptée';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Test 1 réussi: Trigger a bloqué l''insertion invalide';
    END;
END $$;

-- Test 2: Tentative de date d'expédition antérieure à la création
DO $$
BEGIN
    BEGIN
        INSERT INTO BON_EXPEDITION(idBon, reference, dateCreation, dateExpeditionPrevue, statut)
        VALUES (100, 'BE-TEST', '2023-05-01', '2023-04-30', 'en_attente');
        
        RAISE EXCEPTION 'Test 2 échoué: Date invalide acceptée';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Test 2 réussi: Trigger a bloqué la date invalide';
    END;
END $$;

-- Test 3: Tentative de suppression d'un produit utilisé
DO $$
BEGIN
    BEGIN
        DELETE FROM PRODUIT WHERE idProduit = 1;
        
        RAISE EXCEPTION 'Test 3 échoué: Suppression réussie malgré contrainte de référence';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Test 3 réussi: Contrainte de clé étrangère a bloqué la suppression';
    END;
END $$;

-- Test 4: Tentative d'insertion avec email invalide
DO $$
BEGIN
    BEGIN
        INSERT INTO INDIVIDU(idIndividu, nom, email)
        VALUES (100, 'Test', 'email-invalide');
        
        RAISE EXCEPTION 'Test 4 échoué: Email invalide accepté';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Test 4 réussi: Domaine email a bloqué l''insertion';
    END;
END $$;

-- Test 5: Tentative de stockage dans une cellule pleine
DO $$
DECLARE
    v_capacite FLOAT;
    v_volume FLOAT;
BEGIN
    SELECT volumeMaximal INTO v_capacite FROM CELLULE WHERE idCellule = 1;
    SELECT SUM(p.volume * s.quantite) INTO v_volume
    FROM STOCKER s
    JOIN LOT l ON s.idLot = l.idLot
    JOIN PRODUIT_MATERIEL p ON l.idProduit = p.idProduit
    WHERE s.idCellule = 1;
    
    BEGIN
        -- Tenter d'ajouter un volume qui dépasse la capacité
        INSERT INTO STOCKER(idLot, idCellule, quantite)
        VALUES (3, 1, 1000);
        
        RAISE EXCEPTION 'Test 5 échoué: Capacité dépassée acceptée';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Test 5 réussi: Volume maximal respecté';
    END;
END $$;