-- =============================================
-- SGE_cre.sql
-- Schéma complet avec domaines personnalisés
-- Système de Gestion d'Entrepôt (SGE)
-- Projet Amazones et Centaures (SAC)
-- Basé sur le modèle fourni
-- =============================================

-- Suppression des tables existantes (pour réinitialisation)
DROP TABLE IF EXISTS GENERER_RAPPORT CASCADE;
DROP TABLE IF EXISTS RAPPORT_EXCEPTION CASCADE;
DROP TABLE IF EXISTS RESPONSABLE_EXPEDITION CASCADE;
DROP TABLE IF EXISTS EXPEDIER_COLIS CASCADE;
DROP TABLE IF EXISTS BON_EXPEDITION CASCADE;
DROP TABLE IF EXISTS RESPONSABLE_RECEPTION CASCADE;
DROP TABLE IF EXISTS RECEVOIR_COLIS CASCADE;
DROP TABLE IF EXISTS BON_RECEPTION CASCADE;
DROP TABLE IF EXISTS UTILISER_EMBALLAGE CASCADE;
DROP TABLE IF EXISTS STOCKER CASCADE;
DROP TABLE IF EXISTS CONTENIR CASCADE;
DROP TABLE IF EXISTS COLIS CASCADE;
DROP TABLE IF EXISTS LOT CASCADE;
DROP TABLE IF EXISTS COMPOSER_ENTREPOT CASCADE;
DROP TABLE IF EXISTS CELLULE CASCADE;
DROP TABLE IF EXISTS ENTREPOT CASCADE;
DROP TABLE IF EXISTS INVENTAIRE CASCADE;
DROP TABLE IF EXISTS APPROVISIONNER CASCADE;
DROP TABLE IF EXISTS FOURNISSEUR CASCADE;
DROP TABLE IF EXISTS PRODUIT_LOGICIEL CASCADE;
DROP TABLE IF EXISTS PRODUIT_MATERIEL CASCADE;
DROP TABLE IF EXISTS PRODUIT CASCADE;
DROP TABLE IF EXISTS AFFECTER_ROLE CASCADE;
DROP TABLE IF EXISTS INDIVIDU CASCADE;
DROP TABLE IF EXISTS ROLE CASCADE;
DROP TABLE IF EXISTS ORGANISATION CASCADE;

-- Suppression des domaines existants
DROP DOMAIN IF EXISTS dom_id CASCADE;
DROP DOMAIN IF EXISTS dom_nom CASCADE;
DROP DOMAIN IF EXISTS dom_texte CASCADE;
DROP DOMAIN IF EXISTS dom_telephone CASCADE;
DROP DOMAIN IF EXISTS dom_email CASCADE;
DROP DOMAIN IF EXISTS dom_date CASCADE;
DROP DOMAIN IF EXISTS dom_boolean CASCADE;
DROP DOMAIN IF EXISTS dom_type CASCADE;
DROP DOMAIN IF EXISTS dom_reference CASCADE;
DROP DOMAIN IF EXISTS dom_quantite CASCADE;
DROP DOMAIN IF EXISTS dom_float CASCADE;
DROP DOMAIN IF EXISTS dom_position CASCADE;
DROP DOMAIN IF EXISTS dom_statut CASCADE;
DROP DOMAIN IF EXISTS DOM_TYPE_PRODUIT CASCADE;
DROP DOMAIN IF EXISTS DOM_TYPE_ROLE CASCADE;

-- =============================
-- DOMAINES PERSONNALISÉS
-- =============================

-- Domaine pour les identifiants
CREATE DOMAIN dom_id AS INTEGER
CHECK (VALUE > 0);

-- Domaine pour les noms
CREATE DOMAIN dom_nom AS VARCHAR(100)
CHECK (VALUE !~ '^\s*$');

-- Domaine pour les textes longs
CREATE DOMAIN dom_texte AS TEXT;

-- Domaine pour les téléphones
CREATE DOMAIN dom_telephone AS VARCHAR(20)
CHECK (VALUE ~ '^[0-9+][0-9 -]*$');

-- Domaine pour les emails
CREATE DOMAIN dom_email AS VARCHAR(100)
CHECK (VALUE ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Domaine pour les dates
CREATE DOMAIN dom_date AS DATE;

-- Domaine pour les booléens
CREATE DOMAIN dom_boolean AS BOOLEAN;

-- Domaine pour les types génériques
CREATE DOMAIN dom_type AS VARCHAR(50);

-- Domaine pour les références
CREATE DOMAIN dom_reference AS VARCHAR(50)
CHECK (VALUE !~ '^\s*$');

-- Domaine pour les quantités
CREATE DOMAIN dom_quantite AS INTEGER
CHECK (VALUE >= 0);

-- Domaine pour les valeurs décimales
CREATE DOMAIN dom_float AS FLOAT
CHECK (VALUE >= 0);

-- Domaine pour les positions
CREATE DOMAIN dom_position AS VARCHAR(50);

-- Domaine pour les statuts
CREATE DOMAIN dom_statut AS VARCHAR(20)
CHECK (VALUE IN ('actif', 'inactif', 'en_attente', 'en_cours', 'termine', 'annule'));

-- Domaine pour les types de produits
CREATE DOMAIN DOM_TYPE_PRODUIT AS VARCHAR(50)
CHECK (VALUE IN ('materiel', 'logiciel', 'service'));

-- Domaine pour les types de rôles
CREATE DOMAIN DOM_TYPE_ROLE AS VARCHAR(50)
CHECK (VALUE IN ('magasinier', 'responsable', 'livreur', 'technicien', 'gestionnaire', 'securite'));

-- =============================
-- TABLES DE BASE
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
    typeRole DOM_TYPE_ROLE
);

CREATE TABLE INDIVIDU (
    idIndividu dom_id PRIMARY KEY,
    nom dom_nom,
    adresse dom_texte,
    telephone dom_telephone,
    email dom_email
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
-- PRODUITS ET DÉRIVÉS
-- =============================

CREATE TABLE PRODUIT (
    idProduit dom_id PRIMARY KEY,
    reference dom_reference,
    nom dom_nom,
    description dom_texte,
    marque dom_type,
    modele dom_type,
    type DOM_TYPE_PRODUIT,
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
-- FOURNISSEUR
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

-- =============================
-- ENTREPÔT ET STRUCTURES
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
-- LOTS ET COLIS
-- =============================

CREATE TABLE LOT (
    idLot dom_id PRIMARY KEY,
    numeroLot dom_reference,
    quantiteInitiale dom_quantite,
    quantiteDisponible dom_quantite,
    dateProduction dom_date,
    dateExpiration dom_date,
    statut dom_type
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
-- RÉCEPTION
-- =============================

CREATE TABLE BON_RECEPTION (
    idBon dom_id PRIMARY KEY,
    reference dom_reference,
    dateCreation dom_date,
    dateReceptionPrevue dom_date,
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
-- EXPÉDITION
-- =============================

CREATE TABLE BON_EXPEDITION (
    idBon dom_id PRIMARY KEY,
    reference dom_reference,
    dateCreation dom_date,
    dateExpeditionPrevue dom_date,
    priorite dom_statut,
    statut dom_statut
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
    quantiteDisponible dom_quantite,
    PRIMARY KEY (idProduit, idOrganisation),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit),
    FOREIGN KEY (idOrganisation) REFERENCES ORGANISATION(idOrganisation)
);

-- =============================
-- FIN DU SCRIPT
-- =============================