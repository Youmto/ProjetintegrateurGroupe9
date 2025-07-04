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
(51, 'PROD-001', 'Smartphone', 'Téléphone intelligent haut de gamme', 'Samsung', 'Galaxy S25', 'materiel', FALSE),
(52, 'PROD-002', 'Tablette graphique', 'Tablette pour dessinateurs professionnels', 'Wacom', 'Intuos Pro L', 'materiel', FALSE),
(53, 'PROD-003', 'Serveur rackable', 'Serveur puissant pour centre de données', 'HP', 'ProLiant DL380', 'materiel', FALSE),
(4, 'PROD-004', 'Disque dur externe', 'Disque de stockage portable 2To', 'Seagate', 'Backup Plus', 'materiel', FALSE),
(5, 'PROD-005', 'Casque audio sans fil', 'Casque avec annulation de bruit', 'Sony', 'WH-1000XM6', 'materiel', FALSE),
(6, 'PROD-006', 'Webcam 4K', 'Webcam haute résolution pour visioconférence', 'Logitech', 'Brio 500', 'materiel', FALSE),
(7, 'PROD-007', 'Imprimante laser couleur', 'Imprimante pour bureau', 'Brother', 'HL-L8360CDW', 'materiel', FALSE),
(8, 'PROD-008', 'Routeur Wi-Fi 6', 'Routeur haute performance', 'TP-Link', 'Archer AXE75', 'materiel', FALSE),
(9, 'PROD-009', 'Ecran PC 27 pouces', 'Moniteur QHD pour gaming', 'Dell', 'S2721DGF', 'materiel', FALSE),
(10, 'PROD-010', 'Clavier mécanique RGB', 'Clavier de gaming rétroéclairé', 'Corsair', 'K70 RGB MK.2', 'materiel', FALSE),
(54, 'PROD-011', 'Souris gaming', 'Souris haute précision', 'Razer', 'DeathAdder V3', 'materiel', FALSE),
(12, 'PROD-012', 'Boîte d''archives', 'Boîte en carton renforcée', 'Fellowes', 'Bankers Box', 'materiel', TRUE),
(13, 'PROD-013', 'Film étirable', 'Film pour palettisation', '3M', 'Stretch Wrap', 'materiel', TRUE),
(14, 'PROD-014', 'Adhésif d''emballage', 'Ruban adhésif puissant', 'Scotch', 'Heavy Duty', 'materiel', TRUE),
(15, 'PROD-015', 'Logiciel CRM', 'Solution de gestion de la relation client', 'Salesforce', 'Sales Cloud', 'logiciel', FALSE),
(16, 'PROD-016', 'Antivirus professionnel', 'Protection pour entreprises', 'Kaspersky', 'Endpoint Security', 'logiciel', FALSE),
(17, 'PROD-017', 'Suite bureautique', 'Logiciel de productivité', 'Microsoft', 'Office 365 Business', 'logiciel', FALSE),
(18, 'PROD-018', 'Logiciel de CAO', 'Conception assistée par ordinateur', 'Autodesk', 'AutoCAD 2026', 'logiciel', FALSE),
(19, 'PROD-019', 'Système d''exploitation serveur', 'OS pour serveurs', 'Microsoft', 'Windows Server 2022', 'logiciel', FALSE),
(20, 'PROD-020', 'Logiciel de comptabilité', 'Gestion des finances', 'Sage', '50cloud Comptabilité', 'logiciel', FALSE),
(55, 'PROD-021', 'Chaise de bureau ergonomique', 'Chaise de bureau confortable', 'Herman Miller', 'Aeron', 'materiel', FALSE),
(22, 'PROD-022', 'Station de travail graphique', 'PC haute performance pour professionnels', 'Dell', 'Precision 5860', 'materiel', FALSE),
(23, 'PROD-023', 'Projecteur interactif', 'Projecteur pour salles de réunion', 'Epson', 'BrightLink 735Fi', 'materiel', FALSE),
(24, 'PROD-024', 'Système de vidéoconférence', 'Solution complète pour réunions en ligne', 'Poly', 'Studio X50', 'materiel', FALSE),
(25, 'PROD-025', 'Onduleur UPS', 'Protection contre les coupures de courant', 'APC', 'Smart-UPS 1500VA', 'materiel', FALSE),
(26, 'PROD-026', 'Scanner de documents', 'Scanner rapide pour bureau', 'Fujitsu', 'ScanSnap iX1600', 'materiel', FALSE),
(27, 'PROD-027', 'Téléphone IP', 'Téléphone pour système VoIP', 'Cisco', 'Cisco 8845', 'materiel', FALSE),
(28, 'PROD-028', 'Borne Wi-Fi extérieur', 'Point d''accès pour zones extérieures', 'Ubiquiti', 'UniFi AC Mesh Pro', 'materiel', FALSE),
(29, 'PROD-029', 'Disque SSD interne', 'Stockage rapide pour PC', 'Samsung', '990 PRO 2TB', 'materiel', FALSE),
(30, 'PROD-030', 'Carte graphique gaming', 'Carte graphique haute performance', 'NVIDIA', 'GeForce RTX 5090', 'materiel', FALSE),
(31, 'PROD-031', 'Câble réseau Ethernet', 'Câble Cat6a 10m', 'Monoprice', 'Cat6a Patch', 'materiel', TRUE),
(32, 'PROD-032', 'Etiquettes adhésives', 'Rouleau d''étiquettes thermique', 'Dymo', 'LabelWriter', 'materiel', TRUE),
(33, 'PROD-033', 'Pistolet à ruban adhésif', 'Distributeur de ruban', 'Scotch', 'Tape Dispenser', 'materiel', TRUE),
(34, 'PROD-034', 'Logiciel de gestion de projet', 'Outil de planification et suivi', 'Atlassian', 'Jira Software', 'logiciel', FALSE),
(56, 'PROD-035', 'Logiciel de modélisation 3D', 'Création de modèles 3D', 'Trimble', 'SketchUp Pro', 'logiciel', FALSE),
(36, 'PROD-036', 'Logiciel de retouche photo', 'Édition d''images professionnelle', 'Adobe', 'Photoshop 2026', 'logiciel', FALSE),
(37, 'PROD-037', 'Logiciel de gestion de base de données', 'Système de gestion de base de données', 'Oracle', 'Database 23c', 'logiciel', FALSE),
(38, 'PROD-038', 'Logiciel de sauvegarde et récupération', 'Protection des données', 'Veeam', 'Backup & Replication', 'logiciel', FALSE),
(39, 'PROD-039', 'Logiciel de gestion des stocks', 'Optimisation de l''inventaire', 'SAP', 'EWM', 'logiciel', FALSE),
(40, 'PROD-040', 'Logiciel de cybersécurité', 'Protection avancée contre les menaces', 'CrowdStrike', 'Falcon Insight', 'logiciel', FALSE),
(41, 'PROD-041', 'Robot de palettisation', 'Robot pour automatisation d''entrepôt', 'FANUC', 'M-410iB', 'materiel', FALSE),
(42, 'PROD-042', 'Transpalette électrique', 'Engin de manutention', 'Jungheinrich', 'ECE 225', 'materiel', FALSE),
(43, 'PROD-043', 'Chariot élévateur', 'Engin de levage pour entrepôt', 'Toyota', '8FGCU25', 'materiel', FALSE),
(44, 'PROD-044', 'Système de rayonnage industriel', 'Rayonnage pour stockage en hauteur', 'Mecalux', 'Pallet Racking', 'materiel', FALSE),
(45, 'PROD-045', 'Porte sectionnelle industrielle', 'Porte pour quai de chargement', 'Hörmann', 'ALR F42', 'materiel', FALSE),
(46, 'PROD-046', 'Caméra de surveillance IP', 'Caméra pour sécurité d''entrepôt', 'Axis', 'P3245-LV', 'materiel', FALSE),
(47, 'PROD-047', 'Lecteur de codes-barres sans fil', 'Scanner pour inventaire', 'Zebra', 'DS2278', 'materiel', FALSE),
(48, 'PROD-048', 'Balance industrielle', 'Balance de précision pour poids lourds', 'Mettler Toledo', 'IND236', 'materiel', FALSE),
(49, 'PROD-049', 'Logiciel de gestion de flotte', 'Optimisation des livraisons', 'Geotab', 'Fleet Management', 'logiciel', FALSE),
(50, 'PROD-050', 'Logiciel de planification des ressources', 'ERP complet', 'SAP', 'S/4HANA', 'logiciel', FALSE);


