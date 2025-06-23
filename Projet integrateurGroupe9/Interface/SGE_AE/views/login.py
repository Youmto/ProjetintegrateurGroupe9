from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                            QVBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from SGE_AE.models.user_model import authenticate_user

class LoginWindow(QWidget):
    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.setWindowTitle("Connexion - SGE")
        self.setFixedSize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("Connexion au Système de Gestion d'Entrepôt")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Champ email
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre@email.com")
        layout.addWidget(self.email_input)
        
        # Champ mot de passe
        layout.addWidget(QLabel("Mot de passe:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Bouton connexion
        login_btn = QPushButton("Se connecter")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
    
    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Champs manquants", 
                               "Veuillez remplir tous les champs")
            return
        
        user = authenticate_user(self.db_conn, email, password)
        if user:
            self.close()
            from views.main_window import MainWindow
            self.main_window = MainWindow(db_conn=self.db_conn, user=user)
            self.main_window.show()
        else:
            QMessageBox.critical(self, "Échec de connexion", 
                                "Email ou mot de passe incorrect")