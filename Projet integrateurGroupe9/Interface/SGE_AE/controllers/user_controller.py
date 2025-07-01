from models.user_model import (
    list_users,
    list_roles,
    list_organisations,
    assign_role,
    revoke_role,
    get_user_roles
)
import logging

logger = logging.getLogger(__name__)

def get_all_users(conn):
    """
    Récupère la liste des utilisateurs avec état d’activité.

    Args:
        conn: Connexion PostgreSQL active

    Returns:
        List[Dict]: Liste des utilisateurs
    """
    try:
        users = list_users(conn)
        if not users:
            logger.warning("Aucun utilisateur trouvé dans la base")
        return users or []
    except Exception as e:
        logger.error(f"Erreur dans get_all_users: {e}", exc_info=True)
        raise


def get_all_roles(conn):
    """
    Récupère la liste complète des rôles disponibles.

        Args:
        conn: Connexion PostgreSQL active

    Returns:
        List[Dict]: Liste des rôles avec libellé et type
    """
    try:
        raw_roles = list_roles(conn)
        if not raw_roles:
            logger.warning("Aucun rôle trouvé dans la base")
            return []

        roles = []
        for role in raw_roles:
            if isinstance(role, dict):
                roles.append({
                    'id': role.get('idRole'),
                    'libelle': role.get('libelle'),
                    'typeRole': role.get('typeRole')
                })
            elif isinstance(role, (list, tuple)):
                roles.append({
                    'id': role[0],
                    'libelle': role[1],
                    'typeRole': role[2]
                })
        return roles

    except Exception as e:
        logger.error(f"Erreur dans get_all_roles: {e}", exc_info=True)
        return []




def get_all_organisations(conn):
    """
    Récupère la liste des organisations connues.

    Args:
        conn: Connexion PostgreSQL active

    Returns:
        List[Dict]: Liste des organisations (id + nom)
    """
    try:
        orgs = list_organisations(conn)
        if not orgs:
            logger.warning("Aucune organisation trouvée dans la base")
        return orgs or []
    except Exception as e:
        logger.error(f"Erreur dans get_all_organisations: {e}", exc_info=True)
        raise


def activate_user_role(conn, user_id, role_id, organisation_id):
    """
    Attribue (ou réactive) un rôle pour un utilisateur.

    Args:
        conn: Connexion PostgreSQL active
        user_id: ID de l’utilisateur
        role_id: ID du rôle
        organisation_id: ID de l’organisation

    Returns:
        bool: True si succès
    """
    try:
        return assign_role(conn, user_id, role_id, organisation_id)
    except Exception as e:
        logger.error(f"Erreur dans activate_user_role: {e}", exc_info=True)
        return False


def deactivate_user_role(conn, user_id, role_id, organisation_id):
    """
    Désactive un rôle attribué à un utilisateur.

    Args:
        conn: Connexion PostgreSQL active
        user_id: ID de l’utilisateur
        role_id: ID du rôle
        organisation_id: ID de l’organisation

    Returns:
        bool: True si succès
    """
    try:
        return revoke_role(conn, user_id, role_id, organisation_id)
    except Exception as e:
        logger.error(f"Erreur dans deactivate_user_role: {e}", exc_info=True)
        return False


def get_roles_for_user(conn, user_id):
    """
    Récupère les rôles actifs d’un utilisateur donné.

    Args:
        conn: Connexion PostgreSQL active
        user_id: ID de l’utilisateur

    Returns:
        List[Dict]: Liste des rôles avec libellé
    """
    try:
        results = get_user_roles(conn, user_id)
        return [{'libelle': role if isinstance(role, str) else role[0]} for role in results]
    except Exception as e:
        logger.error(f"Erreur dans get_roles_for_user: {e}", exc_info=True)
        return []
