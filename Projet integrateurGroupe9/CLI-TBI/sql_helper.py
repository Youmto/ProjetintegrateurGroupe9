from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextEdit, 
                            QComboBox, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt
from utils.styles import get_module_style
from controllers.sql_helper_controller import SQLHelperController

class SQLHelperModule(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.controller = SQLHelperController(conn) 
        self.setStyleSheet(get_module_style("sql_helper")) 
        self.init_ui()
        self.connect_signals()
        self.load_initial_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Partie Question
        question_group = QGroupBox("Assistant")
        question_layout = QVBoxLayout()

        self.question_input = QTextEdit()
        question_layout.addWidget(self.question_input)

        self.ask_button = QPushButton("Poser question")
        question_layout.addWidget(self.ask_button)

        self.answer_area = QTextEdit()
        self.answer_area.setReadOnly(True)
        question_layout.addWidget(QLabel("Réponse:"))
        question_layout.addWidget(self.answer_area)

        question_group.setLayout(question_layout)
        self.layout.addWidget(question_group)

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
        self.category_combo.currentTextChanged.connect(self.update_display)
        self.ask_button.clicked.connect(self.handle_question)

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

    def handle_question(self):
        """Traite les questions de l'utilisateur"""
        question = self.question_input.toPlainText().strip()
        if not question:
            QMessageBox.warning(self, "Question vide", "Veuillez saisir une question")
            return
            
        try:
            answer = self.controller.process_question(question)  # Utilisez controller
            self.answer_area.setPlainText(answer)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de traitement: {str(e)}")
            self.answer_area.setPlainText("Une erreur est survenue lors du traitement de votre question.")