import os
import datetime
import logging
from models.expedition_model import (
    create_expedition_bon,
    get_pending_expeditions,
    preparer_expedition,
    get_colis_by_bon,
    get_lots_in_colis,
    get_expedition_exceptions,
    valider_expedition,
    confirmer_livraison,
    annuler_colis,
    get_colis_pret_expedition,
    get_colis_en_cours,
    generer_bordereau_pdf,
)

logger = logging.getLogger(__name__)

def handle_create_expedition(conn, ref, date, priorite, user_id):
    return create_expedition_bon(conn, ref, date, priorite, user_id)

def handle_pending_expeditions(conn):
    return get_pending_expeditions(conn)

def handle_preparation_expedition(conn, id_bon, id_produit, quantite):
    return preparer_expedition(conn, id_bon, id_produit, quantite)

def handle_colis_by_bon(conn, bon_id):
    return get_colis_by_bon(conn, bon_id)

def handle_colis_lots(conn, colis_id):
    return get_lots_in_colis(conn, colis_id)

def handle_exceptions(conn, bon_id):
    return get_expedition_exceptions(conn, bon_id)

def handle_valider_expedition(conn, bon_id):
    return valider_expedition(conn, bon_id)

def handle_confirmer_livraison(conn, bon_id):
    return confirmer_livraison(conn, bon_id)

def handle_colis_en_cours(conn):
    return get_colis_en_cours(conn)

def handle_annulation_colis(conn, id_colis):
    return annuler_colis(conn, id_colis)

def handle_colis_prets(conn):
    return get_colis_pret_expedition(conn)

# Doublons utiles pour compatibilité avec d’autres modules
handle_get_colis_by_bon = handle_colis_by_bon
handle_get_contenu_colis = handle_colis_lots
handle_get_exceptions = handle_exceptions

def handle_generer_bordereau_pdf(conn, bon_id):
    """
    Génère un bordereau PDF à partir des colis liés à un bon d’expédition.

    Args:
        conn: Connexion base de données PostgreSQL
        bon_id (int): ID du bon d’expédition

    Returns:
        str: Chemin absolu vers le fichier PDF généré

    Raises:
        Exception: Si aucun colis ou lot n’est trouvé ou erreur de génération
    """
    try:
        colis_list = get_colis_by_bon(conn, bon_id)
        if not colis_list:
            raise Exception(f"Aucun colis trouvé pour le bon {bon_id}")

        contenu = []
        for colis in colis_list:
            lots = get_lots_in_colis(conn, colis['idColis'])
            contenu.extend(lots)

        if not contenu:
            raise Exception("Aucun lot trouvé dans les colis de ce bon")

        # Nom de fichier unique basé sur horodatage
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bordereau_expedition_{bon_id}_{now}.pdf"

        # Répertoire bordereaux/
        output_dir = os.path.join(os.getcwd(), "bordereaux")
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)

        generer_bordereau_pdf(contenu, filepath)
        return filepath

    except Exception as e:
        logger.error(f"Erreur lors de la génération du bordereau : {e}", exc_info=True)
        raise Exception(f"Erreur lors de la génération du bordereau : {str(e)}")