---
---
-- ===============================
-- PRODUIT_MATERIEL
-- ===============================
INSERT INTO PRODUIT_MATERIEL(idProduit, longueur, largeur, hauteur, masse, volume) VALUES
(51, 15.0, 7.0, 0.8, 0.2, 84.0),
(52, 38.0, 25.0, 1.5, 1.0, 1425.0),
(53, 80.0, 45.0, 9.0, 25.0, 32400.0),
(4, 12.0, 8.0, 2.0, 0.25, 192.0),
(5, 20.0, 18.0, 7.0, 0.3, 2520.0),
(6, 9.0, 5.0, 3.0, 0.1, 135.0),
(7, 45.0, 40.0, 30.0, 15.0, 54000.0),
(8, 25.0, 15.0, 5.0, 0.5, 1875.0),
(9, 60.0, 40.0, 5.0, 6.0, 12000.0),
(10, 45.0, 15.0, 4.0, 1.2, 2700.0),
(54, 12.0, 7.0, 4.0, 0.15, 336.0),
(12, 50.0, 30.0, 20.0, 0.5, 30000.0),
(13, 30.0, 10.0, 10.0, 0.1, 3000.0),
(14, 15.0, 5.0, 5.0, 0.05, 375.0),
(55, 70.0, 70.0, 120.0, 20.0, 588000.0),
(22, 50.0, 20.0, 45.0, 10.0, 45000.0),
(23, 35.0, 30.0, 15.0, 5.0, 15750.0),
(24, 60.0, 20.0, 10.0, 3.0, 12000.0),
(25, 30.0, 15.0, 20.0, 10.0, 9000.0),
(26, 30.0, 15.0, 10.0, 2.0, 4500.0),
(27, 25.0, 20.0, 10.0, 1.5, 5000.0),
(28, 30.0, 20.0, 10.0, 1.0, 6000.0),
(29, 8.0, 2.0, 0.5, 0.05, 8.0),
(30, 30.0, 15.0, 5.0, 1.5, 2250.0),
(31, 1.0, 1.0, 1000.0, 0.1, 1000.0), -- Longueur ici est la longueur du câble en cm
(32, 10.0, 10.0, 10.0, 0.2, 1000.0),
(33, 20.0, 5.0, 10.0, 0.3, 1000.0),
(41, 200.0, 150.0, 250.0, 500.0, 75000000.0),
(42, 180.0, 70.0, 120.0, 300.0, 15120000.0),
(43, 250.0, 120.0, 220.0, 4000.0, 66000000.0),
(44, 500.0, 100.0, 600.0, 100.0, 300000000.0),
(45, 400.0, 100.0, 400.0, 200.0, 160000000.0),
(46, 15.0, 10.0, 10.0, 0.5, 1500.0),
(47, 18.0, 7.0, 9.0, 0.3, 1134.0),
(48, 100.0, 100.0, 10.0, 50.0, 100000.0);

