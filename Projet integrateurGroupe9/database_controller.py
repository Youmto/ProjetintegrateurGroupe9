from database import create_connection, execute_query, get_table_names


def __init__(self):
        self.connection = None
        
def connect(self):
        """Établir la connexion à la base de données"""
        self.connection = create_connection()
        return self.connection is not None
        
def disconnect(self):
        """Fermer la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            self.connection = None
            
def execute_sql(self, sql_query, params=None):
        """Exécuter une requête SQL et retourner les résultats"""
        if not self.connection:
            raise Exception("Pas de connexion à la base de données")
           
        try:
            fetch = sql_query.strip().lower().startswith('select')
            result = execute_query(self.connection, sql_query, params, fetch=fetch)
            return result
        except Exception as e:
            raise Exception(f"Erreur SQL: {str(e)}")
            
def get_tables(self):
        """Obtenir la liste des tables de la base de données"""
        if not self.connection:
            raise Exception("Pas de connexion à la base de données")
        return get_table_names(self.connection)