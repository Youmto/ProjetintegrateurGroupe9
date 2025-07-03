from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QListWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import logging
from controllers.user_controller import (
    get_all_users,
    get_all_roles,
    get_all_organisations,
    activate_user_role,
    deactivate_user_role,
    get_roles_for_user
)


logger = logging.getLogger(__name__)

class AdminModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.users = []
        self.roles = []
        self.orgs = []
        self.setup_ui()
        self.load_data()
        logger.info("[AdminModule] Initialisé")

    def setup_ui(self):
        layout = QVBoxLayout()

        # Titre principal avec emoji et style
        title = QLabel("👥 Gestion des utilisateurs et rôles")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2E86C1; margin-bottom: 15px;")
        layout.addWidget(title)

        # Label utilisateurs + liste
        layout.addWidget(QLabel("👤 Liste des utilisateurs :"))
        self.user_list = QListWidget()
        self.user_list.itemSelectionChanged.connect(self.refresh_roles)
        self.user_list.setStyleSheet("""
            QListWidget {
                background-color: #F0F3F4;
                border: 1px solid #D5DBDB;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
        """)
        layout.addWidget(self.user_list)

        # Label rôle + combo
        layout.addWidget(QLabel("🎭 Rôle à attribuer/retirer :"))
        self.role_combo = QComboBox()
        self.role_combo.setStyleSheet("padding: 5px; font-size: 14px;")
        layout.addWidget(self.role_combo)

        # Label organisation + combo
        layout.addWidget(QLabel("🏢 Organisation :"))
        self.org_combo = QComboBox()
        self.org_combo.setStyleSheet("padding: 5px; font-size: 14px;")
        layout.addWidget(self.org_combo)

        # Label rôles actuels
        self.current_roles_label = QLabel("ℹ️ Rôles actuels : Aucun utilisateur sélectionné")
        self.current_roles_label.setWordWrap(True)
        self.current_roles_label.setStyleSheet("font-style: italic; color: #7F8C8D; margin: 10px 0;")
        layout.addWidget(self.current_roles_label)

        # Boutons Attribuer et Révoquer
        btn_layout = QHBoxLayout()

        assign_btn = QPushButton("✅ Attribuer")
        assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #28B463;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #239B56;
            }
        """)
        assign_btn.clicked.connect(self.assign_role)
        btn_layout.addWidget(assign_btn)

        revoke_btn = QPushButton("❌ Révoquer")
        revoke_btn.setStyleSheet("""
            QPushButton {
                background-color: #CB4335;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #922B21;
            }
        """)
        revoke_btn.clicked.connect(self.revoke_role)
        btn_layout.addWidget(revoke_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # Le reste du code inchangé
    def load_data(self):
        try:
            self.users = get_all_users(self.conn)
            self.roles = get_all_roles(self.conn)
            self.orgs = get_all_organisations(self.conn)

            self.user_list.clear()
            for user in self.users:
                self.user_list.addItem(f"{user['nom']} ({user['email']})")

            self.populate_role_combo()
            self.populate_org_combo()
        except Exception as e:
            logger.exception("Erreur chargement données")
            QMessageBox.critical(self, "Erreur", f"Chargement échoué : {e}")

    def populate_role_combo(self):
        self.role_combo.clear()
        for role in self.roles:
            self.role_combo.addItem(f"{role['libelle']} ({role['typeRole']})", role['id'])

    def populate_org_combo(self):
        self.org_combo.clear()
        for org in self.orgs:
            self.org_combo.addItem(org['nom'], org['id'])

    def selected_user(self):
        row = self.user_list.currentRow()
        return self.users[row] if 0 <= row < len(self.users) else None

    def selected_role(self):
        idx = self.role_combo.currentIndex()
        return self.roles[idx] if 0 <= idx < len(self.roles) else None

    def selected_organisation(self):
        idx = self.org_combo.currentIndex()
        return self.orgs[idx] if 0 <= idx < len(self.orgs) else None

    def refresh_roles(self):
        user = self.selected_user()
        if not user:
            self.current_roles_label.setText("Rôles actuels : Aucun utilisateur sélectionné")
            return

        try:
            roles = get_roles_for_user(self.conn, user['id'])
            role_names = [r['libelle'] for r in roles]
            self.current_roles_label.setText(
                f"Rôles actuels pour {user['nom']} : {', '.join(role_names) if role_names else 'Aucun'}"
            )
        except Exception as e:
            logger.exception("Erreur rafraîchissement rôles")
            self.current_roles_label.setText("Erreur lors du chargement des rôles")

    def assign_role(self):
        user, role, org = self.selected_user(), self.selected_role(), self.selected_organisation()
        if not (user and role and org):
            QMessageBox.warning(self, "Sélection incomplète", "Utilisateur, rôle et organisation requis.")
            return

        try:
            success = activate_user_role(self.conn, user['id'], role['id'], org['id'])
            if success:
                QMessageBox.information(self, "Succès", f"Rôle attribué à {user['nom']}")
                self.refresh_roles()
                self.load_data()
            else:
                QMessageBox.information(self, "Déjà attribué", "Ce rôle est déjà actif.")
        except Exception as e:
            logger.exception("Erreur lors de l'attribution du rôle")
            QMessageBox.critical(self, "Erreur", f"Attribution échouée : {e}")

    def revoke_role(self):
        user, role, org = self.selected_user(), self.selected_role(), self.selected_organisation()
        if not (user and role and org):
            QMessageBox.warning(self, "Sélection incomplète", "Utilisateur, rôle et organisation requis.")
            return

        try:
            success = deactivate_user_role(self.conn, user['id'], role['id'], org['id'])
            if success:
                QMessageBox.information(self, "Succès", f"Rôle révoqué pour {user['nom']}")
                self.refresh_roles()
                self.load_data()
            else:
                QMessageBox.information(self, "Non attribué", "Ce rôle n'était pas actif.")
        except Exception as e:
            logger.exception("Erreur lors de la révocation du rôle")
            QMessageBox.critical(self, "Erreur", f"Révocation échouée : {e}")
