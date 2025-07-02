import logging

from models.product_model import get_all_products
from controllers.approvisionnement_controller import handle_demandes_approvisionnement
from controllers.movement_controller import handle_mouvements_produit
from controllers.supervision_controller import (
    handle_occupation_cellules,
    handle_ruptures,
    handle_produits_non_stockes,
    handle_cellules_vides,
    handle_expirations,
    handle_expeditions_terminées,
)

from models.dashboard_model import( fetch_ruptures,get_ruptures_history)

logger = logging.getLogger(__name__)



def get_ruptures(self, conn):
        """
        Produits en rupture avec date de dernière rupture.
        """
        try:
            return fetch_ruptures(conn)
        except Exception as e:
            logger.error("Erreur get_ruptures: %s", e, exc_info=True)
            return []

def get_occupation_cellules(self, conn):
        try:
            return handle_occupation_cellules(conn)
        except Exception as e:
            logger.error("Erreur get_occupation_cellules: %s", e, exc_info=True)
            return []

def get_produits_non_stockes(self, conn):
        try:
            return handle_produits_non_stockes(conn)
        except Exception as e:
            logger.error("Erreur get_produits_non_stockes: %s", e, exc_info=True)
            return []

def get_cellules_vides(self, conn):
        try:
            return handle_cellules_vides(conn)
        except Exception as e:
            logger.error("Erreur get_cellules_vides: %s", e, exc_info=True)
            return []

def get_produits_expirant_bientot(self, conn):
        try:
            return handle_expirations(conn)
        except Exception as e:
            logger.error("Erreur get_produits_expirant_bientot: %s", e, exc_info=True)
            return []

def get_expeditions_terminées(self, conn):
        try:
            return handle_expeditions_terminées(conn)
        except Exception as e:
            logger.error("Erreur get_expeditions_terminées: %s", e, exc_info=True)
            return []

def get_mouvements_produit(self, conn, id_produit):
        try:
            return handle_mouvements_produit(conn, id_produit)
        except Exception as e:
            logger.error("Erreur get_mouvements_produit: %s", e, exc_info=True)
            return []

def get_demandes_approvisionnement(self, conn):
        try:
            return handle_demandes_approvisionnement(conn)
        except Exception as e:
            logger.error("Erreur get_demandes_approvisionnement: %s", e, exc_info=True)
            return []

def get_all_produits(self, conn):
        try:
            return get_all_products(conn)
        except Exception as e:
            logger.error("Erreur get_all_produits: %s", e, exc_info=True)
            return []
        

def handle_ruptures_history(conn, start_date, end_date):
    return get_ruptures_history(conn, start_date, end_date)
