from database import execute_query


def produits_en_rupture(conn):
    query = "SELECT * FROM produits_en_rupture();"
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('idProduit', 'reference', 'nom', 'quantite_disponible'), row)) for row in rows]

def occupation_cellules(conn):
    query = "SELECT * FROM occupation_cellules();"
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('idCellule', 'reference', 'entrepot', 'volume_utilise', 'volume_maximal', 'pourcentage_occupation'), row)) for row in rows]
def produits_jamais_stockes(conn):
    query = "SELECT * FROM produits_jamais_stockes();"
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('idProduit', 'reference', 'nom'), row)) for row in rows]

def cellules_vides(conn):
    query = "SELECT * FROM cellules_vides();"
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('idCellule', 'reference', 'entrepot', 'volume_maximal'), row)) for row in rows]

def produits_expirant_bientot(conn, jours=30):
    query = "SELECT * FROM produits_expirant_bientot(%s);"
    rows = execute_query(conn, query, (jours,), fetch=True)
    return [dict(zip(('idProduit', 'reference', 'nom', 'date_expiration', 'jours_restants', 'quantite_disponible', 'emplacement'), row)) for row in rows]


