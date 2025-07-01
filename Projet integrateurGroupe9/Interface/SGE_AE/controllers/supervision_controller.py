from models.supervision_model import (
    occupation_cellules,
    produits_en_rupture,
    produits_jamais_stockes,
    cellules_vides,
    produits_expirant_bientot
)
import logging
from models.expedition_model import get_colis_termines


logger = logging.getLogger(__name__)

def handle_occupation_cellules(conn):
    """
    Récupère le taux d’occupation des cellules avec détails.
    """
    try:
        return occupation_cellules(conn)
    except Exception as e:
        logger.error(f"Erreur dans handle_occupation_cellules: {e}", exc_info=True)
        return []

def handle_ruptures(conn):
    """
    Récupère les produits en rupture de stock.
    """
    try:
        return produits_en_rupture(conn)
    except Exception as e:
        logger.error(f"Erreur dans handle_ruptures: {e}", exc_info=True)
        return []

def handle_produits_non_stockes(conn):
    """
    Récupère les produits qui n’ont jamais été stockés.
    """
    try:
        return produits_jamais_stockes(conn)
    except Exception as e:
        logger.error(f"Erreur dans handle_produits_non_stockes: {e}", exc_info=True)
        return []

def handle_cellules_vides(conn):
    """
    Récupère les cellules vides dans l'entrepôt.
    """
    try:
        return cellules_vides(conn)
    except Exception as e:
        logger.error(f"Erreur dans handle_cellules_vides: {e}", exc_info=True)
        return []

def handle_expirations(conn, jours=30):
    """
    Récupère les produits expirant dans X jours.

    Args:
        conn: Connexion active
        jours: Période de préavis en jours (défaut 30)
    """
    try:
        return produits_expirant_bientot(conn, jours)
    except Exception as e:
        logger.error(f"Erreur dans handle_expirations ({jours} jours): {e}", exc_info=True)
        return []

def handle_expeditions_terminées(conn):
    return get_colis_termines(conn)
