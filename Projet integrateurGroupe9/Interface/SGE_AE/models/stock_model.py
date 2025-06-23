from database import execute_query

def search_products(conn, search_term=None, product_type=None):
    query = """
    SELECT
        p.idProduit, p.reference, p.nom, p.description,
        p.marque, p.modele, p.type, p.estMaterielEmballage,
        COALESCE(SUM(i.quantiteDisponible), 0) AS quantite_disponible
    FROM PRODUIT p
    LEFT JOIN INVENTAIRE i ON p.idProduit = i.idProduit
    WHERE 1=1
    """
    params = []

    if search_term:
        query += " AND (p.reference ILIKE %s OR p.nom ILIKE %s)"
        params.extend([f"%{search_term}%", f"%{search_term}%"])

    if product_type:
        query += " AND p.type = %s"
        params.append(product_type)

    query += """
    GROUP BY p.idProduit, p.reference, p.nom, p.description,
             p.marque, p.modele, p.type, p.estMaterielEmballage
    """

    rows = execute_query(conn, query, tuple(params), fetch=True)

    return [{
        'idProduit': r[0], 'reference': r[1], 'nom': r[2],
        'description': r[3], 'marque': r[4], 'modele': r[5],
        'type': r[6], 'estMaterielEmballage': r[7], 'quantite_disponible': r[8]
    } for r in rows]

def get_product_details(conn, product_id):
    query = """
    SELECT
    p.idProduit, p.reference, p.nom, p.description,
    p.marque, p.modele, p.type, p.estMaterielEmballage,
    pm.longueur, pm.largeur, pm.hauteur, pm.masse, pm.volume,
    pl.version, pl.typeLicence, pl.dateExpiration
    FROM PRODUIT p
    LEFT JOIN PRODUIT_MATERIEL pm ON p.idProduit = pm.idProduit
    LEFT JOIN PRODUIT_LOGICIEL pl ON p.idProduit = pl.idProduit
    WHERE p.idProduit = %s
    """
    row = execute_query(conn, query, (product_id,), fetch=True)
    if not row:
     return None
    row = row[0]
    product = {
    'idProduit': row[0], 'reference': row[1], 'nom': row[2],
    'description': row[3] or "Non renseignée",
    'marque': row[4] or "Non renseignée",
    'modele': row[5] or "Non renseigné",
    'type': row[6],
    'estMaterielEmballage': "Oui" if row[7] else "Non"
    }
    if row[6] == 'materiel' and row[8]:
     product.update({
    'longueur': f"{row[8]} cm", 'largeur': f"{row[9]} cm",
    'hauteur': f"{row[10]} cm", 'masse': f"{row[11]} kg",
    'volume': f"{row[12]} cm³"
    })
    elif row[6] == 'logiciel' and row[13]:
     product.update({
    'version': row[13], 'typeLicence': row[14],
    'dateExpiration': row[15].strftime("%d/%m/%Y") if row[15] else "Illimitée"
    })
    return product

def get_stock_locations(conn, product_id):
    query = """
    SELECT c.reference, e.nom, s.quantite, l.numeroLot
    FROM STOCKER s
    JOIN LOT l ON s.idLot = l.idLot
    JOIN CELLULE c ON s.idCellule = c.idCellule
    JOIN COMPOSER_ENTREPOT ce ON c.idCellule = ce.idCellule
    JOIN ENTREPOT e ON ce.idEntrepot = e.idEntrepot
    WHERE l.idProduit = %s AND s.quantite > 0
    """
    rows = execute_query(conn, query, (product_id,), fetch=True)
    return [{'reference_cellule': r[0], 'nom_entrepot': r[1], 'quantite': r[2], 'numeroLot': r[3]} for r in rows]

def get_pending_receptions(conn):
    query = """
    SELECT idBon, reference, dateCreation, dateReceptionPrevue, statut
    FROM BON_RECEPTION
    WHERE statut IN ('en_attente', 'en_cours')
    ORDER BY dateReceptionPrevue
    """
    return execute_query(conn, query, fetch=True)

def create_reception(conn, reference, date_prevue, id_responsable):
    query = """
    INSERT INTO BON_RECEPTION(reference, dateCreation, dateReceptionPrevue, statut)
    VALUES (%s, CURRENT_DATE, %s, 'en_attente') RETURNING idBon
    """
    bon_id = execute_query(conn, query, (reference, date_prevue), fetch=True)[0][0]
    query = "INSERT INTO RESPONSABLE_RECEPTION(idIndividu, idBon) VALUES (%s, %s)"
    execute_query(conn, query, (id_responsable, bon_id))
    return bon_id

def get_pending_expeditions(conn):
    """
    Récupère toutes les expéditions en statut 'en_attente' ou 'en_cours'
    Retourne une liste de dictionnaires formatés
    """
    query = """
    SELECT idBon, reference, dateCreation, dateExpeditionPrevue, priorite, statut
    FROM BON_EXPEDITION
    WHERE statut IN ('en_attente', 'en_cours')
    ORDER BY dateExpeditionPrevue, priorite DESC
    """
    rows = execute_query(conn, query, fetch=True)
    
    return [{
        'idBon': r[0],
        'reference': r[1],
        'dateCreation': r[2],
        'dateExpeditionPrevue': r[3],
        'priorite': r[4],
        'statut': r[5]
    } for r in rows]

def create_expedition(conn, reference, date_prevue, priorite, id_responsable):
    query = """
    INSERT INTO BON_EXPEDITION(reference, dateCreation, dateExpeditionPrevue, priorite, statut)
    VALUES (%s, CURRENT_DATE, %s, %s, 'en_attente')
    RETURNING idBon
    """
    bon_id = execute_query(conn, query, (reference, date_prevue, priorite), fetch=True)[0][0]
    query = "INSERT INTO RESPONSABLE_EXPEDITION(idIndividu, idBon) VALUES (%s, %s)"
    execute_query(conn, query, (id_responsable, bon_id))
    return bon_id

def prepare_expedition(conn, bon_id, produit_id, quantite):
    query = "SELECT preparer_expedition(%s, %s, %s);"
    return execute_query(conn, query, (bon_id, produit_id, quantite), fetch=True)[0][0]

def receive_products(conn, bon_id, products):
    for product in products:
     lot_id = execute_query(conn, """
    INSERT INTO LOT(numeroLot, quantiteInitiale, quantiteDisponible, dateProduction, statut)
    VALUES (%s, %s, %s, %s, 'actif')
    RETURNING idLot
    """, (
    product['lot_reference'], product['quantity'],
    product['quantity'], product['production_date']
    ), fetch=True)[0][0] 
    colis_id = execute_query(conn, """
        INSERT INTO COLIS(reference, dateCreation, statut)
        VALUES (%s, CURRENT_DATE, 'recu') RETURNING idColis
    """, (f"COL-{lot_id}",), fetch=True)[0][0]

    execute_query(conn, "INSERT INTO RECEVOIR_COLIS(idBon, idColis) VALUES (%s, %s)", (bon_id, colis_id))
    execute_query(conn, "INSERT INTO CONTENIR(idColis, idLot, quantite) VALUES (%s, %s, %s)", (colis_id, lot_id, product['quantity']))
    execute_query(conn, "INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite) VALUES (%s, %s, CURRENT_DATE, %s)", (lot_id, product['cellule_id'], product['quantity']))
    execute_query(conn, "UPDATE BON_RECEPTION SET statut = 'termine' WHERE idBon = %s", (bon_id,))

