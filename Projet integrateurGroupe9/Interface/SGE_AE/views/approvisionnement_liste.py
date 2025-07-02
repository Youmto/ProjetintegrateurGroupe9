# views/approvisionnement_liste.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from models.approvisionnement_model import charger_demandes_approvisionnement
from PyQt5.QtCore import Qt

class ApprovisionnementListeWindow(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setWindowTitle("Demandes d'approvisionnement")
        self.resize(800, 400)

        self.layout = QVBoxLayout(self)
        self.label = QLabel("Liste des demandes d’approvisionnement")
        self.layout.addWidget(self.label)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.bouton_rafraichir = QPushButton("Rafraîchir")
        self.bouton_rafraichir.clicked.connect(self.charger_table)
        self.layout.addWidget(self.bouton_rafraichir)

        self.charger_table()

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

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
