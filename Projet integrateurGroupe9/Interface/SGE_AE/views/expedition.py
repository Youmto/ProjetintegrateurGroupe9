from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTableWidget, 
                            QTableWidgetItem, QComboBox, QDateEdit, QMessageBox)
from PyQt5.QtCore import QDate, Qt
from models.stock_model import get_pending_expeditions, create_expedition, prepare_expedition
from controllers.expedition_controller import handle_preparation_expedition
class ExpeditionModule(QWidget):
    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Section création bon d'expédition
        creation_group = QWidget()
        creation_layout = QHBoxLayout()
        
        creation_layout.addWidget(QLabel("Référence:"))
        self.ref_input = QLineEdit()
        creation_layout.addWidget(self.ref_input)
        
        creation_layout.addWidget(QLabel("Date prévue:"))
        self.date_input = QDateEdit(QDate.currentDate())
        creation_layout.addWidget(self.date_input)
        
        creation_layout.addWidget(QLabel("Priorité:"))
        self.priority_input = QComboBox()
        self.priority_input.addItems(["normal", "élevée", "urgente"])
        creation_layout.addWidget(self.priority_input)
        
        create_btn = QPushButton("Créer bon")
        create_btn.clicked.connect(self.create_expedition)
        creation_layout.addWidget(create_btn)
        
        creation_group.setLayout(creation_layout)
        layout.addWidget(creation_group)
        
        # Liste des bons en attente
        self.expeditions_table = QTableWidget()
        self.expeditions_table.setColumnCount(6)
        self.expeditions_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Date création", "Date prévue", "Priorité", "Statut"
        ])
        self.expeditions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.expeditions_table.doubleClicked.connect(self.show_expedition_details)
        layout.addWidget(QLabel("Bons d'expédition en attente:"))
        layout.addWidget(self.expeditions_table)
        
        # Bouton rafraîchir
        refresh_btn = QPushButton("Rafraîchir la liste")
        refresh_btn.clicked.connect(self.load_expeditions)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        self.load_expeditions()
    
    def load_expeditions(self):
        expeditions = get_pending_expeditions(self.db_conn)
        
        self.expeditions_table.setRowCount(len(expeditions))
        for row, expedition in enumerate(expeditions):
            self.expeditions_table.setItem(row, 0, QTableWidgetItem(str(expedition['idBon'])))
            self.expeditions_table.setItem(row, 1, QTableWidgetItem(expedition['reference']))
            self.expeditions_table.setItem(row, 2, QTableWidgetItem(expedition['dateCreation'].strftime("%d/%m/%Y")))
            self.expeditions_table.setItem(row, 3, QTableWidgetItem(expedition['dateExpeditionPrevue'].strftime("%d/%m/%Y")))
            self.expeditions_table.setItem(row, 4, QTableWidgetItem(expedition['priorite']))
            self.expeditions_table.setItem(row, 5, QTableWidgetItem(expedition['statut']))
        
        self.expeditions_table.resizeColumnsToContents()
    
    def create_expedition(self):
        reference = self.ref_input.text()
        date_prevue = self.date_input.date().toString("yyyy-MM-dd")
        priority = self.priority_input.currentText()
        
        if not reference:
            QMessageBox.warning(self, "Champ manquant", "Veuillez saisir une référence")
            return
        
        try:
            expedition_id = create_expedition(
                self.db_conn,
                reference,
                date_prevue,
                priority,
                self.user['idIndividu']
            )
            QMessageBox.information(self, "Succès", 
                                  f"Bon d'expédition #{expedition_id} créé avec succès")
            self.load_expeditions()
            self.ref_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la création: {str(e)}")
    
    def show_expedition_details(self, index):
        expedition_id = int(self.expeditions_table.item(index.row(), 0).text())
        from views.expedition_detail import ExpeditionDetailWindow
        self.detail_window = ExpeditionDetailWindow(self.db_conn, self.user, expedition_id)
        self.detail_window.show()

    def prepare_colis(self):
        selected_row = self.expeditions_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un bon d'expédition.")
            return

        expedition_id = int(self.expeditions_table.item(selected_row, 0).text())
        try:
            id_produit = self.get_selected_product_id()
            quantite = int(self.quantity_input.text())

            colis_id = handle_preparation_expedition(self.db_conn, expedition_id, id_produit, quantite)
            QMessageBox.information(self, "Succès", f"Colis #{colis_id} préparé.")
            self.load_expeditions()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la préparation : {str(e)}")