import logging
from fpdf import FPDF
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)

# =============================================================================
# 1. Création et gestion des bons d’expédition
# =============================================================================

def create_expedition_bon(conn, reference, date_prevue, priorite, id_responsable):
    """
    Crée un bon d’expédition avec son responsable associé.
    """
    try:
        query = """
        INSERT INTO BON_EXPEDITION(reference, dateCreation, dateExpeditionPrevue, priorite, statut)
        VALUES (%s, CURRENT_DATE, %s, %s, 'en_attente') RETURNING idBon;
        """
        bon_id = execute_query(conn, query, (reference, date_prevue, priorite), fetch=True)[0][0]

        query2 = "INSERT INTO RESPONSABLE_EXPEDITION(idIndividu, idBon) VALUES (%s, %s);"
        execute_query(conn, query2, (id_responsable, bon_id))
        return bon_id

    except Exception as e:
        logger.error(f"Erreur création bon d'expédition : {e}", exc_info=True)
        return None

def get_pending_expeditions(conn):
    """
    Récupère les bons d’expédition non terminés.
    """
    query = """
    SELECT idBon, reference, dateCreation, dateExpeditionPrevue, priorite, statut
    FROM BON_EXPEDITION
    WHERE statut IN ('en_attente', 'en_cours', 'pret_a_expedier')
    ORDER BY dateExpeditionPrevue, priorite DESC;
    """
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('idBon', 'reference', 'dateCreation', 'dateExpeditionPrevue', 'priorite', 'statut'), r)) for r in rows]

def valider_expedition(conn, id_bon):
    """
    Passe le bon et tous ses colis liés au statut 'en_cours'.
    """
    try:
        # 1. Le bon passe en cours uniquement s’il était prêt
        execute_query(conn, """
            UPDATE BON_EXPEDITION
            SET statut = 'en_cours'
            WHERE idBon = %s AND statut = 'pret_a_expedier';
        """, (id_bon,))

        # 2. Tous les colis liés à ce bon passent en_cours s’ils étaient prêts
        execute_query(conn, """
            UPDATE COLIS
            SET statut = 'en_cours'
            WHERE idColis IN (
                SELECT idColis FROM EXPEDIER_COLIS WHERE idBon = %s
            )
            AND statut = 'pret_a_expedier';
        """, (id_bon,))
    except Exception as e:
        logger.error(f"[valider_expedition] Erreur : {e}", exc_info=True)
        raise

def confirmer_livraison(conn, id_bon):
    try:
        # Met à jour tous les colis du bon en_cours -> terminé
        query = """
        UPDATE COLIS
        SET statut = 'termine'
        WHERE idColis IN (
            SELECT c.idColis
            FROM COLIS c
            JOIN EXPEDIER_COLIS ec ON ec.idColis = c.idColis
            WHERE ec.idBon = %s AND c.statut = 'en_cours'
        );
        """
        execute_query(conn, query, (id_bon,))

        # Vérifie s’il reste des colis en_cours pour ce bon
        query_check = """
        SELECT COUNT(*)
        FROM COLIS c
        JOIN EXPEDIER_COLIS ec ON ec.idColis = c.idColis
        WHERE ec.idBon = %s AND c.statut != 'termine';
        """
        count = execute_query(conn, query_check, (id_bon,), fetch=True)[0][0]

        if count == 0:
            # Tous les colis sont terminés, on termine le bon aussi
            query_bon = """
            UPDATE BON_EXPEDITION
            SET statut = 'termine', dateExpeditionReelle = CURRENT_DATE
            WHERE idBon = %s;
            """
            execute_query(conn, query_bon, (id_bon,))

    except Exception as e:
        logger.error(f"[handle_confirmer_livraison] Erreur : {e}")
        raise



# =============================================================================
# 2. Colis et préparation
# =============================================================================

def preparer_expedition(conn, id_bon: int, id_produit: int, quantite: int) -> int:
    """
    Appelle la fonction PostgreSQL preparer_expedition qui utilise les domaines :
    - dom_id pour les identifiants
    - dom_quantite pour la quantité

    Args:
        conn: Connexion à la base PostgreSQL
        id_bon: ID du bon d'expédition
        id_produit: ID du produit à expédier
        quantite: Quantité à expédier

    Returns:
        int: ID du colis créé

    Raises:
        Exception: En cas d'erreur SQL ou logique
    """
    try:
        result = execute_query(
            conn,
            "SELECT preparer_expedition(%s::dom_id, %s::dom_id, %s::dom_quantite);",
            (id_bon, id_produit, quantite),
            fetch=True
        )
        return result[0][0]
    except Exception as e:
        logger.error(f"[preparer_expedition] Erreur : {e}", exc_info=True)
        raise

def get_colis_by_bon(conn, bon_id):
    """
    Récupère tous les colis liés à un bon.
    """
    query = """
    SELECT c.idColis, c.reference, c.dateCreation, c.statut,
           COALESCE(SUM(ct.quantite), 0) AS quantite_totale
    FROM COLIS c
    JOIN EXPEDIER_COLIS ec ON c.idColis = ec.idColis
    LEFT JOIN CONTENIR ct ON c.idColis = ct.idColis
    WHERE ec.idBon = %s
    GROUP BY c.idColis
    ORDER BY c.dateCreation DESC;
    """
    rows = execute_query(conn, query, (bon_id,), fetch=True)
    return [dict(zip(('idColis', 'reference', 'dateCreation', 'statut', 'quantite_totale'), r)) for r in rows]

