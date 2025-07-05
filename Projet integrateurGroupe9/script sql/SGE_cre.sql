-- ================================
-- SGE_STRUCTURE_PRO.sql
-- Base complète robuste pour Système de Gestion d’Entrepôt (SGE)
-- Amazones et Centaures (SAC)
-- ================================

-- Suppression préalable
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- =============================
-- DOMAINES PERSONNALISÉS
-- =============================

CREATE DOMAIN dom_id AS INTEGER CHECK (VALUE > 0);
CREATE DOMAIN dom_nom AS VARCHAR(100) CHECK (VALUE !~ '^\s*$');
CREATE DOMAIN dom_texte AS TEXT;
CREATE DOMAIN dom_telephone AS VARCHAR(20) CHECK (VALUE ~ '^[0-9+][0-9 -]*$');
CREATE DOMAIN dom_email AS VARCHAR(100) CHECK (VALUE ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
CREATE DOMAIN dom_date AS DATE;
CREATE DOMAIN dom_boolean AS BOOLEAN;
CREATE DOMAIN dom_type AS VARCHAR(50);
CREATE DOMAIN dom_reference AS VARCHAR(50) CHECK (VALUE !~ '^\s*$');
CREATE DOMAIN dom_quantite AS INTEGER CHECK (VALUE >= 0);
CREATE DOMAIN dom_float AS FLOAT CHECK (VALUE >= 0);
CREATE DOMAIN dom_position AS VARCHAR(50);
CREATE DOMAIN dom_statut AS VARCHAR(20) CHECK (
    VALUE IN ('actif', 'inactif', 'en_attente', 'en_cours', 'termine', 'annule', 'pret_a_expedier')
);
CREATE DOMAIN dom_type_produit AS VARCHAR(50) CHECK (VALUE IN ('materiel', 'logiciel', 'service'));
CREATE DOMAIN dom_type_role AS VARCHAR(50) CHECK (
    VALUE IN ('magasinier', 'responsable', 'livreur', 'technicien', 'gestionnaire', 'securite')
);

-- =============================
-- ORGANISATION & UTILISATEURS
-- =============================

CREATE TABLE ORGANISATION (
    idOrganisation dom_id PRIMARY KEY,
    nom dom_nom,
    adresse dom_texte,
    telephone dom_telephone,
    type dom_type
);

CREATE TABLE ROLE (
    idRole dom_id PRIMARY KEY,
    libelle dom_type,
    typeRole dom_type_role
);

CREATE TABLE INDIVIDU (
    idIndividu dom_id PRIMARY KEY,
    nom dom_nom,
    adresse dom_texte,
    telephone dom_telephone,
    email dom_email,
	password TEXT
);

CREATE TABLE AFFECTER_ROLE (
    idIndividu dom_id,
    idOrganisation dom_id,
    idRole dom_id,
    dateDebut dom_date,
    dateFin dom_date,
    estActif dom_boolean,
    PRIMARY KEY (idIndividu, idOrganisation, idRole),
    FOREIGN KEY (idIndividu) REFERENCES INDIVIDU(idIndividu),
    FOREIGN KEY (idOrganisation) REFERENCES ORGANISATION(idOrganisation),
    FOREIGN KEY (idRole) REFERENCES ROLE(idRole)
);

-- =============================
-- PRODUITS
-- =============================

CREATE TABLE PRODUIT (
    idProduit dom_id PRIMARY KEY,
    reference dom_reference,
    nom dom_nom,
    description dom_texte,
    marque dom_type,
    modele dom_type,
    type dom_type_produit,
    estMaterielEmballage dom_boolean
);

CREATE TABLE PRODUIT_MATERIEL (
    idProduit dom_id PRIMARY KEY,
    longueur dom_float,
    largeur dom_float,
    hauteur dom_float,
    masse dom_float,
    volume dom_float,
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);

CREATE TABLE PRODUIT_LOGICIEL (
    idProduit dom_id PRIMARY KEY,
    version dom_type,
    typeLicence dom_type,
    dateExpiration dom_date,
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);

-- =============================
-- FOURNISSEUR & APPROVISIONNER
-- =============================

CREATE TABLE FOURNISSEUR (
    idOrganisation dom_id PRIMARY KEY,
    FOREIGN KEY (idOrganisation) REFERENCES ORGANISATION(idOrganisation)
);

CREATE TABLE APPROVISIONNER (
    idOrganisation dom_id,
    idProduit dom_id,
    delaiLivraisonMoyen dom_quantite,
    conditionnementStandard dom_reference,
    PRIMARY KEY (idOrganisation, idProduit),
    FOREIGN KEY (idOrganisation) REFERENCES FOURNISSEUR(idOrganisation),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);

CREATE TABLE DEMANDE_APPROVISIONNEMENT (
    idDemande SERIAL PRIMARY KEY,
    idOrganisation dom_id,
    idProduit dom_id NOT NULL,
    quantite dom_quantite NOT NULL CHECK (quantite > 0),
    dateDemande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dateLivraisonPrevue dom_date NOT NULL,
    statut dom_statut DEFAULT 'en_attente',

    FOREIGN KEY (idOrganisation) REFERENCES FOURNISSEUR(idOrganisation),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);

-- =============================
-- ENTREPÔT & CELLULES
-- =============================

CREATE TABLE ENTREPOT (
    idEntrepot dom_id PRIMARY KEY,
    nom dom_nom,
    adresse dom_texte,
    telephone dom_telephone,
    description dom_texte,
    capaciteMaximale dom_float,
    statut dom_statut
);

CREATE TABLE CELLULE (
    idCellule dom_id PRIMARY KEY,
    reference dom_reference,
    longueur dom_float,
    largeur dom_float,
    hauteur dom_float,
    masseMaximale dom_float,
    volumeMaximal dom_float,
    statut dom_statut,
    capacite_max dom_quantite, 
    position dom_position
);


CREATE TABLE COMPOSER_ENTREPOT (
    idEntrepot dom_id,
    idCellule dom_id,
    PRIMARY KEY (idEntrepot, idCellule),
    FOREIGN KEY (idEntrepot) REFERENCES ENTREPOT(idEntrepot),
    FOREIGN KEY (idCellule) REFERENCES CELLULE(idCellule)
);

-- =============================
-- LOTS & COLIS
-- =============================

CREATE TABLE LOT (
    idLot dom_id PRIMARY KEY,
    numeroLot dom_reference,
    quantiteInitiale dom_quantite,
    quantiteDisponible dom_quantite,
    dateProduction dom_date,
    dateExpiration dom_date,
    statut dom_type,
    idProduit dom_id REFERENCES PRODUIT(idProduit)
);

CREATE TABLE COLIS (
    idColis dom_id PRIMARY KEY,
    reference dom_reference,
    dateCreation dom_date,
    statut dom_type,
    poidsTotal dom_float,
    volumeTotal dom_float
);

CREATE TABLE CONTENIR (
    idColis dom_id,
    idLot dom_id,
    quantite dom_quantite,
    PRIMARY KEY (idColis, idLot),
    FOREIGN KEY (idColis) REFERENCES COLIS(idColis),
    FOREIGN KEY (idLot) REFERENCES LOT(idLot)
);

-- =============================
-- STOCKAGE
-- =============================

CREATE TABLE STOCKER (
    idLot dom_id,
    idCellule dom_id,
    dateStockage dom_date,
    quantite dom_quantite,
    PRIMARY KEY (idLot, idCellule),
    FOREIGN KEY (idLot) REFERENCES LOT(idLot),
    FOREIGN KEY (idCellule) REFERENCES CELLULE(idCellule)
);

-- =============================
-- EMBALLAGE
-- =============================

CREATE TABLE UTILISER_EMBALLAGE (
    idColis dom_id,
    idProduit dom_id,
    quantiteUtilisee dom_quantite,
    estReutilise dom_boolean,
    PRIMARY KEY (idColis, idProduit),
    FOREIGN KEY (idColis) REFERENCES COLIS(idColis),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);

-- =============================
-- BON DE RÉCEPTION
-- =============================

CREATE TABLE BON_RECEPTION (
    idBon dom_id PRIMARY KEY,
    reference dom_reference,
    dateCreation dom_date,
    dateReceptionPrevue dom_date,
    dateReceptionReelle dom_date, 
    statut dom_statut
);


CREATE TABLE RECEVOIR_COLIS (
    idBon dom_id,
    idColis dom_id,
    PRIMARY KEY (idBon, idColis),
    FOREIGN KEY (idBon) REFERENCES BON_RECEPTION(idBon),
    FOREIGN KEY (idColis) REFERENCES COLIS(idColis)
);

CREATE TABLE RESPONSABLE_RECEPTION (
    idIndividu dom_id,
    idBon dom_id,
    PRIMARY KEY (idIndividu, idBon),
    FOREIGN KEY (idIndividu) REFERENCES INDIVIDU(idIndividu),
    FOREIGN KEY (idBon) REFERENCES BON_RECEPTION(idBon)
);

-- =============================
-- BON D’EXPÉDITION
-- =============================

CREATE TABLE BON_EXPEDITION (
    idBon dom_id PRIMARY KEY,
    reference dom_reference,
    dateCreation dom_date,
    dateExpeditionPrevue dom_date,
    statut dom_statut DEFAULT 'en_attente',
    priorite TEXT DEFAULT 'normal',
    dateExpeditionReelle dom_date
);

CREATE TABLE EXPEDIER_COLIS (
    idBon dom_id,
    idColis dom_id,
    PRIMARY KEY (idBon, idColis),
    FOREIGN KEY (idBon) REFERENCES BON_EXPEDITION(idBon),
    FOREIGN KEY (idColis) REFERENCES COLIS(idColis)
);

CREATE TABLE RESPONSABLE_EXPEDITION (
    idIndividu dom_id,
    idBon dom_id,
    PRIMARY KEY (idIndividu, idBon),
    FOREIGN KEY (idIndividu) REFERENCES INDIVIDU(idIndividu),
    FOREIGN KEY (idBon) REFERENCES BON_EXPEDITION(idBon)
);

CREATE TABLE COMPOSER_EXPEDITION (
    idBon dom_id,
    idProduit dom_id,
    quantite dom_quantite CHECK (quantite > 0),
    PRIMARY KEY (idBon, idProduit),
    FOREIGN KEY (idBon) REFERENCES BON_EXPEDITION(idBon) ON DELETE CASCADE,
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);

-- =============================
-- RAPPORTS
-- =============================

CREATE TABLE RAPPORT_EXCEPTION (
    idRapport dom_id PRIMARY KEY,
    typeRapport dom_type,
    dateGeneration dom_date,
    description dom_texte,
    idBonReception dom_id,
    idBonExpedition dom_id,
    FOREIGN KEY (idBonReception) REFERENCES BON_RECEPTION(idBon),
    FOREIGN KEY (idBonExpedition) REFERENCES BON_EXPEDITION(idBon)
);

CREATE TABLE GENERER_RAPPORT (
    idIndividu dom_id,
    idRapport dom_id,
    PRIMARY KEY (idIndividu, idRapport),
    FOREIGN KEY (idIndividu) REFERENCES INDIVIDU(idIndividu),
    FOREIGN KEY (idRapport) REFERENCES RAPPORT_EXCEPTION(idRapport)
);

-- =============================
-- INVENTAIRE
-- =============================

CREATE TABLE INVENTAIRE (
    idProduit dom_id,
    idOrganisation dom_id,
    PRIMARY KEY (idProduit, idOrganisation),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit),
    FOREIGN KEY (idOrganisation) REFERENCES ORGANISATION(idOrganisation)
);



--Ajouter colunm password
ALTER TABLE INDIVIDU
ADD COLUMN password TEXT;

ALTER TABLE INVENTAIRE
ADD COLUMN quantitedisponible dom_quantite;

-- Extension pour le cryptage
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- Ajouter colunm capacite_max
ALTER TABLE CELLULE
ADD COLUMN capacite_max dom_quantite;

--Ajouter column dateReceptionRelle
ALTER TABLE BON_RECEPTION
ADD COLUMN dateReceptionReelle DATE;
--auto increment id lot
CREATE SEQUENCE IF NOT EXISTS lot_idlot_seq
START WITH 100 INCREMENT BY 1 CACHE 10;

ALTER TABLE LOT
ALTER COLUMN idLot SET DEFAULT nextval('lot_idlot_seq');

