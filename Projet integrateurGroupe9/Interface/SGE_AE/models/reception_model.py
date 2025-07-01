import logging
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)

# =============================================================================
# Réceptionner un lot de produits
# =============================================================================
def receptionner_lot(conn, id_bon, ref_lot, id_produit, quantite, date_prod, date_exp, id_cellule):
    """
    Insère un lot dans la base via la fonction receptionner_lot

    Returns:
        int: ID du lot créé
    """
    try:
        query = """
            SELECT receptionner_lot(
            %s::dom_id, -- id_bon
            %s::dom_reference, -- ref_lot
            %s::dom_id, -- id_produit
            %s::dom_quantite, -- quantite
            %s::dom_date, -- date_prod
            %s::dom_date, -- date_exp
            %s::dom_id -- id_cellule
                );
                """
        params = (id_bon, ref_lot, id_produit, quantite, date_prod, date_exp, id_cellule)
        result = execute_query(conn, query, params, fetch=True)
        return result[0][0] if result else None
    except Exception as e:
        logger.error(f"Erreur lors de la réception du lot : {e}", exc_info=True)
        return None

# =============================================================================
# Valider la réception finale d’un bon
# =============================================================================
def valider_reception(conn, id_bon):
    """
    Valide un bon de réception (met à jour son statut à 'termine').
    """
    try:
        query = "SELECT valider_reception(%s);"
        execute_query(conn, query, (id_bon,))
    except Exception as e:
        logger.error(f"Erreur lors de la validation de la réception : {e}", exc_info=True)

# =============================================================================
# Liste des bons de réception en attente ou en cours
# =============================================================================
def get_bons_reception(conn):
    """
    Récupère tous les bons de réception en attente ou en cours.

    Returns:
        List[Dict]: Liste de bons
    """
    try:
        query = """
        SELECT idBon, reference, dateCreation, dateReceptionPrevue, statut
        FROM BON_RECEPTION
        WHERE statut IN ('en_attente', 'en_cours')
        ORDER BY dateReceptionPrevue;
        """
        rows = execute_query(conn, query, fetch=True)
        return [
            {
                'idBon': r[0],
                'reference': r[1],
                'dateCreation': r[2],
                'dateReceptionPrevue': r[3],
                'statut': r[4]
            } for r in rows
        ]
    except Exception as e:
        logger.error(f"Erreur récupération bons de réception : {e}", exc_info=True)
        return []
