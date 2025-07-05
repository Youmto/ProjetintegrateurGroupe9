-- =============================================
-- SGE_test-pos.sql
-- Tests unitaires positifs (structure & logique métier)
-- Version robuste et professionnelle
-- =============================================

-- TEST 1 : Vérification du nombre d'organisations
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM ORGANISATION) <> 3 THEN
        RAISE EXCEPTION 'Test 1 échoué : nombre d''organisations ≠ 3';
    ELSE
        RAISE NOTICE 'Test 1 réussi : 3 organisations présentes';
    END IF;
END $$;

-- TEST 2 : Vérification du nombre de produits matériels
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM PRODUIT_MATERIEL) <> 2 THEN
        RAISE EXCEPTION 'Test 2 échoué : nombre de produits matériels ≠ 2';
    ELSE
        RAISE NOTICE 'Test 2 réussi : 2 produits matériels détectés';
    END IF;
END $$;

-- TEST 3 : Vérification de la quantité totale stockée
DO $$
DECLARE
    v_total INTEGER;
BEGIN
    SELECT SUM(quantite) INTO v_total FROM STOCKER;
    IF v_total IS DISTINCT FROM 350 THEN
        RAISE EXCEPTION 'Test 3 échoué : total stocké = %, attendu = 350', v_total;
    ELSE
        RAISE NOTICE 'Test 3 réussi : quantité stockée = 350';
    END IF;
END $$;

-- TEST 4 : Appel de la fonction preparer_colis (bon #1, produit #1, 10 unités)
DO $$
DECLARE
    v_id_colis INTEGER;
    v_count_lots INTEGER;
BEGIN
    v_id_colis := preparer_colis(1, 1, 10);

    SELECT COUNT(*) INTO v_count_lots
    FROM CONTENIR WHERE idColis = v_id_colis;

    IF v_count_lots <= 0 THEN
        RAISE EXCEPTION 'Test 4 échoué : aucun lot lié au colis préparé';
    ELSE
        RAISE NOTICE 'Test 4 réussi : colis % contient % lots', v_id_colis, v_count_lots;
    END IF;
END $$;

-- TEST 5 : Vérification du trigger de contrainte sur les quantités dans LOT
DO $$
DECLARE
    v_q_init INTEGER;
BEGIN
    SELECT quantiteInitiale INTO v_q_init FROM LOT WHERE idLot = 1;

    -- Essai d’un update valide
    UPDATE LOT SET quantiteDisponible = LEAST(v_q_init, 40) WHERE idLot = 1;

    RAISE NOTICE 'Test 5 réussi : update quantitéDisponible = 40 autorisé';

    -- Rétablir la valeur initiale si nécessaire
    UPDATE LOT SET quantiteDisponible = v_q_init WHERE idLot = 1;
END $$;
