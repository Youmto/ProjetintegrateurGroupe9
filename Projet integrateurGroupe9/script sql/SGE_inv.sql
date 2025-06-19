-- =============================================
-- SGE_inv.sql
-- Invariants, vues, triggers et routines
-- Système de Gestion d'Entrepôt (SGE)
-- =============================================

-- VUES POUR LES REQUÊTES FRÉQUENTES

-- Vue inventaire global
CREATE OR REPLACE VIEW vue_inventaire_global AS
SELECT 
    p.idProduit, 
    p.reference, 
    p.nom, 
    p.type,
    SUM(i.quantiteDisponible) AS quantite_totale,
    COUNT(DISTINCT i.idOrganisation) AS nb_emplacements
FROM PRODUIT p
LEFT JOIN INVENTAIRE i ON p.idProduit = i.idProduit
GROUP BY p.idProduit, p.reference, p.nom, p.type;

-- Vue emplacements occupés
CREATE OR REPLACE VIEW vue_emplacements_occupes AS
SELECT 
    c.idCellule,
    c.reference,
    e.idEntrepot,
    e.nom AS nom_entrepot,
    COUNT(DISTINCT s.idLot) AS nb_lots,
    SUM(s.quantite) AS quantite_totale
FROM CELLULE c
JOIN COMPOSER_ENTREPOT ce ON c.idCellule = ce.idCellule
JOIN ENTREPOT e ON ce.idEntrepot = e.idEntrepot
LEFT JOIN STOCKER s ON c.idCellule = s.idCellule
GROUP BY c.idCellule, c.reference, e.idEntrepot, e.nom;

-- Vue colis en attente
CREATE OR REPLACE VIEW vue_colis_en_attente AS
SELECT 
    c.idColis,
    c.reference,
    c.statut,
    COUNT(ct.idLot) AS nb_lots,
    SUM(ct.quantite) AS quantite_totale
FROM COLIS c
JOIN CONTENIR ct ON c.idColis = ct.idColis
WHERE c.statut IN ('en_attente', 'en_preparation')
GROUP BY c.idColis, c.reference, c.statut;

-- TRIGGERS POUR LES CONTRAINTES MÉTIER

-- Trigger pour vérifier les quantités dans LOT
CREATE OR REPLACE FUNCTION check_quantite_lot()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantiteDisponible > NEW.quantiteInitiale THEN
        RAISE EXCEPTION 'La quantité disponible ne peut pas dépasser la quantité initiale';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_quantite_lot
BEFORE INSERT OR UPDATE ON LOT
FOR EACH ROW EXECUTE FUNCTION check_quantite_lot();

-- Trigger pour les dates des bons
CREATE OR REPLACE FUNCTION check_dates_bon()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.dateExpeditionPrevue < NEW.dateCreation THEN
        RAISE EXCEPTION 'La date d''expédition prévue doit être postérieure à la date de création';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_dates_bon_expedition
BEFORE INSERT OR UPDATE ON BON_EXPEDITION
FOR EACH ROW EXECUTE FUNCTION check_dates_bon();

CREATE TRIGGER trg_check_dates_bon_reception
BEFORE INSERT OR UPDATE ON BON_RECEPTION
FOR EACH ROW EXECUTE FUNCTION check_dates_bon();

-- Trigger pour mise à jour automatique de l'inventaire
CREATE OR REPLACE FUNCTION update_inventaire()
RETURNS TRIGGER AS $$
BEGIN
    -- Mise à jour lors d'un stockage
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE INVENTAIRE
        SET quantiteDisponible = quantiteDisponible + NEW.quantite
        WHERE idProduit = (SELECT idProduit FROM LOT WHERE idLot = NEW.idLot);
    END IF;
    
    -- Mise à jour lors d'un déstockage
    IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
        IF TG_OP = 'UPDATE' THEN
            UPDATE INVENTAIRE
            SET quantiteDisponible = quantiteDisponible - OLD.quantite
            WHERE idProduit = (SELECT idProduit FROM LOT WHERE idLot = OLD.idLot);
        ELSE
            UPDATE INVENTAIRE
            SET quantiteDisponible = quantiteDisponible - OLD.quantite
            WHERE idProduit = (SELECT idProduit FROM LOT WHERE idLot = OLD.idLot);
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_inventaire
AFTER INSERT OR UPDATE OR DELETE ON STOCKER
FOR EACH ROW EXECUTE FUNCTION update_inventaire();

-- FONCTIONS MÉTIER

-- Fonction pour préparer un colis
CREATE OR REPLACE FUNCTION preparer_colis(
    p_idBonExp INTEGER,
    p_idProduit INTEGER,
    p_quantite INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_idColis INTEGER;
    v_idLot INTEGER;
    v_quantite_restante INTEGER := p_quantite;
BEGIN
    -- Créer un nouveau colis
    INSERT INTO COLIS(reference, dateCreation, statut)
    VALUES ('COL-' || nextval('colis_seq'), CURRENT_DATE, 'en_preparation')
    RETURNING idColis INTO v_idColis;
    
    -- Lier le colis au bon d'expédition
    INSERT INTO EXPEDIER_COLIS(idBon, idColis)
    VALUES (p_idBonExp, v_idColis);
    
    -- Trouver les lots disponibles et les ajouter au colis
    FOR v_idLot IN 
        SELECT idLot FROM LOT 
        WHERE idProduit = p_idProduit AND quantiteDisponible > 0
        ORDER BY dateExpiration
    LOOP
        DECLARE
            v_disponible INTEGER;
        BEGIN
            SELECT quantiteDisponible INTO v_disponible 
            FROM LOT WHERE idLot = v_idLot;
            
            IF v_disponible >= v_quantite_restante THEN
                -- Ajouter au colis
                INSERT INTO CONTENIR(idColis, idLot, quantite)
                VALUES (v_idColis, v_idLot, v_quantite_restante);
                
                -- Mettre à jour le lot
                UPDATE LOT 
                SET quantiteDisponible = quantiteDisponible - v_quantite_restante
                WHERE idLot = v_idLot;
                
                v_quantite_restante := 0;
                EXIT;
            ELSE
                -- Ajouter au colis
                INSERT INTO CONTENIR(idColis, idLot, quantite)
                VALUES (v_idColis, v_idLot, v_disponible);
                
                -- Mettre à jour le lot
                UPDATE LOT 
                SET quantiteDisponible = 0
                WHERE idLot = v_idLot;
                
                v_quantite_restante := v_quantite_restante - v_disponible;
            END IF;
        END;
    END LOOP;
    
    -- Mettre à jour le statut du colis
    UPDATE COLIS 
    SET statut = 'pret_a_expedier'
    WHERE idColis = v_idColis;
    
    RETURN v_idColis;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour recevoir un colis
CREATE OR REPLACE FUNCTION recevoir_colis(
    p_idBonRecept INTEGER,
    p_referenceColis VARCHAR(50),
    p_statut VARCHAR(20)
RETURNS INTEGER AS $$
DECLARE
    v_idColis INTEGER;
BEGIN
    -- Créer un nouveau colis
    INSERT INTO COLIS(reference, dateCreation, statut)
    VALUES (p_referenceColis, CURRENT_DATE, p_statut)
    RETURNING idColis INTO v_idColis;
    
    -- Lier le colis au bon de réception
    INSERT INTO RECEVOIR_COLIS(idBon, idColis)
    VALUES (p_idBonRecept, v_idColis);
    
    RETURN v_idColis;
END;
$$ LANGUAGE plpgsql;