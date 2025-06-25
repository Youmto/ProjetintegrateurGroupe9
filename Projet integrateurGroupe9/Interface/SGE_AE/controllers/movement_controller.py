import logging
from models.movement_model import (
    mouvements_produit,
    deplacer_lot,
    ajuster_inventaire
)

logger = logging.getLogger(__name__)

def handle_mouvements_produit(conn, produit_id):
    """
    Récupère les mouvements de stock liés à un produit donné.

    Args:
        conn: Connexion à la base de données
        produit_id (int): ID du produit à analyser

    Returns:
        list[dict]: Liste des mouvements ou liste vide
    """
    try:
        if not produit_id or not isinstance(produit_id, int):
            logger.error(f"ID produit invalide: {produit_id}")
            return []

        mouvements = mouvements_produit(conn, produit_id)

        if not mouvements:
            logger.info(f"Aucun mouvement trouvé pour le produit {produit_id}")
            return []

        return mouvements

    except Exception as e:
        logger.error(f"Erreur handle_mouvements_produit: {str(e)}", exc_info=True)
        return []

def handle_deplacer_lot(conn, lot_id, cellule_src, cellule_dest, quantite, responsable_id):
    """
    Effectue le déplacement d'un lot entre deux cellules.

    Args:
        conn: Connexion à la base
        lot_id (int): ID du lot
        cellule_src (int): ID cellule source
        cellule_dest (int): ID cellule destination
        quantite (int): Quantité à déplacer
        responsable_id (int): ID utilisateur responsable

    Returns:
        bool: True si succès, False sinon
    """
    try:
        if not all([lot_id, cellule_src, cellule_dest, quantite, responsable_id]):
            logger.warning("Paramètres manquants pour deplacer_lot.")
            return False
        return deplacer_lot(conn, lot_id, cellule_src, cellule_dest, quantite, responsable_id)
    except Exception as e:
        logger.error(f"Erreur handle_deplacer_lot : {e}", exc_info=True)
        return False

def handle_ajuster_inventaire(conn, lot_id, cellule_id, nouvelle_qte, responsable_id, commentaire):
    """
    Effectue un ajustement d'inventaire physique.

    Args:
        conn: Connexion à la base
        lot_id (int): ID du lot
        cellule_id (int): ID de la cellule concernée
        nouvelle_qte (int): Quantité réelle constatée
        responsable_id (int): Utilisateur responsable
        commentaire (str): Description ou justification

    Returns:
        bool: True si succès, False sinon
    """
    try:
        if not all([lot_id, cellule_id, responsable_id]):
            logger.warning("Paramètres essentiels manquants pour ajuster_inventaire.")
            return False
        if not isinstance(nouvelle_qte, int):
            raise ValueError("La quantité doit être un entier.")
        return ajuster_inventaire(conn, lot_id, cellule_id, nouvelle_qte, responsable_id, commentaire)
    except Exception as e:
        logger.error(f"Erreur handle_ajuster_inventaire : {e}", exc_info=True)
        return False