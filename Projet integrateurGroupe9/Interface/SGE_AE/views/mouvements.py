from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox
from controllers.movement_controller import handle_mouvements_produit

class MouvementsModule(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("ID du produit")
        layout.addWidget(QLabel("Suivi des mouvements de stock par produit"))
        layout.addWidget(self.input_id)

        self.btn = QPushButton("Afficher")
        self.btn.clicked.connect(self.load)
        layout.addWidget(self.btn)

        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load(self):
        try:
            pid = int(self.input_id.text())
            rows = handle_mouvements_produit(self.conn, pid)
            self.table.clear()
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Type", "Référence Bon", "Date", "Quantité"])
            self.table.setRowCount(len(rows))
            for row, d in enumerate(rows):
                for col, val in enumerate(d.values()):
                    self.table.setItem(row, col, QTableWidgetItem(str(val)))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))