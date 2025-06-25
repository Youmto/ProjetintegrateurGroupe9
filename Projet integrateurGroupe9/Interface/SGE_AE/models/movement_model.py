from database import execute_query
from SGE_AE.database import execute_query
import logging
def deplacer_lot(conn, id_lot, cellule_src, cellule_dst, quantite, id_resp):
    query = """
    SELECT deplacer_lot(%s, %s, %s, %s, %s);
    """
    params = (id_lot, cellule_src, cellule_dst, quantite, id_resp)
    return execute_query(conn, query, params, fetch=True)[0][0]

def ajuster_inventaire(conn, id_lot, id_cellule, nouvelle_qte, id_resp, commentaire):
    query = """
    SELECT ajuster_inventaire(%s, %s, %s, %s, %s);
    """
    return execute_query(conn, query, (id_lot, id_cellule, nouvelle_qte, id_resp, commentaire), fetch=True)[0][0]

logger = logging.getLogger(__name__)

def mouvements_produit(conn, produit_id):
    """
    Récupère l'historique des mouvements d'un produit via la fonction PostgreSQL mouvements_produit.

    Args:
        conn: Connexion PostgreSQL active
        produit_id (int): ID du produit

    Returns:
        List[Dict]: Liste des mouvements sous forme de dictionnaires
    """
    try:
        query = "SELECT * FROM mouvements_produit(%s);"
        params = (produit_id,)
        rows = execute_query(conn, query, params, fetch=True)

        movements = []
        for row in rows:
            movements.append({
                "type": row[0],
                "reference": row[1],
                "date": row[2],
                "quantite": row[3],
                "lot": row[4],
                "cellule": row[5],
                "description": row[6]
            })
        return movements
    except Exception as e:
        logger.error(f"Erreur dans mouvements_produit : {e}", exc_info=True)
        return []
