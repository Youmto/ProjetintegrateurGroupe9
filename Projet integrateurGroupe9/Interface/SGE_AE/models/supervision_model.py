from SGE_AE.database import execute_query
import logging

logger = logging.getLogger(__name__)

def produits_en_rupture(conn):
    try:
        query = "SELECT * FROM produits_en_rupture();"
        rows = execute_query(conn, query, fetch=True)
        result = [dict(zip((
            'idProduit', 'reference', 'nom', 'description',
            'marque', 'modele', 'type', 'estMaterielEmballage', 'quantite'
        ), row))
        for row in rows
        ]
        return result
    except Exception as e:
        logger.error(f"[produits_en_rupture] Erreur : {e}")
        return []


def occupation_cellules(conn):
    """
    Retourne l'état d'occupation des cellules (taux de remplissage + volume).
    Basé sur la vue SQL vue_emplacements_occupes.
    """
    try:
        query = "SELECT * FROM vue_emplacements_occupes;"
        rows = execute_query(conn, query, fetch=True)

        colonnes = (
            'idCellule', 'reference', 'idEntrepot', 'nom_entrepot', 'capacite_max',
            'volumeMaximal', 'statut', 'nb_lots', 'quantite_totale',
            'volume_utilise', 'volume_restant', 'taux_occupation'
        )

        return [dict(zip(colonnes, row)) for row in rows]

    except Exception as e:
        logger.error(f"[occupation_cellules] Erreur : {e}", exc_info=True)
        return []

def produits_jamais_stockes(conn):
    """
    Retourne les produits qui n'ont jamais été stockés dans une cellule.
    Suppose qu'une vue ou fonction SQL produits_jamais_stockes() existe.
    """
    try:
        query = "SELECT * FROM produits_jamais_stockes();"
        rows = execute_query(conn, query, fetch=True)
        return [dict(zip(('idProduit', 'reference', 'nom'), row)) for row in rows]
    except Exception as e:
        logger.error(f"[produits_jamais_stockes] Erreur : {e}")
        return []

def cellules_vides(conn):
    """
    Retourne les cellules sans aucun lot stocké.
    Suppose que la vue ou fonction cellules_vides() existe.
    """
    try:
        query = "SELECT * FROM cellules_vides();"
        rows = execute_query(conn, query, fetch=True)
        return [dict(zip(('idCellule', 'reference', 'entrepot', 'volume_maximal'), row)) for row in rows]
    except Exception as e:
        logger.error(f"[cellules_vides] Erreur : {e}")
        return []

def produits_expirant_bientot(conn, jours=30):
    """
    Retourne les produits dont la date d'expiration est proche.
    jours : fenêtre temporelle (par défaut 30 jours)
    """
    try:
        query = "SELECT * FROM produits_expirant_bientot(%s);"
        rows = execute_query(conn, query, (jours,), fetch=True)
        return [dict(zip((
            'idProduit', 'reference', 'nom', 'date_expiration',
            'jours_restants', 'quantite_disponible', 'emplacement'
        ), row)) for row in rows]
    except Exception as e:
        logger.error(f"[produits_expirant_bientot] Erreur : {e}")
        return []