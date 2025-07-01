from database import execute_query

def ajouter_cellule(conn, reference, longueur, largeur, hauteur,
                    masse_max, volume_max, capacite_max, position, id_entrepot):
    """
    Ajoute une nouvelle cellule dans l'entrepôt via la fonction SQL ajouter_cellule.

    Args:
        conn: Connexion PostgreSQL active
        reference (str): Référence unique de la cellule
        longueur (float): Longueur en cm
        largeur (float): Largeur en cm
        hauteur (float): Hauteur en cm
        masse_max (float): Masse maximale supportée (kg)
        volume_max (float): Volume maximal (cm³)
        capacite_max (int): Capacité maximale (nb d’unités)
        position (str): Position textuelle
        id_entrepot (int): ID de l’entrepôt

    Returns:
        int: ID de la cellule nouvellement créée
    """
    query = """
        SELECT ajouter_cellule(
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
    """
    params = (
        reference,
        longueur,
        largeur,
        hauteur,
        masse_max,
        volume_max,
        capacite_max,
        position,
        id_entrepot
    )
    result = execute_query(conn, query, params, fetch=True)
    return result[0][0] if result else None


def update_cellule(conn, id_cellule, longueur, largeur, hauteur,
                   masse_max, volume_max, capacite_max, statut):
    """
    Met à jour une cellule existante via la fonction SQL update_cellule.

    Args:
        conn: Connexion PostgreSQL active
        id_cellule (int): ID de la cellule à modifier
        longueur (float): Nouvelle longueur
        largeur (float): Nouvelle largeur
        hauteur (float): Nouvelle hauteur
        masse_max (float): Nouvelle masse maximale
        volume_max (float): Nouveau volume maximal
        capacite_max (int): Nouvelle capacité maximale
        statut (str): Statut de la cellule (actif, inactif, maintenance)

    Returns:
        bool: True si succès
    """
    query = """
        SELECT update_cellule(
            %s, %s, %s, %s, %s, %s, %s, %s
        );
    """
    params = (
        id_cellule,
        longueur,
        largeur,
        hauteur,
        masse_max,
        volume_max,
        capacite_max,
        statut
    )
    execute_query(conn, query, params)
    return True
