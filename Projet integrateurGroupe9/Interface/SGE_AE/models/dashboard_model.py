import logging
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)

def fetch_ruptures(conn):
    """
    Récupère la dernière date de rupture pour chaque produit,
    où le stock cumulatif devient <= 0.
    """
    query = """
        WITH cumul AS (
            SELECT
                idProduit,
                date::date AS date,
                type,
                quantite,
                SUM(CASE WHEN type = 'ENTREE' THEN quantite ELSE -quantite END)
                    OVER (PARTITION BY idProduit ORDER BY date ROWS UNBOUNDED PRECEDING) AS stock_cumulatif
            FROM MOUVEMENT
        ),
        ruptures AS (
            SELECT idProduit, date
            FROM cumul
            WHERE stock_cumulatif <= 0
        )
        SELECT DISTINCT ON (idProduit)
            idProduit,
            date AS date_rupture
        FROM ruptures
        ORDER BY idProduit, date DESC;
    """
    try:
        rows = execute_query(conn, query, fetch=True)
        columns = ['idProduit', 'date_rupture']
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        logger.error(f"[fetch_ruptures] Erreur : {e}")
        return []
    
def get_ruptures_history(conn, start_date, end_date):
    """
    Retourne le nombre de produits différents en rupture par jour entre start_date et end_date.
    """
    query = """
        WITH cumul AS (
            SELECT
                idProduit,
                date::date AS date,
                type,
                quantite,
                SUM(CASE WHEN type = 'ENTREE' THEN quantite ELSE -quantite END)
                    OVER (PARTITION BY idProduit ORDER BY date ROWS UNBOUNDED PRECEDING) AS stock_cumulatif
            FROM MOUVEMENT
        ),
        ruptures AS (
            SELECT idProduit, date
            FROM cumul
            WHERE stock_cumulatif <= 0
        ),
        grouped AS (
            SELECT date, COUNT(DISTINCT idProduit) AS count
            FROM ruptures
            WHERE date BETWEEN %s AND %s
            GROUP BY date
        )
        SELECT date, count
        FROM grouped
        ORDER BY date;
    """
    try:
        rows = execute_query(conn, query, (start_date, end_date), fetch=True)
        return [dict(date=row[0].strftime('%Y-%m-%d'), count=row[1]) for row in rows]
    except Exception as e:
        logger.error(f"[get_ruptures_history] Erreur : {e}")
        return []
