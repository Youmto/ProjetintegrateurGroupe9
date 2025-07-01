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
