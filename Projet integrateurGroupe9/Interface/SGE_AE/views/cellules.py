from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QSpinBox,
    QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from models.stock_model import (
    get_cellules_info, add_cellule, update_cellule,
    get_entrepot_capacite_restante
)

class CellulesModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Gestion des Cellules d'Entrepôt")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Entrepôt", "Capacité Max", "Qté Totale", "Taux Occupation", "Volume Restant"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        form = QFormLayout()
        self.input_id = QLineEdit()
        self.input_reference = QLineEdit()
        self.input_capacite = QSpinBox(); self.input_capacite.setRange(1, 1_000_000)
        self.input_volume = QSpinBox(); self.input_volume.setRange(1, 10_000_000)
        self.input_entrepot = QSpinBox(); self.input_entrepot.setRange(1, 100)
        self.input_longueur = QSpinBox(); self.input_longueur.setRange(1, 10000)
        self.input_largeur = QSpinBox(); self.input_largeur.setRange(1, 10000)
        self.input_hauteur = QSpinBox(); self.input_hauteur.setRange(1, 10000)
        self.input_masse_max = QSpinBox(); self.input_masse_max.setRange(1, 100_000)
        self.input_statut = QComboBox(); self.input_statut.addItems(["actif", "inactif"])

        form.addRow("ID Cellule (modif)", self.input_id)
        form.addRow("Référence", self.input_reference)
        form.addRow("Capacité Max", self.input_capacite)
        form.addRow("Volume Max", self.input_volume)
        form.addRow("ID Entrepôt", self.input_entrepot)
        form.addRow("Longueur (cm)", self.input_longueur)
        form.addRow("Largeur (cm)", self.input_largeur)
        form.addRow("Hauteur (cm)", self.input_hauteur)
        form.addRow("Masse Max (kg)", self.input_masse_max)
        form.addRow("Statut", self.input_statut)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter Cellule")
        self.btn_add.clicked.connect(self.ajouter_cellule)
        buttons.addWidget(self.btn_add)

        self.btn_update = QPushButton("Modifier Cellule")
        self.btn_update.clicked.connect(self.modifier_cellule)
        buttons.addWidget(self.btn_update)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def load_data(self):
        try:
            cellules = get_cellules_info(self.conn)
            self.table.setRowCount(len(cellules))

            for row, c in enumerate(cellules):
                for col, val in enumerate([
                    c['idCellule'], c['reference'], c['nom_entrepot'],
                    c['capacite_max'], c['quantite_totale'],
                    f"{c['taux_occupation']}%", c['volume_restant']
                ]):
                    item = QTableWidgetItem(str(val))
                    if c['quantite_totale'] > c['capacite_max']:
                        item.setBackground(Qt.red)
                    self.table.setItem(row, col, item)

            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement cellules :\n{e}")

    def ajouter_cellule(self):
        try:
            ref = self.input_reference.text().strip()
            cap, vol, entrepot_id = self.input_capacite.value(), self.input_volume.value(), self.input_entrepot.value()
            l, L, h, masse = self.input_longueur.value(), self.input_largeur.value(), self.input_hauteur.value(), self.input_masse_max.value()
            position = f"Auto-{ref}"

            if not ref:
                raise ValueError("Référence obligatoire.")

            restant = get_entrepot_capacite_restante(self.conn, entrepot_id)
            if restant is not None and cap > restant:
                QMessageBox.warning(self, "Capacité dépassée",
                    f"Entrepôt {entrepot_id} : seulement {restant} unités restantes.")
                return

            add_cellule(self.conn, ref, l, L, h, masse, vol, cap, position, entrepot_id)
            QMessageBox.information(self, "Succès", f"Cellule {ref} ajoutée.")
            self.load_data()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Ajout échoué :\n{e}")

    def modifier_cellule(self):
        try:
            cell_id = int(self.input_id.text())
            l, L, h = self.input_longueur.value(), self.input_largeur.value(), self.input_hauteur.value()
            masse, volume, cap = self.input_masse_max.value(), self.input_volume.value(), self.input_capacite.value()
            statut = self.input_statut.currentText()

            update_cellule(self.conn, cell_id, l, L, h, masse, volume, cap, statut)
            QMessageBox.information(self, "Mise à jour", f"Cellule #{cell_id} modifiée.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Mise à jour échouée :\n{e}")

    def clear_form(self):
        self.input_reference.clear()
        self.input_capacite.setValue(1)
        self.input_volume.setValue(1)
        self.input_entrepot.setValue(1)
        self.input_longueur.setValue(1)
        self.input_largeur.setValue(1)
        self.input_hauteur.setValue(1)
        self.input_masse_max.setValue(1)
        self.input_id.clear()
        self.input_statut.setCurrentIndex(0)