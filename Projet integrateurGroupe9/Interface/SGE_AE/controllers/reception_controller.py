from models.reception_model import get_bons_reception, receptionner_lot, valider_reception


def handle_reception(conn, id_bon, lot_data):
    """
    Traite la réception d'un lot et le stocke.
    """
    return receptionner_lot(conn, id_bon, **lot_data)

def handle_validation_reception(conn, reference, date_prevue, id_individu):
    """
    Crée un bon de réception.
    """
    from models.stock_model import create_reception
    return create_reception(conn, reference, date_prevue, id_individu)

def handle_receptions_en_attente(conn):
    """
    Récupère tous les bons de réception en attente ou en cours.
    """
    return get_bons_reception(conn)
