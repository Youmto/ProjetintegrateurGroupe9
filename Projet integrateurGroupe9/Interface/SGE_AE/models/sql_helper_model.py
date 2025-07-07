import json
import os
from pathlib import Path
from chatbot_db import get_chatbot_db_uri
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from gestionErreur.Text_Processing_Service import TextProcessingService
import logging

class SQLHelperModel:
    def __init__(self, conn):
        self.conn = conn
        self.help_data = {}
        self.text_processor = TextProcessingService()
        self.help_data = self.load_help_data()
        self.init_chatbot()
        
    def init_chatbot(self):
        # Configuration PostgreSQL pour ChatterBot
        try:
            os.makedirs("dataChat", exist_ok=True)
            self.chatbot = ChatBot(
                'SQLAssistant',
                storage_adapter='chatterbot.storage.SQLStorageAdapter',
                database_uri=get_chatbot_db_uri(),
                logic_adapters=[{
                    'import_path': 'chatterbot.logic.BestMatch',
                    'maximum_similarity_threshold': 0.85
                }]
            )
            self.train_chatbot()
        except Exception as error:
            logging.error(f"Erreur SQLite : {str(error)}")
            logging.error(f"Erreur d'initialisation du chatbot: {str(error)}")
            raise RuntimeError(f"Échec de l'initialisation du chatbot{str(error)}") from error

    def train_chatbot(self):
        """Entraînement sécurisé"""
        try:
            trainer = ChatterBotCorpusTrainer(self.chatbot)
            trainer.train("chatterbot.corpus.french")
        except Exception as e:
            logging.warning(f"Entraînement partiel: {e}")
            
            
    def generate_training_data(self):
        """Données de secours si le YAML est indisponible"""
        training_data = [
           ["comment voir le stock", "SELECT * FROM inventaire WHERE quantite > 0;"],
           ["liste des livraisons", "SELECT * FROM receptions WHERE statut = 'en_attente';"],
        ]
        # Salutations
        greetings = ["bonjour", "salut", "coucou", "hello", "bjr", "hi", "hey","slt", "cc",]
        for g in greetings:
            training_data.extend([
                g,
                "Bonjour ! Comment puis-je vous aider avec le SGE aujourd'hui ?"
            ])
        
        # Questions spécifiques SGE
        for category, content in self.help_data.items():
            training_data.extend([
                f"Comment faire {category.lower()}",
                f"{content['description']}\nExemples:\n" + "\n".join(content['examples'])
            ])
        
        # Aplatir la liste
        return [item for sublist in training_data for item in sublist]

    def load_help_data(self):
        """Charge les données d'aide depuis un fichier JSON"""
        try:
            base_dir = Path(__file__).parent.parent 
            data_path = base_dir / 'data' / 'sql_help.json'
            with open(data_path, 'r', encoding='utf-8') as f:
                self.help_data = json.load(f)
        except Exception as e:
            print(f"Erreur de chargement: {str(e)}")
            return self.load_fallback_data()

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
        try:
            # Détection des salutations
            if self.is_greeting(question):
                return self.handle_greeting(question)
                
            # Réponses spécifiques SGE
            sge_answer = self.get_sge_specific_answer(question)
            if sge_answer:
                return sge_answer
                
            # Fallback au chatbot générique
            return str(self.chatbot.get_response(question))
            
        except Exception as e:
            logging.error(f"Erreur chatbot: {str(e)}")
            return "Désolé, je rencontre un problème technique. Veuillez reformuler votre question."

    def is_greeting(self, text):
        greetings = ["bonjour", "salut", "coucou", "hello", "bjr", "hi", "hey","slt", "cc",]
        return any(g in text.lower() for g in greetings)

    def handle_greeting(self, text):
        if "aide" in text.lower() or "aider" in text.lower():
            return "Bonjour ! Je suis là pour vous aider avec le SGE. Posez-moi votre question."
        return "Bonjour ! Comment puis-je vous aider avec le système SGE aujourd'hui ?"

    def get_sge_specific_answer(self, question):
        question_lower = question.lower()
        valid_terms = {
          "inventaire": self.text_processor.expand_terms(["stock", "inventaire", "quantité", "disponible", "stocker", "lot"]),
          "réception": self.text_processor.expand_terms(["réception", "livraison", "enregistrer", "recevoir", "bon réception"]),
          "expédition": self.text_processor.expand_terms(["expédition", "envoyer", "colis", "expédier", "bon expédition", "préparer"]),
          "mouvement": self.text_processor.expand_terms(["transfert", "déplacer", "mouvement", "cellule", "déplacement"]),
          "produits": self.text_processor.expand_terms(["produit", "article", "référence", "materiel", "logiciel"]),
          "rapports": self.text_processor.expand_terms(["rapport", "exception", "erreur", "problème"]),
          "utilisateurs": self.text_processor.expand_terms(["utilisateur", "individu", "personne", "rôle", "responsable"])
        }
        
        # Trouver la catégorie la plus proche
        best_match = None
        best_score = float('inf')
        
        for category, terms in valid_terms.items():
            match = self.text_processor.find_closest_match(question, terms)
            if match:
               distance = self.text_processor.levenshtein_distance(self.text_processor.normalize_text(question), self.text_processor.normalize_text(match))
               if distance < best_score:
                best_score = distance
                best_match = category
    
        # Seuil de tolérance (ajustable)
        if best_score > 2:  # seuil de distance de Levenshtein
            return None
    
        responses = {
        "inventaire": (
            "Gestion de l'inventaire:\n"
            "- Pour consulter les stocks: SELECT * FROM vue_inventaire_global\n"
            "- Pour les produits en rupture: SELECT * FROM produits_en_rupture()\n"
            "- Pour les produits expirant bientôt: SELECT * FROM produits_expirant_bientot(30)"
        ),
        "réception": (
            "Processus de réception:\n"
            "- Créer un bon de réception: INSERT INTO BON_RECEPTION(...)\n"
            "- Réceptionner un lot: SELECT receptionner_lot(id_bon, ref_lot, id_produit...)\n"
            "- Marquer comme terminé: UPDATE BON_RECEPTION SET statut='termine'"
        ),
        "expédition": (
            "Processus d'expédition:\n"
            "- Créer un bon: INSERT INTO BON_EXPEDITION(...)\n"
            "- Préparer un colis: SELECT preparer_colis(id_bon, id_produit, quantite)\n"
            "- Marquer comme expédié: UPDATE COLIS SET statut='expedie'"
        ),
        "mouvement": (
            "Gestion des mouvements:\n"
            "- Déplacer un lot: SELECT deplacer_lot(id_lot, cellule_source, cellule_dest, quantite)\n"
            "- Voir l'historique: SELECT * FROM DEPLACEMENT_LOG\n"
            "- Ajuster stock: SELECT ajuster_inventaire(id_lot, id_cellule, nouvelle_quantite)"
        ),
        "produits": (
            "Gestion des produits:\n"
            "- Ajouter produit: INSERT INTO PRODUIT(...)\n"
            "- Lister produits: SELECT * FROM PRODUIT\n"
            "- Détails matériel: SELECT * FROM PRODUIT_MATERIEL\n"
            "- Détails logiciel: SELECT * FROM PRODUIT_LOGICIEL"
        ),
        "rapports": (
            "Gestion des rapports:\n"
            "- Créer rapport: INSERT INTO RAPPORT_EXCEPTION(...)\n"
            "- Lister rapports: SELECT * FROM RAPPORT_EXCEPTION\n"
            "- Rechercher erreurs: SELECT * FROM RAPPORT_EXCEPTION WHERE typeRapport='erreur'"
        ),
        "utilisateurs": (
            "Gestion des utilisateurs:\n"
            "- Ajouter utilisateur: INSERT INTO INDIVIDU(...)\n"
            "- Attribuer rôle: INSERT INTO AFFECTER_ROLE(...)\n"
            "- Lister utilisateurs: SELECT * FROM INDIVIDU"
        )
        }
        
    
        for module, terms in valid_terms.items():
           if any(term in question_lower for term in terms):
            return responses.get(module, f"Module {module} - Consultez l'aide pour plus de détails.")
        
        return responses.get(best_match)
    
    def reload_corpus(self):
        try:
            base_dir = Path(__file__).parent.parent
            corpus_path = base_dir / 'data' / 'sge_corpus.yml'
            trainer = ChatterBotCorpusTrainer(self.chatbot)
            trainer.train(str(corpus_path))
            return True
        except Exception as e:
            logging.error(f"Rechargement échoué: {str(e)}")
            return False