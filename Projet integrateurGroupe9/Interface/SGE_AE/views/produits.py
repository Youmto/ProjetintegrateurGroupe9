import logging
from datetime import datetime, date # Importez aussi date pour isinstance(date_exp, date)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QCheckBox,
    QMessageBox, QFileDialog, QGroupBox, QSizePolicy, QScrollArea, QFrame,
    QHeaderView # Importation de QHeaderView ici
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QDoubleValidator
import csv

# Configuration du logger
logger = logging.getLogger(__name__)

# En supposant que ces imports sont corrects depuis vos contrôleurs
# IMPORTANT: Assurez-vous que product_controller.py contient handle_get_product_details
from controllers.product_controller import (
    handle_get_all_products,
    handle_add_product,
    handle_update_product,
    handle_get_product_details
)

class ProduitsModule(QWidget):
    def __init__(self, conn, user=None):
        super().__init__()
        self.conn = conn
        self.user = user
        self.selected_id = None
        self.init_ui()
        self.load_products() # Charger les produits au démarrage

    def init_ui(self):
        # Mise en page principale pour l'ensemble du module
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Section 1: Formulaire de Saisie des Informations du Produit ---
        form_container = QGroupBox("Détails du Produit")
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)

        # Champs Communs du Produit
        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        self.id_input.setPlaceholderText("Généré automatiquement")
        self.id_input.setMinimumWidth(200)
        self.id_input.setObjectName("idInput")

        self.ref_input = QLineEdit()
        self.ref_input.setPlaceholderText("Ex: REF-PROD-001")
        self.ref_input.setObjectName("refInput")

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Ordinateur portable")
        self.nom_input.setObjectName("nomInput")

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Courte description du produit...")
        self.desc_input.setObjectName("descInput")

        self.marque_input = QLineEdit()
        self.marque_input.setPlaceholderText("Ex: HP, Dell, Microsoft")
        self.marque_input.setObjectName("marqueInput")

        self.modele_input = QLineEdit()
        self.modele_input.setPlaceholderText("Ex: Spectre x360, Latitude 7420")
        self.modele_input.setObjectName("modeleInput")

        self.type_input = QComboBox()
        self.type_input.addItems(["materiel", "logiciel"])
        self.type_input.currentIndexChanged.connect(self.toggle_product_type_fields)
        self.type_input.setObjectName("typeInput")

        self.emballage_input = QCheckBox("Matériel d'emballage")
        self.emballage_input.setObjectName("emballageInput")

        # Ajout des champs communs à la grille de mise en page
        form_layout.addWidget(QLabel("ID Produit:"), 0, 0, Qt.AlignRight)
        form_layout.addWidget(self.id_input, 0, 1, 1, 2)

        form_layout.addWidget(QLabel("Référence *:"), 1, 0, Qt.AlignRight)
        form_layout.addWidget(self.ref_input, 1, 1, 1, 2)

        form_layout.addWidget(QLabel("Nom *:"), 2, 0, Qt.AlignRight)
        form_layout.addWidget(self.nom_input, 2, 1, 1, 2)

        form_layout.addWidget(QLabel("Description:"), 3, 0, Qt.AlignRight)
        form_layout.addWidget(self.desc_input, 3, 1, 1, 2)

        form_layout.addWidget(QLabel("Marque:"), 4, 0, Qt.AlignRight)
        form_layout.addWidget(self.marque_input, 4, 1, 1, 2)

        form_layout.addWidget(QLabel("Modèle:"), 5, 0, Qt.AlignRight)
        form_layout.addWidget(self.modele_input, 5, 1, 1, 2)

        form_layout.addWidget(QLabel("Type:"), 6, 0, Qt.AlignRight)
        form_layout.addWidget(self.type_input, 6, 1, 1, 2)

        form_layout.addWidget(self.emballage_input, 7, 1, 1, 2)

        # --- Champs Dynamiques (Matériel & Logiciel) ---
        self.material_group = QGroupBox("Spécifications Matériel")
        self.material_group.setObjectName("MaterialGroup")
        material_layout = QGridLayout()
        material_layout.setHorizontalSpacing(15)
        material_layout.setVerticalSpacing(10)

        self.longueur_input = QLineEdit()
        self.longueur_input.setPlaceholderText("Longueur (cm)")
        self.longueur_input.setValidator(self.create_float_validator())
        self.largeur_input = QLineEdit()
        self.largeur_input.setPlaceholderText("Largeur (cm)")
        self.largeur_input.setValidator(self.create_float_validator())
        self.hauteur_input = QLineEdit()
        self.hauteur_input.setPlaceholderText("Hauteur (cm)")
        self.hauteur_input.setValidator(self.create_float_validator())
        self.masse_input = QLineEdit()
        self.masse_input.setPlaceholderText("Masse (kg)")
        self.masse_input.setValidator(self.create_float_validator())
        self.volume_input = QLineEdit()
        self.volume_input.setPlaceholderText("Volume (cm³)")
        self.volume_input.setValidator(self.create_float_validator())

        material_layout.addWidget(QLabel("Longueur (cm):"), 0, 0, Qt.AlignRight)
        material_layout.addWidget(self.longueur_input, 0, 1)
        material_layout.addWidget(QLabel("Largeur (cm):"), 1, 0, Qt.AlignRight)
        material_layout.addWidget(self.largeur_input, 1, 1)
        material_layout.addWidget(QLabel("Hauteur (cm):"), 2, 0, Qt.AlignRight)
        material_layout.addWidget(self.hauteur_input, 2, 1)
        material_layout.addWidget(QLabel("Masse (kg):"), 3, 0, Qt.AlignRight)
        material_layout.addWidget(self.masse_input, 3, 1)
        material_layout.addWidget(QLabel("Volume (cm³):"), 4, 0, Qt.AlignRight)
        material_layout.addWidget(self.volume_input, 4, 1)
        self.material_group.setLayout(material_layout)
        form_layout.addWidget(self.material_group, 0, 3, 8, 1)


        self.software_group = QGroupBox("Spécifications Logiciel")
        self.software_group.setObjectName("SoftwareGroup")
        software_layout = QGridLayout()
        software_layout.setHorizontalSpacing(15)
        software_layout.setVerticalSpacing(10)

        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("Ex: 1.0.0")
        self.type_licence_input = QLineEdit()
        self.type_licence_input.setPlaceholderText("Ex: Perpétuelle, Annuelle")
        self.date_expiration_input = QLineEdit()
        self.date_expiration_input.setPlaceholderText("AAAA-MM-JJ (ex: 2025-12-31)")

        software_layout.addWidget(QLabel("Version:"), 0, 0, Qt.AlignRight)
        software_layout.addWidget(self.version_input, 0, 1)
        software_layout.addWidget(QLabel("Type de Licence:"), 1, 0, Qt.AlignRight)
        software_layout.addWidget(self.type_licence_input, 1, 1)
        software_layout.addWidget(QLabel("Date d'Expiration:"), 2, 0, Qt.AlignRight)
        software_layout.addWidget(self.date_expiration_input, 2, 1)
        self.software_group.setLayout(software_layout)
        form_layout.addWidget(self.software_group, 0, 3, 8, 1)

        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)

        self.toggle_product_type_fields() # Initialise l'affichage des champs spécifiques

        # --- Section 2: Actions / Boutons ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignLeft)

        add_btn = QPushButton("Ajouter")
        # add_btn.setIcon(QIcon(":/icons/add.png")) # Décommenter si les icônes sont configurées
        add_btn.clicked.connect(self.add_product)
        add_btn.setObjectName("addButton")

        edit_btn = QPushButton("Modifier")
        # edit_btn.setIcon(QIcon(":/icons/edit.png")) # Décommenter si les icônes sont configurées
        edit_btn.clicked.connect(self.edit_product)
        edit_btn.setObjectName("editButton")

        clear_btn = QPushButton("Réinitialiser")
        # clear_btn.setIcon(QIcon(":/icons/clear.png")) # Décommenter si les icônes sont configurées
        clear_btn.clicked.connect(self.clear_form)
        clear_btn.setObjectName("clearButton")

        export_btn = QPushButton("Exporter CSV")
        # export_btn.setIcon(QIcon(":/icons/export.png")) # Décommenter si les icônes sont configurées
        export_btn.clicked.connect(self.export_to_csv)
        export_btn.setObjectName("exportButton")

        for btn in [add_btn, edit_btn, clear_btn, export_btn]:
            btn.setFixedSize(140, 35)
            button_layout.addWidget(btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # --- Section 3: Table des Produits ---
        table_group = QGroupBox("Liste des Produits")
        table_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(16) # Le nombre de colonnes est correct pour tous les détails
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Nom", "Description", "Marque", "Modèle", "Type", "Emballage",
            "Longueur (cm)", "Largeur (cm)", "Hauteur (cm)", "Masse (kg)", "Volume (cm³)",
            "Version", "Type Licence", "Date Exp."
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.select_product) # Connecte le signal au slot select_product
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        header = self.table.horizontalHeader()
        # LA CORRECTION EST ICI : Utiliser QHeaderView.ResizeToContents
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)

        # Ajustements finaux
        self.setWindowTitle("Gestion des Produits")
        self.setGeometry(100, 100, 1200, 800) # Taille initiale de la fenêtre

        # Appliquer un style QSS de base pour un aspect légèrement plus moderne
        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI", "Helvetica Neue", sans-serif;
                font-size: 10pt;
            }
            QGroupBox {
                font-size: 11pt;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                left: 10px;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007bff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                selection-background-color: #b0e0e6;
                selection-color: black;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border-bottom: 1px solid #ccc;
                font-weight: bold;
            }
            #idInput, #refInput, #nomInput {
                background-color: #f8f8f8;
            }
        """)

    def create_float_validator(self):
        # Permet des nombres décimaux avec jusqu'à 3 chiffres après la virgule
        validator = QDoubleValidator()
        validator.setRange(0.0, 999999999.0, 3)
        validator.setNotation(QDoubleValidator.StandardNotation)
        return validator

    def toggle_product_type_fields(self):
        current_type = self.type_input.currentText()
        is_material = (current_type == "materiel")
        is_software = (current_type == "logiciel")

        self.material_group.setVisible(is_material)
        self.software_group.setVisible(is_software)
        self.emballage_input.setVisible(is_material) # L'emballage n'a de sens que pour le matériel

        # Effacer les champs des groupes masqués pour éviter la soumission de données obsolètes
        if not is_material:
            for line_edit in [self.longueur_input, self.largeur_input, self.hauteur_input, self.masse_input, self.volume_input]:
                line_edit.clear()
        if not is_software:
            for line_edit in [self.version_input, self.type_licence_input, self.date_expiration_input]:
                line_edit.clear()

    def clear_form(self):
        self.selected_id = None
        self.id_input.clear()
        self.ref_input.clear()
        self.nom_input.clear()
        self.desc_input.clear()
        self.marque_input.clear()
        self.modele_input.clear()
        self.type_input.setCurrentIndex(0) # Revient au premier élément ("materiel")
        self.emballage_input.setChecked(False)

        # Assurer que tous les champs spécifiques sont également effacés
        self.longueur_input.clear()
        self.largeur_input.clear()
        self.hauteur_input.clear()
        self.masse_input.clear()
        self.volume_input.clear()
        self.version_input.clear()
        self.type_licence_input.clear()
        self.date_expiration_input.clear()

        self.table.clearSelection()
        self.toggle_product_type_fields() # S'assure que le bon groupe est visible après le reset

    def load_products(self):
        data = handle_get_all_products(self.conn)
        self.table.setRowCount(len(data))

        self.table.setSortingEnabled(False) # Désactiver le tri pendant le remplissage
        for row_idx, item in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item.get("idProduit", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(item.get("reference", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(item.get("nom", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(item.get("description", "") or ""))
            self.table.setItem(row_idx, 4, QTableWidgetItem(item.get("marque", "") or ""))
            self.table.setItem(row_idx, 5, QTableWidgetItem(item.get("modele", "") or ""))
            self.table.setItem(row_idx, 6, QTableWidgetItem(item.get("type", "")))
            self.table.setItem(row_idx, 7, QTableWidgetItem("Oui" if item.get("estMaterielEmballage") else "Non"))

            # Remplir les champs matériel
            # Simplification: str() gère None en retournant "None", ce qui peut être affiché.
            # L'opérateur OR pour les chaînes vides ou None est plus propre pour les QTableWidgetItem
            self.table.setItem(row_idx, 8, QTableWidgetItem(str(item.get("longueur", "") or "")))
            self.table.setItem(row_idx, 9, QTableWidgetItem(str(item.get("largeur", "") or "")))
            self.table.setItem(row_idx, 10, QTableWidgetItem(str(item.get("hauteur", "") or "")))
            self.table.setItem(row_idx, 11, QTableWidgetItem(str(item.get("masse", "") or "")))
            self.table.setItem(row_idx, 12, QTableWidgetItem(str(item.get("volume", "") or "")))

            # Remplir les champs logiciel
            self.table.setItem(row_idx, 13, QTableWidgetItem(item.get("version", "") or ""))
            self.table.setItem(row_idx, 14, QTableWidgetItem(item.get("typeLicence", "") or ""))
            
            date_exp = item.get("dateExpiration")
            # Assurez-vous que date_exp est une date, un datetime ou None
            if isinstance(date_exp, (datetime, date)):
                self.table.setItem(row_idx, 15, QTableWidgetItem(date_exp.strftime('%d/%m/%Y')))
            elif date_exp: # Si c'est une chaîne non vide (e.g., de la DB si pas convertie en datetime)
                self.table.setItem(row_idx, 15, QTableWidgetItem(str(date_exp)))
            else: # None ou chaîne vide
                self.table.setItem(row_idx, 15, QTableWidgetItem("Illimitée" if item.get("type") == "logiciel" else "")) # Affiche "Illimitée" seulement pour les logiciels

        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True) # Réactiver le tri après le remplissage

    def select_product(self, row, _):
        product_id = int(self.table.item(row, 0).text())
        self.selected_id = product_id
        
        product_details = handle_get_product_details(self.conn, product_id)
        
        if product_details:
            self.id_input.setText(str(product_details.get("idProduit", "")))
            self.ref_input.setText(product_details.get("reference", ""))
            self.nom_input.setText(product_details.get("nom", ""))
            self.desc_input.setText(product_details.get("description", "") or "")
            self.marque_input.setText(product_details.get("marque", "") or "")
            self.modele_input.setText(product_details.get("modele", "") or "")
            
            product_type = product_details.get("type", "")
            # Utilisation de findText pour définir le ComboBox, c'est plus robuste si les textes varient.
            index = self.type_input.findText(product_type, Qt.MatchFixedString)
            if index >= 0:
                self.type_input.setCurrentIndex(index) # Cela déclenchera toggle_product_type_fields
            
            self.emballage_input.setChecked(product_details.get("estMaterielEmballage", False))

            # Remplir les champs spécifiques en fonction du type
            if product_type == 'materiel':
                self.longueur_input.setText(str(product_details.get("longueur", "") or ""))
                self.largeur_input.setText(str(product_details.get("largeur", "") or ""))
                self.hauteur_input.setText(str(product_details.get("hauteur", "") or ""))
                self.masse_input.setText(str(product_details.get("masse", "") or ""))
                self.volume_input.setText(str(product_details.get("volume", "") or ""))
                # S'assurer que les champs logiciel sont effacés par toggle_product_type_fields
                # (pas besoin de les effacer explicitement ici si toggle_product_type_fields est appelé)

            elif product_type == 'logiciel':
                self.version_input.setText(product_details.get("version", "") or "")
                self.type_licence_input.setText(product_details.get("typeLicence", "") or "")
                
                date_exp = product_details.get("dateExpiration")
                if isinstance(date_exp, (datetime, date)):
                    self.date_expiration_input.setText(date_exp.strftime('%Y-%m-%d')) # Format attendu par le QLineEdit pour la saisie
                elif date_exp: # Si c'est une chaîne non vide (e.g., 'YYYY-MM-DD')
                    self.date_expiration_input.setText(str(date_exp))
                else: # None ou chaîne vide
                    self.date_expiration_input.setText("")
                
                # S'assurer que les champs matériel sont effacés par toggle_product_type_fields
                # (pas besoin de les effacer explicitement ici si toggle_product_type_fields est appelé)
            
            # toggle_product_type_fields est déjà appelé par setCurrentText,
            # donc il assure la visibilité et l'effacement.

        else:
            QMessageBox.warning(self, "Erreur", f"Impossible de récupérer les détails du produit ID {product_id}.")
            self.clear_form() # Efface le formulaire si les détails ne sont pas trouvés

    def get_form_data(self):
        reference = self.ref_input.text().strip()
        nom = self.nom_input.text().strip()

        if not reference or not nom:
            raise ValueError("Les champs Référence et Nom sont obligatoires.")

        product_data = {
            "reference": reference,
            "nom": nom,
            "description": self.desc_input.text().strip(),
            "marque": self.marque_input.text().strip(),
            "modele": self.modele_input.text().strip(),
            "type": self.type_input.currentText(),
            "estMaterielEmballage": self.emballage_input.isChecked()
        }

        current_type = self.type_input.currentText()
        if current_type == "materiel":
            try:
                product_data.update({
                    'longueur': float(self.longueur_input.text()) if self.longueur_input.text() else None,
                    'largeur': float(self.largeur_input.text()) if self.largeur_input.text() else None,
                    'hauteur': float(self.hauteur_input.text()) if self.hauteur_input.text() else None,
                    'masse': float(self.masse_input.text()) if self.masse_input.text() else None,
                    'volume': float(self.volume_input.text()) if self.volume_input.text() else None
                })
            except ValueError:
                raise ValueError("Veuillez entrer des valeurs numériques valides pour les spécifications matérielles.")
        elif current_type == "logiciel":
            date_exp_str = self.date_expiration_input.text().strip()
            
            date_expiration_obj = None
            if date_exp_str:
                try:
                    date_expiration_obj = datetime.strptime(date_exp_str, '%Y-%m-%d').date() # Stocker comme objet date
                except ValueError:
                    raise ValueError("Le format de la date d'expiration doit être AAAA-MM-JJ (ex: 2025-12-31).")
            
            product_data.update({
                'version': self.version_input.text().strip(),
                'typeLicence': self.type_licence_input.text().strip(),
                'dateExpiration': date_expiration_obj # Passer l'objet date ou None
            })

        return product_data

    def add_product(self):
        try:
            data = self.get_form_data()
            success = handle_add_product(self.conn, data)
            if success:
                QMessageBox.information(self, "Succès", "Produit ajouté avec succès.")
                self.clear_form()
                self.load_products()
            else:
                QMessageBox.warning(self, "Erreur", "Échec de l'ajout du produit. Voir les logs pour plus de détails.")
        except ValueError as ve:
            QMessageBox.warning(self, "Erreur de Saisie", str(ve))
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du produit: {e}", exc_info=True)
            QMessageBox.warning(self, "Erreur", f"Une erreur inattendue est survenue: {e}")

    def edit_product(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un produit à modifier.")
            return

        try:
            data = self.get_form_data()
            success = handle_update_product(self.conn, self.selected_id, data)
            if success:
                QMessageBox.information(self, "Succès", "Produit modifié avec succès.")
                self.clear_form()
                self.load_products()
            else:
                QMessageBox.warning(self, "Erreur", "Échec de la modification du produit. Voir les logs pour plus de détails.")
        except ValueError as ve:
            QMessageBox.warning(self, "Erreur de Saisie", str(ve))
        except Exception as e:
            logger.error(f"Erreur lors de la modification du produit: {e}", exc_info=True)
            QMessageBox.warning(self, "Erreur", f"Une erreur inattendue est survenue: {e}")

    def export_to_csv(self):
        data_to_export = []
        headers = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]

        for row in range(self.table.rowCount()):
            row_data = {}
            for col, header in enumerate(headers):
                item = self.table.item(row, col)
                row_data[header] = item.text() if item else ""
            data_to_export.append(row_data)

        if not data_to_export:
            QMessageBox.information(self, "Exportation CSV", "Aucune donnée à exporter.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les Produits en CSV",
            "produits.csv",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)",
            options=options
        )
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(data_to_export)
                QMessageBox.information(self, "Exportation CSV", "Produits exportés avec succès !")
            except Exception as e:
                logger.error(f"Erreur lors de l'exportation CSV: {e}", exc_info=True)
                QMessageBox.warning(self, "Erreur d'Exportation", f"Une erreur est survenue lors de l'exportation: {e}")