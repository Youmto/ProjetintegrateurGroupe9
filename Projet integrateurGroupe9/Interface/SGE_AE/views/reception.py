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
    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.last_created_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Section création bon de réception
        creation_group = QWidget()
        creation_layout = QHBoxLayout()

        creation_layout.addWidget(QLabel("Référence*:"))
        self.ref_input = QLineEdit()
        self.ref_input.setPlaceholderText("Ex: REC-2023-001")
        creation_layout.addWidget(self.ref_input)

        creation_layout.addWidget(QLabel("Date prévue*:"))
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        creation_layout.addWidget(self.date_input)

        create_btn = QPushButton("Créer bon")
        create_btn.clicked.connect(self.create_reception)
        create_btn.setStyleSheet("background-color: #4CAF50; color: white;")
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
        self.receptions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.receptions_table.doubleClicked.connect(self.show_reception_details)
        self.receptions_table.setAlternatingRowColors(True)
        layout.addWidget(QLabel("Bons de réception en attente:"))
        layout.addWidget(self.receptions_table)

        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Rafraîchir")
        refresh_btn.clicked.connect(self.load_receptions)
        btn_layout.addWidget(refresh_btn)

        validate_btn = QPushButton("Valider la réception finale")
        validate_btn.clicked.connect(self.validate_selected_reception)
        validate_btn.setStyleSheet("background-color: #2196F3; color: white;")
        btn_layout.addWidget(validate_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_receptions()

    def load_receptions(self):
        try:
            receptions = handle_receptions_en_attente(self.db_conn)
            self.receptions_table.setRowCount(len(receptions))
            
            for row, reception in enumerate(receptions):
                # Ajout des données
                self.receptions_table.setItem(row, 0, QTableWidgetItem(str(reception['idBon'])))
                self.receptions_table.setItem(row, 1, QTableWidgetItem(reception['reference']))
                self.receptions_table.setItem(row, 2, QTableWidgetItem(reception['dateCreation'].strftime("%d/%m/%Y")))
                self.receptions_table.setItem(row, 3, QTableWidgetItem(reception['dateReceptionPrevue'].strftime("%d/%m/%Y")))
                self.receptions_table.setItem(row, 4, QTableWidgetItem(reception['statut']))
                
                # Colorisation selon le statut
                if reception['statut'] == "en_cours":
                    color = QColor(255, 255, 200)  # Jaune clair
                elif reception['statut'] == "en_attente":
                    color = QColor(240, 240, 240)  # Gris clair
                else:
                    color = QColor(200, 255, 200)  # Vert clair
                
                for col in range(self.receptions_table.columnCount()):
                    self.receptions_table.item(row, col).setBackground(color)
            
            self.receptions_table.resizeColumnsToContents()
            
            # Sélection automatique de la dernière création
            if self.last_created_id:
                for row in range(self.receptions_table.rowCount()):
                    if int(self.receptions_table.item(row, 0).text()) == self.last_created_id:
                        self.receptions_table.selectRow(row)
                        self.last_created_id = None  # Reset après sélection
                        break
                        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement échoué : {str(e)}")

    def create_reception(self):
        reference = self.ref_input.text().strip()
        date_prevue = self.date_input.date().toString("yyyy-MM-dd")

        if not reference:
            QMessageBox.warning(self, "Champ manquant", "La référence est obligatoire")
            return

        try:
            reception_id = handle_validation_reception(
                self.db_conn,
                reference,
                date_prevue,
                self.user['idIndividu']
            )
            self.last_created_id = reception_id
            QMessageBox.information(
                self, 
                "Succès", 
                f"Bon de réception #{reception_id} créé avec succès"
            )
            self.load_receptions()
            self.ref_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la création: {str(e)}")

    def show_reception_details(self, index):
        reception_id = int(self.receptions_table.item(index.row(), 0).text())
        self.detail_window = ReceptionDetailWindow(self.db_conn, self.user, reception_id)
        self.detail_window.reception_completed.connect(self.load_receptions)
        self.detail_window.show()

    def validate_selected_reception(self):
        selected_row = self.receptions_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un bon à valider")
            return
            
        try:
            reception_id = int(self.receptions_table.item(selected_row, 0).text())
            statut = self.receptions_table.item(selected_row, 4).text()
            
            if statut != "en_cours":
                QMessageBox.warning(
                    self, 
                    "Validation impossible", 
                    "Seuls les bons 'en_cours' peuvent être validés"
                )
                return
                
            valider_reception(self.db_conn, reception_id)
            QMessageBox.information(
                self, 
                "Succès", 
                f"Bon #{reception_id} validé avec succès"
            )
            self.load_receptions()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erreur", 
                f"Validation échouée : {str(e)}"
            )