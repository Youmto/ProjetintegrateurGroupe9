import logging
from models.reception_model import (
    get_bons_reception,
    receptionner_lot,
    valider_reception
)
from models.stock_model import create_reception

logger = logging.getLogger(__name__)

def handle_receptionner_lot(conn, id_bon, ref_lot, id_produit, quantite, date_prod, date_exp, id_cellule):
    """
    Enregistre un lot reçu dans un bon de réception existant.

    Args:
        conn: Connexion active
        id_bon: ID du bon de réception
        ref_lot: Référence du lot
        id_produit: ID du produit
        quantite: Quantité reçue
        date_prod: Date de production
        date_exp: Date d’expiration (nullable)
        id_cellule: Cellule de stockage

    Returns:
        ID du lot inséré
    """
    try:
        return receptionner_lot(conn, id_bon, ref_lot, id_produit, quantite, date_prod, date_exp, id_cellule)
    except Exception as e:
        logger.error(f"Erreur lors de la réception du lot {ref_lot} : {e}", exc_info=True)
        return None

def handle_validation_reception(conn, reference, date_prevue, id_individu):
    """
    Crée un bon de réception en attente et l’associe à un responsable.

    Args:
        conn: Connexion
        reference: Référence du bon
        date_prevue: Date prévue de réception
        id_individu: ID du responsable

    Returns:
        ID du bon de réception
    """
    try:
        return create_reception(conn, reference, date_prevue, id_individu)
    except Exception as e:
        logger.error(f"Erreur lors de la création du bon de réception {reference} : {e}", exc_info=True)
        return None

def handle_receptions_en_attente(conn):
    """
    Récupère les bons de réception en attente ou en cours.

    Args:
        conn: Connexion à la base

    Returns:
        Liste de bons de réception
    """
    try:
        return get_bons_reception(conn)
    except Exception as e:
        logger.error(f"Erreur récupération bons de réception : {e}", exc_info=True)
        return []
