import psycopg2
from psycopg2 import OperationalError
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def create_connection():
    """Établir une connexion à la base de données PostgreSQL"""
    conn = None
    try:
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Connexion à la base de données réussie")
        return conn
    except OperationalError as e:
        print(f"Erreur de connexion: {e}")
        return None

def execute_query(conn, query, params=None, fetch=False):
    """Exécuter une requête SQL avec gestion des erreurs"""
    result = None
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'exécution de la requête: {e}")
        raise
    return result