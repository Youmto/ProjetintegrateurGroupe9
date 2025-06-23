from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QListWidget, QMessageBox
from controllers.user_controller import get_all_users, get_all_roles, activate_user_role, deactivate_user_role

class AdminModule(QWidget):
    def __init__(self, conn,user):
        self.user = user
        super().__init__()
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.user_list = QListWidget()
        self.user_list.itemSelectionChanged.connect(self.refresh_roles)
        layout.addWidget(QLabel("Utilisateurs"))
        layout.addWidget(self.user_list)

        self.role_combo = QComboBox()
        layout.addWidget(QLabel("Rôle à attribuer/retirer"))
        layout.addWidget(self.role_combo)

        btns = QHBoxLayout()
        add_btn = QPushButton("Attribuer")
        add_btn.clicked.connect(self.assign)
        btns.addWidget(add_btn)
        del_btn = QPushButton("Révoquer")
        del_btn.clicked.connect(self.revoke)
        btns.addWidget(del_btn)

        layout.addLayout(btns)
        self.setLayout(layout)
        self.load()

    def load(self):
        self.users = get_all_users(self.conn)
        self.roles = get_all_roles(self.conn)
        self.user_list.clear()
        for user in self.users:
            self.user_list.addItem(f"{user['id']} - {user['nom']} ({user['email']})")
        self.role_combo.clear()
        for role in self.roles:
            self.role_combo.addItem(role['libelle'], role['id'])

    def selected_user_id(self):
        row = self.user_list.currentRow()
        if row < 0:
            return None
        return self.users[row]['id']

    def selected_role_id(self):
        return self.role_combo.currentData()

    def assign(self):
        uid = self.selected_user_id()
        rid = self.selected_role_id()
        if uid and rid:
            activate_user_role(self.conn, uid, rid)
            QMessageBox.information(self, "Succès", "Rôle attribué")

    def revoke(self):
        uid = self.selected_user_id()
        rid = self.selected_role_id()
        if uid and rid:
            deactivate_user_role(self.conn, uid, rid)
            QMessageBox.information(self, "Succès", "Rôle révoqué")