from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDateEdit, QPushButton, QMessageBox,
    QHBoxLayout
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator
from controllers.reception_controller import handle_receptionner_lot
from models.product_model import get_all_products




class ReceptionDetailWindow(QWidget):
    """
    Fenêtre de saisie pour réceptionner un lot.
    """
    reception_completed = pyqtSignal()

    def __init__(self, conn, user, reception_id):
        super().__init__()
        self.conn = conn
        self.user = user
        self.reception_id = reception_id

        self._setup_ui()
        self._load_products()

    def _setup_ui(self):
        """Initialise l’interface utilisateur."""
        self.setWindowTitle(f"Réception - Bon #{self.reception_id}")
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout()

        main_layout.addWidget(QLabel(f"Bon de Réception ID : {self.reception_id}"))
        main_layout.addSpacing(10)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setSpacing(15)

        # Référence du lot
        self.lot_ref = QLineEdit()
        self.lot_ref.setPlaceholderText("Ex: LOT-2023-001")
        form_layout.addRow("Référence du lot*:", self.lot_ref)

        # Produit (combo editable)
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.NoInsert)
        form_layout.addRow("Produit*:", self.product_combo)

        # Quantité
        self.quantite = QSpinBox()
        self.quantite.setRange(1, 100000)
        self.quantite.setValue(1)
        form_layout.addRow("Quantité*:", self.quantite)

        # Date production
        self.date_prod = QDateEdit(QDate.currentDate())
        self.date_prod.setCalendarPopup(True)
        form_layout.addRow("Date de production:", self.date_prod)

        # Date expiration
        self.date_exp = QDateEdit(QDate.currentDate().addYears(1))
        self.date_exp.setCalendarPopup(True)
        form_layout.addRow("Date d'expiration:", self.date_exp)

        # Cellule
        self.cellule = QLineEdit()
        self.cellule.setValidator(QIntValidator(1, 100000))
        self.cellule.setPlaceholderText("Numéro de cellule")
        form_layout.addRow("Cellule*:", self.cellule)

        main_layout.addLayout(form_layout)

        # Boutons Valider / Annuler
        btn_layout = QHBoxLayout()
        btn_valider = QPushButton("Valider la réception")
        btn_valider.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_valider.clicked.connect(self._receptionner)

        btn_annuler = QPushButton("Annuler")
        btn_annuler.setStyleSheet("background-color: #f44336; color: white;")
        btn_annuler.clicked.connect(self.close)

        btn_layout.addWidget(btn_valider)
        btn_layout.addWidget(btn_annuler)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def _load_products(self):
        """Charge la liste des produits pour la combo."""
        try:
            products = get_all_products(self.conn)
            for prod in products:
                display = f"{prod['idProduit']} - {prod['reference']} - {prod['nom']}"
                self.product_combo.addItem(display, prod['idProduit'])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Chargement produits",
                f"Impossible de charger les produits:\n{e}"
            )

    def _validate_form(self):
        """Vérifie que les champs obligatoires sont remplis."""
        if not self.lot_ref.text().strip():
            QMessageBox.warning(self, "Champ requis", "Veuillez entrer la référence du lot.")
            return False
        if not self.product_combo.currentData():
            QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un produit valide.")
            return False
        if not self.cellule.text().strip():
            QMessageBox.warning(self, "Champ requis", "Veuillez entrer un numéro de cellule.")
            return False
        return True

    def _receptionner(self):
        """Valide et enregistre la réception du lot."""
        if not self._validate_form():
            return
        try:
            id_lot = handle_receptionner_lot(
                self.conn,
                self.reception_id,
                self.lot_ref.text().strip(),
                self.product_combo.currentData(),
                self.quantite.value(),
                self.date_prod.date().toPyDate(),
                self.date_exp.date().toPyDate(),
                int(self.cellule.text())
            )
            QMessageBox.information(
                self,
                "Succès",
                f"Réception enregistrée avec succès.\nID Lot : {id_lot}"
            )
            self.reception_completed.emit()
            self.close()

        except ValueError as ve:
            QMessageBox.warning(self, "Erreur de saisie", str(ve))

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la réception :\n{e}"
            )


class SupervisionModule(QWidget):
    def __init__(self,):
        super().__init__()
        # ... ton code ...