---
-- ===============================
-- PRODUIT_LOGICIEL
-- ===============================
INSERT INTO PRODUIT_LOGICIEL(idProduit, version, typeLicence, dateExpiration) VALUES
(15, '2025.1', 'annuelle', '2026-06-30'),
(16, '15.0.3', 'perpetuelle', '2030-01-01'),
(17, '2025.0', 'mensuelle', '2025-08-31'),
(18, '2026.0', 'perpetuelle', NULL),
(19, '2022', 'annuelle', '2026-03-15'),
(20, '2025.R1', 'perpetuelle', NULL),
(34, '7.0', 'annuelle', '2026-07-01'),
(56, '2024.1', 'perpetuelle', NULL),
(36, '2026.0', 'mensuelle', '2025-09-30'),
(37, '23c', 'perpetuelle', NULL),
(38, '12.0', 'annuelle', '2026-05-20'),
(39, '9.0', 'perpetuelle', NULL),
(40, '6.5', 'annuelle', '2026-02-28'),
(49, '3.0', 'mensuelle', '2025-10-15'),
(50, '2025', 'perpetuelle', NULL);


---
-- ===============================
-- FOURNISSEUR ET APPROVISIONNEMENT
-- ===============================
INSERT INTO FOURNISSEUR(idOrganisation) VALUES (2);

