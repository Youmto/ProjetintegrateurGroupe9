import logging
import psycopg2
from models.stock_model import deplacer_lot, get_lot_info, get_cellule_details

logger = logging.getLogger(__name__)

def handle_deplacement(conn, id_lot, cellule_source, cellule_dest, quantite, id_responsable):
    """
    Gère le déplacement d'un lot entre cellules via la fonction SQL deplacer_lot
    après contrôles métier préalables (volume, compatibilité, cellule active).

    Returns:
        bool: True si succès, sinon Exception levée
    """
    try:
        if not all(isinstance(val, int) and val > 0 for val in [id_lot, cellule_source, cellule_dest, quantite, id_responsable]):
            raise ValueError("Tous les paramètres doivent être des entiers strictement positifs.")

        # 1. Infos du lot
        lot = get_lot_info(conn, id_lot)
        if not lot:
            raise ValueError(f"Le lot {id_lot} est introuvable.")

        if quantite > lot['quantite_disponible']:
            raise ValueError(f"Quantité demandée ({quantite}) > disponible ({lot['quantite_disponible']}).")

        volume_unitaire = lot.get('volume_unitaire')
        if lot["type"] == "materiel" and volume_unitaire is None:
            raise ValueError("Volume non défini pour ce produit matériel.")

        volume_total = volume_unitaire * quantite if volume_unitaire else 0

        # 2. Infos cellule destination
        dest = get_cellule_details(conn, cellule_dest)
        if not dest:
            raise ValueError(f"Cellule destination {cellule_dest} introuvable.")

        if dest['statut'] != 'actif':
            raise ValueError("Cellule destination inactive.")

        if volume_unitaire and volume_total > dest['volume_restant']:
            raise ValueError(f"Pas assez de place dans la cellule (volume restant : {dest['volume_restant']}).")

        # 3. Déplacement SQL
        success = deplacer_lot(conn, id_lot, cellule_source, cellule_dest, quantite, id_responsable)

        if success:
            logger.info(f"Lot {id_lot} déplacé avec succès vers cellule {cellule_dest} ({quantite} unités).")
        else:
            logger.warning(f"Le déplacement du lot {id_lot} a échoué.")

        return success

    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Erreur SQL lors du déplacement : {e.pgerror}", exc_info=True)
        raise Exception(f"Erreur SQL : {e.pgerror}")

    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur dans handle_deplacement : {str(e)}", exc_info=True)
        raise