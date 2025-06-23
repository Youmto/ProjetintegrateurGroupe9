from models.expedition_model import preparer_expedition, annuler_colis
from models.expedition_model import (
    create_expedition_bon,
    get_pending_expeditions,
    preparer_expedition,
    get_colis_pret_expedition
)

def handle_preparation_expedition(conn, id_bon, id_produit, quantite):
    return preparer_expedition(conn, id_bon, id_produit, quantite)

def handle_annulation_colis(conn, id_colis):
    annuler_colis(conn, id_colis)

def handle_colis_prets(conn):
    return get_colis_pret_expedition(conn)
def handle_create_expedition(conn, reference, date_prevue, priorite, id_responsable):
    return create_expedition_bon(conn, reference, date_prevue, priorite, id_responsable)

def handle_pending_expeditions(conn):
    return get_pending_expeditions(conn)