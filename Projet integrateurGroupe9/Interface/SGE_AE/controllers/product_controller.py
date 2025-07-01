import logging
from models.product_model import (
    get_all_products,
    add_product,
    update_product
)

logger = logging.getLogger(__name__)

def handle_get_all_products(conn):
    """
    Récupère la liste complète des produits.

    Args:
        conn: Connexion à la base de données

    Returns:
        Liste de dictionnaires représentant les produits
    """
    try:
        return get_all_products(conn)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des produits : {e}", exc_info=True)
        return []

def handle_add_product(conn, product_data):
    """
    Ajoute un nouveau produit à la base.

    Args:
        conn: Connexion à la base de données
        product_data: Dictionnaire contenant les informations du produit

    Returns:
        bool: True si succès, False si erreur
    """
    try:
        add_product(conn, product_data)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du produit : {e}", exc_info=True)
        return False

def handle_update_product(conn, id_produit, product_data):
    """
    Met à jour un produit existant.

    Args:
        conn: Connexion à la base de données
        id_produit: ID du produit à mettre à jour
        product_data: Nouvelles données du produit

    Returns:
        bool: True si succès, False si erreur
    """
    try:
        update_product(conn, id_produit, product_data)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du produit {id_produit} : {e}", exc_info=True)
        return False
