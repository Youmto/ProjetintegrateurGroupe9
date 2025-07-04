from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from datetime import datetime
from controllers.expedition_controller import handle_colis_en_cours, handle_confirmer_livraison 
from models.expedition_model import get_pending_expeditions

class LivreurConfirmationWindow(QWidget):
    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.setWindowTitle("Confirmation de Livraison")
        self.setMinimumSize(800, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("Colis en cours de livraison")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID Colis", "Référence", "Date création", "Bon d'expédition", "Statut"
        ])
        
        # Configuration améliorée du tableau
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        self.confirm_btn = QPushButton("Confirmer la livraison")
        self.confirm_btn.clicked.connect(self.confirmer_livraison)
        buttons.addWidget(self.confirm_btn)

        self.refresh_btn = QPushButton("Rafraîchir")
        self.refresh_btn.clicked.connect(self.charger_colis)
        buttons.addWidget(self.refresh_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)
        self.charger_colis()

    def charger_colis(self):
        try:
            colis = handle_colis_en_cours(self.db_conn)

            if not colis:
                QMessageBox.information(self, "Aucun colis", "Aucun colis en cours à livrer.")
                self.title.setText("Colis en cours de livraison (0)")
                self.table.setRowCount(0)
                return
                
            self.table.setRowCount(len(colis))
            for row, c in enumerate(colis):
                self.table.setItem(row, 0, QTableWidgetItem(str(c['idColis'])))
                self.table.setItem(row, 1, QTableWidgetItem(c['reference']))
                
                # Gestion robuste de la date
                date = c['date_creation']
                if isinstance(date, str):
                    date = datetime.fromisoformat(date)
                self.table.setItem(row, 2, QTableWidgetItem(date.strftime("%d/%m/%Y")))
                
                self.table.setItem(row, 3, QTableWidgetItem(c['bon_expedition']))
                self.table.setItem(row, 4, QTableWidgetItem(c['statut']))
            
            self.table.resizeColumnsToContents()
            self.title.setText(f"Colis en cours de livraison ({len(colis)})")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement échoué : {str(e)}")

    def confirmer_livraison(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un colis.")
            return
            
        try:
            # Correction du problème logique : on utilise maintenant la référence du bon
            bon_ref = self.table.item(selected_row, 3).text()
            colis_id = int(self.table.item(selected_row, 0).text())
            
            # Recherche du bon correspondant
            bons = get_pending_expeditions(self.db_conn)
            bon_trouve = None
            
            for bon in bons:
                if bon['reference'] == bon_ref:
                    bon_trouve = bon
                    break
                    
            if not bon_trouve:
                raise ValueError("Bon d'expédition non trouvé")
                
            handle_confirmer_livraison(self.db_conn, bon_trouve['idBon'])
            QMessageBox.information(self, "Succès", "Colis marqué comme livré.")
            self.charger_colis()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de confirmation : {str(e)}")