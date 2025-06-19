-- =============================================
-- SGE_jdd_01.sql
-- Jeu de données de test
-- =============================================

-- ORGANISATIONS
INSERT INTO ORGANISATION(idOrganisation, nom, adresse, telephone, type)
VALUES 
(1, 'Amazones et Centaures', '123 Rue Principale, Montréal, QC', '+15145551234', 'entreprise'),
(2, 'Fournisseur ABC', '456 Avenue Commerciale, Laval, QC', '+15145552345', 'fournisseur'),
(3, 'Transport XYZ', '789 Boulevard Industriel, Longueuil, QC', '+15145553456', 'transporteur');

-- ROLES
INSERT INTO ROLE(idRole, libelle, typeRole)
VALUES 
(1, 'Magasinier principal', 'magasinier'),
(2, 'Responsable logistique', 'responsable'),
(3, 'Livreur', 'livreur'),
(4, 'Technicien', 'technicien');

-- INDIVIDUS
INSERT INTO INDIVIDU(idIndividu, nom, adresse, telephone, email)
VALUES 
(1, 'Jean Dupont', '101 Rue des Employés, Montréal', '+15145554567', 'jean.dupont@sac.ca'),
(2, 'Marie Tremblay', '202 Ave des Gestionnaires, Laval', '+15145555678', 'marie.tremblay@sac.ca'),
(3, 'Pierre Gagnon', '303 Blvd des Techniciens, Longueuil', '+15145556789', 'pierre.gagnon@sac.ca');

-- AFFECTATION ROLES
INSERT INTO AFFECTER_ROLE(idIndividu, idOrganisation, idRole, dateDebut, dateFin, estActif)
VALUES 
(1, 1, 1, '2023-01-01', NULL, TRUE),
(2, 1, 2, '2023-01-01', NULL, TRUE),
(3, 3, 3, '2023-01-01', NULL, TRUE);

-- PRODUITS
INSERT INTO PRODUIT(idProduit, reference, nom, description, marque, modele, type, estMaterielEmballage)
VALUES 
(1, 'PROD-001', 'Ordinateur portable', 'Ordinateur portable 15 pouces', 'Dell', 'XPS 15', 'materiel', FALSE),
(2, 'PROD-002', 'Boîte carton', 'Boîte carton moyen format', 'Uline', 'M-10', 'materiel', TRUE),
(3, 'PROD-003', 'Logiciel gestion', 'Logiciel de gestion d entrepôt', 'SAP', 'WM 2.0', 'logiciel', FALSE);

-- PRODUITS MATERIELS
INSERT INTO PRODUIT_MATERIEL(idProduit, longueur, largeur, hauteur, masse, volume)
VALUES 
(1, 35.5, 23.5, 1.8, 1.8, 1502.65),
(2, 40.0, 30.0, 30.0, 0.5, 36000.0);

-- PRODUITS LOGICIELS
INSERT INTO PRODUIT_LOGICIEL(idProduit, version, typeLicence, dateExpiration)
VALUES 
(3, '2.0.1', 'perpetuelle', NULL);

-- FOURNISSEURS
INSERT INTO FOURNISSEUR(idOrganisation)
VALUES (2);

-- APPROVISIONNEMENT
INSERT INTO APPROVISIONNER(idOrganisation, idProduit, delaiLivraisonMoyen, conditionnementStandard)
VALUES 
(2, 1, 5, 'UNITE'),
(2, 2, 2, 'LOT-10'),
(2, 3, 1, 'LICENCE');

-- ENTREPOTS
INSERT INTO ENTREPOT(idEntrepot, nom, adresse, telephone, description, capaciteMaximale, statut)
VALUES 
(1, 'Entrepôt principal', '123 Rue de l Entrepôt Montréal', '+15145557890', 'Entrepôt principal de la SAC', 100000.0, 'actif');

-- CELLULES
INSERT INTO CELLULE(idCellule, reference, longueur, largeur, hauteur, masseMaximale, volumeMaximal, statut, position)
VALUES 
(1, 'E0-A1', 100.0, 100.0, 250.0, 1000.0, 2500000.0, 'actif', 'Zone E0, Rack A, Niveau 1'),
(2, 'E1-B2', 100.0, 100.0, 250.0, 1000.0, 2500000.0, 'actif', 'Zone E1, Rack B, Niveau 2'),
(3, 'EMB-1', 50.0, 50.0, 50.0, 500.0, 125000.0, 'actif', 'Zone emballage, Rack 1');

-- COMPOSITION ENTREPOT
INSERT INTO COMPOSER_ENTREPOT(idEntrepot, idCellule)
VALUES 
(1, 1),
(1, 2),
(1, 3);

-- LOTS
INSERT INTO LOT(idLot, numeroLot, quantiteInitiale, quantiteDisponible, dateProduction, dateExpiration, statut)
VALUES 
(1, 'LOT-2023-001', 50, 50, '2023-01-15', '2025-01-15', 'actif'),
(2, 'LOT-2023-002', 100, 100, '2023-02-20', NULL, 'actif'),
(3, 'LOT-2023-003', 200, 200, '2023-03-10', '2026-03-10', 'actif');

-- INVENTAIRE
INSERT INTO INVENTAIRE(idProduit, idOrganisation, quantiteDisponible)
VALUES 
(1, 1, 50),
(2, 1, 100),
(3, 1, 200);

-- STOCKAGE
INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite)
VALUES 
(1, 1, '2023-01-20', 50),
(2, 3, '2023-02-25', 100),
(3, 2, '2023-03-15', 200);

-- BONS DE RÉCEPTION
INSERT INTO BON_RECEPTION(idBon, reference, dateCreation, dateReceptionPrevue, statut)
VALUES 
(1, 'BR-2023-001', '2023-01-10', '2023-01-18', 'termine'),
(2, 'BR-2023-002', '2023-02-15', '2023-02-22', 'termine'),
(3, 'BR-2023-003', '2023-03-05', '2023-03-12', 'termine');

-- BONS D'EXPÉDITION
INSERT INTO BON_EXPEDITION(idBon, reference, datecreation, dateexpeditionprevue, priorite, statut)
VALUES 
(1, 'BE-2023-001', '2023-04-01', '2023-04-05', 'normal', 'en_attente'),
(2, 'BE-2023-002', '2023-04-02', '2023-04-06', 'elevee', 'en_attente');

-- RESPONSABLES
INSERT INTO RESPONSABLE_RECEPTION(idIndividu, idBon)
VALUES (2, 1), (2, 2), (2, 3);

INSERT INTO RESPONSABLE_EXPEDITION(idIndividu, idBon)
VALUES (2, 1), (2, 2);