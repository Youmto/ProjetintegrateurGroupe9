-- =============================================
-- SGE_doc.sql
-- Documentation du schéma
-- =============================================

COMMENT ON DOMAIN dom_id IS 'Identifiant numérique unique et positif';
COMMENT ON DOMAIN dom_nom IS 'Nom avec contenu non vide';
COMMENT ON DOMAIN dom_texte IS 'Texte descriptif libre';
COMMENT ON DOMAIN dom_telephone IS 'Numéro de téléphone valide';
COMMENT ON DOMAIN dom_email IS 'Adresse email valide';
COMMENT ON DOMAIN dom_date IS 'Date au format YYYY-MM-DD';
COMMENT ON DOMAIN dom_boolean IS 'Valeur booléenne TRUE/FALSE';
COMMENT ON DOMAIN dom_type IS 'Classification générique';
COMMENT ON DOMAIN dom_reference IS 'Code référence non vide';
COMMENT ON DOMAIN dom_quantite IS 'Quantité numérique positive';
COMMENT ON DOMAIN dom_float IS 'Valeur décimale positive';
COMMENT ON DOMAIN dom_position IS 'Position physique dans l''entrepôt';
COMMENT ON DOMAIN dom_statut IS 'Statut standard des entités';
COMMENT ON DOMAIN DOM_TYPE_PRODUIT IS 'Classification des produits gérés';
COMMENT ON DOMAIN DOM_TYPE_ROLE IS 'Rôles des individus dans le système';

-- Documentation des tables principales
COMMENT ON TABLE ORGANISATION IS 'Organisations partenaires ou internes';
COMMENT ON TABLE ROLE IS 'Rôles des individus dans le système';
COMMENT ON TABLE INDIVIDU IS 'Personnes physiques du système';
COMMENT ON TABLE AFFECTER_ROLE IS 'Assignation des rôles aux individus';
COMMENT ON TABLE PRODUIT IS 'Produits gérés dans l''entrepôt';
COMMENT ON TABLE PRODUIT_MATERIEL IS 'Produits physiques avec dimensions';
COMMENT ON TABLE PRODUIT_LOGICIEL IS 'Produits logiciels et licences';
COMMENT ON TABLE FOURNISSEUR IS 'Organisations fournissant des produits';
COMMENT ON TABLE APPROVISIONNER IS 'Conditions d''approvisionnement';
COMMENT ON TABLE ENTREPOT IS 'Entrepôts physiques';
COMMENT ON TABLE CELLULE IS 'Emplacements de stockage individuels';
COMMENT ON TABLE COMPOSER_ENTREPOT IS 'Composition des entrepôts en cellules';
COMMENT ON TABLE LOT IS 'Lots de produits gérés';
COMMENT ON TABLE COLIS IS 'Colis physiques ou logistiques';
COMMENT ON TABLE CONTENIR IS 'Contenu des colis en lots';
COMMENT ON TABLE STOCKER IS 'Assignation des lots aux cellules';
COMMENT ON TABLE UTILISER_EMBALLAGE IS 'Utilisation de matériel d''emballage';
COMMENT ON TABLE BON_RECEPTION IS 'Bons de réception de marchandises';
COMMENT ON TABLE RECEVOIR_COLIS IS 'Liaison bons-colis reçus';
COMMENT ON TABLE RESPONSABLE_RECEPTION IS 'Responsables des réceptions';
COMMENT ON TABLE BON_EXPEDITION IS 'Bons d''expédition de marchandises';
COMMENT ON TABLE EXPEDIER_COLIS IS 'Liaison bons-colis expédiés';
COMMENT ON TABLE RESPONSABLE_EXPEDITION IS 'Responsables des expéditions';
COMMENT ON TABLE RAPPORT_EXCEPTION IS 'Rapports d''anomalies logistiques';
COMMENT ON TABLE GENERER_RAPPORT IS 'Générateurs des rapports';
COMMENT ON TABLE INVENTAIRE IS 'Inventaire global des produits';