INSERT INTO APPROVISIONNER(idOrganisation, idProduit, delaiLivraisonMoyen, conditionnementStandard) VALUES
(2, 51, 7, 'UNITE'),
(2, 52, 6, 'BOITE-1'),
(2, 53, 10, 'UNITE'),
(2, 4, 3, 'PACK-5'),
(2, 5, 4, 'UNITE'),
(2, 6, 2, 'UNITE'),
(2, 7, 8, 'PALETTE'),
(2, 8, 5, 'CARTON-10'),
(2, 9, 7, 'UNITE'),
(2, 10, 3, 'UNITE'),
(2, 54, 2, 'UNITE'),
(2, 12, 1, 'PALETTE-50'),
(2, 13, 2, 'ROULEAU'),
(2, 14, 1, 'CARTON-20'),
(2, 15, 0, 'LICENCE'),
(2, 16, 0, 'LICENCE'),
(2, 17, 0, 'LICENCE'),
(2, 18, 0, 'LICENCE'),
(2, 19, 0, 'LICENCE'),
(2, 20, 0, 'LICENCE'),
(2, 55, 9, 'UNITE'),
(2, 22, 12, 'UNITE'),
(2, 23, 8, 'UNITE'),
(2, 24, 7, 'KIT'),
(2, 25, 6, 'UNITE'),
(2, 26, 4, 'UNITE'),
(2, 27, 5, 'UNITE'),
(2, 28, 6, 'UNITE'),
(2, 29, 2, 'UNITE'),
(2, 30, 5, 'UNITE'),
(2, 31, 1, 'ROULEAU-100m'),
(2, 32, 2, 'BOITE-500'),
(2, 33, 1, 'UNITE'),
(2, 34, 0, 'LICENCE'),
(2, 56, 0, 'LICENCE'),
(2, 36, 0, 'LICENCE'),
(2, 37, 0, 'LICENCE'),
(2, 38, 0, 'LICENCE'),
(2, 39, 0, 'LICENCE'),
(2, 40, 0, 'LICENCE'),
(2, 41, 15, 'UNITE'),
(2, 42, 10, 'UNITE'),
(2, 43, 14, 'UNITE'),
(2, 44, 20, 'SECTION'),
(2, 45, 18, 'UNITE'),
(2, 46, 5, 'UNITE'),
(2, 47, 3, 'UNITE'),
(2, 48, 8, 'UNITE'),
(2, 49, 0, 'LICENCE'),
(2, 50, 0, 'LICENCE');


---
-- ===============================
-- ENTREPOT
-- ===============================
INSERT INTO ENTREPOT(idEntrepot, nom, adresse, telephone, description, capaciteMaximale, statut) VALUES
(1, 'Entrepôt principal', '123 Rue de l''Entrepôt, Montréal', '+15145557890', 'Entrepôt central de SAC', 200000.0, 'actif');

---
-- ===============================
-- CELLULES
-- ===============================
INSERT INTO CELLULE(idCellule, reference, longueur, largeur, hauteur, masseMaximale, volumeMaximal, statut, capacite_max, position) VALUES
(101, 'EO-Z1-R1-N1', 120.0, 100.0, 300.0, 1500.0, 3600000.0, 'actif', 120, 'Zone 1, Rack 1, Niveau 1'),
(102, 'EO-Z1-R1-N2', 120.0, 100.0, 300.0, 1500.0, 3600000.0, 'actif', 120, 'Zone 1, Rack 1, Niveau 2'),
(103, 'EO-Z2-R2-N1', 150.0, 120.0, 280.0, 2000.0, 5040000.0, 'actif', 150, 'Zone 2, Rack 2, Niveau 1'),
(104, 'EO-Z2-R2-N2', 150.0, 120.0, 280.0, 2000.0, 5040000.0, 'actif', 150, 'Zone 2, Rack 2, Niveau 2'),
(105, 'EO-EMB-ZONE', 60.0, 60.0, 60.0, 600.0, 216000.0, 'actif', 75, 'Zone emballage Ouest'),
(201, 'EE-Z1-R1-N1', 110.0, 90.0, 280.0, 1200.0, 2772000.0, 'actif', 100, 'Zone 1, Rack 1, Niveau 1'),
(202, 'EE-Z1-R1-N2', 110.0, 90.0, 280.0, 1200.0, 2772000.0, 'actif', 100, 'Zone 1, Rack 1, Niveau 2'),
(203, 'EE-Z2-R2-N1', 130.0, 110.0, 260.0, 1800.0, 3718000.0, 'actif', 130, 'Zone 2, Rack 2, Niveau 1'),
(204, 'EE-Z2-R2-N2', 130.0, 110.0, 260.0, 1800.0, 3718000.0, 'actif', 130, 'Zone 2, Rack 2, Niveau 2'),
(205, 'EE-EMB-ZONE', 55.0, 55.0, 55.0, 550.0, 166375.0, 'actif', 65, 'Zone emballage Est');

