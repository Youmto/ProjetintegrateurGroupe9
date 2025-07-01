import logging
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)

def get_produits_par_lot(conn, id_lot):
    try:
        query = """
            SELECT idColis, idProduit, nomProduit, typeProduit, quantiteDansColis,
                   version, typeLicence, dateExpiration,
                   longueur, largeur, hauteur, masse, volume
            FROM vue_produits_par_lot_complet
            WHERE idLot = %s
        """
        rows = execute_query(conn, query, (id_lot,), fetch=True)
        return rows
    except Exception as e:
        logger.error(f"[get_produits_par_lot] Erreur : {e}")
        return []

def supprimer_produit_dans_colis(conn, id_colis, id_lot):
    try:
        # Suppression d'une entrée dans CONTENIR (produit indirect via lot)
        query = "DELETE FROM CONTENIR WHERE idColis = %s AND idLot = %s;"
        execute_query(conn, query, (id_colis, id_lot))
    except Exception as e:
        logger.error(f"[supprimer_produit_dans_colis] Erreur : {e}")

def modifier_produit_dans_colis(conn, id_colis, id_produit, quantite,
                                 version=None, type_licence=None, date_expiration=None,
                                 longueur=None, largeur=None, hauteur=None, masse=None, volume=None):
    try:
        # Trouver le lot correspondant au produit et colis (on prend le premier lot trouvé)
        query_lot = """
            SELECT l.idLot
            FROM LOT l
            JOIN CONTENIR co ON co.idLot = l.idLot
            WHERE co.idColis = %s AND l.idProduit = %s
            LIMIT 1
        """
        result = execute_query(conn, query_lot, (id_colis, id_produit), fetch=True)
        if not result:
            logger.error(f"[modifier_produit_dans_colis] Aucun lot trouvé pour colis {id_colis} et produit {id_produit}")
            return

        id_lot = result[0][0]

        # Met à jour ou insère dans CONTENIR
        query1 = """
            INSERT INTO CONTENIR (idColis, idLot, quantite)
            VALUES (%s, %s, %s)
            ON CONFLICT (idColis, idLot) DO UPDATE SET quantite = EXCLUDED.quantite
        """
        execute_query(conn, query1, (id_colis, id_lot, quantite))

        # Mise à jour attributs logiciel
        if version is not None:
            query2 = """
                INSERT INTO produit_logiciel (idProduit, version, typeLicence, dateExpiration)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (idProduit) DO UPDATE
                  SET version = EXCLUDED.version,
                      typeLicence = EXCLUDED.typeLicence,
                      dateExpiration = EXCLUDED.dateExpiration
            """
            execute_query(conn, query2, (id_produit, version, type_licence, date_expiration))

        # Mise à jour attributs matériel
        if longueur is not None:
            query3 = """
                INSERT INTO produit_materiel (idProduit, longueur, largeur, hauteur, masse, volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (idProduit) DO UPDATE
                  SET longueur = EXCLUDED.longueur,
                      largeur = EXCLUDED.largeur,
                      hauteur = EXCLUDED.hauteur,
                      masse = EXCLUDED.masse,
                      volume = EXCLUDED.volume
            """
            execute_query(conn, query3, (id_produit, longueur, largeur, hauteur, masse, volume))

    except Exception as e:
        logger.error(f"[modifier_produit_dans_colis] Erreur : {e}")

def get_all_lots(conn):
    try:
        query = "SELECT idLot, numeroLot FROM LOT ORDER BY numeroLot;"
        return execute_query(conn, query, fetch=True)
    except Exception as e:
        logger.error(f"[get_all_lots] Erreur : {e}")
        return []
