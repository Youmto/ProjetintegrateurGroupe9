-- =============================================
-- SGE_test-pos.sql
-- Tests unitaires positifs
-- =============================================

-- Test 1: Vérification du nombre d'organisations
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM ORGANISATION) <> 3 THEN
        RAISE EXCEPTION 'Test 1 échoué: Nombre incorrect d''organisations';
    ELSE
        RAISE NOTICE 'Test 1 réussi: 3 organisations trouvées';
    END IF;
END $$;

-- Test 2: Vérification des produits matériels
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM PRODUIT_MATERIEL) <> 2 THEN
        RAISE EXCEPTION 'Test 2 échoué: Nombre incorrect de produits matériels';
    ELSE
        RAISE NOTICE 'Test 2 réussi: 2 produits matériels trouvés';
    END IF;
END $$;

-- Test 3: Vérification du stockage
DO $$
BEGIN
    IF (SELECT SUM(quantite) FROM STOCKER) <> 350 THEN
        RAISE EXCEPTION 'Test 3 échoué: Quantité totale stockée incorrecte';
    ELSE
        RAISE NOTICE 'Test 3 réussi: 350 unités stockées au total';
    END IF;
END $$;

-- Test 4: Test de la fonction preparer_colis
DO $$
DECLARE
    v_idColis INTEGER;
BEGIN
    v_idColis := preparer_colis(1, 1, 10);
    
    IF (SELECT COUNT(*) FROM CONTENIR WHERE idColis = v_idColis) = 0 THEN
        RAISE EXCEPTION 'Test 4 échoué: Aucun lot ajouté au colis';
    ELSE
        RAISE NOTICE 'Test 4 réussi: Colis % préparé avec succès', v_idColis;
    END IF;
END $$;

-- Test 5: Vérification du trigger de quantité
DO $$
BEGIN
    -- Doit réussir car quantité <= quantité initiale
    UPDATE LOT SET quantiteDisponible = 40 WHERE idLot = 1;
    RAISE NOTICE 'Test 5 réussi: Trigger de quantité fonctionne (update valide)';
END $$;