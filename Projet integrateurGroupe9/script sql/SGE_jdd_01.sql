-- =============================================
-- SGE_jdd.sql
-- Jeu de données réaliste pour le SGE
-- =============================================

-- ===============================
-- ORGANISATIONS
-- ===============================
INSERT INTO ORGANISATION(idOrganisation, nom, adresse, telephone, type) VALUES
(1, 'Amazones et Centaures', '123 Rue Principale, Montréal, QC', '+15145551234', 'entreprise'),
(2, 'Fournisseur ABC',        '456 Avenue Commerciale, Laval, QC',   '+15145552345', 'fournisseur'),
(3, 'Transport XYZ',          '789 Boulevard Industriel, Longueuil', '+15145553456', 'transporteur');

-- ===============================
-- ROLES
-- ===============================
INSERT INTO ROLE(idRole, libelle, typeRole) VALUES
(1, 'Magasinier principal',     'magasinier'),
(2, 'Responsable logistique',   'responsable'),
(3, 'Livreur',                  'livreur'),
(4, 'Technicien',               'technicien');

-- ===============================
-- INDIVIDUS
-- ===============================
INSERT INTO INDIVIDU(idIndividu, nom, adresse, telephone, email, password) VALUES
(1, 'Jean Dupont',   '101 Rue des Employés, Montréal', '+15145554567', 'jean.dupont@sac.ca', crypt('Youmto12', gen_salt('bf'))),
(2, 'Marie Tremblay','202 Ave des Gestionnaires, Laval', '+15145555678', 'marie.tremblay@sac.ca', crypt('Youmto12', gen_salt('bf'))),
(3, 'Pierre Gagnon', '303 Blvd des Techniciens, Longueuil', '+15145556789', 'pierre.gagnon@sac.ca', crypt('Youmto12', gen_salt('bf')));

-- ===============================
-- AFFECTATION DES RÔLES
-- ===============================
INSERT INTO AFFECTER_ROLE(idIndividu, idOrganisation, idRole, dateDebut, dateFin, estActif) VALUES
(1, 1, 1, '2024-01-01', NULL, TRUE),
(2, 1, 2, '2024-01-01', NULL, TRUE),
(3, 3, 3, '2024-01-01', NULL, TRUE);

-- ===============================
-- PRODUITS
-- ===============================
INSERT INTO PRODUIT(idProduit, reference, nom, description, marque, modele, type, estMaterielEmballage) VALUES
(100, 'PROD-001', 'Ordinateur portable', 'Ordinateur 15 pouces pro', 'Dell', 'XPS 15', 'materiel', FALSE),
(200, 'PROD-002', 'Boîte carton',        'Boîte moyenne recyclée',  'Uline', 'M-10',  'materiel', TRUE),
(35, 'PROD-003', 'Logiciel de gestion', 'Suite de gestion entrepôt','SAP', 'WM 2.0', 'logiciel', FALSE);

-- ===============================
-- PRODUIT_MATERIEL
-- ===============================
INSERT INTO PRODUIT_MATERIEL(idProduit, longueur, largeur, hauteur, masse, volume) VALUES
(100, 35.0, 24.0, 2.0, 1.5, 1680.0),
(200, 40.0, 30.0, 30.0, 0.3, 36000.0);

-- ===============================
-- PRODUIT_LOGICIEL
-- ===============================
INSERT INTO PRODUIT_LOGICIEL(idProduit, version, typeLicence, dateExpiration) VALUES
(35, '2.0.1', 'perpetuelle', '2026-12-31');

-- ===============================
-- FOURNISSEUR ET APPROVISIONNEMENT
-- ===============================
INSERT INTO FOURNISSEUR(idOrganisation) VALUES (2);

INSERT INTO APPROVISIONNER(idOrganisation, idProduit, delaiLivraisonMoyen, conditionnementStandard) VALUES
(2, 100, 5, 'UNITE'),
(2, 200, 2, 'CARTON-25'),
(2, 35, 1, 'LICENCE');

-- ===============================
-- ENTREPOT
-- ===============================
INSERT INTO ENTREPOT(idEntrepot, nom, adresse, telephone, description, capaciteMaximale, statut) VALUES
(1, 'Entrepôt principal', '123 Rue de l''Entrepôt, Montréal', '+15145557890', 'Entrepôt central de SAC', 200000.0, 'actif');

