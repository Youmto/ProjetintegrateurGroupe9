from models.movement_model import (
    mouvements_produit,
    deplacer_lot,
    ajuster_inventaire
)

def handle_mouvements_produit(conn, produit_id):
    return mouvements_produit(conn, produit_id)

def handle_deplacer_lot(conn, lot_id, cellule_src, cellule_dest, quantite, responsable_id):
    return deplacer_lot(conn, lot_id, cellule_src, cellule_dest, quantite, responsable_id)

def handle_ajuster_inventaire(conn, lot_id, cellule_id, nouvelle_qte, responsable_id, commentaire):
    return ajuster_inventaire(conn, lot_id, cellule_id, nouvelle_qte, responsable_id, commentaire)