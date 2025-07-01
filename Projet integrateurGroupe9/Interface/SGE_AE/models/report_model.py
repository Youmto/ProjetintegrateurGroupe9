import logging
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)

# ============================================================================
# Rapport global de l'inventaire
# ============================================================================
def generate_stock_report(conn):
    try:
        query = "SELECT * FROM vue_inventaire_global;"
        rows = execute_query(conn, query, fetch=True)
        return [
            {
                'idProduit': row[0],
                'reference': row[1],
                'nom': row[2],
                'type': row[3],
                'quantite_totale': row[4],
                'nb_emplacements': row[5],
                'prochaine_expiration': row[6]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"[generate_stock_report] Erreur : {e}")
        return []

# ============================================================================
# Rapport de mouvements d’un produit
# ============================================================================
def generate_movement_report(conn, id_produit):
    try:
        query = "SELECT * FROM mouvements_produit(%s);"
        rows = execute_query(conn, query, (id_produit,), fetch=True)
        return [
            {
                'type_mouvement': row[0],
                'reference_bon': row[1],
                'date_mouvement': row[2],
                'quantite': row[3],
                'lot': row[4],
                'cellule': row[5],
                'description': row[6]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"[generate_movement_report] Erreur : {e}")
        return []

# ============================================================================
# Rapport des exceptions récentes
# ============================================================================
def generate_exception_reports(conn):
    try:
        query = """
        SELECT typeRapport, dateGeneration, description, idBonReception, idBonExpedition
        FROM RAPPORT_EXCEPTION
        ORDER BY dateGeneration DESC;
        """
        rows = execute_query(conn, query, fetch=True)
        return [
            {
                'typeRapport': row[0],
                'dateGeneration': row[1],
                'description': row[2],
                'idBonReception': row[3],
                'idBonExpedition': row[4]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"[generate_exception_reports] Erreur : {e}")
        return []
