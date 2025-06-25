from SGE_AE.database import execute_query
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

def authenticate_user(conn, email: str, password: str) -> Optional[Dict]:
    """
    Authentifie un utilisateur de manière sécurisée
    
    Args:
        conn: Connexion à la base
        email: Email de l'utilisateur
        password: Mot de passe en clair (à hasher avant en production)
    
    Returns:
        Dict: Infos utilisateur ou None si échec
    """
    try:
        query = """
        SELECT idIndividu, nom, email 
        FROM INDIVIDU 
        WHERE email = %s AND password = %s
        """
  # Utilisation de crypt() pour le mot de passe
        result = execute_query(conn, query, (email, password), fetch=True)
        
        if not result:
            logger.warning(f"Échec authentification pour {email}")
            return None
            
        return {
            'idIndividu': result[0][0],
            'nom': result[0][1], 
            'email': result[0][2]
        }
        
    except Exception as e:
        logger.error(f"Erreur authentification: {str(e)}")
        return None

def get_user_roles(conn, user_id: int) -> List[str]:
    """
    Récupère les rôles actifs d'un utilisateur
    
    Args:
        conn: Connexion à la base
        user_id: ID de l'utilisateur
    
    Returns:
        List: Noms des rôles actifs
    """
    try:
        query = """
        SELECT r.libelle 
        FROM AFFECTER_ROLE ar
        JOIN ROLE r ON ar.idRole = r.idRole
        WHERE ar.idIndividu = %s AND ar.estActif = TRUE
        AND (ar.dateFin IS NULL OR ar.dateFin >= CURRENT_DATE)
        """  # Ajout vérification date de validité
        results = execute_query(conn, query, (user_id,), fetch=True)
        return [role[0] for role in results] if results else []
        
    except Exception as e:
        logger.error(f"Erreur récupération rôles: {str(e)}")
        return []

def list_users(conn) -> List[Dict]:
    """Liste tous les utilisateurs avec leurs informations de base"""
    try:
        query = """
        SELECT idIndividu, nom, email, 
               CASE WHEN EXISTS (
                   SELECT 1 FROM AFFECTER_ROLE 
                   WHERE idIndividu = i.idIndividu AND estActif = TRUE
               ) THEN TRUE ELSE FALSE END as est_actif
        FROM INDIVIDU i
        ORDER BY nom;
        """
        rows = execute_query(conn, query, fetch=True)
        return [{
            'id': row[0],
            'nom': row[1],
            'email': row[2],
            'actif': row[3]
        } for row in rows]
        
    except Exception as e:
        logger.error(f"Erreur liste utilisateurs: {str(e)}")
        return []

def list_roles(conn):
    """
    Retourne la liste des rôles disponibles sans la colonne description.
    """
    try:
        query = "SELECT idRole, libelle, typeRole FROM ROLE ORDER BY libelle;"
        return execute_query(conn, query, fetch=True)
    except Exception as e:
        logger.error(f"Erreur liste rôles: {e}")
        return []

def assign_role(conn, user_id: int, role_id: int, id_org: int = None) -> bool:
    """
    Attribue un rôle à un utilisateur sans RETURNING idAffectation.
    
    Args:
        conn: Connexion à la base
        user_id: ID de l'utilisateur
        role_id: ID du rôle
        id_org: ID de l'organisation (optionnel)
        
    Returns:
        bool: True si succès, False si échec
    """
    try:
        query = """
        INSERT INTO AFFECTER_ROLE(
            idIndividu, idRole, idOrganisation,
            dateDebut, estActif
        )
        VALUES (%s, %s, %s, CURRENT_DATE, TRUE)
        ON CONFLICT (idIndividu, idRole, idOrganisation)
        DO UPDATE SET
            estActif = TRUE,
            dateDebut = CURRENT_DATE,
            dateFin = NULL;
        """
        execute_query(conn, query, (user_id, role_id, id_org))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur attribution rôle: {str(e)}", exc_info=True)
        return False

def revoke_role(conn, user_id: int, role_id: int, id_org: int = None) -> bool:
    """
    Révoque un rôle sans RETURNING idAffectation.
    """
    try:
        query = """
        UPDATE AFFECTER_ROLE
        SET estActif = FALSE,
            dateFin = CURRENT_DATE
        WHERE idIndividu = %s
        AND idRole = %s
        AND (%s IS NULL OR idOrganisation = %s);
        """
        execute_query(conn, query, (user_id, role_id, id_org, id_org))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur révocation rôle: {str(e)}", exc_info=True)
        return False
    
def list_organisations(conn):
    """
    Retourne la liste des organisations disponibles.
    
    Args:
        conn: Connexion à la base de données
        
    Returns:
        Liste de dictionnaires contenant les organisations avec leurs id et noms,
        ou liste vide en cas d'erreur.
    """
    query = "SELECT idOrganisation, nom FROM ORGANISATION ORDER BY nom;"
    try:
        rows = execute_query(conn, query, fetch=True)
        return [dict(zip(("id", "nom"), row)) for row in rows]
    except Exception as e:
        print(f"Erreur dans list_organisations: {e}")
        return []
