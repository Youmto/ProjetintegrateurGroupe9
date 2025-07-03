from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton
)
from models.approvisionnement_model import charger_demandes_approvisionnement
from PyQt5.QtCore import Qt


class ApprovisionnementListeWindow(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setWindowTitle("📋 Demandes d'approvisionnement")
        self.resize(820, 420)

        self.layout = QVBoxLayout(self)

        # Titre clair avec emoji
        self.label = QLabel("📌 Liste des demandes d’approvisionnement")
        self.label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        self.layout.addWidget(self.label)

        # Table stylisée
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Bouton rafraîchir stylé
        self.bouton_rafraichir = QPushButton("🔄 Rafraîchir")
        self.bouton_rafraichir.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.bouton_rafraichir.clicked.connect(self.charger_table)
        self.layout.addWidget(self.bouton_rafraichir)

        self.charger_table()

        # Style global pour la table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #f9f9f9;
                alternate-background-color: #e8f5e9;
                font-size: 13px;
                gridline-color: #d0d7d9;
            }
            QHeaderView::section {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        self.table.setAlternatingRowColors(True)

    def charger_table(self):
        demandes = charger_demandes_approvisionnement(self.conn)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID Organisation", "ID Produit", "Quantité", "Date prévue", "Date enregistrement"
        ])
        self.table.setRowCount(len(demandes))

        for row, demande in enumerate(demandes):
            for col, value in enumerate(demande):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

        # Colonnes ajustées, nom colonne 1 en stretch pour lisibilité
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
