import logging
from models.report_model import (
    generate_stock_report,
    generate_movement_report,
    generate_exception_reports,
    generate_stockouts,
    generate_expiring_products
)

logger = logging.getLogger(__name__)

def handle_stock_report(conn):
    """
    Génère un rapport global d’inventaire.
    """
    try:
        return generate_stock_report(conn)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport de stock : {e}", exc_info=True)
        return []

def handle_movement_report(conn, id_produit):
    """
    Génère un rapport des mouvements pour un produit donné.

    Args:
        conn: Connexion active
        id_produit (int): ID du produit ciblé
    """
    try:
        return generate_movement_report(conn, id_produit)
    except Exception as e:
        logger.error(f"Erreur rapport mouvements produit {id_produit} : {e}", exc_info=True)
        return []

def handle_exception_report(conn):
    """
    Récupère la liste des rapports d’exception récents.
    """
    try:
        return generate_exception_reports(conn)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des rapports d'exception : {e}", exc_info=True)
        return []

def handle_stockout_report(conn):
    """
    Récupère les produits en rupture de stock.
    """
    try:
        return generate_stockouts(conn)
    except Exception as e:
        logger.error(f"Erreur lors du rapport de ruptures : {e}", exc_info=True)
        return []

def handle_expiring_report(conn, days=30):
    """
    Récupère les produits expirant dans un délai défini.

    Args:
        conn: Connexion active
        days (int): Délai avant expiration
    """
    try:
        return generate_expiring_products(conn, days)
    except Exception as e:
        logger.error(f"Erreur rapport produits expirant dans {days} jours : {e}", exc_info=True)
        return []
