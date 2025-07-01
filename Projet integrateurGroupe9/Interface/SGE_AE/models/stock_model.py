import logging
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)


def search_products(conn, search_term=None, product_type=None):
    try:
        query = """
        SELECT
            p.idProduit, p.reference, p.nom, p.description,
            p.marque, p.modele, p.type, p.estMaterielEmballage,
            COALESCE(SUM(i.quantiteDisponible), 0)
        FROM PRODUIT p
        LEFT JOIN INVENTAIRE i ON p.idProduit = i.idProduit
        WHERE 1=1
        """
        params = []

        if search_term:
            query += " AND (p.reference ILIKE %s OR p.nom ILIKE %s)"
            params += [f"%{search_term}%", f"%{search_term}%"]

        if product_type:
            query += " AND p.type = %s"
            params.append(product_type)

        query += " GROUP BY p.idProduit, p.reference, p.nom, p.description, p.marque, p.modele, p.type, p.estMaterielEmballage"

        rows = execute_query(conn, query, tuple(params), fetch=True)
        return [{
            'idProduit': r[0], 'reference': r[1], 'nom': r[2],
            'description': r[3], 'marque': r[4], 'modele': r[5],
            'type': r[6], 'estMaterielEmballage': r[7], 'quantite_disponible': r[8]
        } for r in rows]
    except Exception as e:
        logger.error(f"[search_products] Erreur : {e}")
        return []

def get_product_details(conn, product_id):
    try:
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
        r = row[0]
        product = {
            'idProduit': r[0], 'reference': r[1], 'nom': r[2],
            'description': r[3] or "Non renseignée",
            'marque': r[4] or "Non renseignée",
            'modele': r[5] or "Non renseigné",
            'type': r[6],
            'estMaterielEmballage': "Oui" if r[7] else "Non"
        }
        if r[6] == 'materiel' and r[8]:
            product.update({
                'longueur': f"{r[8]} cm", 'largeur': f"{r[9]} cm",
                'hauteur': f"{r[10]} cm", 'masse': f"{r[11]} kg", 'volume': f"{r[12]} cm³"
            })
        elif r[6] == 'logiciel':
            product.update({
                'version': r[13], 'typeLicence': r[14],
                'dateExpiration': r[15].strftime('%d/%m/%Y') if r[15] else "Illimitée"
            })
        return product
    except Exception as e:
        logger.error(f"[get_product_details] Erreur : {e}")
        return None

def get_stock_locations(conn, product_id):
    try:
        query = """
        SELECT c.reference, e.nom, s.quantite, l.numeroLot
        FROM STOCKER s
        JOIN LOT l ON s.idLot = l.idLot
        JOIN CELLULE c ON s.idCellule = c.idCellule
        JOIN COMPOSER_ENTREPOT ce ON ce.idCellule = c.idCellule
        JOIN ENTREPOT e ON ce.idEntrepot = e.idEntrepot
        WHERE l.idProduit = %s AND s.quantite > 0
        """
        rows = execute_query(conn, query, (product_id,), fetch=True)
        return [{'reference_cellule': r[0], 'nom_entrepot': r[1], 'quantite': r[2], 'numeroLot': r[3]} for r in rows]
    except Exception as e:
        logger.error(f"[get_stock_locations] Erreur : {e}")
        return []


def get_pending_receptions(conn):
    return execute_query(conn, """
        SELECT idBon, reference, dateCreation, dateReceptionPrevue, statut
        FROM BON_RECEPTION
        WHERE statut IN ('en_attente', 'en_cours')
        ORDER BY dateReceptionPrevue
    """, fetch=True)

def create_reception(conn, reference, date_prevue, id_responsable):
    bon_id = execute_query(conn, """
        INSERT INTO BON_RECEPTION(reference, dateCreation, dateReceptionPrevue, statut)
        VALUES (%s, CURRENT_DATE, %s, 'en_attente') RETURNING idBon
    """, (reference, date_prevue), fetch=True)[0][0]
    execute_query(conn, "INSERT INTO RESPONSABLE_RECEPTION(idIndividu, idBon) VALUES (%s, %s)", (id_responsable, bon_id))
    return bon_id

def receive_products(conn, bon_id, products):
    try:
        for product in products:
            lot_id = execute_query(conn, """
                INSERT INTO LOT(numeroLot, quantiteInitiale, quantiteDisponible, dateProduction, statut)
                VALUES (%s, %s, %s, %s, 'actif') RETURNING idLot
            """, (product['lot_reference'], product['quantity'], product['quantity'], product['production_date']), fetch=True)[0][0]

            colis_id = execute_query(conn, """
                INSERT INTO COLIS(reference, dateCreation, statut)
                VALUES (%s, CURRENT_DATE, 'termine') RETURNING idColis
            """, (f"COL-{lot_id}",), fetch=True)[0][0]

            execute_query(conn, "INSERT INTO RECEVOIR_COLIS(idBon, idColis) VALUES (%s, %s)", (bon_id, colis_id))
            execute_query(conn, "INSERT INTO CONTENIR(idColis, idLot, quantite) VALUES (%s, %s, %s)", (colis_id, lot_id, product['quantity']))
            execute_query(conn, "INSERT INTO STOCKER(idLot, idCellule, dateStockage, quantite) VALUES (%s, %s, CURRENT_DATE, %s)", (lot_id, product['cellule_id'], product['quantity']))

        execute_query(conn, "UPDATE BON_RECEPTION SET statut = 'termine' WHERE idBon = %s", (bon_id,))
    except Exception as e:
        logger.error(f"[receive_products] Erreur : {e}")
        conn.rollback()

