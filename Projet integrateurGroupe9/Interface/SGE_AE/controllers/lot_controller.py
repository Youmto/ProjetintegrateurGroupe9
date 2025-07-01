import logging
from models import lot_model

logger = logging.getLogger(__name__)

def get_all_lots(conn):
    """
    Récupère tous les lots disponibles dans la base.
    """
    try:
        lots = lot_model.get_all_lots(conn)
        if not lots:
            logger.warning("[get_all_lots] Aucun lot trouvé.")
        return lots
    except Exception as e:
        logger.error(f"[get_all_lots] Erreur : {e}", exc_info=True)
        return []

def get_produits_du_lot(conn, id_lot):
    """
    Récupère les produits d’un lot donné.
    """
    try:
        produits = lot_model.get_produits_par_lot(conn, id_lot)
        return produits or []
    except Exception as e:
        logger.error(f"[get_produits_du_lot] Erreur : {e}", exc_info=True)
        return []

def supprimer_produit(conn, id_colis, id_produit):
    """
    Supprime un produit d’un colis (d’un lot).
    """
    try:
        lot_model.supprimer_produit_dans_colis(conn, id_colis, id_produit)
        return True
    except Exception as e:
        logger.error(f"[supprimer_produit] Erreur : {e}", exc_info=True)
        return False

def modifier_produit(conn, id_colis, id_produit, quantite, **kwargs):
    """
    Modifie les détails d’un produit dans un colis.
    `kwargs` permet de passer version, licence, dimensions, masse, volume, etc.
    """
    try:
        lot_model.modifier_produit_dans_colis(conn, id_colis, id_produit, quantite, **kwargs)
        return True
    except Exception as e:
        logger.error(f"[modifier_produit] Erreur : {e}", exc_info=True)
        return False
