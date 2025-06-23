from models.supervision_model import (
    occupation_cellules, produits_en_rupture,
    produits_jamais_stockes, cellules_vides,
    produits_expirant_bientot
)

def handle_occupation_cellules(conn):
    return occupation_cellules(conn)

def handle_ruptures(conn):
    return produits_en_rupture(conn)

def handle_produits_non_stockes(conn):
    return produits_jamais_stockes(conn)

def handle_cellules_vides(conn):
    return cellules_vides(conn)

def handle_expirations(conn, jours):
    return produits_expirant_bientot(conn, jours)