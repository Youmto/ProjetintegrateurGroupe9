from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate, Qt
from controllers.reception_controller import handle_receptions_en_attente, handle_validation_reception

class ReceptionModule(QWidget):
    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Section création bon de réception
        creation_group = QWidget()
        creation_layout = QHBoxLayout()

        creation_layout.addWidget(QLabel("Référence:"))
        self.ref_input = QLineEdit()
        creation_layout.addWidget(self.ref_input)

        creation_layout.addWidget(QLabel("Date prévue:"))
        self.date_input = QDateEdit(QDate.currentDate())
        creation_layout.addWidget(self.date_input)

        create_btn = QPushButton("Créer bon")
        create_btn.clicked.connect(self.create_reception)
        creation_layout.addWidget(create_btn)

        creation_group.setLayout(creation_layout)
        layout.addWidget(creation_group)

        # Liste des bons en attente
        self.receptions_table = QTableWidget()
        self.receptions_table.setColumnCount(5)
        self.receptions_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Date création", "Date prévue", "Statut"
        ])
        self.receptions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.receptions_table.doubleClicked.connect(self.show_reception_details)
        layout.addWidget(QLabel("Bons de réception en attente:"))
        layout.addWidget(self.receptions_table)

        # Bouton rafraîchir
        refresh_btn = QPushButton("Rafraîchir la liste")
        refresh_btn.clicked.connect(self.load_receptions)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)
        self.load_receptions()

    def load_receptions(self):
        try:
            receptions = handle_receptions_en_attente(self.db_conn)
            self.receptions_table.setRowCount(len(receptions))
            for row, reception in enumerate(receptions):
                self.receptions_table.setItem(row, 0, QTableWidgetItem(str(reception['idBon'])))
                self.receptions_table.setItem(row, 1, QTableWidgetItem(reception['reference']))
                self.receptions_table.setItem(row, 2, QTableWidgetItem(reception['dateCreation'].strftime("%d/%m/%Y")))
                self.receptions_table.setItem(row, 3, QTableWidgetItem(reception['dateReceptionPrevue'].strftime("%d/%m/%Y")))
                self.receptions_table.setItem(row, 4, QTableWidgetItem(reception['statut']))
            self.receptions_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement échoué : {str(e)}")

    def create_reception(self):
        reference = self.ref_input.text()
        date_prevue = self.date_input.date().toString("yyyy-MM-dd")

        if not reference:
            QMessageBox.warning(self, "Champ manquant", "Veuillez saisir une référence")
            return

        try:
            reception_id = handle_validation_reception(
                self.db_conn,
                reference,
                date_prevue,
                self.user['idIndividu']
            )
            QMessageBox.information(self, "Succès", 
                                  f"Bon de réception #{reception_id} créé avec succès")
            self.load_receptions()
            self.ref_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la création: {str(e)}")

    def show_reception_details(self, index):
        reception_id = int(self.receptions_table.item(index.row(), 0).text())
        from views.reception_detail import ReceptionDetailWindow
        self.detail_window = ReceptionDetailWindow(self.db_conn, self.user, reception_id)
        self.detail_window.show()
