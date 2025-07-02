import logging
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)

def get_produits_a_approvisionner(conn, seuil=10):
    try:
        query = """
            SELECT p.idProduit, p.nom, COALESCE(SUM(s.quantite), 0) AS quantite_totale
            FROM PRODUIT p
            LEFT JOIN LOT l ON l.idProduit = p.idProduit
            LEFT JOIN STOCKER s ON s.idLot = l.idLot
            GROUP BY p.idProduit, p.nom
            HAVING COALESCE(SUM(s.quantite), 0) <= %s
            ORDER BY quantite_totale ASC;
        """
        return execute_query(conn, query, (seuil,), fetch=True)
    except Exception as e:
        logger.error(f"[get_produits_a_approvisionner] Erreur : {e}")
        return []


def enregistrer_approvisionnement(conn, id_produit, quantite, date_livraison_prevue, id_organisation=None):
    try:
        query = """
            INSERT INTO DEMANDE_APPROVISIONNEMENT (idOrganisation, idProduit, quantite, dateLivraisonPrevue)
            VALUES (%s, %s, %s, %s);
        """
        params = (id_organisation, id_produit, quantite, date_livraison_prevue)
        execute_query(conn, query, params)
    except Exception as e:
        logger.error(f"[enregistrer_approvisionnement] Erreur : {e}")
        raise



def get_demandes_approvisionnement(conn):
    try:
        query = """
            SELECT 
                da.idDemande,
                o.nom AS organisation,
                p.nom AS produit,
                da.quantite,
                da.dateLivraisonPrevue,
                da.dateDemande
            FROM DEMANDE_APPROVISIONNEMENT da
            JOIN ORGANISATION o ON o.idOrganisation = da.idOrganisation
            JOIN PRODUIT p ON p.idProduit = da.idProduit
            ORDER BY da.dateDemande DESC;
        """
        rows = execute_query(conn, query, fetch=True)
        columns = ['idDemande', 'organisation', 'produit', 'quantite', 'dateLivraisonPrevue', 'dateDemande']
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        logger.error(f"[get_demandes_approvisionnement] Erreur : {e}")
        return []
