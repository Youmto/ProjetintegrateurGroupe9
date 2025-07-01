from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QListWidget, QMessageBox
)
from PyQt5.QtCore import Qt
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

        layout.addWidget(QLabel("Utilisateurs"))
        self.user_list = QListWidget()
        self.user_list.itemSelectionChanged.connect(self.refresh_roles)
        layout.addWidget(self.user_list)

        layout.addWidget(QLabel("Rôle à attribuer/retirer"))
        self.role_combo = QComboBox()
        layout.addWidget(self.role_combo)

        layout.addWidget(QLabel("Organisation"))
        self.org_combo = QComboBox()
        layout.addWidget(self.org_combo)

        self.current_roles_label = QLabel("Rôles actuels : Aucun utilisateur sélectionné")
        self.current_roles_label.setWordWrap(True)
        layout.addWidget(self.current_roles_label)

        btn_layout = QHBoxLayout()
        assign_btn = QPushButton("Attribuer")
        assign_btn.clicked.connect(self.assign_role)
        btn_layout.addWidget(assign_btn)

        revoke_btn = QPushButton("Révoquer")
        revoke_btn.clicked.connect(self.revoke_role)
        btn_layout.addWidget(revoke_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

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
            else:
                QMessageBox.information(self, "Non attribué", "Ce rôle n'était pas actif.")
        except Exception as e:
            logger.exception("Erreur lors de la révocation du rôle")
            QMessageBox.critical(self, "Erreur", f"Révocation échouée : {e}")