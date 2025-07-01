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
        
        # Connexion via touche Entrée
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Label caché pour accessibilité
        self.accessibility_label = QLabel("Formulaire de connexion au système de gestion d'entrepôt")
        self.accessibility_label.setAccessibleName("Formulaire de connexion")
        self.accessibility_label.hide()
        layout.addWidget(self.accessibility_label)
        
        self.setLayout(layout)
    
    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Champs manquants", 
                              "Veuillez remplir tous les champs")
            return
        
        try:
            user = authenticate_user(self.db_conn, email, password)
            if user:
                # Feedback visuel avant transition
                self.setEnabled(False)
                QMessageBox.information(self, "Connexion réussie", 
                                      f"Bienvenue {user['email']} {user['nom']}")
                self.close()
                
                from views.main_window import MainWindow
                self.main_window = MainWindow(db_conn=self.db_conn, user=user)
                self.main_window.show()
            else:
                QMessageBox.critical(self, "Échec de connexion", 
                                   "Email ou mot de passe incorrect")
        except Exception as e:
            QMessageBox.critical(self, "Erreur technique", 
                               f"Une erreur est survenue :\n{str(e)}")
            # Réactiver l'interface en cas d'erreur
            self.setEnabled(True)