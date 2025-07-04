from models.sql_helper_model import SQLHelperModel

class SQLHelperController:
   def __init__(self, conn):
        self.model = SQLHelperModel(conn) 
        
   def get_categories(self):
        return self.model.get_categories()
        
   def get_category_content(self, category):
        return self.model.get_categories_content(category)
        
   def process_question(self, question):
        return self.model.answer_question(question)