---
-- ===============================
-- COMPOSITION ENTREPOT
-- ===============================
INSERT INTO COMPOSER_ENTREPOT(idEntrepot, idCellule) VALUES
(1, 101),
(1, 102),
(1, 103),
(1, 104),
(1, 105),
(1, 201),
(1, 202),
(1, 203),
(1, 204),
(1, 205);

---
-- ===============================
-- LOTS
-- ===============================
INSERT INTO LOT(idLot, numeroLot, quantiteInitiale, quantiteDisponible, dateProduction, dateExpiration, statut, idProduit) VALUES
(1, 'LOT-SMART-2024-001', 150, 150, '2024-01-01', '2027-01-01', 'actif', 51),
(2, 'LOT-TABLET-2024-001', 80, 80, '2024-01-10', '2028-01-10', 'actif', 52),
(3, 'LOT-SERV-2024-001', 10, 10, '2024-01-20', NULL, 'actif', 53),
(4, 'LOT-DISK-2024-001', 200, 200, '2024-02-01', NULL, 'actif', 4),
(5, 'LOT-HEAD-2024-001', 120, 120, '2024-02-15', NULL, 'actif', 5),
(6, 'LOT-WEB-2024-001', 90, 90, '2024-03-01', NULL, 'actif', 6),
(7, 'LOT-PRINT-2024-001', 30, 30, '2024-03-10', '2029-03-10', 'actif', 7),
(8, 'LOT-ROUT-2024-001', 70, 70, '2024-03-20', NULL, 'actif', 8),
(9, 'LOT-SCREEN-2024-001', 40, 40, '2024-04-01', NULL, 'actif', 9),
(10, 'LOT-KEYB-2024-001', 60, 60, '2024-04-10', NULL, 'actif', 10),
(11, 'LOT-MOUSE-2024-001', 110, 110, '2024-04-20', NULL, 'actif', 54),
(12, 'LOT-BOX-2024-001', 500, 500, '2024-05-01', NULL, 'actif', 12),
(13, 'LOT-FILM-2024-001', 300, 300, '2024-05-10', NULL, 'actif', 13),
(14, 'LOT-ADH-2024-001', 400, 400, '2024-05-20', NULL, 'actif', 14),
(15, 'LOT-CRM-2024-001', 5, 5, '2024-01-05', '2025-07-01', 'actif', 15),
(16, 'LOT-ANTI-2024-001', 10, 10, '2024-01-15', '2030-01-01', 'actif', 16),
(17, 'LOT-OFFICE-2024-001', 20, 20, '2024-02-05', '2025-09-01', 'actif', 17),
(18, 'LOT-CAO-2024-001', 3, 3, '2024-02-20', NULL, 'actif', 18),
(19, 'LOT-OS-2024-001', 8, 8, '2024-03-05', '2026-03-15', 'actif', 19),
(20, 'LOT-COMPTA-2024-001', 12, 12, '2024-03-15', NULL, 'actif', 20),
(21, 'LOT-CHAIR-2024-001', 25, 25, '2024-06-01', NULL, 'actif', 55),
(22, 'LOT-WORK-2024-001', 7, 7, '2024-06-10', NULL, 'actif', 22),
(23, 'LOT-PROJ-2024-001', 15, 15, '2024-06-20', NULL, 'actif', 23),
(24, 'LOT-VID-2024-001', 10, 10, '2024-07-01', NULL, 'actif', 24),
(25, 'LOT-UPS-2024-001', 18, 18, '2024-07-10', NULL, 'actif', 25),
(26, 'LOT-SCAN-2024-001', 22, 22, '2024-07-20', NULL, 'actif', 26),
(27, 'LOT-IP-2024-001', 35, 35, '2024-08-01', NULL, 'actif', 27),
(28, 'LOT-WIFI-2024-001', 28, 28, '2024-08-10', NULL, 'actif', 28),
(29, 'LOT-SSD-2024-001', 45, 45, '2024-08-20', NULL, 'actif', 29),
(30, 'LOT-GPU-2024-001', 15, 15, '2024-09-01', NULL, 'actif', 30),
(31, 'LOT-CABLE-2024-001', 100, 100, '2024-09-10', NULL, 'actif', 31),
(32, 'LOT-ETIQ-2024-001', 200, 200, '2024-09-20', NULL, 'actif', 32),
(33, 'LOT-PIST-2024-001', 50, 50, '2024-10-01', NULL, 'actif', 33),
(34, 'LOT-PROJMGMT-2024-001', 7, 7, '2024-06-05', '2026-07-01', 'actif', 34),
(35, 'LOT-3D-2024-001', 4, 4, '2024-06-15', NULL, 'actif', 56),
(36, 'LOT-PHOTO-2024-001', 10, 10, '2024-06-25', '2025-10-01', 'actif', 36),
(37, 'LOT-DB-2024-001', 2, 2, '2024-07-05', NULL, 'actif', 37),
(38, 'LOT-BACKUP-2024-001', 6, 6, '2024-07-15', '2026-05-20', 'actif', 38),
(39, 'LOT-STOCK-2024-001', 1, 1, '2024-07-25', NULL, 'actif', 39),
(40, 'LOT-CYBER-2024-001', 3, 3, '2024-08-05', '2026-02-28', 'actif', 40),
(41, 'LOT-ROBOT-2024-001', 1, 1, '2024-10-10', NULL, 'actif', 41),
(42, 'LOT-TRANS-2024-001', 3, 3, '2024-10-20', NULL, 'actif', 42),
(43, 'LOT-CHARIOT-2024-001', 2, 2, '2024-11-01', NULL, 'actif', 43),
(44, 'LOT-RAYON-2024-001', 5, 5, '2024-11-10', NULL, 'actif', 44),
(45, 'LOT-DOOR-2024-001', 1, 1, '2024-11-20', NULL, 'actif', 45),
(46, 'LOT-CAM-2024-001', 8, 8, '2024-12-01', NULL, 'actif', 46),
(47, 'LOT-BARCODE-2024-001', 12, 12, '2024-12-10', NULL, 'actif', 47),
(48, 'LOT-BALANCE-2024-001', 4, 4, '2024-12-20', NULL, 'actif', 48),
(49, 'LOT-FLEET-2024-001', 6, 6, '2024-09-05', '2025-11-01', 'actif', 49),
(50, 'LOT-ERP-2024-001', 1, 1, '2024-09-15', NULL, 'actif', 50);
---
-- ===============================
-- INVENTAIRE
-- ===============================
INSERT INTO INVENTAIRE(idProduit, idOrganisation) VALUES
(51, 1 ), 
(52, 1), 
(53, 1), 
(4, 1), 
(5, 1), 
(6, 1), 
(7, 1), 
(8, 1), 
(9, 1), 
(10, 1), 
(54, 1),
(12, 1), 
(13, 1), 
(14, 1), 
(15, 1),
(16, 1),
(17, 1),
(18, 1),
(19, 1),
(20, 1),
(55, 1), 
(22, 1),
(23, 1), 
(24, 1), 
(25, 1), 
(26, 1), 
(27, 1), 
(28, 1), 
(29, 1), 
(30, 1), 
(31, 1), 
(32, 1), 
(33, 1), 
(34, 1),
(56, 1),
(36, 1),
(37, 1),
(38, 1),
(39, 1),
(40, 1),
(41, 1),
(42, 1),
(43, 1), 
(44, 1), 
(45, 1),
(46, 1), 
(47, 1), 
(48, 1), 
(49, 1),
(50, 1);

