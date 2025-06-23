from database import execute_query

def deplacer_lot(conn, id_lot, cellule_src, cellule_dst, quantite, id_resp):
    query = """
    SELECT deplacer_lot(%s, %s, %s, %s, %s);
    """
    params = (id_lot, cellule_src, cellule_dst, quantite, id_resp)
    return execute_query(conn, query, params, fetch=True)[0][0]

def ajuster_inventaire(conn, id_lot, id_cellule, nouvelle_qte, id_resp, commentaire):
    query = """
    SELECT ajuster_inventaire(%s, %s, %s, %s, %s);
    """
    return execute_query(conn, query, (id_lot, id_cellule, nouvelle_qte, id_resp, commentaire), fetch=True)[0][0]

def mouvements_produit(conn, id_produit):
    query = "SELECT * FROM mouvements_produit(%s);"
    rows = execute_query(conn, query, (id_produit,), fetch=True)
    return [dict(zip(('type_mouvement', 'reference_bon', 'date_mouvement', 'quantite'), row)) for row in rows]