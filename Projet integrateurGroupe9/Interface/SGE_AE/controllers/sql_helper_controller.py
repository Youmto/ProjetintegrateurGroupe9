from models.sql_helper_model import SQLHelperModel
from gestionErreur.Text_Processing_Service import TextProcessingService
from chatbot_db import get_chatbot_db_uri

class SQLHelperController:
   def __init__(self, conn):
        try:
            self.model = SQLHelperModel(conn)
            self.text_processor = TextProcessingService()
        except Exception as e:
            raise RuntimeError(f"Erreur contrôleur: {e}") from e
        
   def get_categories(self):
        return self.model.get_categories()
        
   def get_category_content(self, category):
        return self.model.get_categories_content(category)
        
   def process_question(self, question):
        processed_question = self.text_processor.normalize_text(question)
        return self.model.answer_question(processed_question)