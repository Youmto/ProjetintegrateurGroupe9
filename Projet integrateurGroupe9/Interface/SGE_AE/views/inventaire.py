from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QComboBox, QMessageBox,
    QHeaderView, QGroupBox
)
from PyQt5.QtCore import Qt
from models.stock_model import search_products, get_product_details, get_stock_locations
from controllers.supervision_controller import handle_ruptures, handle_occupation_cellules

class InventaireModule(QWidget):
    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Barre de recherche améliorée
        search_group = QGroupBox("Recherche de produits")
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Recherche:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Référence ou nom du produit")
        search_layout.addWidget(self.search_input)
        
        self.search_type = QComboBox()
        self.search_type.addItems(["Tous", "Matériel", "Logiciel", "Emballage"])
        search_layout.addWidget(self.search_type)
        
        search_btn = QPushButton("Rechercher")
        search_btn.clicked.connect(self.search_products)
        search_layout.addWidget(search_btn)
        
        # Bouton pour les produits en rupture
        out_of_stock_btn = QPushButton("Produits en rupture")
        out_of_stock_btn.clicked.connect(self.load_out_of_stock)
        search_layout.addWidget(out_of_stock_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Tableau des résultats
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Nom", "Description", 
            "Marque", "Modèle", "Type", "Emballage"
        ])
        
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.doubleClicked.connect(self.show_product_details)
        layout.addWidget(self.products_table)
        
        # Section détails améliorée
        self.details_group = QGroupBox("Détails du produit")
        self.details_group.setVisible(False)
        details_layout = QVBoxLayout()
        
        self.product_title = QLabel()
        self.product_title.setAlignment(Qt.AlignCenter)
        self.product_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        details_layout.addWidget(self.product_title)
        
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(2)
        self.details_table.setHorizontalHeaderLabels(["Attribut", "Valeur"])
        self.details_table.horizontalHeader().setStretchLastSection(True)
        details_layout.addWidget(self.details_table)
        
        self.locations_table = QTableWidget()
        self.locations_table.setColumnCount(4)
        self.locations_table.setHorizontalHeaderLabels([
            "Cellule", "Entrepôt", "Quantité", "Lot"
        ])
        details_layout.addWidget(QLabel("Emplacements de stockage:"))
        details_layout.addWidget(self.locations_table)
        
        self.details_group.setLayout(details_layout)
        layout.addWidget(self.details_group)
        
        self.setLayout(layout)

    def clear_details(self):
        """Nettoie les détails affichés"""
        self.details_table.setRowCount(0)
        self.locations_table.setRowCount(0)
        self.product_title.setText("")
        self.details_group.setVisible(False)

    def search_products(self):
        search_term = self.search_input.text().strip()
        
        # Mapping amélioré pour le type de produit
        type_map = {
            "Matériel": "materiel",
            "Logiciel": "logiciel",
            "Emballage": "emballage"
        }
        product_type = self.search_type.currentText()
        type_filter = None if product_type == "Tous" else type_map.get(product_type)
        
        try:
            products = search_products(self.db_conn, search_term, type_filter)
            
            if not products:
                QMessageBox.information(self, "Aucun résultat", "Aucun produit correspondant trouvé.")
                self.products_table.setRowCount(0)
                self.clear_details()
                return
            
            self.products_table.setRowCount(len(products))
            for row, product in enumerate(products):
                self.products_table.setItem(row, 0, QTableWidgetItem(str(product['idProduit'])))
                self.products_table.setItem(row, 1, QTableWidgetItem(product['reference']))
                self.products_table.setItem(row, 2, QTableWidgetItem(product['nom']))
                self.products_table.setItem(row, 3, QTableWidgetItem(product.get('description', '')))
                self.products_table.setItem(row, 4, QTableWidgetItem(product.get('marque', '')))
                self.products_table.setItem(row, 5, QTableWidgetItem(product.get('modele', '')))
                self.products_table.setItem(row, 6, QTableWidgetItem(product['type']))
                self.products_table.setItem(row, 7, QTableWidgetItem(
                    "Oui" if product.get('estMaterielEmballage', False) else "Non"))
            
            self.products_table.resizeColumnsToContents()
            self.clear_details()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la recherche: {str(e)}")
            self.clear_details()
    
    def show_product_details(self, index):
        if not index.isValid():
            return
            
        try:
            self.clear_details()
            product_id = int(self.products_table.item(index.row(), 0).text())
            
            product = get_product_details(self.db_conn, product_id)
            if not product:
                raise ValueError("Produit non trouvé")
            
            self.product_title.setText(f"{product['reference']} - {product['nom']}")
            
            # Construction des détails de base
            base_fields = [
                ("ID Produit", product['idProduit']),
                ("Référence", product['reference']),
                ("Nom", product['nom']),
                ("Description", product.get('description', 'Non renseignée')),
                ("Marque", product.get('marque', 'Non renseignée')),
                ("Modèle", product.get('modele', 'Non renseigné')),
                ("Type", product['type']),
                ("Matériel d'emballage", "Oui" if product.get('estMaterielEmballage', False) else "Non")
            ]
            
            self.details_table.setRowCount(len(base_fields))
            for row, (field_name, field_value) in enumerate(base_fields):
                self.details_table.setItem(row, 0, QTableWidgetItem(field_name))
                self.details_table.setItem(row, 1, QTableWidgetItem(str(field_value)))
            
            # Ajout des spécificités selon le type de produit
            if product['type'] == 'materiel':
                current_rows = self.details_table.rowCount()
                self.details_table.setRowCount(current_rows + 5)
                
                material_fields = [
                    ("Longueur", f"{product.get('longueur', 'N/A')} cm"),
                    ("Largeur", f"{product.get('largeur', 'N/A')} cm"),
                    ("Hauteur", f"{product.get('hauteur', 'N/A')} cm"),
                    ("Masse", f"{product.get('masse', 'N/A')} kg"),
                    ("Volume", f"{product.get('volume', 'N/A')} cm³")
                ]
                
                for row, (field_name, field_value) in enumerate(material_fields, start=current_rows):
                    self.details_table.setItem(row, 0, QTableWidgetItem(field_name))
                    self.details_table.setItem(row, 1, QTableWidgetItem(field_value))
            
            elif product['type'] == 'logiciel':
                current_rows = self.details_table.rowCount()
                self.details_table.setRowCount(current_rows + 3)
                
                software_fields = [
                    ("Version", product.get('version', 'N/A')),
                    ("Type de licence", product.get('typeLicence', 'N/A')),
                    ("Date expiration", product.get('dateExpiration', 'N/A'))
                ]
                
                for row, (field_name, field_value) in enumerate(software_fields, start=current_rows):
                    self.details_table.setItem(row, 0, QTableWidgetItem(field_name))
                    self.details_table.setItem(row, 1, QTableWidgetItem(str(field_value)))
            
            # Affichage des emplacements de stockage
            locations = get_stock_locations(self.db_conn, product_id)
            self.locations_table.setRowCount(len(locations))
            for row, loc in enumerate(locations):
                self.locations_table.setItem(row, 0, QTableWidgetItem(loc.get('reference_cellule', '')))
                self.locations_table.setItem(row, 1, QTableWidgetItem(loc.get('nom_entrepot', '')))
                self.locations_table.setItem(row, 2, QTableWidgetItem(str(loc.get('quantite', 0))))
                self.locations_table.setItem(row, 3, QTableWidgetItem(loc.get('numeroLot', '')))
            
            self.details_group.setVisible(True)
            self.details_table.resizeColumnsToContents()
            self.locations_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec du chargement des détails: {str(e)}")
            self.clear_details()

    def load_out_of_stock(self):
        """Charge les produits en rupture de stock"""
        try:
            products = handle_ruptures(self.db_conn)
            
            if not products:
                QMessageBox.information(self, "Aucun résultat", "Aucun produit en rupture de stock.")
                self.products_table.setRowCount(0)
                self.clear_details()
                return
                
            self.products_table.setRowCount(len(products))
            for row, product in enumerate(products):
                self.products_table.setItem(row, 0, QTableWidgetItem(str(product['idProduit'])))
                self.products_table.setItem(row, 1, QTableWidgetItem(product['reference']))
                self.products_table.setItem(row, 2, QTableWidgetItem(product['nom']))
                self.products_table.setItem(row, 3, QTableWidgetItem(product.get('description', '')))
                self.products_table.setItem(row, 4, QTableWidgetItem(product.get('marque', '')))
                self.products_table.setItem(row, 5, QTableWidgetItem(product.get('modele', '')))
                self.products_table.setItem(row, 6, QTableWidgetItem(product['type']))
                self.products_table.setItem(row, 7, QTableWidgetItem(
                    "Oui" if product.get('estMaterielEmballage', False) else "Non"))
            
            self.products_table.resizeColumnsToContents()
            self.clear_details()
            QMessageBox.information(self, "Produits en rupture", 
                                   f"{len(products)} produits en rupture de stock trouvés.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec du chargement des ruptures: {str(e)}")
            self.clear_details()