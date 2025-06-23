-- =============================================
-- SGE_inv.sql
-- Invariants, vues, triggers et routines
-- Système de Gestion d'Entrepôt (SGE)
-- Version optimisée et sécurisée
-- =============================================

SET client_encoding = 'UTF8';
SET search_path = public;

-- SECTION 1: VUES METIER OPTIMISEES
------------------------------------------------

-- Vue inventaire global avec indicateurs de stock
CREATE OR REPLACE VIEW vue_inventaire_global AS
SELECT
    p.idProduit,
    p.reference,
    p.nom,
    p.type,
    COALESCE(SUM(i.quantiteDisponible), 0) AS quantite_totale,
    COUNT(DISTINCT i.idOrganisation) AS nb_emplacements,
    MIN(l.dateExpiration) FILTER (WHERE l.dateExpiration > CURRENT_DATE) AS prochaine_expiration
FROM PRODUIT p
LEFT JOIN LOT l ON p.idProduit = l.idProduit
LEFT JOIN INVENTAIRE i ON p.idProduit = i.idProduit
GROUP BY p.idProduit, p.reference, p.nom, p.type;

-- Vue emplacements occupés avec taux d'occupation
CREATE OR REPLACE VIEW vue_emplacements_occupes AS
SELECT
    c.idCellule,
    c.reference,
    e.idEntrepot,
    e.nom AS nom_entrepot,
    c.capacite_max,
    COUNT(DISTINCT s.idLot) AS nb_lots,
    SUM(s.quantite) AS quantite_totale,
    ROUND(SUM(s.quantite) * 100.0 / NULLIF(c.capacite_max, 0), 2) AS taux_occupation
FROM CELLULE c
JOIN COMPOSER_ENTREPOT ce ON c.idCellule = ce.idCellule
JOIN ENTREPOT e ON ce.idEntrepot = e.idEntrepot
LEFT JOIN STOCKER s ON c.idCellule = s.idCellule
GROUP BY c.idCellule, c.reference, e.idEntrepot, e.nom, c.capacite_max;

-- Vue colis avec détails complets
CREATE OR REPLACE VIEW vue_colis_etat AS
SELECT
    c.idColis,
    c.reference,
    c.statut,
    c.dateCreation,
    be.reference AS bon_expedition,
    br.reference AS bon_reception,
    COUNT(ct.idLot) AS nb_lots,
    SUM(ct.quantite) AS quantite_totale,
    STRING_AGG(DISTINCT p.nom, ', ' ORDER BY p.nom) AS produits
FROM COLIS c
LEFT JOIN CONTENIR ct ON c.idColis = ct.idColis
LEFT JOIN LOT l ON ct.idLot = l.idLot
LEFT JOIN PRODUIT p ON l.idProduit = p.idProduit
LEFT JOIN EXPEDIER_COLIS ec ON c.idColis = ec.idColis
LEFT JOIN BON_EXPEDITION be ON ec.idBon = be.idBon
LEFT JOIN RECEVOIR_COLIS rc ON c.idColis = rc.idColis
LEFT JOIN BON_RECEPTION br ON rc.idBon = br.idBon
GROUP BY c.idColis, c.reference, c.statut, c.dateCreation, be.reference, br.reference;

-- SECTION 2: TRIGGERS ET CONTRAINTES METIER
------------------------------------------------

-- Contrôle d'intégrité des quantités dans LOT
CREATE OR REPLACE FUNCTION trg_check_quantite_lot()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantiteDisponible < 0 THEN
        RAISE EXCEPTION 'La quantité disponible ne peut pas être négative';
    END IF;
    
    IF NEW.quantiteDisponible > NEW.quantiteInitiale THEN
        RAISE EXCEPTION 'La quantité disponible (%) ne peut dépasser la quantité initiale (%)', 
            NEW.quantiteDisponible, NEW.quantiteInitiale;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Contrôle des dates dans BON_EXPEDITION
CREATE OR REPLACE FUNCTION trg_check_dates_expedition()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.dateExpeditionPrevue < CURRENT_DATE THEN
        RAISE WARNING 'Date d''expédition prévue dans le passé: %', NEW.dateExpeditionPrevue;
    END IF;
    
    IF NEW.dateExpeditionPrevue < NEW.dateCreation THEN
        RAISE EXCEPTION 'La date d''expédition prévue doit être postérieure à la date de création';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Gestion automatique de l'inventaire
CREATE OR REPLACE FUNCTION trg_update_inventaire()
RETURNS TRIGGER AS $$
DECLARE
    v_idProduit INTEGER;
BEGIN
    -- Récupération de l'idProduit selon l'opération
    IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
        SELECT idProduit INTO v_idProduit 
        FROM LOT WHERE idLot = OLD.idLot;
        
        UPDATE INVENTAIRE
        SET quantiteDisponible = quantiteDisponible - OLD.quantite
        WHERE idProduit = v_idProduit;
    END IF;
    
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        SELECT idProduit INTO v_idProduit 
        FROM LOT WHERE idLot = NEW.idLot;
        
        UPDATE INVENTAIRE
        SET quantiteDisponible = quantiteDisponible + NEW.quantite
        WHERE idProduit = v_idProduit;
    END IF;
    
    RETURN NULL; -- Après trigger donc retour ignoré
END;
$$ LANGUAGE plpgsql;

-- SECTION 3: CREATION DES DECLENCHEURS
------------------------------------------------

