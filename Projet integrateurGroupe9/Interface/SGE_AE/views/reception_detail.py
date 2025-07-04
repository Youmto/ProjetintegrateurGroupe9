from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDateEdit, QPushButton, QMessageBox,
    QHBoxLayout, QGraphicsDropShadowEffect, QFrame # Ajout de QGraphicsDropShadowEffect, QFrame
)
from PyQt5.QtCore import QDate, pyqtSignal, Qt
from PyQt5.QtGui import QIntValidator, QColor, QFont # Ajout de QColor, QFont
from controllers.reception_controller import handle_receptionner_lot
from models.product_model import get_all_products

# Supposons que ModernCard est définie globalement ou importée
# Pour cet exemple, je la redéfinis ici pour la clarté.
class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(15, 15, 15, 15)
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

# Fin de la définition de ModernCard pour l'exemple. Dans une application réelle, importez-la.


class ReceptionDetailWindow(QWidget):
    """
    Fenêtre de saisie pour réceptionner un lot.
    Interface utilisateur modernisée.
    """
    reception_completed = pyqtSignal()
    # Ajout d'un signal 'closed' pour rafraîchir la liste principale
    closed = pyqtSignal() 

    def __init__(self, conn, user, reception_id):
        super().__init__()
        self.conn = conn
        self.user = user
        self.reception_id = reception_id
        self._init_ui()
        self._apply_modern_theme() # Appliquer le thème moderne
        self._load_products()
        # Optionnel: Si vous voulez pouvoir changer le bon de réception sans fermer la fenêtre
        self.load_reception_data(reception_id)

    def load_reception_data(self, new_reception_id):
        """Met à jour l'ID de la réception affichée et le titre."""
        self.reception_id = new_reception_id
        self.setWindowTitle(f"Réception de Lot - Bon #{self.reception_id}")
        self.reception_title_label.setText(f"Réception de Lot pour Bon : <span style='color:#2196F3; font-weight:bold;'>#{self.reception_id}</span>")


    def _init_ui(self):
        self.setWindowTitle(f"Réception de Lot - Bon #{self.reception_id}")
        self.setMinimumWidth(450)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # Optionnel: Garder au-dessus

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Titre de la fenêtre de détail
        self.reception_title_label = QLabel(f"Réception de Lot pour Bon : <span style='color:#2196F3; font-weight:bold;'>#{self.reception_id}</span>")
        self.reception_title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.reception_title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.reception_title_label)
        main_layout.addSpacing(15)

        # Utilisation de ModernCard pour encapsuler le formulaire
        form_card = ModernCard()
        form_layout = QFormLayout(form_card)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setSpacing(15) # Espacement entre les lignes du formulaire

        # Styles pour les labels et inputs
        label_style = "QLabel { color: #424242; font-weight: 600; }"
        input_style = """
            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                border: 1px solid #CFD8DC;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #F5F5F5;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
                border: 2px solid #2196F3; /* Bleu primaire */
                background-color: #FFFFFF;
            }
            QComboBox::drop-down, QDateEdit::drop-down {
                border: none;
                width: 20px;
                subcontrol-origin: padding;
                subcontrol-position: right center;
                image: url(icons/arrow_down.png); /* Remplacez par le chemin de votre icône de flèche */
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                background-color: #ECEFF1;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                image: url(icons/arrow_up.png); /* Flèche haut */
                width: 10px;
                height: 10px;
            }
            QSpinBox::down-arrow {
                image: url(icons/arrow_down.png); /* Flèche bas */
            }
        """

        # Référence lot
        lot_ref_label = QLabel("Référence du lot*:")
        lot_ref_label.setStyleSheet(label_style)
        self.lot_ref = QLineEdit()
        self.lot_ref.setPlaceholderText("Ex: LOT-2023-001")
        self.lot_ref.setStyleSheet(input_style)
        form_layout.addRow(lot_ref_label, self.lot_ref)

        # Produit (combo editable avec autocomplétion)
        product_label = QLabel("Produit*:")
        product_label.setStyleSheet(label_style)
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.NoInsert)
        self.product_combo.setStyleSheet(input_style)
        form_layout.addRow(product_label, self.product_combo)

        # Quantité
        quantite_label = QLabel("Quantité*:")
        quantite_label.setStyleSheet(label_style)
        self.quantite = QSpinBox()
        self.quantite.setRange(1, 1_000_000) # Augmenté la plage max
        self.quantite.setValue(1)
        self.quantite.setStyleSheet(input_style)
        form_layout.addRow(quantite_label, self.quantite)

        # Date production
        date_prod_label = QLabel("Date de production:")
        date_prod_label.setStyleSheet(label_style)
        self.date_prod = QDateEdit(QDate.currentDate())
        self.date_prod.setCalendarPopup(True)
        self.date_prod.setStyleSheet(input_style)
        form_layout.addRow(date_prod_label, self.date_prod)

        # Date expiration
        date_exp_label = QLabel("Date d'expiration:")
        date_exp_label.setStyleSheet(label_style)
        self.date_exp = QDateEdit(QDate.currentDate().addYears(1))
        self.date_exp.setCalendarPopup(True)
        self.date_exp.setStyleSheet(input_style)
        form_layout.addRow(date_exp_label, self.date_exp)

        # Cellule (numérique)
        cellule_label = QLabel("Cellule*:")
        cellule_label.setStyleSheet(label_style)
        self.cellule = QLineEdit()
        self.cellule.setValidator(QIntValidator(1, 100_000))
        self.cellule.setPlaceholderText("Numéro de cellule")
        self.cellule.setStyleSheet(input_style)
        form_layout.addRow(cellule_label, self.cellule)

        main_layout.addWidget(form_card) # Ajout de la carte du formulaire

        # Boutons Valider / Annuler (dans une QHBoxLayout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15) # Espacement entre les boutons
        btn_layout.setAlignment(Qt.AlignCenter) # Centrer les boutons

        btn_valider = QPushButton("✅ Valider la réception")
        btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; /* Vert */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        btn_valider.clicked.connect(self._receptionner)

        btn_annuler = QPushButton("❌ Annuler")
        btn_annuler.setStyleSheet("""
            QPushButton {
                background-color: #F44336; /* Rouge */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E57373;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)
        btn_annuler.clicked.connect(self.close)

        btn_layout.addWidget(btn_valider)
        btn_layout.addWidget(btn_annuler)

        main_layout.addLayout(btn_layout)

    def _apply_modern_theme(self):
        """Applique le thème moderne à la fenêtre principale."""
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA; /* Fond clair pour la fenêtre */
                color: #212121;
                font-family: "Arial", sans-serif;
            }
        """)
        # Appliquer l'ombre à la fenêtre elle-même si elle n'est pas déjà une ModernCard
        # Si la fenêtre est directement un QWidget, on peut lui donner une ombre aussi.
        # shadow = QGraphicsDropShadowEffect(self)
        # shadow.setBlurRadius(25)
        # shadow.setXOffset(0)
        # shadow.setYOffset(8)
        # shadow.setColor(QColor(0, 0, 0, 40))
        # self.setGraphicsEffect(shadow)

    def _load_products(self):
        """Charge la liste des produits dans la combo pour autocomplétion."""
        try:
            products = get_all_products(self.conn)
            # Tri par nom ou référence pour une meilleure UX
            products_sorted = sorted(products, key=lambda x: x.get('nom', x.get('reference', '')))
            
            self.product_combo.clear() # Vider avant de recharger
            for prod in products_sorted:
                display = f"{prod.get('reference', 'N/A')} - {prod.get('nom', 'N/A')}"
                self.product_combo.addItem(display, prod['idProduit']) # Stocke idProduit comme userData
            
            # Pour l'autocomplétion, on peut utiliser un completer si nécessaire
            # from PyQt5.QtWidgets import QCompleter
            # completer = QCompleter([p['nom'] for p in products], self.product_combo)
            # self.product_combo.setCompleter(completer)

        except Exception as e:
            QMessageBox.warning(
                self,
                "Chargement produits",
                f"Impossible de charger les produits:\n{str(e)}"
            )

    def _validate_form(self):
        """Valide les champs obligatoires du formulaire."""
        if not self.lot_ref.text().strip():
            QMessageBox.warning(self, "Champ requis", "Veuillez entrer la référence du lot.")
            return False

        # Vérifier si un produit est sélectionné (currentData() est None si rien n'est sélectionné/valide)
        if self.product_combo.currentData() is None:
            QMessageBox.warning(self, "Champ requis", "Veuillez sélectionner un produit valide dans la liste.")
            return False

        if not self.cellule.text().strip():
            QMessageBox.warning(self, "Champ requis", "Veuillez entrer un numéro de cellule.")
            return False
        
        # Vérification de la date d'expiration
        if self.date_exp.date() < self.date_prod.date():
            QMessageBox.warning(self, "Erreur de date", "La date d'expiration ne peut pas être antérieure à la date de production.")
            return False


        return True

    def _receptionner(self):
        """Traite la réception du lot après validation."""
        if not self._validate_form():
            return

        try:
            # Récupérer l'ID du produit sélectionné
            selected_product_id = self.product_combo.currentData()

            id_lot = handle_receptionner_lot(
                self.conn,
                self.reception_id,
                self.lot_ref.text().strip(),
                selected_product_id, # Utilise l'ID du produit
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
            self.reception_completed.emit() # Émet le signal de complétion
            self.close() # Ferme la fenêtre après succès

        except ValueError as ve:
            QMessageBox.warning(self, "Erreur de saisie", str(ve))

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Une erreur est survenue lors de la réception :\n{str(e)}"
            )
            
    def closeEvent(self, event):
        """Redéfinit l'événement de fermeture pour émettre le signal 'closed'."""
        self.closed.emit()
        super().closeEvent(event)