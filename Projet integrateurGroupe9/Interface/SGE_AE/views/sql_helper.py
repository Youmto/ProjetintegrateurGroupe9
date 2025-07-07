from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextEdit, 
                            QComboBox, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor, QColor
from utils.styles import get_module_style
from controllers.sql_helper_controller import SQLHelperController

class SQLHelperModule(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.controller = SQLHelperController(conn) 
        self.setStyleSheet(get_module_style("sql_helper")) 
        self.init_ui()
        self.connect = self.connect_signals()
        self.load_initial_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        base_style = get_module_style("sql_helper")
        self.setStyleSheet(f"""
            {base_style}
            QTextEdit {{
                border: 1px solid #8BCDF6;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }}
            QGroupBox::title {{
                color: #015C92;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}
        """)

        # Partie Chat
        conv_group = QGroupBox("Assistant Conversationnel SGE")
        conv_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        conv_layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.user_input = QTextEdit()
        self.user_input.setMaximumHeight(60)
        input_layout.addWidget(self.user_input)
        
        self.send_btn = QPushButton("Envoyer")
        input_layout.addWidget(self.send_btn)
        
        conv_layout.addLayout(input_layout)
        conv_group.setLayout(conv_layout)
        self.layout.addWidget(conv_group)
        
        # Partie Aide
        help_group = QGroupBox("Aide SQL")
        help_layout = QVBoxLayout()

        self.category_combo = QComboBox()
        help_layout.addWidget(self.category_combo)

        self.description_area = QTextEdit()
        self.description_area.setReadOnly(True)
        help_layout.addWidget(QLabel("Description:"))
        help_layout.addWidget(self.description_area)

        self.examples_area = QTextEdit()
        self.examples_area.setReadOnly(True)
        help_layout.addWidget(QLabel("Exemples:"))
        help_layout.addWidget(self.examples_area)

        help_group.setLayout(help_layout)
        self.layout.addWidget(help_group)


    def connect_signals(self):
        self.send_btn.clicked.connect(self.handle_user_message)
        self.category_combo.currentTextChanged.connect(self.update_display)
        
        # Envoyer avec Ctrl+Entrée
        self.user_input.keyPressEvent = lambda event: (
            self.handle_key_press(event) or 
            QTextEdit.keyPressEvent(self.user_input, event))
            
    def handle_key_press(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self.handle_user_message()
            return True
        return False


    def load_initial_data(self):
        """Charge les catégories au démarrage"""
        try:
            categories = self.controller.get_categories()
            self.category_combo.addItems([""] + categories)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les catégories: {str(e)}")

    def update_display(self, category):
        """Met à jour l'affichage quand une catégorie est sélectionnée"""
        if not category:
            self.description_area.clear()
            self.examples_area.clear()
            return
            
        try:
            content = self.controller.get_category_content(category)  # Utilisez controller
            self.description_area.setPlainText(content["description"])
            self.examples_area.setPlainText("\n\n".join(content["examples"]))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger le contenu: {str(e)}")
            self.description_area.clear()
            self.examples_area.clear()

            
    def handle_chat(self):
        """Gère la conversation avec le chatbot"""
        question = self.user_input.toPlainText().strip()
        if not question:
            return
            
        # Afficher la question de l'utilisateur
        self.append_to_chat("Vous: " + question, "user")
        self.user_input.clear()
        
        # Obtenir la réponse
        try:
            answer = self.controller.process_question(question)
            self.append_to_chat("Assistant: " + answer, "bot")
        except Exception as e:
            self.append_to_chat("Assistant: Désolé, je rencontre un problème technique", "error")

    def append_to_chat(self, text, sender_type):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        colors = {
            "user": QColor("#015C92"),
            "bot": QColor("#2D8285"), 
            "error": QColor("#FF0000")
        }
        
        self.chat_display.setTextColor(colors.get(sender_type, QColor("#000000")))
        cursor.insertText(text + "\n\n")
        self.chat_display.ensureCursorVisible()
        
    def handle_user_message(self):
        question = self.user_input.toPlainText().strip()
        if not question:
            return
            
        self.append_to_chat(f"Vous: {question}", "user")
        self.user_input.clear()
        
        QTimer.singleShot(100, lambda: self.process_bot_response(question))

    def process_bot_response(self, question):
        try:
            response = self.controller.process_question(question)
            self.append_to_chat(f"Assistant: {response}", "bot")
        except Exception as e:
            self.append_to_chat("Assistant: Désolé, service temporairement indisponible", "error")
