from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QLabel, QLineEdit,
    QComboBox, QFormLayout, QDialogButtonBox, QSpinBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from models import lot_model



class LotDetailWindow(QMainWindow):
    def __init__(self, conn, user=None):
        super().__init__()
        self.conn = conn
        self.user = user
        self.id_lot = None

        self.setWindowTitle("📦 Détails des lots")
        self.resize(900, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.lot_selector = QComboBox()
        self.lot_selector.currentIndexChanged.connect(self.on_lot_selected)
        self.lot_selector.setStyleSheet("font-weight: bold; font-size: 14px; color: #2874A6;")
        self.layout.addWidget(QLabel("🔍 Sélectionnez un lot"))
        self.layout.addWidget(self.lot_selector)

        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #F0F8FF;
                gridline-color: #AED6F1;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #2980B9;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
        """)
        self.layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_modifier = QPushButton("✏️ Modifier")
        self.btn_modifier.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white; font-weight: bold;
                padding: 8px; border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.btn_supprimer = QPushButton("🗑️ Supprimer")
        self.btn_supprimer.setStyleSheet("""
            QPushButton {
                background-color: #C0392B; color: white; font-weight: bold;
                padding: 8px; border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #922B21;
            }
        """)
        btn_layout.addWidget(self.btn_modifier)
        btn_layout.addWidget(self.btn_supprimer)
        self.layout.addLayout(btn_layout)

        self.btn_modifier.clicked.connect(self.modifier_produit)
        self.btn_supprimer.clicked.connect(self.supprimer_produit)

        self.charger_lots()

    def charger_lots(self):
        lots = lot_model.get_all_lots(self.conn)
        self.lot_selector.clear()
        self.lots_map = {}
        for index, (id_lot, numero) in enumerate(lots):
            self.lot_selector.addItem(f"📦 {numero} (ID {id_lot})")
            self.lots_map[index] = id_lot
        if lots:
            self.id_lot = lots[0][0]
            self.charger_produits()

    def on_lot_selected(self, index):
        self.id_lot = self.lots_map.get(index)
        self.charger_produits()

    def charger_produits(self):
        if not self.id_lot:
            return
        self.table.clear()
        produits = lot_model.get_produits_par_lot(self.conn, self.id_lot)

        headers = ["Colis", "Produit", "Nom", "Type", "Quantité", "Version", "Licence", "Expiration",
                   "Longueur", "Largeur", "Hauteur", "Masse", "Volume"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(produits))

        for row, prod in enumerate(produits):
            for col, val in enumerate(prod):
                item = QTableWidgetItem(str(val) if val is not None else "")
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

    def get_selection(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "⚠️ Sélection requise", "Veuillez sélectionner un produit.")
            return None
        id_colis = self.table.item(row, 0).text()
        id_produit = self.table.item(row, 1).text()
        type_produit = self.table.item(row, 3).text()
        return id_colis, id_produit, type_produit

    def modifier_produit(self):
        sel = self.get_selection()
        if not sel:
            return
        id_colis, id_produit, type_produit = sel

        dlg = ProduitEditDialog(self.conn, id_colis, id_produit, type_produit, parent=self)
        if dlg.exec_():
            QMessageBox.information(self, "✔️ Modifié", "Le produit a été mis à jour avec succès.")
            self.charger_produits()

    def supprimer_produit(self):
        sel = self.get_selection()
        if not sel:
            return
        id_colis, id_produit, _ = sel

        confirm = QMessageBox.question(
            self, "❌ Confirmation",
            f"Supprimer le produit {id_produit} du colis {id_colis} ?"
        )
        if confirm == QMessageBox.Yes:
            lot_model.supprimer_produit_dans_colis(self.conn, id_colis, id_produit)
            QMessageBox.information(self, "🗑️ Supprimé", "Produit supprimé avec succès.")
            self.charger_produits()


class ProduitEditDialog(QDialog):
    def __init__(self, conn, id_colis, id_produit, type_produit, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.id_colis = id_colis
        self.id_produit = id_produit
        self.type_produit = type_produit

        self.setWindowTitle("✏️ Modifier Produit")
        self.resize(400, 300)
        layout = QFormLayout(self)

        self.quantite = QSpinBox()
        self.quantite.setMinimum(1)
        layout.addRow("Quantité:", self.quantite)

        if self.type_produit == 'logiciel':
            self.version = QLineEdit()
            self.licence = QLineEdit()
            self.date_exp = QDateEdit()
            self.date_exp.setCalendarPopup(True)
            self.date_exp.setDate(QDate.currentDate())

            layout.addRow("Version:", self.version)
            layout.addRow("Type Licence:", self.licence)
            layout.addRow("Date Expiration:", self.date_exp)

        elif self.type_produit == 'materiel':
            self.longueur = QLineEdit()
            self.largeur = QLineEdit()
            self.hauteur = QLineEdit()
            self.masse = QLineEdit()
            self.volume = QLineEdit()

            layout.addRow("Longueur:", self.longueur)
            layout.addRow("Largeur:", self.largeur)
            layout.addRow("Hauteur:", self.hauteur)
            layout.addRow("Masse:", self.masse)
            layout.addRow("Volume:", self.volume)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.submit)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        # Style général du dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #E8F6F3;
                font-size: 13px;
            }
            QLabel {
                color: #21618C;
                font-weight: bold;
            }
            QLineEdit, QSpinBox, QDateEdit {
                background-color: white;
                border: 1px solid #A9CCE3;
                border-radius: 4px;
                padding: 4px;
            }
        """)

    def submit(self):
        if self.type_produit == 'logiciel':
            lot_model.modifier_produit_dans_colis(
                self.conn, self.id_colis, self.id_produit, self.quantite.value(),
                version=self.version.text(),
                type_licence=self.licence.text(),
                date_expiration=self.date_exp.date().toString("yyyy-MM-dd")
            )
        elif self.type_produit == 'materiel':
            lot_model.modifier_produit_dans_colis(
                self.conn, self.id_colis, self.id_produit, self.quantite.value(),
                longueur=self.longueur.text(),
                largeur=self.largeur.text(),
                hauteur=self.hauteur.text(),
                masse=self.masse.text(),
                volume=self.volume.text()
            )
        self.accept()
