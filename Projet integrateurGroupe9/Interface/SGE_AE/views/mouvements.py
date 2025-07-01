from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QDateEdit, QFormLayout
)
from PyQt5.QtCore import Qt, QDate
from controllers.movement_controller import handle_mouvements_produit
from models.product_model import get_all_products
import logging
import csv
from PyQt5.QtWidgets import QFileDialog
from datetime import datetime, date
from PyQt5.QtGui import QColor


logger = logging.getLogger(__name__)

class MouvementsModule(QWidget):
    def __init__(self, conn, user=None):
        super().__init__()
        self.conn = conn
        self.user = user
        self.products = []
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Titre
        title = QLabel("Suivi des mouvements de stock par produit")
        title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            margin-bottom: 15px;
            color: #2c3e50;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Filtres
        filter_group = QWidget()
        filter_layout = QFormLayout()
        
        # Sélection produit avec recherche
        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(300)
        self.product_combo.setPlaceholderText("Sélectionnez un produit")
        filter_layout.addRow("Produit:", self.product_combo)
        
        # Filtre type de mouvement
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Tous", "Réception", "Expédition", "Déplacement", "Ajustement"])
        filter_layout.addRow("Type mouvement:", self.type_combo)
        
        # Filtres date
        date_layout = QHBoxLayout()
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        date_layout.addWidget(self.date_from)
        
        date_layout.addWidget(QLabel("au"))
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        date_layout.addWidget(self.date_to)
        
        filter_layout.addRow("Période:", date_layout)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Boutons
        btn_layout = QHBoxLayout()
        
        self.btn = QPushButton("Afficher les mouvements")
        self.btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn.clicked.connect(self.load_movements)
        btn_layout.addWidget(self.btn)
        
        self.export_btn = QPushButton("Exporter CSV")
        self.export_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.export_btn.clicked.connect(self.export_to_csv)
        self.export_btn.setEnabled(False)
        btn_layout.addWidget(self.export_btn)
        
        layout.addLayout(btn_layout)

        # Table des mouvements
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Type", "Référence Bon", "Date", "Quantité", "Lot", "Cellule", "Description"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_products(self):
        try:
            self.products = get_all_products(self.conn)
            self.product_combo.clear()

            if not self.products:
                logger.warning("Aucun produit trouvé")
                QMessageBox.information(self, "Information", "Aucun produit disponible.")
                return

            for product in self.products:
                label = f"{product.get('reference', '')} - {product.get('nom', '')}"
                self.product_combo.addItem(label, product.get('idProduit'))  # Correction de la casse

        except Exception as e:
            logger.error(f"Erreur chargement produits: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self, "Erreur",
                "Échec du chargement des produits.\nVérifiez votre connexion ou contactez un administrateur."
            )

    def load_movements(self):
        try:
            index = self.product_combo.currentIndex()
            if index == -1:
                QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un produit.")
                return

            product_id = self.product_combo.itemData(index)
            if not product_id:
                raise ValueError("ID produit invalide")

            self.btn.setEnabled(False)
            self.btn.setText("Chargement...")

            # ✅ Conversion correcte des dates
            date_from = self.date_from.date().toPyDate()
            date_to = self.date_to.date().toPyDate()

            # ✅ Récupération du type de mouvement
            mvt_type = self.type_combo.currentText()
            if mvt_type == "Tous":
                mvt_type = None  # Ne pas filtrer

            # ✅ Appel au contrôleur avec bons arguments
            mouvements = handle_mouvements_produit(
                self.conn,
                product_id,
                date_from,
                date_to,
                mvt_type
            )

            self.display_results(mouvements)

        except Exception as e:
            logger.error(f"Erreur chargement mouvements: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n{str(e)}")
        finally:
            self.btn.setEnabled(True)
            self.btn.setText("Afficher les mouvements")

    def display_results(self, mouvements):
        self.table.setRowCount(0)
        self.export_btn.setEnabled(False)

        if not mouvements:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Aucun mouvement trouvé"))
            self.table.setSpan(0, 0, 1, self.table.columnCount())
            return

        self.table.setRowCount(len(mouvements))
        self.export_btn.setEnabled(True)

        for row, mouvement in enumerate(mouvements):
            raw_date = mouvement.get("date", "")
            type_mvt = mouvement.get("type", "")
            qte = mouvement.get("quantite", "")
            lot = mouvement.get("lot", "")
            cellule = mouvement.get("cellule", "")
            desc = mouvement.get("description", "")
            ref_bon = mouvement.get("reference_bon", "")

            # Formatage de la date
            if isinstance(raw_date, (datetime, date)):
                date_str = raw_date.strftime("%d/%m/%Y")
            else:
                date_str = str(raw_date)

            items = [
                QTableWidgetItem(str(type_mvt)),
                QTableWidgetItem(str(ref_bon)),
                QTableWidgetItem(date_str),
                QTableWidgetItem(str(qte)),
                QTableWidgetItem(str(lot)),
                QTableWidgetItem(str(cellule)),
                QTableWidgetItem(str(desc))
            ]

            # Colorisation selon le type
            if type_mvt == "Réception":
                color = "#d4edda"
            elif type_mvt == "Expédition":
                color = "#f8d7da"
            elif type_mvt == "Ajustement":
                color = "#fff3cd"
            else:
                color = "#e2e3e5"

            for col, item in enumerate(items):
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setBackground(Qt.white if row % 2 == 0 else Qt.lightGray)
                if col == 0:
                    item.setBackground(QColor(color))
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

    def export_to_csv(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter en CSV", "", "Fichiers CSV (*.csv)")
            
            if not filename:
                return

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # En-têtes
                headers = []
                for col in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Données
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
                    
            QMessageBox.information(self, "Export réussi", 
                                   "Les données ont été exportées avec succès.")
                                   
        except Exception as e:
            logger.error(f"Erreur export CSV: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Échec de l'export :\n{str(e)}")