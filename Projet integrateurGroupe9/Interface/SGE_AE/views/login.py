from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QMessageBox, QFrame)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QLinearGradient, QBrush, QColor
from PyQt5.QtCore import Qt, QSize
from SGE_AE.models.user_model import authenticate_user


class LoginWindow(QWidget):
    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.setup_ui()
        
    def setup_ui(self):
        # Configuration de la fenêtre
        self.setWindowTitle("Connexion - Système de Gestion d'Entrepôts")
        self.setFixedSize(1300, 1200)
        self.setWindowIcon(QIcon("assets/icons/logo.png"))
        
        # Fond dégradé professionnel
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#2c3e50"))  # Bleu foncé
        gradient.setColorAt(1, QColor("#3498db"))  # Bleu clair
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        # Carte de connexion
        login_card = QFrame()
        login_card.setFixedWidth(550)  # Augmente la largeur de la carte
        login_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
                padding: 30px;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo = QLabel()
        logo_pixmap = QPixmap("assets/icons/logo.png").scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        
        # Titre
        title = QLabel("SYSTÈME DE GESTION\nD'ENTREPÔTS")
        title.setFont(QFont('Arial', 20, QFont.Bold))  # Augmente la taille de la police
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)  # Permet le retour à la ligne automatique
        
        # Formulaire
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Champ Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adresse email professionnelle")
        self.email_input.setStyleSheet(self.get_input_style())
        
        # Champ Mot de passe
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.get_input_style())
        
        # Bouton de connexion
        login_btn = QPushButton("SE CONNECTER")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1d6fa5;
            }
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        
        # Lien mot de passe oublié
        forgot_pwd = QLabel("<a href='#' style='color:#3498db;text-decoration:none;'>Mot de passe oublié ?</a>")
        forgot_pwd.setAlignment(Qt.AlignCenter)
        forgot_pwd.setOpenExternalLinks(False)
        
        # Assemblage de la carte
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(login_btn)
        form_layout.addWidget(forgot_pwd)
        
        card_layout.addWidget(logo)
        card_layout.addWidget(title)
        card_layout.addLayout(form_layout)
        
        login_card.setLayout(card_layout)
        
        # Footer
        footer = QLabel("© 2024 UCAC-ULC - Version 1.0.0")
        footer.setStyleSheet("color: white; font-size: 11px;")
        footer.setAlignment(Qt.AlignCenter)
        
        # Assemblage final
        main_layout.addWidget(login_card)
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)
    
    def get_input_style(self):
        return """
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
        """
    
    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # Validation
        if not email:
            self.show_error("Champ requis", "Veuillez saisir votre adresse email")
            self.email_input.setFocus()
            return
            
        if not password:
            self.show_error("Champ requis", "Veuillez saisir votre mot de passe")
            self.password_input.setFocus()
            return
            
        # Authentification
        try:
            user = authenticate_user(self.db_conn, email, password)
            if user:
                self.open_main_window(user)
            else:
                self.show_error("Authentification échouée", "Email ou mot de passe incorrect")
        except Exception as e:
            self.show_error("Erreur système", f"Une erreur est survenue: {str(e)}")
    
    def open_main_window(self, user):
        from SGE_AE.views.main_window import MainWindow
        self.close()
        self.main_window = MainWindow(db_conn=self.db_conn, user=user)
        self.main_window.show()
    
    def show_error(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()