import logging
from typing import Optional, Dict, List
from SGE_AE.database import execute_query

logger = logging.getLogger(__name__)

# Authentifier un utilisateur en comparant avec mot de passe crypté (pgcrypto)
def authenticate_user(conn, email: str, password: str) -> Optional[Dict]:
    try:
        query = """
        SELECT idIndividu, nom, email
        FROM INDIVIDU
        WHERE email = %s AND password = crypt(%s, password)
        """
        result = execute_query(conn, query, (email, password), fetch=True)
        if not result:
            logger.warning("Échec d'authentification pour %s", email)
            return None

        return {
            "idIndividu": result[0][0],
            "nom": result[0][1],
            "email": result[0][2]
        }

    except Exception as e:
        logger.exception(f"Erreur lors de l'authentification de {email}: {e}")
        return None

# Récupérer les rôles actifs d’un utilisateur
def get_user_roles(conn, user_id: int) -> List[str]:
    try:
        query = """
        SELECT r.libelle
        FROM AFFECTER_ROLE ar
        JOIN ROLE r ON r.idRole = ar.idRole
        WHERE ar.idIndividu = %s AND ar.estActif = TRUE
        AND (ar.dateFin IS NULL OR ar.dateFin >= CURRENT_DATE)
        """
        results = execute_query(conn, query, (user_id,), fetch=True)
        return [r[0] for r in results] if results else []

    except Exception as e:
        logger.exception(f"Erreur récupération des rôles pour utilisateur {user_id}: {e}")
        return []

# Liste des utilisateurs avec leur statut d'activité
def list_users(conn) -> List[Dict]:
    try:
        query = """
        SELECT i.idIndividu, i.nom, i.email,
            EXISTS (
                SELECT 1 FROM AFFECTER_ROLE ar 
                WHERE ar.idIndividu = i.idIndividu AND ar.estActif = TRUE
            ) AS est_actif
        FROM INDIVIDU i
        ORDER BY i.nom
        """
        rows = execute_query(conn, query, fetch=True)
        return [
            {
                "id": r[0],
                "nom": r[1],
                "email": r[2],
                "actif": r[3]
            }
            for r in rows
        ]
    except Exception as e:
        logger.exception("Erreur chargement liste utilisateurs: %s", e)
        return []

# Liste des rôles disponibles
def list_roles(conn) -> List[Dict]:
    try:
        query = "SELECT idRole, libelle, typeRole FROM ROLE ORDER BY libelle;"
        rows = execute_query(conn, query, fetch=True)
        return [dict(zip(["idRole", "libelle", "typeRole"], r)) for r in rows]
    except Exception as e:
        logger.exception("Erreur chargement des rôles: %s", e)
        return []

# Liste des organisations
def list_organisations(conn) -> List[Dict]:
    try:
        query = "SELECT idOrganisation, nom FROM ORGANISATION ORDER BY nom;"
        rows = execute_query(conn, query, fetch=True)
        return [dict(zip(["id", "nom"], r)) for r in rows]
    except Exception as e:
        logger.exception("Erreur chargement organisations: %s", e)
        return []

# Attribuer un rôle à un utilisateur
def assign_role(conn, user_id: int, role_id: int, id_org: Optional[int] = None) -> bool:
    try:
        query = """
        INSERT INTO AFFECTER_ROLE(idIndividu, idRole, idOrganisation, dateDebut, estActif)
        VALUES (%s, %s, %s, CURRENT_DATE, TRUE)
        ON CONFLICT (idIndividu, idRole, idOrganisation)
        DO UPDATE SET estActif = TRUE, dateDebut = CURRENT_DATE, dateFin = NULL
        """
        execute_query(conn, query, (user_id, role_id, id_org))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.exception(f"Erreur assignation rôle {role_id} à utilisateur {user_id}: {e}")
        return False

# Révoquer un rôle actif
def revoke_role(conn, user_id: int, role_id: int, id_org: Optional[int] = None) -> bool:
    try:
        query = """
        UPDATE AFFECTER_ROLE
        SET estActif = FALSE,
            dateFin = CURRENT_DATE
        WHERE idIndividu = %s
          AND idRole = %s
          AND (%s IS NULL OR idOrganisation = %s)
        """
        execute_query(conn, query, (user_id, role_id, id_org, id_org))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.exception(f"Erreur révocation rôle {role_id} pour utilisateur {user_id}: {e}")
        return False
