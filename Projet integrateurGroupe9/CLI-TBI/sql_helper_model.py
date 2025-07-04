import json
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal

class SQLHelperModel:
    def __init__(self, conn):
        self.conn = conn
        self.help_data = {}
        self.load_help_data()

    def load_help_data(self):
        """Charge les données d'aide depuis un fichier JSON"""
        try:
            base_dir = Path(__file__).parent.parent 
            data_path = base_dir / 'data' / 'sql_help.json'
            with open(data_path, 'r', encoding='utf-8') as f:
                self.help_data = json.load(f)
        except Exception as e:
            print(f"Erreur de chargement: {str(e)}")
            self.load_fallback_data()

    def load_fallback_data(self):
        """Données de secours si le JSON est indisponible"""
        self.help_data = {
            "Requêtes basiques": {
                "description": "Données non chargées. Exemple : SELECT * FROM table;",
                "examples": ["SELECT * FROM table;"]
            }
        }


    def get_categories(self):
        """Retourne les catégories d'aide disponibles"""
        return list(self.help_data.keys())

    def get_categories_content(self, category):
        """Retourne le contenu d'aide pour une catégorie"""
        return self.help_data.get(category, {
            "description": "Catégorie non trouvée",
            "examples": []
        })

    def answer_question(self, question):
        """Répond à une question avec un système simple de correspondance"""
        question = question.lower()
        answers = {
            "select": "SELECT champ1, champ2 FROM table WHERE condition;",
            "insert": "INSERT INTO table (champ1, champ2) VALUES (valeur1, valeur2);",
            "join": "SELECT t1.champ, t2.champ FROM table1 t1 JOIN table2 t2 ON t1.id = t2.t1_id;"
        }
        
        for keyword, answer in answers.items():
            if keyword in question:
                return answer
        return "Je n'ai pas compris. Essayez avec des termes comme SELECT, INSERT, JOIN, etc."