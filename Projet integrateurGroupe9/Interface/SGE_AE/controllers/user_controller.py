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
    try:
        users = list_users(conn)
        if not users:
            logger.warning("Aucun utilisateur trouvé dans la base")
            return []
        return users
    except Exception as e:
        logger.error(f"Erreur get_all_users: {str(e)}")
        raise

def get_all_roles(conn):
    try:
        raw_roles = list_roles(conn)
        if not raw_roles:
            logger.warning("Aucun rôle trouvé dans la base")
            return []
        return [{
            'id': role[0],
            'libelle': role[1],
            'typeRole': role[2]
        } for role in raw_roles]
    except Exception as e:
        logger.error(f"Erreur get_all_roles: {str(e)}", exc_info=True)
        return []

def get_all_organisations(conn):
    try:
        orgs = list_organisations(conn)
        if not orgs:
            logger.warning("Aucune organisation trouvée dans la base")
            return []
        return orgs
    except Exception as e:
        logger.error(f"Erreur get_all_organisations: {str(e)}")
        raise

def activate_user_role(conn, user_id, role_id, organisation_id):
    """Active un rôle pour un utilisateur dans une organisation"""
    try:
        return assign_role(conn, user_id, role_id, organisation_id)
    except Exception as e:
        logger.error(f"Erreur dans activate_user_role: {e}")
        return False

def deactivate_user_role(conn, user_id, role_id, organisation_id):
    """Désactive un rôle pour un utilisateur dans une organisation"""
    try:
        return revoke_role(conn, user_id, role_id, organisation_id)
    except Exception as e:
        logger.error(f"Erreur dans deactivate_user_role: {e}")
        return False

def get_roles_for_user(conn, user_id):
    try:
        results = get_user_roles(conn, user_id)
        return [{
            'libelle': role[0] if isinstance(role, (tuple, list)) else str(role)
        } for role in results]
    except Exception as e:
        logger.error(f"Erreur get_roles_for_user: {str(e)}", exc_info=True)
        return []
