from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView
)
from PyQt5.QtCore import Qt
from controllers.movement_controller import handle_mouvements_produit
from models.product_model import get_all_products
import logging

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

        # Sélection produit
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(300)
        self.product_combo.setPlaceholderText("Sélectionnez un produit")
        control_layout.addWidget(self.product_combo)

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
        control_layout.addWidget(self.btn)

        layout.addLayout(control_layout)

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
                self.product_combo.addItem(label, product.get('idproduit'))

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

            mouvements = handle_mouvements_produit(self.conn, product_id)
            self.display_results(mouvements)

        except Exception as e:
            logger.error(f"Erreur chargement mouvements: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n{str(e)}")
        finally:
            self.btn.setEnabled(True)
            self.btn.setText("Afficher les mouvements")

    def display_results(self, mouvements):
        self.table.setRowCount(0)

        if not mouvements:
            QMessageBox.information(self, "Aucun résultat", "Aucun mouvement trouvé pour ce produit.")
            return

        self.table.setRowCount(len(mouvements))

        for row, mouvement in enumerate(mouvements):
            date = mouvement.get("date", "")
            type_mvt = mouvement.get("type", "")
            qte = mouvement.get("quantite", "")
            lot = mouvement.get("lot", "")
            cellule = mouvement.get("cellule", "")
            desc = mouvement.get("description", "")

            items = [
                QTableWidgetItem(str(type_mvt)),
                QTableWidgetItem(str(mouvement.get("reference", ""))),
                QTableWidgetItem(str(date)),
                QTableWidgetItem(str(qte)),
                QTableWidgetItem(str(lot)),
                QTableWidgetItem(str(cellule)),
                QTableWidgetItem(str(desc))
            ]

            for col, item in enumerate(items):
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()