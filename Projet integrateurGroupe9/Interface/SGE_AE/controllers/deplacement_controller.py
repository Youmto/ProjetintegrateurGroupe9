from models.stock_model import deplacer_lot
import psycopg2

def handle_deplacement(conn, id_lot, cellule_source, cellule_dest, quantite, id_responsable):
    """
    Gère le déplacement d'un lot entre cellules en base de données
    
    Args:
        conn: Connexion PostgreSQL
        id_lot: ID du lot à déplacer
        cellule_source: Cellule d'origine
        cellule_dest: Cellule de destination
        quantite: Quantité à déplacer
        id_responsable: ID du responsable
        
    Returns:
        bool: True si succès, False sinon
        
    Raises:
        Exception: En cas d'erreur SQL ou autre
    """
    try:
        with conn.cursor() as cur:
            # Exécution de la procédure stockée
            cur.callproc(
                "deplacer_lot", 
                (id_lot, cellule_source, cellule_dest, quantite, id_responsable)
            )
            conn.commit()  # Validation explicite
            return True
            
    except psycopg2.Error as e:
        conn.rollback()  # Annulation impérative en cas d'erreur
        raise Exception(f"Erreur SQL lors du déplacement : {e.pgerror}")
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur inattendue : {str(e)}")