-- ===============================
-- CELLULES
-- ===============================
INSERT INTO CELLULE(idCellule, reference, longueur, largeur, hauteur, masseMaximale, volumeMaximal, statut, capacite_max, position) VALUES
(1, 'E0-A1', 100.0, 100.0, 250.0, 1000.0, 2500000.0, 'actif', 100, 'Zone E0, Rack A, Niveau 1'),
(2, 'E1-B2', 80.0,  80.0,  200.0, 800.0, 1280000.0, 'actif',  80,  'Zone E1, Rack B, Niveau 2'),
(3, 'EMB-1', 50.0,  50.0,  50.0,  500.0, 125000.0,  'actif',  60,  'Zone emballage, Rack 1');

-- ===============================
-- COMPOSITION ENTREPOT
-- ===============================
INSERT INTO COMPOSER_ENTREPOT(idEntrepot, idCellule) VALUES
(1, 1),
(1, 2),
(1, 3);

-- ===============================
-- LOTS
-- ===============================
INSERT INTO LOT(idLot, numeroLot, quantiteInitiale, quantiteDisponible, dateProduction, dateExpiration, statut, idProduit) VALUES
(15, 'LOT-2023-001', 50, 50, '2023-01-15', '2025-01-15', 'actif', 100),
(25, 'LOT-2023-002', 100, 100, '2023-02-20', NULL,         'actif', 200),
(4, 'LOT-2023-003', 200, 200, '2023-03-10', '2026-03-10', 'actif', 200);

-- ===============================
-- INVENTAIRE
-- ===============================
INSERT INTO INVENTAIRE(idProduit, idOrganisation, quantiteDisponible) VALUES
(100, 1, 50),
(200, 1, 100),
(35, 1, 0);

-- ===============================
-- STOCKER
-- ===============================
INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite) VALUES
(15, 1, '2023-01-20', 50),
(25, 2, '2023-02-25', 100),
(4, 3, '2023-03-15', 200);

-- ===============================
-- BON DE RÉCEPTION
-- ===============================
INSERT INTO BON_RECEPTION(idBon, reference, dateCreation, dateReceptionPrevue, statut) VALUES
(1, 'BR-2023-001', '2023-01-10', '2023-01-18', 'termine'),
(2, 'BR-2023-002', '2023-02-15', '2023-02-22', 'termine');

-- ===============================
-- COLIS (réceptionnés)
-- ===============================
INSERT INTO COLIS(idColis, reference, dateCreation, statut, poidsTotal, volumeTotal) VALUES
(1, 'REC-LOT-2023-001', '2023-01-18', 'recu', 3.5, 2000.0),
(2, 'REC-LOT-2023-002', '2023-02-22', 'recu', 1.2, 36000.0);

-- ===============================
-- RECEVOIR_COLIS
-- ===============================
INSERT INTO RECEVOIR_COLIS(idBon, idColis) VALUES
(1, 1),
(2, 2);

-- ===============================
-- CONTENIR
-- ===============================
INSERT INTO CONTENIR(idColis, idLot, quantite) VALUES
(1, 15, 50),
(2, 25, 100);

-- ===============================
-- RESPONSABLE RÉCEPTION
-- ===============================
INSERT INTO RESPONSABLE_RECEPTION(idIndividu, idBon) VALUES
(2, 1),
(2, 2);

-- ===============================
-- BON D’EXPÉDITION
-- ===============================
INSERT INTO BON_EXPEDITION(idBon, reference, dateCreation, dateExpeditionPrevue, priorite, statut) VALUES
(1, 'BE-2023-001', '2023-03-01', '2023-03-10', 'normal', 'en_attente'),
(2, 'BE-2023-002', '2023-04-01', '2023-04-10', 'urgente', 'en_attente');

-- ===============================
-- RESPONSABLE EXPÉDITION
-- ===============================
INSERT INTO RESPONSABLE_EXPEDITION(idIndividu, idBon) VALUES
(2, 1),
(2, 2);

-- ===============================
-- COMPOSER_EXPEDITION
-- ===============================
INSERT INTO COMPOSER_EXPEDITION(idBon, idProduit, quantite) VALUES
(1, 100, 20),
(1, 200, 30),
(2, 100, 10);

INSERT INTO ORGANISATION (idOrganisation, nom, type)
VALUES (1, 'Entrepôt Principal', 'entrepot')
ON CONFLICT (idOrganisation) DO NOTHING;

INSERT INTO FOURNISSEUR (idOrganisation)
VALUES (1)
ON CONFLICT (idOrganisation) DO NOTHING;




