from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, 
                            QComboBox, QSpinBox, QDateEdit, QPushButton, QMessageBox,
                            QHBoxLayout)
from PyQt5.QtCore import QDate, pyqtSignal, Qt
from PyQt5.QtGui import QIntValidator
from controllers.reception_controller import handle_receptionner_lot
from models.product_model import get_all_products  # Pour l'autocomplétion

class ReceptionDetailWindow(QWidget):
    reception_completed = pyqtSignal()

    def __init__(self, conn, user, reception_id):
        super().__init__()
        self.conn = conn
        self.user = user
        self.reception_id = reception_id
        self.init_ui()
        self.load_products()  # Chargement des produits pour l'autocomplétion

    def init_ui(self):
        self.setWindowTitle(f"Réception - Bon #{self.reception_id}")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        # Affichage du numéro de réception
        layout.addWidget(QLabel(f"Bon de Réception ID : {self.reception_id}"))
        layout.addWidget(QLabel(""))  # Espacement

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form.setSpacing(15)

        # Champ référence lot
        self.lot_ref = QLineEdit()
        self.lot_ref.setPlaceholderText("Ex: LOT-2023-001")
        form.addRow("Référence du lot*:", self.lot_ref)

        # Champ ID Produit avec autocomplétion
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.NoInsert)
        form.addRow("Produit*:", self.product_combo)

        # Champ quantité
        self.quantite = QSpinBox()
        self.quantite.setRange(1, 100000)
        self.quantite.setValue(1)
        form.addRow("Quantité*:", self.quantite)

        # Dates production et expiration
        self.date_prod = QDateEdit(QDate.currentDate())
        self.date_prod.setCalendarPopup(True)
        form.addRow("Date de production:", self.date_prod)

        self.date_exp = QDateEdit(QDate.currentDate().addYears(1))
        self.date_exp.setCalendarPopup(True)
        form.addRow("Date d'expiration:", self.date_exp)

        # Champ cellule
        self.cellule = QLineEdit()
        self.cellule.setValidator(QIntValidator(1, 100000))
        self.cellule.setPlaceholderText("Numéro de cellule")
        form.addRow("Cellule*:", self.cellule)

        layout.addLayout(form)

        # Boutons Valider/Annuler
        btn_layout = QHBoxLayout()
        validate_btn = QPushButton("Valider la réception")
        validate_btn.clicked.connect(self.receptionner)
        validate_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setStyleSheet("background-color: #f44336; color: white;")
        
        btn_layout.addWidget(validate_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_products(self):
        """Charge la liste des produits pour l'autocomplétion"""
        try:
            products = get_all_products(self.conn)
            for product in products:
                self.product_combo.addItem(
                    f"{product['idProduit']} - {product['reference']} - {product['nom']}",
                    product['idProduit']
                )
        except Exception as e:
            QMessageBox.warning(self, "Chargement produits", 
                              f"Impossible de charger la liste des produits: {str(e)}")

    def validate_form(self):
        """Valide les champs obligatoires"""
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

    def receptionner(self):
        """Traite la réception du lot"""
        if not self.validate_form():
            return
            
        try:
            id_lot = handle_receptionner_lot(
                self.conn,
                self.reception_id,
                self.lot_ref.text().strip(),
                self.product_combo.currentData(),  # ID produit
                self.quantite.value(),
                self.date_prod.date().toPyDate(),
                self.date_exp.date().toPyDate(),
                int(self.cellule.text())
            )
            
            QMessageBox.information(
                self, 
                "Succès", 
                f"Réception enregistrée avec succès.\nID Lot: {id_lot}"
            )
            self.reception_completed.emit()
            self.close()
            
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de saisie", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erreur", 
                f"Une erreur est survenue lors de la réception:\n{str(e)}"
            )