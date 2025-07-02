import logging
from models.approvisionnement_model import (
    get_produits_a_approvisionner,
    enregistrer_approvisionnement,
    get_demandes_approvisionnement
)

logger = logging.getLogger(__name__)

def charger_produits_a_approvisionner(conn, seuil=10):
    try:
        return get_produits_a_approvisionner(conn, seuil)
    except Exception as e:
        logger.error(f"[charger_produits_a_approvisionner] Erreur : {e}")
        return []

def ajouter_demande_approvisionnement(conn, id_produit, quantite, date_livraison, id_organisation):
    try:
        enregistrer_approvisionnement(conn, id_produit, quantite, date_livraison, id_organisation)
        return True
    except Exception as e:
        logger.error(f"[ajouter_demande_approvisionnement] Erreur : {e}")
        return False

def handle_demandes_approvisionnement(conn):
    return get_demandes_approvisionnement(conn)