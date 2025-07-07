import logging
from models.movement_model import (
    mouvements_produit,
    deplacer_lot,
    ajuster_inventaire,
    get_product_movement_totals
)
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

def handle_mouvements_produit(conn, produit_id, date_debut=None, date_fin=None, type_mouvement=None):
    """
    Récupère les mouvements de stock pour un produit avec filtres optionnels.

    Args:
        conn: Connexion à la base de données
        produit_id (int): ID du produit
        date_debut (str|date): Date de début (optionnelle)
        date_fin (str|date): Date de fin (optionnelle)
        type_mouvement (str): Filtre sur le type de mouvement (optionnel)

    Returns:
        list[dict]: Liste des mouvements
    """
    try:
        if not isinstance(produit_id, int) or produit_id <= 0:
            logger.warning(f"ID produit invalide : {produit_id}")
            return []

        mouvements = mouvements_produit(conn, produit_id, date_debut, date_fin, type_mouvement)
        return mouvements or []

    except Exception as e:
        logger.error(f"Erreur dans handle_mouvements_produit : {str(e)}", exc_info=True)
        return []

def handle_get_product_movement_totals(conn, product_id):
    """
    Récupère les totaux des mouvements d'un produit.

    Args:
        conn: Connexion à la base de données
        product_id (int): ID du produit

    Returns:
        dict: Totaux des mouvements (entrées, sorties, ajustements)
    """
    try:
        if not isinstance(product_id, int) or product_id <= 0:
            logger.warning(f"ID produit invalide : {product_id}")
            return {}

        return get_product_movement_totals(conn, product_id)

    except Exception as e:
        logger.error(f"Erreur dans handle_get_product_movement_totals : {str(e)}", exc_info=True)
        return {}


def handle_deplacer_lot(conn, lot_id, cellule_src, cellule_dest, quantite, responsable_id):
    """
    Déplace une quantité d’un lot d’une cellule à une autre.

    Args:
        conn: Connexion DB
        lot_id (int): ID du lot
        cellule_src (int): ID cellule source
        cellule_dest (int): ID cellule destination
        quantite (int): Quantité à déplacer
        responsable_id (int): ID de l’individu responsable

    Returns:
        bool: True si succès, False sinon
    """
    try:
        if not all(isinstance(x, int) and x > 0 for x in [lot_id, cellule_src, cellule_dest, quantite, responsable_id]):
            logger.warning("Paramètres invalides pour le déplacement de lot.")
            return False

        return deplacer_lot(conn, lot_id, cellule_src, cellule_dest, quantite, responsable_id)

    except Exception as e:
        logger.error(f"Erreur dans handle_deplacer_lot : {e}", exc_info=True)
        return False


def handle_ajuster_inventaire(conn, lot_id, cellule_id, nouvelle_qte, responsable_id, commentaire):
    """
    Ajuste manuellement l'inventaire d’un lot dans une cellule donnée.

    Args:
        conn: Connexion DB
        lot_id (int): ID du lot concerné
        cellule_id (int): ID de la cellule
        nouvelle_qte (int): Nouvelle quantité physique constatée
        responsable_id (int): ID utilisateur responsable
        commentaire (str): Motif ou commentaire

    Returns:
        bool: True si succès, False sinon
    """
    try:
        if not all(isinstance(x, int) and x >= 0 for x in [lot_id, cellule_id, nouvelle_qte, responsable_id]):
            logger.warning("Paramètres numériques invalides pour ajustement inventaire.")
            return False

        if not commentaire or not isinstance(commentaire, str):
            logger.warning("Commentaire requis pour l’ajustement.")
            return False

        return ajuster_inventaire(conn, lot_id, cellule_id, nouvelle_qte, responsable_id, commentaire)

    except Exception as e:
        logger.error(f"Erreur dans handle_ajuster_inventaire : {e}", exc_info=True)
        return False
