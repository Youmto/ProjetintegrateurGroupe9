from database import execute_query

def generate_stock_report(conn):
    query = "SELECT * FROM vue_inventaire_global;"
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('idProduit', 'reference', 'nom', 'type', 'quantite_totale', 'nb_emplacements'), row)) for row in rows]

def generate_movement_report(conn, id_produit):
    query = "SELECT * FROM mouvements_produit(%s);"
    rows = execute_query(conn, query, (id_produit,), fetch=True)
    return [dict(zip(('type_mouvement', 'reference_bon', 'date_mouvement', 'quantite'), row)) for row in rows]

def generate_exception_reports(conn):
    query = "SELECT * FROM RAPPORT_EXCEPTION ORDER BY dateGeneration DESC;"
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('typeRapport', 'dateGeneration', 'description', 'idBonReception', 'idBonExpedition'), row)) for row in rows]