---
-- ===============================
-- STOCKER
-- ===============================
INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite) VALUES
(1, 101, '2024-01-05', 100), (1, 201, '2024-01-05', 50),
(2, 102, '2024-01-12', 60), (2, 202, '2024-01-12', 20),
(3, 103, '2024-01-22', 8), (3, 203, '2024-01-22', 2),
(4, 104, '2024-02-03', 150), (4, 204, '2024-02-03', 50),
(5, 101, '2024-02-17', 90), (5, 201, '2024-02-17', 30),
(6, 102, '2024-03-03', 70), (6, 202, '2024-03-03', 20),
(7, 103, '2024-03-12', 20), (7, 203, '2024-03-12', 10),
(8, 104, '2024-03-22', 50), (8, 204, '2024-03-22', 20),
(9, 101, '2024-04-03', 30), (9, 201, '2024-04-03', 10),
(10, 102, '2024-04-12', 40), (10, 202, '2024-04-12', 20),
(11, 103, '2024-04-22', 80), (11, 203, '2024-04-22', 30),
(12, 105, '2024-05-03', 300), (12, 205, '2024-05-03', 200),
(13, 105, '2024-05-12', 180), (13, 205, '2024-05-12', 120),
(14, 105, '2024-05-22', 250), (14, 205, '2024-05-22', 150),
(21, 101, '2024-06-03', 15), (21, 201, '2024-06-03', 10),
(22, 102, '2024-06-12', 5), (22, 202, '2024-06-12', 2),
(23, 103, '2024-06-22', 10), (23, 203, '2024-06-22', 5),
(24, 104, '2024-07-03', 7), (24, 204, '2024-07-03', 3),
(25, 101, '2024-07-12', 12), (25, 201, '2024-07-12', 6),
(26, 102, '2024-07-22', 15), (26, 202, '2024-07-22', 7),
(27, 103, '2024-08-03', 20), (27, 203, '2024-08-03', 15),
(28, 104, '2024-08-12', 18), (28, 204, '2024-08-12', 10),
(29, 101, '2024-08-22', 30), (29, 201, '2024-08-22', 15),
(30, 102, '2024-09-03', 10), (30, 202, '2024-09-03', 5),
(31, 105, '2024-09-12', 60), (31, 205, '2024-09-12', 40),
(32, 105, '2024-09-22', 120), (32, 205, '2024-09-22', 80),
(33, 105, '2024-10-03', 30), (33, 205, '2024-10-03', 20),
(41, 103, '2024-10-12', 1),
(42, 104, '2024-10-22', 2), (42, 204, '2024-10-22', 1),
(43, 103, '2024-11-03', 1), (43, 203, '2024-11-03', 1),
(44, 104, '2024-11-12', 3), (44, 204, '2024-11-12', 2),
(45, 103, '2024-11-22', 1),
(46, 101, '2024-12-03', 5), (46, 201, '2024-12-03', 3),
(47, 102, '2024-12-12', 8), (47, 202, '2024-12-12', 4),
(48, 103, '2024-12-22', 2), (48, 203, '2024-12-22', 2);

