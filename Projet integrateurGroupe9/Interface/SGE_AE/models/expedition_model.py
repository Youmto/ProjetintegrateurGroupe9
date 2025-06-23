from database import execute_query

def get_colis_pret_expedition(conn):
    """
    Récupère tous les colis marqués comme 'pret_a_expedier' avec leurs métadonnées
    Retourne une liste de dictionnaires structurés
    """
    query = """
    SELECT
        c.idColis,
        c.reference,
        c.dateCreation,
        be.reference AS bon_expedition_ref,
        be.dateExpeditionPrevue,
        i.nom AS destinataire,
        COUNT(DISTINCT ct.idLot) AS nb_lots,
        COALESCE(SUM(ct.quantite), 0) AS quantite_totale
    FROM COLIS c
    JOIN EXPEDIER_COLIS ec ON c.idColis = ec.idColis
    JOIN BON_EXPEDITION be ON ec.idBon = be.idBon
    JOIN INDIVIDU i ON c.idDestinataire = i.idIndividu
    LEFT JOIN CONTENIR ct ON c.idColis = ct.idColis
    WHERE c.statut = 'pret_a_expedier'
    GROUP BY 
        c.idColis, 
        c.reference, 
        c.dateCreation, 
        be.reference, 
        be.dateExpeditionPrevue,
        i.nom
    ORDER BY be.dateExpeditionPrevue ASC, c.dateCreation DESC;
    """
    
    rows = execute_query(conn, query, fetch=True)
    
    return [{
        "id": row[0],
        "reference": row[1],
        "date_creation": row[2],
        "bon_expedition": row[3],
        "date_expedition_prevue": row[4],
        "destinataire": row[5],
        "nb_lots": row[6],
        "quantite_totale": row[7]
    } for row in rows]

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
def preparer_expedition(conn, id_bon, id_produit, quantite):
    query = "SELECT preparer_expedition(%s, %s, %s);"
    return execute_query(conn, query, (id_bon, id_produit, quantite), fetch=True)[0][0]

def annuler_colis(conn, id_colis):
    query = "SELECT annuler_colis(%s);"
    execute_query(conn, query, (id_colis,))

def get_colis_prets(conn):
    query = "SELECT * FROM colis_pret_expedition();"
    rows = execute_query(conn, query, fetch=True)
    return [
        dict(zip(
            ('idColis', 'reference', 'date_creation', 'bon_expedition', 'date_expedition_prevue', 'nb_lots', 'quantite_totale'),
            row
        )) for row in rows
    ]

def create_expedition_bon(conn, reference, date_prevue, priorite, id_responsable):
    query = """
    INSERT INTO BON_EXPEDITION(reference, dateCreation, dateExpeditionPrevue, priorite, statut)
    VALUES (%s, CURRENT_DATE, %s, %s, 'en_attente')
    RETURNING idBon
    """
    bon_id = execute_query(conn, query, (reference, date_prevue, priorite), fetch=True)[0][0]
    
    query2 = """
    INSERT INTO RESPONSABLE_EXPEDITION(idIndividu, idBon)
    VALUES (%s, %s)
    """
    execute_query(conn, query2, (id_responsable, bon_id))
    
    return bon_id