import logging
import psycopg2
from models.stock_model import deplacer_lot, get_lot_info, get_cellule_details

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_deplacement(conn, id_lot, cellule_source, cellule_dest, quantite, id_responsable):
    """
    Gère le déplacement d'un lot entre cellules après des contrôles métier préalables
    (vérification de l'emplacement du lot, volume, compatibilité, cellule active).

    Args:
        conn: Objet de connexion à la base de données.
        id_lot (int): ID du lot à déplacer.
        cellule_source (int): ID de la cellule d'où le lot est déplacé.
        cellule_dest (int): ID de la cellule vers laquelle le lot est déplacé.
        quantite (int): Quantité à déplacer.
        id_responsable (int): ID de l'individu responsable de l'opération.

    Returns:
        bool: True si succès, False si échec après validation ou opération SQL.
              Lève une exception en cas d'erreur critique non gérée.
    """
    try:
        # Validation initiale des paramètres
        if not all(isinstance(val, int) and val > 0 for val in [id_lot, cellule_source, cellule_dest, quantite, id_responsable]):
            raise ValueError("Tous les paramètres (ID lot, cellules, quantité, responsable) doivent être des entiers strictement positifs.")
        
        if quantite <= 0: # S'assurer que la quantité à déplacer est positive
            raise ValueError("La quantité à déplacer doit être supérieure à zéro.")

        # 1. Récupération des informations du lot
        # get_lot_info est censée retourner un dictionnaire avec 'idCellule' (emplacement actuel)
        # et 'quantite_actuelle_en_cellule' (quantité de ce lot dans cette cellule spécifique)
        # ainsi que 'type' et 'volume_unitaire'.
        lot = get_lot_info(conn, id_lot)
        if not lot:
            raise ValueError(f"Le lot {id_lot} est introuvable. Veuillez vérifier l'ID du lot.")

        # Validation de l'emplacement actuel du lot (résout le problème de 'cellule None')
        current_lot_cell_id = lot.get('idCellule')
        if current_lot_cell_id is None:
            raise ValueError(f"Le lot {id_lot} n'est actuellement stocké dans aucune cellule connue. Impossible de le déplacer.")
        
        # Vérifier si le lot se trouve bien dans la cellule source déclarée
        if current_lot_cell_id != cellule_source:
            raise ValueError(f"Le lot {id_lot} n'est pas situé dans la cellule source déclarée ({cellule_source}). Son emplacement actuel est la cellule {current_lot_cell_id}.")

        # Valider la quantité à déplacer par rapport à la quantité disponible dans la *cellule source*
        # Prioriser 'quantite_actuelle_en_cellule' pour la validation de la source.
        quantite_disponible_dans_source = lot.get('quantite_actuelle_en_cellule', 0)
        if quantite > quantite_disponible_dans_source:
            raise ValueError(f"La quantité à déplacer ({quantite}) est supérieure à la quantité disponible du lot {id_lot} dans la cellule source {cellule_source} ({quantite_disponible_dans_source}).")
        
        # Récupérer le volume unitaire (si applicable)
        volume_unitaire = lot.get('volume_unitaire')
        if lot["type"] == "materiel" and (volume_unitaire is None or volume_unitaire <= 0):
            raise ValueError("Volume unitaire non défini ou invalide pour ce produit matériel.")

        # Calculer le volume total pour le déplacement
        volume_total_deplacement = volume_unitaire * quantite if lot["type"] == "materiel" else 0

        # 2. Récupération des informations de la cellule de destination
        # get_cellule_details est censée retourner 'statut', 'capacite_max',
        # 'quantite_actuelle' (quantité totale de tous les articles dans la cellule), et 'volume_restant'.
        dest = get_cellule_details(conn, cellule_dest)
        if not dest:
            raise ValueError(f"Cellule destination {cellule_dest} introuvable. Veuillez vérifier l'ID de la cellule.")

        if dest.get('statut') != 'actif':
            raise ValueError(f"La cellule destination {cellule_dest} est inactive et ne peut pas recevoir de lots.")

        # Validation de la capacité de la cellule de destination (quantité)
        capacite_max_dest = dest.get("capacite_max", 0)
        quantite_occupee_dest = dest.get("quantite_actuelle", 0) # Ceci devrait être la somme de toutes les quantités de lots actuellement dans la cellule
        
        if capacite_max_dest is None or capacite_max_dest < 0:
            raise ValueError(f"La capacité maximale de la cellule de destination (ID: {cellule_dest}) est invalide ou non définie.")

        # Vérifier si l'ajout de la nouvelle quantité dépasserait la capacité de la cellule
        quantite_apres_deplacement = quantite_occupee_dest + quantite
        if quantite_apres_deplacement > capacite_max_dest:
            raise ValueError(f"La quantité totale dans la cellule destination {cellule_dest} ({quantite_apres_deplacement}) dépasserait sa capacité maximale ({capacite_max_dest}).")

        # Validation du volume de la cellule de destination (si le produit est 'materiel')
        if lot["type"] == "materiel":
            volume_restant_dest = dest.get("volume_restant", 0.0)
            if volume_restant_dest is None or volume_restant_dest < 0:
                raise ValueError(f"Le volume restant de la cellule de destination (ID: {cellule_dest}) est invalide ou non défini.")
                
            if volume_total_deplacement > volume_restant_dest:
                raise ValueError(f"Pas assez de place en volume dans la cellule destination {cellule_dest} (volume restant : {volume_restant_dest:.2f} cm³; besoin de {volume_total_deplacement:.2f} cm³).")

        # 3. Exécuter la fonction de déplacement SQL via la fonction Python importée
        # La fonction 'deplacer_lot' de models.stock_model est censée appeler directement
        # la fonction SQL et gérer sa propre transaction (commit/rollback)
        # ou que la transaction de niveau supérieur gérant 'conn' le fera.
        success = deplacer_lot(conn, id_lot, cellule_source, cellule_dest, quantite, id_responsable)

        if success:
            logger.info(f"Lot {id_lot} déplacé avec succès de la cellule {cellule_source} à la cellule {cellule_dest} ({quantite} unités).")
        else:
            # Cette branche est atteinte si la fonction Python 'deplacer_lot' retourne False
            # (par exemple, si la fonction SQL sous-jacente retourne FALSE).
            logger.warning(f"Le déplacement du lot {id_lot} a échoué en base de données (fonction deplacer_lot a retourné FALSE).")
            # Pas de rollback ici car 'deplacer_lot' (Python) devrait gérer sa propre transaction.
            return False

        return success

    except ValueError as ve:
        # Erreurs de validation métier
        logger.warning(f"Erreur de validation métier lors du déplacement: {str(ve)}")
        # Pas de rollback ici car c'est une erreur de validation avant l'opération DB.
        raise # Relancer l'exception pour que l'interface utilisateur la capture et l'affiche

    except psycopg2.Error as e:
        # Erreurs spécifiques à PostgreSQL
        conn.rollback() # S'assurer que la transaction est annulée en cas d'erreur DB
        logger.error(f"Erreur SQL lors du déplacement : {e.pgerror if hasattr(e, 'pgerror') else str(e)}", exc_info=True)
        raise Exception(f"Erreur SQL : {e.pgerror if hasattr(e, 'pgerror') else str(e)}")

    except Exception as e:
        # Erreurs générales inattendues
        conn.rollback() # S'assurer que la transaction est annulée
        logger.critical(f"Erreur critique inattendue dans handle_deplacement : {str(e)}", exc_info=True)
        raise # Relancer l'exception pour une gestion de niveau supérieur (par exemple, affichage d'un message d'erreur générique dans l'interface utilisateur)