---
-- ===============================
-- BON DE RÉCEPTION
-- ===============================
INSERT INTO BON_RECEPTION(idBon, reference, dateCreation, dateReceptionPrevue, statut) VALUES
(10, 'BR-2024-001', '2024-01-08', '2024-01-15', 'termine'),
(11, 'BR-2024-002', '2024-02-05', '2024-02-12', 'termine'),
(12, 'BR-2024-003', '2024-03-01', '2024-03-08', 'en_cours'),
(13, 'BR-2024-004', '2024-04-10', '2024-04-17', 'en_cours'),
(14, 'BR-2024-005', '2024-05-15', '2024-05-22', 'termine'),
(15, 'BR-2024-006', '2024-06-01', '2024-06-08', 'termine'),
(16, 'BR-2024-007', '2024-07-01', '2024-07-08', 'en_cours'),
(17, 'BR-2024-008', '2024-08-01', '2024-08-08', 'en_cours'),
(18, 'BR-2024-009', '2024-09-01', '2024-09-08', 'termine'),
(19, 'BR-2024-010', '2024-10-01', '2024-10-08', 'termine'),
(20, 'BR-2024-011', '2024-11-01', '2024-11-08', 'en_cours'),
(21, 'BR-2024-012', '2024-12-01', '2024-12-08', 'en_cours');

