import logging
from SGE_AE.database import execute_query
from datetime import date
from psycopg2.extras import RealDictCursor



logger = logging.getLogger(__name__)

# =============================================================================
# 1. Déplacement de lot entre cellules
# =============================================================================
def deplacer_lot(conn, id_lot, cellule_src, cellule_dst, quantite, id_resp):
    """
    Déplace une quantité d’un lot d’une cellule vers une autre.

    Args:
        conn: Connexion DB
        id_lot: ID du lot concerné
        cellule_src: ID de la cellule source
        cellule_dst: ID de la cellule de destination
        quantite: Quantité à déplacer
        id_resp: ID du responsable

    Returns:
        bool: True si succès, False sinon
    """
    try:
        query = "SELECT deplacer_lot(%s, %s, %s, %s, %s);"
        result = execute_query(conn, query, (id_lot, cellule_src, cellule_dst, quantite, id_resp), fetch=True)
        return result[0][0] if result else False
    except Exception as e:
        logger.error(f"Erreur déplacement lot : {e}", exc_info=True)
        return False

# =============================================================================
# 2. Ajustement de l’inventaire
# =============================================================================
def ajuster_inventaire(conn, id_lot, id_cellule, nouvelle_qte, id_resp, commentaire):
    """
    Ajuste l’inventaire manuellement suite à un inventaire physique.

    Args:
        conn: Connexion DB
        id_lot: ID du lot concerné
        id_cellule: ID de la cellule concernée
        nouvelle_qte: Nouvelle quantité constatée
        id_resp: ID du responsable
        commentaire: Description ou justification

    Returns:
        bool: True si succès, False sinon
    """
    try:
        query = "SELECT ajuster_inventaire(%s, %s, %s, %s, %s);"
        result = execute_query(conn, query, (id_lot, id_cellule, nouvelle_qte, id_resp, commentaire), fetch=True)
        return result[0][0] if result else False
    except Exception as e:
        logger.error(f"Erreur ajustement inventaire : {e}", exc_info=True)
        return False

# =============================================================================
# 3. Historique des mouvements d’un produit
# =============================================================================
def mouvements_produit(conn, id_produit, date_debut=None, date_fin=None, type_mouvement=None):
    """
    Récupère les mouvements d'un produit en appelant la fonction SQL mouvements_produit(dom_id)
    et filtre en Python (car la fonction SQL n'accepte qu'un paramètre).
    """
    try:
        query = "SELECT * FROM mouvements_produit(%s);"
        rows = execute_query(conn, query, (id_produit,), fetch=True)


        mouvements = [
            dict(zip(
                ['type', 'reference_bon', 'date', 'quantite', 'lot', 'cellule', 'description'], r
            )) for r in rows
        ]

        # ✅ conversion sécurisée des dates
        def safe_parse(d):
            if isinstance(d, str):
                try:
                    return date.fromisoformat(d)
                except ValueError:
                    logger.warning(f"[mouvements_produit] Mauvaise date ignorée : {d}")
                    return None
            return d

        date_debut = safe_parse(date_debut)
        date_fin = safe_parse(date_fin)

        if date_debut:
            mouvements = [m for m in mouvements if m['date'] >= date_debut]
        if date_fin:
            mouvements = [m for m in mouvements if m['date'] <= date_fin]
        if type_mouvement:
            mouvements = [m for m in mouvements if m['type'] == type_mouvement]

        return mouvements

    except Exception as e:
        logger.error(f"[mouvements_produit] Erreur : {e}", exc_info=True)
        return []

def get_product_movement_totals(conn, product_id):
    """
    Récupère les totaux agrégés (réceptions, expéditions, déplacements, mouvements aujourd'hui)
    pour un produit donné. Ces totaux sont globaux pour le produit (sauf "aujourd'hui").
    """
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            totals_query = """
            SELECT
                SUM(CASE WHEN type = 'Entrée' THEN quantite ELSE 0 END) AS "TotalReceptions",
                SUM(CASE WHEN type = 'Sortie' THEN ABS(quantite) ELSE 0 END) AS "TotalExpeditions",
                SUM(CASE WHEN type = 'Déplacement' THEN quantite ELSE 0 END) AS "TotalDeplacements",
                SUM(CASE WHEN date = CURRENT_DATE::dom_date THEN 1 ELSE 0 END) AS "TotalMouvementsAujourdHui"
            FROM
                mouvements_produit(%s);
            """
            cur.execute(totals_query, (product_id,))
            totals = cur.fetchone() # Il n'y aura qu'une seule ligne de totaux
            logger.info(f"Totaux de mouvements récupérés pour le produit {product_id}: {totals}")
            return totals if totals else {} # Retourne un dictionnaire ou un dictionnaire vide si aucun résultat
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des totaux pour le produit {product_id}: {e}", exc_info=True)
        raise