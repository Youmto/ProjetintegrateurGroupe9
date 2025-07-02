-- =============================================
-- SGE_req.sql (Version consolidée et robuste)
-- Système de Gestion d’Entrepôt (SGE)
-- Amazones & Centaures - Requêtes métiers fréquentes
-- =============================================
SET search_path TO public;

-- =============================================
-- 1. Obtenir l'inventaire d'un produit
-- =============================================
CREATE OR REPLACE FUNCTION obtenir_inventaire_produit(p_id_produit INTEGER)
RETURNS TABLE (
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
        COALESCE(SUM(s.quantite), 0),
        STRING_AGG(DISTINCT c.reference, ', ' ORDER BY c.reference)
    FROM PRODUIT p
    LEFT JOIN LOT l ON l.idProduit = p.idProduit
    LEFT JOIN STOCKER s ON s.idLot = l.idLot
    LEFT JOIN CELLULE c ON c.idCellule = s.idCellule
    WHERE p.idProduit = p_id_produit
    GROUP BY p.idProduit, p.reference, p.nom;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 2. Produits en rupture de stock
-- =============================================
CREATE OR REPLACE FUNCTION produits_en_rupture()
RETURNS TABLE (
    idProduit dom_id,
    reference dom_reference,
    nom dom_nom,
    description dom_texte,
    marque dom_type,
    modele dom_type,
    type dom_type_produit,
    estMaterielEmballage dom_boolean,
    quantite dom_quantite
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.idProduit,
        p.reference,
        p.nom,
        p.description,
        p.marque,
        p.modele,
        p.type,
        p.estMaterielEmballage,
        0::dom_quantite AS quantite  -- car en rupture
    FROM PRODUIT p
    LEFT JOIN LOT l ON l.idProduit = p.idProduit
    LEFT JOIN STOCKER s ON s.idLot = l.idLot
    GROUP BY p.idProduit, p.reference, p.nom, p.description,
             p.marque, p.modele, p.type, p.estMaterielEmballage
    HAVING COALESCE(SUM(s.quantite), 0) = 0;
END;
$$;

--vue approvisionnement 
DROP VIEW IF EXISTS vue_approvisionnement;

CREATE OR REPLACE VIEW vue_approvisionnement AS
SELECT 
    p.idProduit,
    p.nom,
    p.reference,
    p.type,
    COALESCE(SUM(s.quantite), 0) AS quantite_actuelle,
    CASE
        WHEN COALESCE(SUM(s.quantite), 0) = 0 THEN 'rupture'
        WHEN COALESCE(SUM(s.quantite), 0) < 10 THEN 'faible'
        ELSE 'ok'
    END AS niveau_stock
FROM PRODUIT p
LEFT JOIN LOT l ON p.idProduit = l.idProduit
LEFT JOIN STOCKER s ON s.idLot = l.idLot
GROUP BY p.idProduit, p.nom, p.reference, p.type
HAVING COALESCE(SUM(s.quantite), 0) < 10;


-- =============================================
-- 3. Produits expirant bientôt
-- =============================================
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

-- =============================================
-- 4. Mouvements d’un produit (réception / expédition)
-- =============================================
CREATE OR REPLACE FUNCTION mouvements_produit(p_id_produit dom_id)
RETURNS TABLE (
    type TEXT,
    reference_bon dom_reference,
    date dom_date,
    quantite INTEGER, -- ❗ doit permettre les valeurs négatives
    lot dom_reference,
    cellule dom_reference,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM (
        -- Réceptions
        SELECT
            'Entrée'::TEXT,
            br.reference,
            br.dateReceptionPrevue,
            ct.quantite, -- OK, positive
            l.numeroLot,
            ce.reference,
            'Réception bon #' || br.reference
        FROM BON_RECEPTION br
        JOIN RECEVOIR_COLIS rc ON rc.idBon = br.idBon
        JOIN COLIS c ON rc.idColis = c.idColis
        JOIN CONTENIR ct ON ct.idColis = c.idColis
        JOIN LOT l ON l.idLot = ct.idLot
        JOIN STOCKER s ON s.idLot = l.idLot
        JOIN CELLULE ce ON ce.idCellule = s.idCellule
        WHERE l.idProduit = p_id_produit

        UNION ALL

        -- Expéditions
        SELECT
            'Sortie'::TEXT,
            be.reference,
            be.dateExpeditionPrevue,
            -ct.quantite, -- ❗ NE PAS caster en dom_quantite
            l.numeroLot,
            ce.reference,
            'Expédition bon #' || be.reference
        FROM BON_EXPEDITION be
        JOIN EXPEDIER_COLIS ec ON ec.idBon = be.idBon
        JOIN COLIS c ON ec.idColis = c.idColis
        JOIN CONTENIR ct ON c.idColis = ct.idColis
        JOIN LOT l ON l.idLot = ct.idLot
        JOIN STOCKER s ON s.idLot = l.idLot
        JOIN CELLULE ce ON ce.idCellule = s.idCellule
        WHERE l.idProduit = p_id_produit
    ) mouvements
    ORDER BY date DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 5. Colis prêts à expédier
-- =============================================
CREATE OR REPLACE FUNCTION colis_pret_expedition()
RETURNS TABLE (
    idColis INTEGER,
    reference VARCHAR(50),
    date_creation DATE,
    bon_expedition_ref VARCHAR(50),
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
        COUNT(DISTINCT ct.idLot),
        COALESCE(SUM(ct.quantite), 0)
    FROM COLIS c
    JOIN EXPEDIER_COLIS ec ON ec.idColis = c.idColis
    JOIN BON_EXPEDITION be ON be.idBon = ec.idBon
    LEFT JOIN CONTENIR ct ON ct.idColis = c.idColis
    WHERE c.statut = 'pret_a_expedier'
    GROUP BY c.idColis, c.reference, c.dateCreation, be.reference, be.dateExpeditionPrevue;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 6. Annuler un colis
-- =============================================
CREATE OR REPLACE FUNCTION annuler_colis(p_idColis INTEGER)
RETURNS VOID AS $$
DECLARE
    r RECORD;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM COLIS WHERE idColis = p_idColis) THEN
        RAISE EXCEPTION 'Colis avec ID % introuvable.', p_idColis;
    END IF;

    FOR r IN SELECT idLot, quantite FROM CONTENIR WHERE idColis = p_idColis
    LOOP
        UPDATE LOT
        SET quantiteDisponible = quantiteDisponible + r.quantite
        WHERE idLot = r.idLot;
    END LOOP;

    UPDATE COLIS SET statut = 'annule' WHERE idColis = p_idColis;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 7. Ajouter une cellule
-- =============================================
CREATE OR REPLACE FUNCTION ajouter_cellule(
    p_reference VARCHAR,
    p_longueur NUMERIC,
    p_largeur NUMERIC,
    p_hauteur NUMERIC,
    p_masse_max NUMERIC,
    p_volume_max NUMERIC, -- facultatif (calculé si null ou 0)
    p_capacite_max INTEGER,
    p_position TEXT,
    p_id_entrepot INTEGER
) RETURNS INTEGER AS $$
DECLARE
    new_id INTEGER;
    v_volume NUMERIC;
BEGIN
    -- Calcul automatique si volume non fourni ou invalide
    v_volume := COALESCE(NULLIF(p_volume_max, 0), p_longueur * p_largeur * p_hauteur);

    INSERT INTO CELLULE(
        reference, longueur, largeur, hauteur,
        masseMaximale, volumeMaximal,
        statut, capacite_max, position
    ) VALUES (
        p_reference, p_longueur, p_largeur, p_hauteur,
        p_masse_max, v_volume,
        'actif', p_capacite_max, p_position
    )
    RETURNING idCellule INTO new_id;

    INSERT INTO COMPOSER_ENTREPOT(idEntrepot, idCellule)
    VALUES (p_id_entrepot, new_id);

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 8. Mise à jour d’une cellule
-- =============================================
CREATE OR REPLACE FUNCTION update_cellule(
    p_id_cellule INTEGER,
    p_longueur NUMERIC,
    p_largeur NUMERIC,
    p_hauteur NUMERIC,
    p_masse_max NUMERIC,
    p_volume_max NUMERIC,
    p_capacite_max INTEGER,
    p_statut TEXT
) RETURNS VOID AS $$
BEGIN
    UPDATE CELLULE SET
        longueur = p_longueur,
        largeur = p_largeur,
        hauteur = p_hauteur,
        masseMaximale = p_masse_max,
        volumeMaximal = p_volume_max,
        capacite_max = p_capacite_max,
        statut = p_statut
    WHERE idCellule = p_id_cellule;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cellule avec ID % introuvable', p_id_cellule;
    END IF;
END;
$$ LANGUAGE plpgsql;
DROP FUNCTION IF EXISTS produits_expirant_bientot(integer);
DROP FUNCTION IF EXISTS mouvements_produit(p_id_produit dom_id);

-- CREATE OR REPLACE FUNCTION produits_jamais_stockes() [...]
CREATE OR REPLACE FUNCTION produits_jamais_stockes()
RETURNS TABLE (
    idProduit dom_id,
    reference dom_reference,
    nom dom_nom,
    description dom_texte,
    marque dom_type,
    modele dom_type,
    type dom_type_produit,
    estMaterielEmballage dom_boolean
)
LANGUAGE plpgsql  -- Déclaration de langage requise
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.idProduit,
        p.reference,
        p.nom,
        p.description,
        p.marque,
        p.modele,
        p.type,
        p.estMaterielEmballage
    FROM PRODUIT p
    WHERE NOT EXISTS (
        SELECT 1 FROM LOT l
        WHERE l.idProduit = p.idProduit
    );
END;
$$;
--cellule vide 
CREATE OR REPLACE FUNCTION cellules_vides()
RETURNS TABLE (
    idCellule dom_id,
    reference dom_reference,
    nom_entrepot dom_nom,
    volumeDisponible dom_float
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.idCellule,
        c.reference,
        e.nom,
        c.volumeMaximal
    FROM CELLULE c
    JOIN COMPOSER_ENTREPOT ce ON ce.idCellule = c.idCellule
    JOIN ENTREPOT e ON e.idEntrepot = ce.idEntrepot
    LEFT JOIN STOCKER s ON s.idCellule = c.idCellule
    WHERE s.idLot IS NULL; 
END;
$$ LANGUAGE plpgsql;
-- deplament d'un lot 
CREATE OR REPLACE FUNCTION deplacer_lot(
    p_id_lot dom_id,
    p_id_cellule_source dom_id,
    p_id_cellule_destination dom_id,
    p_quantite dom_quantite,
    p_id_responsable dom_id
)
RETURNS BOOLEAN AS $$
DECLARE
    stock_actuel INTEGER;
BEGIN
    -- Vérifie l'existence et la quantité dans la cellule source
    SELECT quantite INTO stock_actuel
    FROM STOCKER
    WHERE idLot = p_id_lot AND idCellule = p_id_cellule_source;

    IF stock_actuel IS NULL THEN
        RAISE EXCEPTION 'Le lot % n''existe pas dans la cellule source %', p_id_lot, p_id_cellule_source;
    ELSIF stock_actuel < p_quantite THEN
        RAISE EXCEPTION 'Quantité insuffisante (% disponible, % demandée)', stock_actuel, p_quantite;
    END IF;

    -- Décrémenter la cellule source
    UPDATE STOCKER
    SET quantite = quantite - p_quantite
    WHERE idLot = p_id_lot AND idCellule = p_id_cellule_source;

    -- Supprime si quantité devient 0
    DELETE FROM STOCKER
    WHERE idLot = p_id_lot AND idCellule = p_id_cellule_source AND quantite = 0;

    -- Ajout ou mise à jour dans la cellule destination
    INSERT INTO STOCKER(idLot, idCellule, quantite)
    VALUES (p_id_lot, p_id_cellule_destination, p_quantite)
    ON CONFLICT (idLot, idCellule)
    DO UPDATE SET quantite = STOCKER.quantite + EXCLUDED.quantite;

    -- Enregistrement du mouvement (optionnel)
    INSERT INTO DEPLACEMENT_LOG(idLot, cellule_source, cellule_destination, quantite, idResponsable, date_deplacement)
    VALUES (p_id_lot, p_id_cellule_source, p_id_cellule_destination, p_quantite, p_id_responsable, CURRENT_TIMESTAMP)
    ON CONFLICT DO NOTHING;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
--Créé la table Deplacement_log
CREATE TABLE IF NOT EXISTS DEPLACEMENT_LOG (
	idLog SERIAL PRIMARY KEY,
	idLot dom_id NOT NULL,
	cellule_source dom_id NOT NULL,
	cellule_destination dom_id NOT NULL,
	quantite dom_quantite NOT NULL,
	idResponsable dom_id NOT NULL,
	date_deplacement TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);
-- Mise a jour des cellules 
UPDATE CELLULE
SET volumeMaximal = longueur * largeur * hauteur
WHERE volumeMaximal IS NULL OR volumeMaximal = 0;
--verifier le stockage si le volume dépasse le capacité
CREATE OR REPLACE FUNCTION verifier_volume_cellule()
RETURNS TRIGGER AS $$
DECLARE
    v_volume_unitaire NUMERIC := 0;
    v_volume_total_exist NUMERIC := 0;
    v_capacite_max INTEGER := 0;
    v_volume_max NUMERIC := 0;
    v_quantite_existante INTEGER := 0;
BEGIN
    -- Récupérer le volume unitaire du produit (si matériel)
    SELECT COALESCE(pm.volume, 0)
    INTO v_volume_unitaire
    FROM LOT l
    JOIN PRODUIT p ON l.idProduit = p.idProduit
    LEFT JOIN PRODUIT_MATERIEL pm ON p.idProduit = pm.idProduit
    WHERE l.idLot = NEW.idLot;

    -- Quantité déjà présente dans la cellule
    SELECT COALESCE(SUM(quantite), 0)
    INTO v_quantite_existante
    FROM STOCKER
    WHERE idCellule = NEW.idCellule AND idLot != NEW.idLot;

    -- Volume total déjà utilisé dans la cellule
    SELECT COALESCE(SUM(
        CASE
            WHEN p.type = 'materiel' THEN COALESCE(pm.volume, 0) * COALESCE(s.quantite, 0)
            ELSE 0
        END
    ), 0)
    INTO v_volume_total_exist
    FROM STOCKER s
    JOIN LOT l ON s.idLot = l.idLot
    JOIN PRODUIT p ON l.idProduit = p.idProduit
    LEFT JOIN PRODUIT_MATERIEL pm ON p.idProduit = pm.idProduit
    WHERE s.idCellule = NEW.idCellule AND s.idLot != NEW.idLot;

    -- Capacité max et volume max de la cellule
    SELECT capacite_max, volumeMaximal
    INTO v_capacite_max, v_volume_max
    FROM CELLULE
    WHERE idCellule = NEW.idCellule;

    -- Vérification de capacité
    IF (v_quantite_existante + NEW.quantite) > v_capacite_max THEN
        RAISE EXCEPTION 'Capacité maximale dépassée dans la cellule % (capacité max: %, tentative: %)', 
            NEW.idCellule, v_capacite_max, v_quantite_existante + NEW.quantite;
    END IF;

    -- Vérification de volume
    IF (v_volume_total_exist + (v_volume_unitaire * NEW.quantite)) > v_volume_max THEN
        RAISE EXCEPTION 'Volume maximal dépassé dans la cellule % (volume max: %, tentative: %)', 
            NEW.idCellule, v_volume_max, v_volume_total_exist + (v_volume_unitaire * NEW.quantite);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Afficher les colis contenant un lot
CREATE OR REPLACE FUNCTION get_produits_par_lot(p_id_lot dom_id)
RETURNS TABLE (
  id_colis dom_id,
  id_produit dom_id,
  nom_produit text,
  quantite dom_quantite
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    cc.idColis,
    cc.idProduit,
    p.nom,
    cc.quantite
  FROM colis_contenu cc
  JOIN colis c ON c.idColis = cc.idColis
  JOIN produit p ON p.idProduit = cc.idProduit
  WHERE c.idLot = p_id_lot
  ORDER BY cc.idColis, p.nom;
END;
$$ LANGUAGE plpgsql;

--Modifier la contenance dans un lot 
CREATE OR REPLACE FUNCTION ajouter_ou_modifier_produit_dans_colis(
    p_id_colis dom_id,
    p_id_produit dom_id,
    p_quantite dom_quantite,

    -- Attributs logiciel
    p_version dom_type DEFAULT NULL,
    p_type_licence dom_type DEFAULT NULL,
    p_date_expiration dom_date DEFAULT NULL,

    -- Attributs matériel
    p_longueur dom_float DEFAULT NULL,
    p_largeur dom_float DEFAULT NULL,
    p_hauteur dom_float DEFAULT NULL,
    p_masse dom_float DEFAULT NULL,
    p_volume dom_float DEFAULT NULL
)
RETURNS void AS $$
DECLARE
    v_type text;
    v_id_lot dom_id;
BEGIN
  -- Vérifier le type du produit
  SELECT type INTO v_type FROM produit WHERE idProduit = p_id_produit;
  IF v_type IS NULL THEN
    RAISE EXCEPTION 'Produit % inexistant.', p_id_produit;
  END IF;

  -- Chercher le lot actif correspondant au produit (on prend le plus récent encore disponible)
  SELECT idLot INTO v_id_lot
  FROM LOT
  WHERE idProduit = p_id_produit AND quantiteDisponible > 0
  ORDER BY dateProduction DESC
  LIMIT 1;

  IF v_id_lot IS NULL THEN
    RAISE EXCEPTION 'Aucun lot disponible pour le produit %.', p_id_produit;
  END IF;

  -- Insérer ou mettre à jour CONTENIR
  IF EXISTS (
    SELECT 1 FROM CONTENIR WHERE idColis = p_id_colis AND idLot = v_id_lot
  ) THEN
    UPDATE CONTENIR
    SET quantite = p_quantite
    WHERE idColis = p_id_colis AND idLot = v_id_lot;
  ELSE
    INSERT INTO CONTENIR(idColis, idLot, quantite)
    VALUES (p_id_colis, v_id_lot, p_quantite);
  END IF;

  -- Mise à jour des attributs spécifiques
  IF v_type = 'logiciel' THEN
    INSERT INTO produit_logiciel(idProduit, version, typeLicence, dateExpiration)
    VALUES (p_id_produit, p_version, p_type_licence, p_date_expiration)
    ON CONFLICT (idProduit) DO UPDATE
      SET version = EXCLUDED.version,
          typeLicence = EXCLUDED.typeLicence,
          dateExpiration = EXCLUDED.dateExpiration;
  ELSIF v_type = 'materiel' THEN
    INSERT INTO produit_materiel(idProduit, longueur, largeur, hauteur, masse, volume)
    VALUES (p_id_produit, p_longueur, p_largeur, p_hauteur, p_masse, p_volume)
    ON CONFLICT (idProduit) DO UPDATE
      SET longueur = EXCLUDED.longueur,
          largeur = EXCLUDED.largeur,
          hauteur = EXCLUDED.hauteur,
          masse = EXCLUDED.masse,
          volume = EXCLUDED.volume;
  END IF;
END;
$$ LANGUAGE plpgsql;


-- vue_produits_complets_par_lot
CREATE OR REPLACE VIEW vue_produits_par_lot_complet AS
SELECT
    l.idLot,
    l.numeroLot,
    l.idProduit AS idProduit_lot,
    co.idColis,
    l.idProduit,
    p.nom AS nomProduit,
    p.type AS typeProduit,
    co.quantite AS quantiteDansColis,

    -- LOGICIEL
    pl.version,
    pl.typeLicence,
    pl.dateExpiration,

    -- MATERIEL
    pm.longueur,
    pm.largeur,
    pm.hauteur,
    pm.masse,
    pm.volume

FROM LOT l
JOIN CONTENIR co ON l.idLot = co.idLot
JOIN COLIS c ON c.idColis = co.idColis
JOIN PRODUIT p ON p.idProduit = l.idProduit

LEFT JOIN PRODUIT_LOGICIEL pl ON pl.idProduit = p.idProduit AND p.type = 'logiciel'
LEFT JOIN PRODUIT_MATERIEL pm ON pm.idProduit = p.idProduit AND p.type = 'materiel'

ORDER BY l.idLot, co.idColis, p.nom;


--supprimer_produit_du_lot

CREATE OR REPLACE FUNCTION supprimer_produit_du_lot(
  p_id_lot dom_id,
  p_id_produit dom_id
) RETURNS void AS $$
DECLARE
  v_existe BOOLEAN;
BEGIN
  -- Vérifie que le lot est bien lié au produit
  SELECT TRUE INTO v_existe
  FROM lot
  WHERE idLot = p_id_lot AND idProduit = p_id_produit;

  IF NOT v_existe THEN
    RAISE EXCEPTION 'Le produit % n''est pas présent dans le lot %.', p_id_produit, p_id_lot;
  END IF;

  -- Supprimer le lot
  DELETE FROM lot
  WHERE idLot = p_id_lot;
END;
$$ LANGUAGE plpgsql;