---
-- ===============================
-- COLIS (réceptionnés)
-- ===============================
INSERT INTO COLIS(idColis, reference, dateCreation, statut, poidsTotal, volumeTotal) VALUES
(10, 'REC-SMART-2024-001', '2024-01-15', 'recu', 3.0, 168.0),
(11, 'REC-TABLET-2024-001', '2024-02-12', 'recu', 4.0, 5700.0),
(12, 'REC-DISK-2024-001', '2024-02-03', 'recu', 1.0, 768.0),
(13, 'REC-HEAD-2024-001', '2024-02-17', 'recu', 1.2, 10080.0),
(14, 'REC-BOX-2024-001', '2024-05-03', 'recu', 2.5, 150000.0),
(15, 'REC-CHAIR-2024-001', '2024-06-08', 'recu', 50.0, 1176000.0),
(16, 'REC-SCAN-2024-001', '2024-07-22', 'recu', 4.0, 9000.0),
(17, 'REC-CABLE-2024-001', '2024-09-12', 'recu', 1.0, 100000.0);

---
-- ===============================
-- RECEVOIR_COLIS
-- ===============================
INSERT INTO RECEVOIR_COLIS(idBon, idColis) VALUES
(10, 10),
(11, 11),
(11, 12),
(11, 13),
(14, 14),
(15, 15),
(16, 16),
(18, 17);

---
-- ===============================
-- CONTENIR
-- ===============================
INSERT INTO CONTENIR(idColis, idLot, quantite) VALUES
(10, 1, 150),
(11, 2, 80),
(12, 4, 200),
(13, 5, 120),
(14, 12, 500),
(15, 21, 25),
(16, 26, 22),
(17, 31, 100);

---
-- ===============================
-- RESPONSABLE RÉCEPTION
-- ===============================
INSERT INTO RESPONSABLE_RECEPTION(idIndividu, idBon) VALUES
(2, 10),
(2, 11),
(2, 12),
(2, 13),
(2, 14),
(2, 15),
(2, 16),
(2, 17),
(2, 18),
(2, 19),
(2, 20),
(2, 21);

---
-- ===============================
-- BON D’EXPÉDITION
-- ===============================
INSERT INTO BON_EXPEDITION(idBon, reference, dateCreation, dateExpeditionPrevue, priorite, statut) VALUES
(10, 'BE-2024-001', '2024-01-20', '2024-01-25', 'normal', 'termine'),
(11, 'BE-2024-002', '2024-02-10', '2024-02-18', 'urgente', 'termine'),
(12, 'BE-2024-003', '2024-03-05', '2024-03-12', 'normal', 'en_attente'),
(13, 'BE-2024-004', '2024-04-15', '2024-04-22', 'normale', 'en_attente'),
(14, 'BE-2024-005', '2024-05-20', '2024-05-27', 'urgente', 'termine'),
(15, 'BE-2024-006', '2024-06-10', '2024-06-17', 'normale', 'en_attente'),
(16, 'BE-2024-007', '2024-07-10', '2024-07-17', 'normale', 'en_attente'),
(17, 'BE-2024-008', '2024-08-10', '2024-08-17', 'urgente', 'en_attente'),
(18, 'BE-2024-009', '2024-09-10', '2024-09-17', 'normale', 'termine'),
(19, 'BE-2024-010', '2024-10-10', '2024-10-17', 'normale', 'en_attente'),
(20, 'BE-2024-011', '2024-11-10', '2024-11-17', 'urgente', 'en_attente');

---
-- ===============================
-- RESPONSABLE EXPÉDITION
-- ===============================
INSERT INTO RESPONSABLE_EXPEDITION(idIndividu, idBon) VALUES
(2, 10),
(2, 11),
(2, 12),
(2, 13),
(2, 14),
(2, 15),
(2, 16),
(2, 17),
(2, 18),
(2, 19),
(2, 20);

---
-- ===============================
-- COMPOSER_EXPEDITION
-- ===============================
INSERT INTO COMPOSER_EXPEDITION(idBon, idProduit, quantite) VALUES
(10, 51, 50),
(10, 4, 100),
(11, 52, 30),
(11, 5, 60),
(12, 53, 5),
(12, 6, 40),
(13, 7, 10),
(13, 8, 30),
(14, 9, 20),
(14, 10, 30),
(14, 54, 50),
(15, 15, 2),
(15, 17, 5),
(16, 55, 10),
(16, 23, 5),
(17, 25, 8),
(17, 27, 15),
(18, 29, 20),
(18, 32, 50),
(19, 34, 3),
(19, 36, 4),
(20, 41, 1),
(20, 43, 1);


