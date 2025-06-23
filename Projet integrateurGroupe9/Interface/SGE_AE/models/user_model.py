from SGE_AE.database import execute_query

def authenticate_user(conn, email, password):
    """Authentifie un utilisateur avec son email et mot de passe"""
    query = """
    SELECT idIndividu, nom, email 
    FROM INDIVIDU 
    WHERE email = %s AND password = %s  
    """
    result = execute_query(conn, query, (email, password), fetch=True)
    if result:
        return{
            'idIndividu': result[0][0],
            'nom': result[0][1],
            'email': result[0][2]
        }
        return None


def get_user_roles(conn, user_id):
    """Récupère les rôles d'un utilisateur"""
    query = """
    SELECT r.libelle 
    FROM AFFECTER_ROLE ar
    JOIN ROLE r ON ar.idRole = r.idRole
    WHERE ar.idIndividu = %s AND ar.estActif = TRUE
    """
    results = execute_query(conn, query, (user_id,), fetch=True)
    return [role[0] for role in results] if results else []
def list_users(conn):
    query = "SELECT idIndividu, nom, email FROM INDIVIDU ORDER BY nom;"
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('id', 'nom', 'email'), row)) for row in rows]

def list_roles(conn):
    query = "SELECT idRole, libelle FROM ROLE ORDER BY libelle;"
    rows = execute_query(conn, query, fetch=True)
    return [dict(zip(('id', 'libelle'), row)) for row in rows]

def assign_role(conn, user_id, role_id):
    query = """
    INSERT INTO AFFECTER_ROLE(idIndividu, idRole, estActif)
    VALUES (%s, %s, TRUE)
    ON CONFLICT (idIndividu, idRole) DO UPDATE SET estActif = TRUE;
    """
    execute_query(conn, query, (user_id, role_id))

def revoke_role(conn, user_id, role_id):
    query = """
    UPDATE AFFECTER_ROLE
    SET estActif = FALSE
    WHERE idIndividu = %s AND idRole = %s;
    """
    execute_query(conn, query, (user_id, role_id))