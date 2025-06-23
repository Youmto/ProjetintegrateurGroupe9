from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from controllers.supervision_controller import (
    handle_occupation_cellules, handle_ruptures,
    handle_produits_non_stockes, handle_cellules_vides
)

class SupervisionModule(QWidget):
    def __init__(self, conn,user):
        self.user = user
        super().__init__()
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.select = QComboBox()
        self.select.addItems([
            "Occupation des cellules",
            "Produits jamais stockés",
            "Ruptures de stock",
            "Cellules vides"
        ])
        layout.addWidget(QLabel("Sélection du rapport de supervision"))
        layout.addWidget(self.select)

        btn = QPushButton("Afficher")
        btn.clicked.connect(self.load_data)
        layout.addWidget(btn)

        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        try:
            option = self.select.currentText()
            if option == "Occupation des cellules":
                data = handle_occupation_cellules(self.conn)
                headers = ["ID", "Référence", "Entrepôt", "Utilisé", "Max", "%"]
            elif option == "Produits jamais stockés":
                data = handle_produits_non_stockes(self.conn)
                headers = ["ID", "Référence", "Nom"]
            elif option == "Ruptures de stock":
                data = handle_ruptures(self.conn)
                headers = ["ID", "Référence", "Nom", "Quantité"]
            elif option == "Cellules vides":
                data = handle_cellules_vides(self.conn)
                headers = ["ID", "Référence", "Entrepôt", "Volume"]
            else:
                return

            self.table.clear()
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(data))
            for row, item in enumerate(data):
                for col, value in enumerate(item.values()):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))