def get_pending_expeditions(conn):
    rows = execute_query(conn, """
        SELECT idBon, reference, dateCreation, dateExpeditionPrevue, priorite, statut
        FROM BON_EXPEDITION
        WHERE statut IN ('en_attente', 'en_cours')
        ORDER BY dateExpeditionPrevue, priorite DESC
    """, fetch=True)
    return [{'idBon': r[0], 'reference': r[1], 'dateCreation': r[2], 'dateExpeditionPrevue': r[3], 'priorite': r[4], 'statut': r[5]} for r in rows]

def create_expedition(conn, reference, date_prevue, priorite, id_responsable):
    bon_id = execute_query(conn, """
        INSERT INTO BON_EXPEDITION(reference, dateCreation, dateExpeditionPrevue, priorite, statut)
        VALUES (%s, CURRENT_DATE, %s, %s, 'en_attente') RETURNING idBon
    """, (reference, date_prevue, priorite), fetch=True)[0][0]
    execute_query(conn, "INSERT INTO RESPONSABLE_EXPEDITION(idIndividu, idBon) VALUES (%s, %s)", (id_responsable, bon_id))
    return bon_id

def prepare_expedition(conn, bon_id, produit_id, quantite):
    return execute_query(conn, "SELECT preparer_expedition(%s, %s, %s);", (bon_id, produit_id, quantite), fetch=True)[0][0]


def add_cellule(conn, reference, longueur, largeur, hauteur, masse_max, volume_max, capacite_max, position, entrepot_id):
    execute_query(conn, """
        SELECT ajouter_cellule(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (reference, longueur, largeur, hauteur, masse_max, volume_max, capacite_max, position, entrepot_id))

def update_cellule(conn, id_cellule, longueur, largeur, hauteur, masse_max, volume_max, capacite_max, statut):
    execute_query(conn, """
        SELECT update_cellule(%s, %s, %s, %s, %s, %s, %s, %s)
    """, (id_cellule, longueur, largeur, hauteur, masse_max, volume_max, capacite_max, statut))

def get_cellules_info(conn):
    """
    Récupère toutes les cellules d'entrepôt avec leurs informations d'occupation.
    """
    rows = execute_query(conn, "SELECT * FROM vue_emplacements_occupes;", fetch=True)

    if not rows:
        return []

    return [{
        "idCellule": r[0],
        "reference": r[1],
        "idEntrepot": r[2],
        "nom_entrepot": r[3],
        "capacite_max": r[4],
        "volumeMaximal": r[5],
        "statut": r[6],
        "nb_lots": r[7],
        "quantite_totale": r[8],
        "volume_utilise": r[9],
        "volume_restant": r[10],
        "taux_occupation": r[11]
    } for r in rows]
def get_entrepot_capacite_restante(conn, id_entrepot):
    result = execute_query(conn, """
        SELECT e.capaciteMaximale - COALESCE(SUM(c.capacite_max), 0)
        FROM ENTREPOT e
        LEFT JOIN COMPOSER_ENTREPOT ce ON e.idEntrepot = ce.idEntrepot
        LEFT JOIN CELLULE c ON ce.idCellule = c.idCellule
        WHERE e.idEntrepot = %s
        GROUP BY e.capaciteMaximale
    """, (id_entrepot,), fetch=True)
    return result[0][0] if result else None

def deplacer_lot(conn, id_lot, id_cellule_source, id_cellule_destination, quantite, id_responsable):
    return execute_query(conn, "SELECT deplacer_lot(%s, %s, %s, %s, %s);", (id_lot, id_cellule_source, id_cellule_destination, quantite, id_responsable), fetch=True)[0][0]


def receptionner_lot(conn, id_bon, ref_lot, id_produit, quantite, date_prod, date_exp, id_cellule):
    return execute_query(conn, "SELECT receptionner_lot(%s, %s, %s, %s, %s, %s, %s);", (id_bon, ref_lot, id_produit, quantite, date_prod, date_exp, id_cellule), fetch=True)[0][0]

def get_cellule_details(conn, id_cellule):
    query = "SELECT * FROM vue_emplacements_occupes WHERE idCellule = %s;"
    rows = execute_query(conn, query, (id_cellule,), fetch=True)
    if not rows:
        raise ValueError(f"Cellule {id_cellule} introuvable.")
    r = rows[0]
    return {
        "idCellule": r[0],
        "reference": r[1],
        "idEntrepot": r[2],
        "nom_entrepot": r[3],
        "capacite_max": r[4],
        "volumeMaximal": r[5],
        "statut": r[6],  # ✅ Ce champ est maintenant présent
        "nb_lots": r[7],
        "quantite_totale": r[8],
        "volume_utilise": r[9],
        "volume_restant": r[10],
        "taux_occupation": r[11]
    }
def get_lot_info(conn, id_lot):
    rows = execute_query(conn, """
    SELECT l.idLot, l.numeroLot, l.idProduit, l.quantiteDisponible,
    p.type, pm.volume
    FROM LOT l
    JOIN PRODUIT p ON l.idProduit = p.idProduit
    LEFT JOIN PRODUIT_MATERIEL pm ON pm.idProduit = p.idProduit
    WHERE l.idLot = %s;
    """, (id_lot,), fetch=True)

    if not rows:
        return None

    row = rows[0]
    lot = {
        "idLot": row[0],
        "numeroLot": row[1],
        "idProduit": row[2],
        "quantite_disponible": row[3],
        "type": row[4],
        "volume_unitaire": row[5]
    }

    print("[DEBUG get_lot_info]", lot)  # ⬅️ Ajoute ceci temporairement
    return lot