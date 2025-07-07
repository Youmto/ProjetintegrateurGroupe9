import logging
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)

# =============================================================================
# 1. Récupération de tous les produits
# =============================================================================
def get_all_products(conn):
    """
    Récupère tous les produits enregistrés dans la base.

    Returns:
        List[Dict]: Liste de produits
    """
    try:
        query = """
        SELECT idProduit, reference, nom, description,
               marque, modele, type, estMaterielEmballage
        FROM PRODUIT
        ORDER BY nom;
        """
        rows = execute_query(conn, query, fetch=True)
        return [dict(zip((
            "idProduit", "reference", "nom", "description",
            "marque", "modele", "type", "estMaterielEmballage"
        ), row)) for row in rows]
    except Exception as e:
        logger.error(f"Erreur récupération produits : {e}", exc_info=True)
        return []

# =============================================================================
# 2. Ajout d’un nouveau produit
# =============================================================================
def add_product(conn, product):
    """
    Ajoute un nouveau produit dans la base de données.

    Args:
        conn: Connexion
        product: Dictionnaire contenant les champs requis

    Returns:
        bool: True si succès, False sinon
    """
    try:
        query = """
        INSERT INTO PRODUIT (
            idProduit, reference, nom, description,
            marque, modele, type, estMaterielEmballage
        )
        VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            product["reference"], product["nom"], product["description"],
            product["marque"], product["modele"], product["type"],
            product["estMaterielEmballage"]
        )
        execute_query(conn, query, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur ajout produit : {e}", exc_info=True)
        return False

# =============================================================================
# 3. Mise à jour d’un produit existant
# =============================================================================
def update_product(conn, id_produit, product):
    """
    Met à jour un produit existant.

    Args:
        conn: Connexion
        id_produit: ID du produit à modifier
        product: Dictionnaire contenant les champs modifiés

    Returns:
        bool: True si succès, False sinon
    """
    try:
        query = """
        UPDATE PRODUIT
        SET reference = %s,
            nom = %s,
            description = %s,
            marque = %s,
            modele = %s,
            type = %s,
            estMaterielEmballage = %s
        WHERE idProduit = %s
        """
        params = (
            product["reference"], product["nom"], product["description"],
            product["marque"], product["modele"], product["type"],
            product["estMaterielEmballage"], id_produit
        )
        execute_query(conn, query, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur mise à jour produit (ID {id_produit}) : {e}", exc_info=True)
        return False
def get_product_details_from_db(conn, product_id):
    """
    Récupère tous les détails d'un produit, y compris ses spécifications matérielles ou logicielles.
    """
    query = """
        SELECT
            p.idProduit, p.reference, p.nom, p.description, p.marque, p.modele, p.type, p.estMaterielEmballage,
            pm.longueur, pm.largeur, pm.hauteur, pm.masse, pm.volume,
            pl.version, pl.typeLicence, pl.dateExpiration
        FROM PRODUIT p
        LEFT JOIN produit_materiel pm ON p.idProduit = pm.idProduit
        LEFT JOIN produit_logiciel pl ON p.idProduit = pl.idProduit
        WHERE p.idProduit = %s;
    """
    try:
        result = execute_query(conn, query, (product_id,), fetch=True)
        if result:
            columns = [
                "idProduit", "reference", "nom", "description", "marque", "modele", "type", "estMaterielEmballage",
                "longueur", "largeur", "hauteur", "masse", "volume",
                "version", "typeLicence", "dateExpiration"
            ]
            product_data = dict(zip(columns, result[0]))
            return product_data
        return None
    except Exception as e:
        logger.error(f"❌ [get_product_details_from_db] Erreur lors de la récupération des détails du produit {product_id}: {e}", exc_info=True)
        raise # Rélancer l'exception

# --- Votre fonction modifier_produit_dans_colis avec la vérification du type ---
def modifier_produit_dans_colis(conn, id_colis, id_produit, quantite,
                                version=None, type_licence=None, date_expiration=None,
                                longueur=None, largeur=None, hauteur=None, masse=None, volume=None):
    try:
        # 1. Trouver le lot correspondant
        query_lot = """
            SELECT l.idLot
            FROM LOT l
            WHERE l.idProduit = %s
            AND EXISTS (
                SELECT 1 FROM CONTENIR co
                WHERE co.idColis = %s AND co.idLot = l.idLot
            )
            LIMIT 1
        """
        result = execute_query(conn, query_lot, (id_produit, id_colis), fetch=True)
        if not result:
            logger.error(f"⚠️ [modifier_produit_dans_colis] Aucun lot trouvé pour colis {id_colis} et produit {id_produit}")
            raise ValueError(f"Aucun lot trouvé pour le produit ID {id_produit} dans le colis ID {id_colis}.")

        id_lot = result[0][0]

        # 2. Mettre à jour la quantité dans CONTENIR (ou insérer si non existant)
        query1 = """
            INSERT INTO CONTENIR (idColis, idLot, quantite)
            VALUES (%s, %s, %s)
            ON CONFLICT (idColis, idLot) DO UPDATE SET quantite = EXCLUDED.quantite
        """
        execute_query(conn, query1, (id_colis, id_lot, quantite))

        # 3. Récupérer le type de produit pour savoir quelles dimensions mettre à jour
        # Il est plus sûr de récupérer le type de la DB plutôt que de se fier aux paramètres d'entrée
        query_product_type = "SELECT type FROM PRODUIT WHERE idProduit = %s"
        product_type_result = execute_query(conn, query_product_type, (id_produit,), fetch=True)
        product_type = product_type_result[0][0] if product_type_result else None

        if not product_type:
            logger.warning(f"⚠️ [modifier_produit_dans_colis] Type de produit non trouvé pour l'ID {id_produit}. Les détails spécifiques ne seront pas mis à jour.")
            return True # Continuer si la quantité a été mise à jour

        if product_type == "logiciel":
            # Si le produit est logiciel, mettez à jour les champs logiciel
            # (même si version est None, on veut mettre à jour avec None si c'est le cas)
            query2 = """
                INSERT INTO produit_logiciel (idProduit, version, typeLicence, dateExpiration)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (idProduit) DO UPDATE SET
                    version = EXCLUDED.version,
                    typeLicence = EXCLUDED.typeLicence,
                    dateExpiration = EXCLUDED.dateExpiration
            """
            # Assurez-vous que date_expiration est un objet date ou None, pas une chaîne vide
            execute_query(conn, query2, (id_produit, version, type_licence, date_expiration))
            logger.info(f"✅ [modifier_produit_dans_colis] Infos logiciel mises à jour pour produit {id_produit}.")

        elif product_type == "materiel":
            # Si le produit est matériel, mettez à jour les champs matériel
            # (même si longueur est None, on veut mettre à jour avec None si c'est le cas)
            query3 = """
                INSERT INTO produit_materiel (idProduit, longueur, largeur, hauteur, masse, volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (idProduit) DO UPDATE SET
                    longueur = EXCLUDED.longueur,
                    largeur = EXCLUDED.largeur,
                    hauteur = EXCLUDED.hauteur,
                    masse = EXCLUDED.masse,
                    volume = EXCLUDED.volume
            """
            execute_query(conn, query3, (id_produit, longueur, largeur, hauteur, masse, volume))
            logger.info(f"✅ [modifier_produit_dans_colis] Infos matériel mises à jour pour produit {id_produit}.")
        
        return True # Indiquer le succès
    except Exception as e:
        logger.error(f"❌ [modifier_produit_dans_colis] Erreur : {e}", exc_info=True)
        # Rélancer l'exception pour la gérer au niveau de l'UI
        raise
