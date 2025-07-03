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
        
        # Titre centré, gras, taille plus grande, couleur pro bleu foncé
        title = QLabel("📦 Gestion des Cellules d'Entrepôt")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title)

        # Tableau avec couleurs douces et lignes alternées
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Entrepôt", "Capacité Max", "Qté Totale", "Taux Occupation", "Volume Restant"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #f9fbfc;
                alternate-background-color: #eaf1f7;
                gridline-color: #cfd8dc;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #2980b9;
                color: white;
                padding: 5px;
                font-weight: bold;
                border: none;
            }
        """)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Formulaire stylé avec labels alignés et espacement
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)
        form.setVerticalSpacing(12)

        # Inputs avec bordure douce, padding et focus coloré
        style_inputs = """
            QLineEdit, QSpinBox, QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 6px 8px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #2980b9;
                background-color: #eaf4fc;
            }
        """

        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("ID existant pour modifier")
        self.input_id.setStyleSheet(style_inputs)

        self.input_reference = QLineEdit()
        self.input_reference.setPlaceholderText("Référence unique")
        self.input_reference.setStyleSheet(style_inputs)

        self.input_capacite = QSpinBox()
        self.input_capacite.setRange(1, 1_000_000)
        self.input_capacite.setStyleSheet(style_inputs)

        self.input_volume = QSpinBox()
        self.input_volume.setRange(1, 10_000_000)
        self.input_volume.setStyleSheet(style_inputs)

        self.input_entrepot = QSpinBox()
        self.input_entrepot.setRange(1, 100)
        self.input_entrepot.setStyleSheet(style_inputs)

        self.input_longueur = QSpinBox()
        self.input_longueur.setRange(1, 10000)
        self.input_longueur.setStyleSheet(style_inputs)

        self.input_largeur = QSpinBox()
        self.input_largeur.setRange(1, 10000)
        self.input_largeur.setStyleSheet(style_inputs)

        self.input_hauteur = QSpinBox()
        self.input_hauteur.setRange(1, 10000)
        self.input_hauteur.setStyleSheet(style_inputs)

        self.input_masse_max = QSpinBox()
        self.input_masse_max.setRange(1, 100_000)
        self.input_masse_max.setStyleSheet(style_inputs)

        self.input_statut = QComboBox()
        self.input_statut.addItems(["actif", "inactif"])
        self.input_statut.setStyleSheet(style_inputs)

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

        # Boutons alignés, avec couleurs et hover, spacing
        buttons = QHBoxLayout()
        buttons.setSpacing(20)

        self.btn_add = QPushButton("➕ Ajouter Cellule")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.btn_add.clicked.connect(self.ajouter_cellule)
        buttons.addWidget(self.btn_add)

        self.btn_update = QPushButton("✏️ Modifier Cellule")
        self.btn_update.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        self.btn_update.clicked.connect(self.modifier_cellule)
        buttons.addWidget(self.btn_update)

        layout.addLayout(buttons)

        # Marges autour du widget pour respirer
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

    # ... le reste du code load_data, ajouter_cellule, modifier_cellule, clear_form reste inchangé ...
