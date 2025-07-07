from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QLabel, QLineEdit,
    QComboBox, QFormLayout, QDialogButtonBox, QSpinBox, QDateEdit,
    QHeaderView, QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QDoubleValidator # Ajout de QDoubleValidator
from datetime import date, datetime # Pour la manipulation des dates

from models import lot_model # Garde l'importation du modèle


class LotDetailWindow(QMainWindow):
    def __init__(self, conn, user=None):
        super().__init__()
        self.conn = conn
        self.user = user
        self.id_lot = None
        self.lots_map = {} # Pour mapper l'index de la ComboBox à l'ID du lot
        self.current_produits_data = [] # Stocke les données brutes des produits pour le filtrage

        self.setWindowTitle("📦 Détails des Lots")
        self.resize(1200, 750) # Augmente la taille pour une meilleure vue

        # Widget Central Principal et Mise en page
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- Section En-tête (Titre et Recherche) ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)

        # Label du Titre
        title_label = QLabel("📦 Détails et Gestion des Lots de Produits")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2C3E50;") # Bleu foncé pour le titre
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        # Mise en page du Sélecteur de Lot et de la Barre de Recherche
        search_lot_layout = QHBoxLayout()
        search_lot_layout.setSpacing(10)
        search_lot_layout.setAlignment(Qt.AlignLeft)

        search_lot_layout.addWidget(QLabel("Sélectionnez un Lot:"))
        self.lot_selector = QComboBox()
        self.lot_selector.currentIndexChanged.connect(self.on_lot_selected)
        self.lot_selector.setMinimumWidth(250)
        self.lot_selector.setStyleSheet("""
            QComboBox {
                font-weight: bold;
                font-size: 14px;
                color: #2874A6;
                padding: 8px;
                border: 1px solid #A9CCE3;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox::drop-down {
                border-left: 1px solid #A9CCE3;
                width: 25px;
            }
            QComboBox::down-arrow {
                /* image: url(./icons/arrow_down.png); */ /* Placeholder: remplacer par le chemin réel de l'icône */
                width: 15px;
                height: 15px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #A9CCE3;
                selection-background-color: #D6EAF8;
                selection-color: #2874A6;
            }
        """)
        search_lot_layout.addWidget(self.lot_selector)

        search_lot_layout.addStretch(1) # Pousse les éléments vers la gauche

        # Optionnel : Ajouter une barre de recherche pour les produits du lot actuel
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔎 Rechercher un produit par nom ou ID...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #A9CCE3;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #2980B9;
            }
        """)
        self.search_input.textChanged.connect(self.filter_products) # Connecter à une fonction de filtrage
        search_lot_layout.addWidget(self.search_input)

        header_layout.addLayout(search_lot_layout)
        self.main_layout.addLayout(header_layout)

        # Ligne de Séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #D5DBDB;")
        self.main_layout.addWidget(separator)

        # --- Section Tableau ---
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Rendre le tableau en lecture seule
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # Sélectionner des lignes entières
        self.table.setAlternatingRowColors(True) # Rayures pour les lignes pour une meilleure lisibilité
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ECF0F1; /* Gris clair */
                gridline-color: #BDC3C7; /* Gris */
                font-size: 13px;
                border: 1px solid #BDC3C7;
                border-radius: 8px; /* Coins légèrement plus arrondis */
            }
            QHeaderView::section {
                background-color: #34495E; /* Bleu-gris foncé */
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #2C3E50;
                border-bottom: 2px solid #1ABC9C; /* Accent vert */
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #85C1E9; /* Bleu clair */
                color: black;
            }
        """)
        
        # Ajuster l'étirement des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        self.main_layout.addWidget(self.table)

        # --- Section Boutons ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setAlignment(Qt.AlignCenter) # Centrer les boutons

        self.btn_modifier = QPushButton("✏️ Modifier le produit")
        self.btn_modifier.setFont(QFont("Arial", 11, QFont.Bold))
        self.btn_modifier.setStyleSheet("""
            QPushButton {
                background-color: #28A745; /* Vert */
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                border: none;
                /* transition: background-color 0.3s ease; */ /* COMMENTÉ OU SUPPRIMÉ */
            }
            QPushButton:hover {
                background-color: #218838; /* Vert plus foncé au survol */
            }
            QPushButton:pressed {
                background-color: #1E7E34; /* Encore plus foncé en appuyant */
            }
        """)
        self.btn_modifier.setCursor(Qt.PointingHandCursor) # Curseur main au survol
        self.btn_modifier.setFixedSize(200, 50) # Taille fixe pour l'uniformité

        self.btn_supprimer = QPushButton("🗑️ Supprimer le produit")
        self.btn_supprimer.setFont(QFont("Arial", 11, QFont.Bold))
        self.btn_supprimer.setStyleSheet("""
            QPushButton {
                background-color: #DC3545; /* Rouge */
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                border: none;
                /* transition: background-color 0.3s ease; */ /* COMMENTÉ OU SUPPRIMÉ */
            }
            QPushButton:hover {
                background-color: #C82333; /* Rouge plus foncé au survol */
            }
            QPushButton:pressed {
                background-color: #BD2130; /* Encore plus foncé en appuyant */
            }
        """)
        self.btn_supprimer.setCursor(Qt.PointingHandCursor)
        self.btn_supprimer.setFixedSize(200, 50) # Taille fixe pour l'uniformité


        btn_layout.addWidget(self.btn_modifier)
        btn_layout.addWidget(self.btn_supprimer)
        self.main_layout.addLayout(btn_layout)

        # Appliquer le style général de la fenêtre (similaire à Inventaire)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA; /* Gris très clair pour l'arrière-plan */
            }
            QLabel {
                color: #34495E; /* Bleu-gris foncé pour le texte général */
                font-size: 13px;
            }
        """)

        # Connecter les signaux
        self.btn_modifier.clicked.connect(self.modifier_produit)
        self.btn_supprimer.clicked.connect(self.supprimer_produit)

        # Chargement initial des données
        self.charger_lots()

    def charger_lots(self):
        lots = lot_model.get_all_lots(self.conn)
        self.lot_selector.clear()
        self.lots_map = {}
        if not lots:
            self.lot_selector.addItem("Aucun lot disponible")
            self.id_lot = None
            self.table.setRowCount(0)
            self.table.clearContents()
            # Désactiver les boutons si aucun lot
            self.btn_modifier.setEnabled(False)
            self.btn_supprimer.setEnabled(False)
            return
        
        self.btn_modifier.setEnabled(True)
        self.btn_supprimer.setEnabled(True)

        for index, (id_lot, numero) in enumerate(lots):
            self.lot_selector.addItem(f"📦 Lot N°{numero} (ID: {id_lot})")
            self.lots_map[index] = id_lot
        
        # Sélectionner le premier lot par défaut et charger ses produits
        self.id_lot = lots[0][0]
        self.lot_selector.setCurrentIndex(0) # Cela déclenchera on_lot_selected


    def on_lot_selected(self, index):
        if index >= 0 and index in self.lots_map:
            self.id_lot = self.lots_map.get(index)
            self.charger_produits()
        else:
            self.id_lot = None
            self.table.setRowCount(0)
            self.table.clearContents()


    def charger_produits(self):
        if not self.id_lot:
            self.table.setRowCount(0)
            self.table.clearContents()
            return

        self.table.setSortingEnabled(False)
        self.table.clearContents()

        # Supposant que lot_model.get_produits_par_lot retourne maintenant une liste de dictionnaires
        produits = lot_model.get_produits_par_lot(self.conn, self.id_lot)
        self.current_produits_data = produits # Stocke les données brutes pour le filtrage

        self.display_products(produits)


    def display_products(self, products_to_display):
        """Aide à afficher les produits dans le tableau, utilisée par charger_produits et filter_products."""
        headers = [
            "ID Colis", "ID Produit", "Nom Produit", "Type", "Quantité",
            "Version", "Type Licence", "Date Exp.",
            "Longueur (cm)", "Largeur (cm)", "Hauteur (cm)", "Masse (kg)", "Volume (cm³)"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(products_to_display))

        for row_idx, prod_data in enumerate(products_to_display):
            # Les accès sont maintenant via .get() sur des dictionnaires
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(prod_data.get("idColis", "") or "")))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(prod_data.get("idProduit", "") or "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(prod_data.get("nom", "") or ""))
            self.table.setItem(row_idx, 3, QTableWidgetItem(prod_data.get("type", "") or "")) # Accès à la clé 'type'
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(prod_data.get("quantite", "") or "")))

            self.table.setItem(row_idx, 5, QTableWidgetItem(prod_data.get("version", "") or ""))
            self.table.setItem(row_idx, 6, QTableWidgetItem(prod_data.get("typeLicence", "") or ""))
            
            date_exp = prod_data.get("dateExpiration")
            if isinstance(date_exp, (date, datetime)):
                self.table.setItem(row_idx, 7, QTableWidgetItem(date_exp.strftime('%Y-%m-%d')))
            elif isinstance(date_exp, QDate): # Au cas où, si une QDate traîne, mais le modèle renvoie date/datetime
                self.table.setItem(row_idx, 7, QTableWidgetItem(date_exp.toString("yyyy-MM-dd")))
            else:
                self.table.setItem(row_idx, 7, QTableWidgetItem(str(date_exp) if date_exp else "")) # Fallback pour string vide si None


            # Pour les valeurs numériques, assurez-vous qu'elles sont affichées comme des chaînes
            # et que les None sont gérés correctement pour éviter 'None' dans le tableau
            self.table.setItem(row_idx, 8, QTableWidgetItem(str(prod_data.get('longueur', '') or '')))
            self.table.setItem(row_idx, 9, QTableWidgetItem(str(prod_data.get('largeur', '') or '')))
            self.table.setItem(row_idx, 10, QTableWidgetItem(str(prod_data.get('hauteur', '') or '')))
            self.table.setItem(row_idx, 11, QTableWidgetItem(str(prod_data.get('masse', '') or '')))
            self.table.setItem(row_idx, 12, QTableWidgetItem(str(prod_data.get('volume', '') or '')))

        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)

    def filter_products(self):
        filter_text = self.search_input.text().lower()
        if not filter_text:
            self.display_products(self.current_produits_data) # Afficher tout si le filtre est vide
            return

        filtered_list = []
        for prod_data in self.current_produits_data:
            # Vérifier ID Colis, ID Produit, Nom Produit, et TYPE (nouvellement ajouté pour le filtre)
            if (filter_text in str(prod_data.get("idColis", "")).lower() or
                filter_text in str(prod_data.get("idProduit", "")).lower() or
                filter_text in str(prod_data.get("nom", "")).lower() or
                filter_text in str(prod_data.get("type", "")).lower()): # Ajout du type au filtrage
                filtered_list.append(prod_data)
        
        self.display_products(filtered_list)


    def get_selection(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "⚠️ Sélection requise", "Veuillez sélectionner un produit dans le tableau.")
            return None
        
        try:
            # Récupérer à partir des données brutes stockées (qui sont des dictionnaires)
            if self.current_produits_data and row < len(self.current_produits_data):
                selected_prod_data = self.current_produits_data[row]
                id_colis = selected_prod_data.get("idColis")
                id_produit = selected_prod_data.get("idProduit")
                type_produit = selected_prod_data.get("type") # Accès à la clé 'type'
            else:
                # Fallback: Si current_produits_data n'est pas fiable, récupérer depuis la table
                id_colis = int(self.table.item(row, 0).text())
                id_produit = int(self.table.item(row, 1).text())
                type_produit = self.table.item(row, 3).text() # Récupérer le type depuis la colonne 'Type'

            return id_colis, id_produit, type_produit

        except (ValueError, AttributeError) as e:
            QMessageBox.critical(self, "Erreur de sélection", f"Impossible de récupérer les informations du produit sélectionné: {e}")
            return None

    def modifier_produit(self):
        sel = self.get_selection()
        if not sel:
            return
        id_colis, id_produit, type_produit = sel

        # Récupérer tous les détails du produit pour pré-remplir le dialogue
        # Cette fonction doit exister dans votre lot_model.py et retourner un dictionnaire
        produit_details = lot_model.get_produit_details_in_colis(self.conn, id_colis, id_produit)
        
        if not produit_details:
            QMessageBox.warning(self, "Erreur", "Impossible de charger les détails du produit pour la modification.")
            return

        # Passez `produit_details` qui est un dictionnaire
        dlg = ProduitEditDialog(self.conn, id_colis, id_produit, type_produit, produit_details, parent=self)
        if dlg.exec_(): # Ceci retournera True si le dialogue a été accepté
            QMessageBox.information(self, "✔️ Modifié", "Le produit a été mis à jour avec succès.")
            self.charger_produits() # Recharger après une modification réussie

    def supprimer_produit(self):
        sel = self.get_selection()
        if not sel:
            return
        id_colis, id_produit, _ = sel # Le type n'est pas nécessaire pour la suppression

        confirm = QMessageBox.question(
            self, "❌ Confirmation de Suppression",
            f"Êtes-vous sûr de vouloir supprimer le produit avec ID {id_produit} du colis {id_colis} ?"
            "\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No # Spécifier les boutons
        )
        if confirm == QMessageBox.Yes:
            # Appel de la fonction du modèle, qui attend maintenant id_colis et id_produit
            success = lot_model.supprimer_produit_dans_colis(self.conn, id_colis, id_produit)
            if success:
                QMessageBox.information(self, "🗑️ Supprimé", "Produit supprimé avec succès.")
                self.charger_produits()
            else:
                QMessageBox.critical(self, "Erreur de Suppression", "Échec de la suppression du produit. Veuillez consulter les logs.")


class ProduitEditDialog(QDialog):
    def __init__(self, conn, id_colis, id_produit, type_produit, initial_data, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.id_colis = id_colis
        self.id_produit = id_produit
        self.type_produit = type_produit
        self.initial_data = initial_data

        self.setWindowTitle(f"✏️ Modifier Produit (ID: {id_produit}, Colis: {id_colis})")
        self.setMinimumSize(450, 300) # Taille minimale
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # Reste au-dessus

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        # Ajouter un titre au dialogue
        dialog_title = QLabel("Détails du Produit")
        dialog_title.setFont(QFont("Arial", 16, QFont.Bold))
        dialog_title.setAlignment(Qt.AlignCenter)
        dialog_title.setStyleSheet("color: #2C3E50; margin-bottom: 15px;")
        layout.addRow(dialog_title)

        # Champ Quantité
        self.quantite = QSpinBox()
        self.quantite.setMinimum(1)
        self.quantite.setMaximum(999999)
        # Accéder à 'quantite' via .get()
        self.quantite.setValue(self.initial_data.get('quantite', 1)) 
        layout.addRow("Quantité:", self.quantite)

        # Champs spécifiques selon le type de produit
        if self.type_produit == 'logiciel':
            self.version = QLineEdit()
            self.licence = QLineEdit()
            self.date_exp = QDateEdit()
            self.date_exp.setCalendarPopup(True)
            self.date_exp.setDisplayFormat("yyyy-MM-dd")

            self.version.setText(self.initial_data.get('version', '') or '')
            self.licence.setText(self.initial_data.get('typeLicence', '') or '')
            
            date_exp_val = self.initial_data.get('dateExpiration')
            if date_exp_val:
                # Convertir date/datetime en QDate
                if isinstance(date_exp_val, (datetime, date)):
                    self.date_exp.setDate(QDate(date_exp_val.year, date_exp_val.month, date_exp_val.day))
                elif isinstance(date_exp_val, str): # Au cas où une chaîne de caractères date est passée
                    parsed_date = QDate.fromString(date_exp_val, "yyyy-MM-dd")
                    if parsed_date.isValid():
                        self.date_exp.setDate(parsed_date)
                    else:
                        self.date_exp.setDate(QDate.currentDate()) # Fallback si string invalide
                else:
                    self.date_exp.setDate(QDate.currentDate()) # Fallback pour autres types
            else:
                self.date_exp.setDate(QDate.currentDate()) # Si date_exp_val est None

            layout.addRow("Version:", self.version)
            layout.addRow("Type Licence:", self.licence)
            layout.addRow("Date Expiration:", self.date_exp)

        elif self.type_produit == 'materiel':
            float_validator = QDoubleValidator()
            float_validator.setRange(0.0, 999999999.0, 3) # Plage et précision pour 3 décimales
            float_validator.setNotation(QDoubleValidator.StandardNotation)

            self.longueur = QLineEdit()
            self.longueur.setValidator(float_validator)
            self.largeur = QLineEdit()
            self.largeur.setValidator(float_validator)
            self.hauteur = QLineEdit()
            self.hauteur.setValidator(float_validator)
            self.masse = QLineEdit()
            self.masse.setValidator(float_validator)
            self.volume = QLineEdit()
            self.volume.setValidator(float_validator)

            # Pré-remplir les champs, en s'assurant de convertir les valeurs numériques en str
            self.longueur.setText(str(self.initial_data.get('longueur', '') or ''))
            self.largeur.setText(str(self.initial_data.get('largeur', '') or ''))
            self.hauteur.setText(str(self.initial_data.get('hauteur', '') or ''))
            self.masse.setText(str(self.initial_data.get('masse', '') or ''))
            self.volume.setText(str(self.initial_data.get('volume', '') or ''))

            layout.addRow("Longueur (cm):", self.longueur)
            layout.addRow("Largeur (cm):", self.largeur)
            layout.addRow("Hauteur (cm):", self.hauteur)
            layout.addRow("Masse (kg):", self.masse)
            layout.addRow("Volume (cm³):", self.volume)

        # Boutons du dialogue
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.submit)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        # Style spécifique du dialogue (aligné avec le nouveau style de la fenêtre principale)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA; /* Gris très clair */
                border: 1px solid #BDC3C7;
                border-radius: 10px;
            }
            QLabel {
                color: #34495E;
                font-weight: bold;
                font-size: 14px;
            }
            QLineEdit, QSpinBox, QDateEdit {
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                color: #34495E;
            }
            QLineEdit:focus, QSpinBox:focus, QDateEdit:focus {
                border: 1px solid #2980B9;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #BDC3C7;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QDateEdit::down-arrow {
                /* image: url(./icons/calendar.png); */ /* Placeholder: remplacer par le chemin réel de l'icône */
                width: 15px;
                height: 15px;
            }
            QDialogButtonBox QPushButton {
                background-color: #28A745; /* Vert */
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #218838;
            }
            QDialogButtonBox QPushButton:last-child { /* Bouton Annuler */
                background-color: #6C757D; /* Gris */
            }
            QDialogButtonBox QPushButton:last-child:hover {
                background-color: #5A6268;
            }
        """)

    def submit(self):
        quantite = self.quantite.value()
        update_data = {"quantite": quantite}

        if self.type_produit == 'logiciel':
            update_data["version"] = self.version.text().strip() or None
            update_data["type_licence"] = self.licence.text().strip() or None
            
            date_exp_qdate = self.date_exp.date()
            if date_exp_qdate.isValid():
                # Convertir QDate en objet datetime.date pour le modèle
                update_data["date_expiration"] = date(date_exp_qdate.year(), date_exp_qdate.month(), date_exp_qdate.day())
            else:
                update_data["date_expiration"] = None

        elif self.type_produit == 'materiel':
            try:
                # Utiliser des 'None' si la chaîne est vide pour les champs numériques
                update_data["longueur"] = float(self.longueur.text()) if self.longueur.text() else None
                update_data["largeur"] = float(self.largeur.text()) if self.largeur.text() else None
                update_data["hauteur"] = float(self.hauteur.text()) if self.hauteur.text() else None
                update_data["masse"] = float(self.masse.text()) if self.masse.text() else None
                update_data["volume"] = float(self.volume.text()) if self.volume.text() else None
            except ValueError:
                QMessageBox.warning(self, "Erreur de saisie", "Veuillez entrer des nombres valides pour les dimensions et la masse.")
                return

        # Appeler la fonction du modèle avec les données mises à jour
        # Utilisez **update_data pour passer les éléments du dictionnaire comme arguments nommés
        success = lot_model.modifier_produit_dans_colis(self.conn, self.id_colis, self.id_produit, **update_data)
        
        if success:
            self.accept() # Fermer le dialogue avec succès
        else:
            QMessageBox.critical(self, "Erreur de mise à jour", "Échec de la mise à jour du produit. Vérifiez les logs.")