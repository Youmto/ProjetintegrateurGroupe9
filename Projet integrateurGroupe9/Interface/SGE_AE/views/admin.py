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
        self.init_ui()
        logger.info("Module Admin initialisé")

    def init_ui(self):
        layout = QVBoxLayout()

        self.user_list = QListWidget()
        self.user_list.itemSelectionChanged.connect(self.refresh_roles)
        layout.addWidget(QLabel("Utilisateurs"))
        layout.addWidget(self.user_list)

        self.role_combo = QComboBox()
        layout.addWidget(QLabel("Rôle à attribuer/retirer"))
        layout.addWidget(self.role_combo)

        self.org_combo = QComboBox()
        layout.addWidget(QLabel("Organisation"))
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
        self.load_data()

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
            logger.error("Erreur chargement données: %s", str(e))
            QMessageBox.critical(self, "Erreur", str(e))

    def populate_role_combo(self):
        self.role_combo.clear()
        for role in self.roles:
            display_text = f"{role['libelle']} ({role['typeRole']})"
            self.role_combo.addItem(display_text, role['id'])

    def populate_org_combo(self):
        self.org_combo.clear()
        for org in self.orgs:
            self.org_combo.addItem(org['nom'], org['id'])

    def selected_user(self):
        row = self.user_list.currentRow()
        return self.users[row] if 0 <= row < len(self.users) else None

    def selected_role(self):
        index = self.role_combo.currentIndex()
        return self.roles[index] if 0 <= index < len(self.roles) else None

    def selected_organisation(self):
        index = self.org_combo.currentIndex()
        return self.orgs[index] if 0 <= index < len(self.orgs) else None

    def refresh_roles(self):
        user = self.selected_user()
        if not user:
            self.current_roles_label.setText("Rôles actuels : Aucun utilisateur sélectionné")
            return

        try:
            roles = get_roles_for_user(self.conn, user['id'])
            role_names = [role['libelle'] for role in roles]
            self.current_roles_label.setText(f"Rôles actuels pour {user['nom']} : {', '.join(role_names)}")
        except Exception as e:
            logger.error("Erreur rafraîchissement rôles: %s", str(e))
            self.current_roles_label.setText("Erreur lors du chargement des rôles")

    def assign_role(self):
        user = self.selected_user()
        role = self.selected_role()
        org = self.selected_organisation()
        if not user or not role or not org:
            QMessageBox.warning(self, "Champ manquant", "Sélectionnez un utilisateur, un rôle et une organisation")
            return

        try:
            if activate_user_role(self.conn, user['id'], role['id'], org['id']):
                QMessageBox.information(self, "Succès", f"Rôle attribué à {user['nom']}")
                self.refresh_roles()
            else:
                QMessageBox.warning(self, "Attention", "Ce rôle est déjà attribué")
        except Exception as e:
            logger.error("Erreur attribution rôle: %s", str(e))
            QMessageBox.critical(self, "Erreur", str(e))

    def revoke_role(self):
        user = self.selected_user()
        role = self.selected_role()
        org = self.selected_organisation()
        if not user or not role or not org:
            QMessageBox.warning(self, "Champ manquant", "Sélectionnez un utilisateur, un rôle et une organisation")
            return

        try:
            if deactivate_user_role(self.conn, user['id'], role['id'], org['id']):
                QMessageBox.information(self, "Succès", f"Rôle révoqué pour {user['nom']}")
                self.refresh_roles()
            else:
                QMessageBox.warning(self, "Non attribué", "Ce rôle n'était pas attribué")
        except Exception as e:
            logger.error("Erreur révocation rôle: %s", str(e))
            QMessageBox.critical(self, "Erreur", str(e))