-- Suppression des triggers existants pour éviter les doublons
DROP TRIGGER IF EXISTS trg_check_quantite_lot ON LOT;
DROP TRIGGER IF EXISTS trg_check_dates_expedition ON BON_EXPEDITION;
DROP TRIGGER IF EXISTS trg_update_inventaire ON STOCKER;

-- Application des triggers
CREATE TRIGGER trg_check_quantite_lot
BEFORE INSERT OR UPDATE ON LOT
FOR EACH ROW EXECUTE FUNCTION trg_check_quantite_lot();

CREATE TRIGGER trg_check_dates_expedition
BEFORE INSERT OR UPDATE ON BON_EXPEDITION
FOR EACH ROW EXECUTE FUNCTION trg_check_dates_expedition();

CREATE TRIGGER trg_update_inventaire
AFTER INSERT OR UPDATE OR DELETE ON STOCKER
FOR EACH ROW EXECUTE FUNCTION trg_update_inventaire();

-- SECTION 4: FONCTIONS METIER AMELIOREES
------------------------------------------------

-- Fonction de préparation de colis avec gestion des erreurs
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
    -- Vérification du stock disponible
    SELECT COALESCE(SUM(quantiteDisponible), 0) INTO v_stock_disponible
    FROM LOT WHERE idProduit = p_idProduit;
    
    IF v_stock_disponible < p_quantite THEN
        RAISE EXCEPTION 'Stock insuffisant. Disponible: %, Demandé: %', 
            v_stock_disponible, p_quantite;
    END IF;
    
    -- Création du colis
    v_referenceColis := 'COL-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD-') || 
                        LPAD(NEXTVAL('colis_seq')::TEXT, 6, '0');
    
    INSERT INTO COLIS(reference, dateCreation, statut)
    VALUES (v_referenceColis, CURRENT_DATE, 'en_preparation')
    RETURNING idColis INTO v_idColis;
    
    -- Association au bon d'expédition
    INSERT INTO EXPEDIER_COLIS(idBon, idColis)
    VALUES (p_idBonExp, v_idColis);
    
    -- Remplissage du colis par ordre FIFO
    FOR v_lot IN 
        SELECT idLot, quantiteDisponible 
        FROM LOT 
        WHERE idProduit = p_idProduit AND quantiteDisponible > 0
        ORDER BY dateExpiration
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
    
    -- Finalisation du colis
    UPDATE COLIS 
    SET statut = 'pret_a_expedier' 
    WHERE idColis = v_idColis;
    
    RETURN v_idColis;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur lors de la préparation du colis: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Fonction de réception de colis avec validation
CREATE OR REPLACE FUNCTION recevoir_colis(
    p_idBonRecept INTEGER,
    p_referenceColis TEXT,
    p_statut TEXT
) RETURNS INTEGER AS $$
DECLARE
    v_idColis INTEGER;
    v_bon_existant BOOLEAN;
BEGIN
    -- Validation du bon de réception
    SELECT EXISTS(SELECT 1 FROM BON_RECEPTION WHERE idBon = p_idBonRecept) 
    INTO v_bon_existant;
    
    IF NOT v_bon_existant THEN
        RAISE EXCEPTION 'Bon de réception % inexistant', p_idBonRecept;
    END IF;
    
    -- Vérification du statut valide
    IF p_statut NOT IN ('recu', 'partiel', 'endommage') THEN
        RAISE EXCEPTION 'Statut invalide: %', p_statut;
    END IF;
    
    -- Création du colis
    INSERT INTO COLIS(reference, dateCreation, statut)
    VALUES (p_referenceColis, CURRENT_DATE, p_statut)
    RETURNING idColis INTO v_idColis;
    
    -- Association au bon de réception
    INSERT INTO RECEVOIR_COLIS(idBon, idColis)
    VALUES (p_idBonRecept, v_idColis);
    
    RETURN v_idColis;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erreur lors de la réception du colis: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- SECTION 5: GESTION DES SEQUENCES
------------------------------------------------

-- Séquence pour les colis avec cache
CREATE SEQUENCE IF NOT EXISTS seq_colis
    START WITH 1
    INCREMENT BY 1
    CACHE 10;

-- Application de la séquence à la table COLIS
ALTER TABLE COLIS 
ALTER COLUMN idColis SET DEFAULT NEXTVAL('seq_colis');

-- SECTION 6: VERIFICATIONS FINALES
------------------------------------------------

-- Vérification de la colonne idProduit dans LOT
DO $$
BEGIN
    -- Ajout de la colonne si absente
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'lot' AND column_name = 'idproduit'
    ) THEN
        ALTER TABLE lot ADD COLUMN idProduit INTEGER;
        
        -- Mise à jour des lots existants si possible
        UPDATE lot l
        SET idProduit = (SELECT MIN(idProduit) FROM produit p 
                         WHERE p.reference = l.referenceProduit)
        WHERE idProduit IS NULL;
    END IF;
    
    -- Ajout de la contrainte de clé étrangère
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_lot_produit' AND table_name = 'lot'
    ) THEN
        ALTER TABLE lot
        ADD CONSTRAINT fk_lot_produit 
        FOREIGN KEY (idProduit) REFERENCES produit(idProduit)
        ON DELETE RESTRICT;
    END IF;
END $$;

-- Vérification de la vue d'inventaire
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.views 
        WHERE table_name = 'vue_inventaire_global'
    ) THEN
        RAISE NOTICE 'La vue vue_inventaire_global a été recréée';
    END IF;
END $$;
