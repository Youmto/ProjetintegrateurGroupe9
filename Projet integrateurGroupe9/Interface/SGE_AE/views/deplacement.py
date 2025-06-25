from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QMessageBox, QFormLayout
from controllers.deplacement_controller import handle_deplacement

class DeplacementModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.lot_input = QLineEdit()
        self.src_cellule_input = QLineEdit()
        self.dest_cellule_input = QLineEdit()
        self.quantite_input = QSpinBox()
        self.quantite_input.setRange(1, 100000)

        layout.addRow("ID Lot :", self.lot_input)
        layout.addRow("Cellule source :", self.src_cellule_input)
        layout.addRow("Cellule destination :", self.dest_cellule_input)
        layout.addRow("Quantité :", self.quantite_input)

        self.btn = QPushButton("Déplacer")
        self.btn.clicked.connect(self.effectuer_deplacement)
        layout.addRow(self.btn)

        self.setLayout(layout)

    def effectuer_deplacement(self):
        try:
            id_lot = int(self.lot_input.text())
            cellule_src = int(self.src_cellule_input.text())
            cellule_dest = int(self.dest_cellule_input.text())
            quantite = self.quantite_input.value()
            responsable_id = self.user['idIndividu']

            success = handle_deplacement(self.conn, id_lot, cellule_src, cellule_dest, quantite, responsable_id)
            if success:
                QMessageBox.information(self, "Succès", "Déplacement effectué avec succès.")
            else:
                QMessageBox.warning(self, "Avertissement", "Le déplacement a échoué.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du déplacement : {str(e)}")