def get_lots_in_colis(conn, colis_id):
    """
    Détail des lots contenus dans un colis.
    """
    query = """
    SELECT l.numeroLot, l.dateProduction, l.dateExpiration, ct.quantite
    FROM CONTENIR ct
    JOIN LOT l ON l.idLot = ct.idLot
    WHERE ct.idColis = %s;
    """
    rows = execute_query(conn, query, (colis_id,), fetch=True)
    return [dict(zip(('numeroLot', 'dateProduction', 'dateExpiration', 'quantite'), r)) for r in rows]

def annuler_colis(conn, id_colis):
    """
    Annule un colis via fonction SQL.
    """
    query = "SELECT annuler_colis(%s);"
    execute_query(conn, query, (id_colis,))


# =============================================================================
# 3. États et rapports
# =============================================================================

def get_colis_pret_expedition(conn):
    """
    Retourne les colis au statut 'pret_a_expedier'.
    """
    query = """
    SELECT c.idColis, c.reference, c.dateCreation,
           be.reference, be.dateExpeditionPrevue,
           COUNT(DISTINCT ct.idLot), COALESCE(SUM(ct.quantite), 0)
    FROM COLIS c
    JOIN EXPEDIER_COLIS ec ON c.idColis = ec.idColis
    JOIN BON_EXPEDITION be ON ec.idBon = be.idBon
    LEFT JOIN CONTENIR ct ON c.idColis = ct.idColis
    WHERE c.statut = 'pret_a_expedier'
    GROUP BY c.idColis, be.reference, be.dateExpeditionPrevue
    ORDER BY be.dateExpeditionPrevue ASC, c.dateCreation DESC;
    """
    rows = execute_query(conn, query, fetch=True)
    return [
        {
            "idColis": r[0],
            "reference": r[1],
            "date_creation": r[2],
            "bon_expedition": r[3],
            "date_expedition_prevue": r[4],
            "nb_lots": r[5],
            "quantite_totale": r[6]
        } for r in rows
    ]

def get_colis_en_cours(conn):
    query = """
    SELECT c.idColis, c.reference, c.dateCreation,
           be.reference, be.dateExpeditionPrevue,
           COALESCE(SUM(ct.quantite), 0),
           c.statut
    FROM COLIS c
    JOIN EXPEDIER_COLIS ec ON c.idColis = ec.idColis
    JOIN BON_EXPEDITION be ON ec.idBon = be.idBon
    LEFT JOIN CONTENIR ct ON c.idColis = ct.idColis
    WHERE c.statut = 'en_cours'
    GROUP BY c.idColis, be.reference, be.dateExpeditionPrevue, c.statut
    ORDER BY be.dateExpeditionPrevue;
    """
    rows = execute_query(conn, fetch=True, query=query)
    return [
        {
            "idColis": r[0],
            "reference": r[1],
            "date_creation": r[2],
            "bon_expedition": r[3],
            "date_expedition_prevue": r[4],
            "quantite_totale": r[5],
            "statut": r[6]
        } for r in rows
    ]
def get_expedition_exceptions(conn, bon_id):
    """
    Récupère les exceptions liées à un bon d’expédition.
    """
    query = """
    SELECT dateGeneration, description
    FROM RAPPORT_EXCEPTION
    WHERE idBonExpedition = %s
    ORDER BY dateGeneration DESC;
    """
    rows = execute_query(conn, query, (bon_id,), fetch=True)
    return [dict(zip(('date', 'description'), r)) for r in rows]


# =============================================================================
# 4. Génération de bordereau PDF
# =============================================================================

def generer_bordereau_pdf(contenu, filename):
    """
    Génère un bordereau PDF à partir des lots d’un colis.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Bordereau de Colis", ln=True, align='C')
    pdf.ln(10)
    
    for item in contenu:
        ligne = (
            f"Lot: {item['numeroLot']}, "
            f"Qté: {item['quantite']}, "
            f"Prod: {item['dateProduction']}, "
            f"Exp: {item['dateExpiration']}"
        )
        pdf.cell(200, 10, ligne, ln=True)
    
    pdf.output(filename)

def get_colis_termines(conn):
    query = """
    SELECT c.idColis, c.reference, c.dateCreation,
           be.reference AS bon_expedition, be.dateExpeditionPrevue,
           COALESCE(SUM(ct.quantite), 0) AS quantite_totale,
           c.statut
    FROM COLIS c
    JOIN EXPEDIER_COLIS ec ON c.idColis = ec.idColis
    JOIN BON_EXPEDITION be ON ec.idBon = be.idBon
    LEFT JOIN CONTENIR ct ON c.idColis = ct.idColis
    WHERE c.statut = 'termine' AND be.statut = 'termine'
    GROUP BY c.idColis, be.reference, be.dateExpeditionPrevue, c.statut
    ORDER BY be.dateExpeditionPrevue DESC;
    """
    return [
        {
            "idColis": r[0],
            "reference": r[1],
            "date_creation": r[2],
            "bon_expedition": r[3],
            "date_expedition_prevue": r[4],
            "quantite_totale": r[5],
            "statut": r[6]
        } for r in execute_query(conn, fetch=True, query=query)
    ]
