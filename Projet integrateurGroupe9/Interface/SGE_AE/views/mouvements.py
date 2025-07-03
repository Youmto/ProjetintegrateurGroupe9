from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDateEdit,
    QFormLayout, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from datetime import datetime, date
import logging
import csv

from controllers.movement_controller import handle_mouvements_produit
from models.product_model import get_all_products



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

        # 🔷 Titre
        title = QLabel("📦 Suivi des mouvements de stock")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        # 🔎 Filtres
        filter_group = QWidget()
        filter_layout = QFormLayout()

        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(300)
        self.product_combo.setPlaceholderText("Sélectionnez un produit")
        filter_layout.addRow("Produit :", self.product_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Tous", "Réception", "Expédition", "Déplacement", "Ajustement"])
        filter_layout.addRow("Type de mouvement :", self.type_combo)

        date_layout = QHBoxLayout()
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)

        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)

        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("au"))
        date_layout.addWidget(self.date_to)

        filter_layout.addRow("Période :", date_layout)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # 🧭 Boutons
        btn_layout = QHBoxLayout()

        self.btn = QPushButton("Afficher les mouvements")
        self.btn.clicked.connect(self.load_movements)
        self.btn.setStyleSheet(self._button_style("#3498db", "#2980b9"))
        btn_layout.addWidget(self.btn)

        self.export_btn = QPushButton("Exporter CSV")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_to_csv)
        self.export_btn.setStyleSheet(self._button_style("#2ecc71", "#27ae60"))
        btn_layout.addWidget(self.export_btn)

        layout.addLayout(btn_layout)

        # 📊 Table des résultats
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
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def _button_style(self, color, hover_color) -> str:
        return f"""
            QPushButton {{
                padding: 5px 15px;
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    def load_products(self):
        try:
            logger.info("📦 Chargement des produits disponibles...")
            self.products = get_all_products(self.conn)
            self.product_combo.clear()

            if not self.products:
                logger.warning("🚫 Aucun produit trouvé.")
                QMessageBox.information(self, "Information", "Aucun produit disponible.")
                return

            for product in self.products:
                label = f"{product.get('reference', '')} - {product.get('nom', '')}"
                self.product_combo.addItem(label, product.get('idProduit'))

            logger.info(f"✅ {len(self.products)} produits chargés.")

        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des produits : {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", "Échec du chargement des produits.")

    def load_movements(self):
        try:
            index = self.product_combo.currentIndex()
            if index == -1:
                QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un produit.")
                return

            product_id = self.product_combo.itemData(index)
            if not product_id:
                raise ValueError("ID produit invalide.")

            self.btn.setEnabled(False)
            self.btn.setText("Chargement...")

            mvt_type = self.type_combo.currentText()
            mvt_type = None if mvt_type == "Tous" else mvt_type

            date_from = self.date_from.date().toPyDate()
            date_to = self.date_to.date().toPyDate()

            mouvements = handle_mouvements_produit(
                self.conn, product_id, date_from, date_to, mvt_type
            )
            self.display_results(mouvements)

        except Exception as e:
            logger.error(f"❌ Erreur chargement mouvements : {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n{str(e)}")

        finally:
            self.btn.setEnabled(True)
            self.btn.setText("Afficher les mouvements")

    def display_results(self, mouvements):
        self.table.setRowCount(0)
        self.export_btn.setEnabled(False)

        if not mouvements:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Aucun mouvement trouvé."))
            self.table.setSpan(0, 0, 1, self.table.columnCount())
            return

        self.table.setRowCount(len(mouvements))
        self.export_btn.setEnabled(True)

        color_map = {
            "Réception": "#d4edda",
            "Expédition": "#f8d7da",
            "Ajustement": "#fff3cd",
            "Déplacement": "#e2e3e5"
        }

        for row, mouvement in enumerate(mouvements):
            raw_date = mouvement.get("date", "")
            date_str = raw_date.strftime("%d/%m/%Y") if isinstance(raw_date, (datetime, date)) else str(raw_date)

            items = [
                QTableWidgetItem(str(mouvement.get("type", ""))),
                QTableWidgetItem(str(mouvement.get("reference_bon", ""))),
                QTableWidgetItem(date_str),
                QTableWidgetItem(str(mouvement.get("quantite", ""))),
                QTableWidgetItem(str(mouvement.get("lot", ""))),
                QTableWidgetItem(str(mouvement.get("cellule", ""))),
                QTableWidgetItem(str(mouvement.get("description", "")))
            ]

            for col, item in enumerate(items):
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                if col == 0:
                    bg_color = color_map.get(items[0].text(), "#ffffff")
                    item.setBackground(QColor(bg_color))
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

    def export_to_csv(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter en CSV", f"mouvements_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "Fichiers CSV (*.csv)"
            )
            if not filename:
                return

            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')

                # En-têtes
                headers = [
                    self.table.horizontalHeaderItem(i).text()
                    for i in range(self.table.columnCount())
                ]
                writer.writerow(headers)

                # Lignes
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(self, "Export réussi", "Le fichier CSV a été enregistré avec succès.")
            logger.info(f"✅ Données exportées vers : {filename}")

        except Exception as e:
            logger.error(f"❌ Échec export CSV : {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Échec de l'export :\n{str(e)}")
