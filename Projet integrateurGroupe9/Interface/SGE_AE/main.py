import sys
import os
from PyQt5.QtWidgets import QApplication
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from views.login import LoginWindow
from database import create_connection
import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.ERROR)


def main():
    # Créer l'application Qt
    app = QApplication(sys.argv)
    
    # Établir la connexion à la base de données
    conn = create_connection()
    if conn is None:
        print("Erreur: Impossible de se connecter à la base de données")
        sys.exit(1)
    
    # Afficher la fenêtre de login
    login_window = LoginWindow(conn)
    login_window.show()
    
    # Exécuter l'application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()