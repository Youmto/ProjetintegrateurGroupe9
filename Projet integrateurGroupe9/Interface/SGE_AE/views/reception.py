from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor
from controllers.reception_controller import (
    handle_receptions_en_attente, 
    handle_validation_reception,
    valider_reception
)
from views.reception_detail import ReceptionDetailWindow


class ReceptionModule(QWidget):
    """Module de gestion des bons de réception"""

    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.last_created_id = None
        self.detail_window = None
        self.setup_ui()
        self.load_receptions()

    def setup_ui(self):
        """Construction de l'interface utilisateur"""
        main_layout = QVBoxLayout(self)

        # --- Section création bon de réception ---
        creation_layout = QHBoxLayout()
        creation_layout.addWidget(QLabel("Référence*:"))
        self.ref_input = QLineEdit()
        self.ref_input.setPlaceholderText("Ex: REC-2023-001")
        creation_layout.addWidget(self.ref_input)

        creation_layout.addWidget(QLabel("Date prévue*:"))
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        creation_layout.addWidget(self.date_input)

        self.create_btn = QPushButton("Créer bon")
        self.create_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.create_btn.clicked.connect(self.create_reception)
        creation_layout.addWidget(self.create_btn)

        main_layout.addLayout(creation_layout)

        # --- Liste des bons en attente ---
        main_layout.addWidget(QLabel("Bons de réception en attente:"))
        self.receptions_table = QTableWidget()
        self.receptions_table.setColumnCount(5)
        self.receptions_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Date création", "Date prévue", "Statut"
        ])
        self.receptions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.receptions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.receptions_table.setAlternatingRowColors(True)
        self.receptions_table.doubleClicked.connect(self.show_reception_details)
        main_layout.addWidget(self.receptions_table)

        # --- Boutons d'action ---
        btn_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Rafraîchir")
        self.refresh_btn.clicked.connect(self.load_receptions)
        btn_layout.addWidget(self.refresh_btn)

        self.validate_btn = QPushButton("Valider la réception finale")
        self.validate_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.validate_btn.clicked.connect(self.validate_selected_reception)
        btn_layout.addWidget(self.validate_btn)

        main_layout.addLayout(btn_layout)

    def load_receptions(self):
        """Charge et affiche la liste des bons de réception en attente"""
        try:
            receptions = handle_receptions_en_attente(self.db_conn)
            self.receptions_table.setRowCount(len(receptions))

            for row_idx, reception in enumerate(receptions):
                self.receptions_table.setItem(row_idx, 0, QTableWidgetItem(str(reception['idBon'])))
                self.receptions_table.setItem(row_idx, 1, QTableWidgetItem(reception['reference']))
                self.receptions_table.setItem(row_idx, 2, QTableWidgetItem(reception['dateCreation'].strftime("%d/%m/%Y")))
                self.receptions_table.setItem(row_idx, 3, QTableWidgetItem(reception['dateReceptionPrevue'].strftime("%d/%m/%Y")))
                self.receptions_table.setItem(row_idx, 4, QTableWidgetItem(reception['statut']))

                # Colorisation des lignes selon le statut
                color = QColor(240, 240, 240)  # Par défaut gris clair
                if reception['statut'] == "en_cours":
                    color = QColor(255, 255, 200)  # Jaune clair
                elif reception['statut'] == "validé":
                    color = QColor(200, 255, 200)  # Vert clair
                
                for col in range(self.receptions_table.columnCount()):
                    self.receptions_table.item(row_idx, col).setBackground(color)

            self.receptions_table.resizeColumnsToContents()

            # Sélectionne automatiquement le dernier bon créé
            if self.last_created_id is not None:
                for r in range(self.receptions_table.rowCount()):
                    if int(self.receptions_table.item(r, 0).text()) == self.last_created_id:
                        self.receptions_table.selectRow(r)
                        self.last_created_id = None
                        break
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec du chargement des réceptions :\n{e}")

    def create_reception(self):
        """Crée un nouveau bon de réception"""
        reference = self.ref_input.text().strip()
        date_prevue = self.date_input.date().toString("yyyy-MM-dd")

        if not reference:
            QMessageBox.warning(self, "Champ requis", "La référence est obligatoire.")
            return

        try:
            reception_id = handle_validation_reception(
                self.db_conn,
                reference,
                date_prevue,
                self.user['idIndividu']
            )
            self.last_created_id = reception_id
            QMessageBox.information(self, "Succès", f"Bon de réception #{reception_id} créé avec succès.")
            self.ref_input.clear()
            self.load_receptions()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la création :\n{e}")

    def show_reception_details(self, index):
        """Affiche les détails du bon de réception sélectionné"""
        reception_id = int(self.receptions_table.item(index.row(), 0).text())
        if self.detail_window is None or not self.detail_window.isVisible():
            self.detail_window = ReceptionDetailWindow(self.db_conn, self.user, reception_id)
            self.detail_window.reception_completed.connect(self.load_receptions)
            self.detail_window.show()
        else:
            self.detail_window.raise_()
            self.detail_window.activateWindow()

    def validate_selected_reception(self):
        """Valide le bon de réception sélectionné"""
        selected_row = self.receptions_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un bon de réception à valider.")
            return
        
        reception_id = int(self.receptions_table.item(selected_row, 0).text())
        statut = self.receptions_table.item(selected_row, 4).text()

        if statut != "en_cours":
            QMessageBox.warning(self, "Validation impossible", "Seuls les bons 'en_cours' peuvent être validés.")
            return

        try:
            valider_reception(self.db_conn, reception_id)
            QMessageBox.information(self, "Succès", f"Bon #{reception_id} validé avec succès.")
            self.load_receptions()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la validation :\n{e}")
