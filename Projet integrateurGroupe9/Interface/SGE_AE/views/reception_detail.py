from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from controllers.reception_controller import handle_details_reception, handle_finalize_reception

class ReceptionDetailWindow(QWidget):
    def __init__(self, conn, user, reception_id):
        super().__init__()
        self.conn = conn
        self.user = user
        self.reception_id = reception_id
        self.setWindowTitle(f"Détails du bon de réception #{reception_id}")
        self.resize(800, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel(f"Détails du bon #{self.reception_id}")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.validate_btn = QPushButton("Valider la réception")
        self.validate_btn.clicked.connect(self.validate_reception)
        layout.addWidget(self.validate_btn)

        self.setLayout(layout)
        self.load_details()

    def load_details(self):
        try:
            rows = handle_details_reception(self.conn, self.reception_id)
            if not rows:
                self.table.setRowCount(0)
                self.table.setColumnCount(1)
                self.table.setHorizontalHeaderLabels(["Aucune donnée"])
                return
            headers = list(rows[0].keys())
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(rows))
            for row, data in enumerate(rows):
                for col, val in enumerate(data.values()):
                    self.table.setItem(row, col, QTableWidgetItem(str(val)))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec du chargement: {str(e)}")

    def validate_reception(self):
        try:
            handle_finalize_reception(self.conn, self.reception_id)
            QMessageBox.information(self, "Succès", f"Réception #{self.reception_id} validée")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la validation: {str(e)}")
