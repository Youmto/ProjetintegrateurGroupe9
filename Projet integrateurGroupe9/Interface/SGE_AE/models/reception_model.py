from database import execute_query

def receptionner_lot(conn, id_bon, ref_lot, id_produit, quantite, date_prod, date_exp, id_cellule):
    query = """
    SELECT receptionner_lot(%s, %s, %s, %s, %s, %s, %s);
    """
    params = (id_bon, ref_lot, id_produit, quantite, date_prod, date_exp, id_cellule)
    return execute_query(conn, query, params, fetch=True)[0][0]

def valider_reception(conn, id_bon):
    query = "SELECT valider_reception(%s);"
    execute_query(conn, query, (id_bon,))
    
def get_bons_reception(conn):
    query = """
    SELECT idBon, reference, dateCreation, dateReceptionPrevue, statut
    FROM BON_RECEPTION
    WHERE statut IN ('en_attente', 'en_cours')
    ORDER BY dateReceptionPrevue
    """
    rows = execute_query(conn, query, fetch=True)
    return [
        {
            'idBon': r[0],
            'reference': r[1],
            'dateCreation': r[2],
            'dateReceptionPrevue': r[3],
            'statut': r[4]
        }
        for r in rows
    ]
                
  