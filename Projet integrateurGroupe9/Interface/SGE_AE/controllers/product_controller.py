import logging
from models.product_model import (
    get_all_products,
    add_product,
    update_product,
    modifier_produit_dans_colis, 
    get_product_details_from_db 
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

def handle_get_product_details(conn, product_id):
    """
    Récupère les détails complets d'un produit spécifique, y compris les spécifications
    matérielles ou logicielles.

    Args:
        conn: Connexion à la base de données
        product_id: ID du produit dont les détails sont à récupérer

    Returns:
        Dict: Dictionnaire des détails du produit, ou None si non trouvé/erreur.
    """
    try:
        details = get_product_details_from_db(conn, product_id)
        if details:
            logger.info(f"Détails récupérés pour le produit {product_id}.")
        else:
            logger.warning(f"Aucun détail trouvé pour le produit {product_id}.")
        return details
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails du produit {product_id} : {e}", exc_info=True)
        return None

def handle_modify_product_in_package(conn, id_colis, id_produit, quantite, **kwargs):
    """
    Modifie la quantité d'un produit dans un colis et met à jour ses spécifications
    si elles sont fournies.

    Args:
        conn: Connexion à la base de données
        id_colis: ID du colis
        id_produit: ID du produit
        quantite: Nouvelle quantité du produit dans le colis
        **kwargs: Arguments supplémentaires pour les détails du produit (version, type_licence, date_expiration
                  pour les logiciels; longueur, largeur, hauteur, masse, volume pour le matériel).

    Returns:
        bool: True si succès, False si erreur
    """
    try:
        
        success = modifier_produit_dans_colis(conn, id_colis, id_produit, quantite, **kwargs)
        if success:
            logger.info(f"Produit {id_produit} dans colis {id_colis} modifié avec succès.")
        else:
            logger.warning(f"Échec de la modification du produit {id_produit} dans colis {id_colis}.")
        return success
    except ValueError as ve:
        logger.error(f"Erreur métier lors de la modification du produit dans le colis: {ve}")
        
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la modification du produit {id_produit} dans colis {id_colis}: {e}", exc_info=True)
        return False