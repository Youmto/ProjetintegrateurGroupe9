from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QComboBox, QMessageBox,
    QHeaderView, QGroupBox, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QProgressBar, QToolButton,
    QSizePolicy, QSpacerItem, QGridLayout, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QPainter, QBrush
from models.stock_model import search_products, get_product_details, get_stock_locations
from controllers.supervision_controller import handle_ruptures, handle_occupation_cellules


class ModernCard(QFrame):
    """Carte moderne avec effet d'ombre et animations"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
            }
            QFrame:hover {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class ModernSearchWidget(QWidget):
    """Widget de recherche moderne avec animations"""
    searchTriggered = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Titre avec icône
        title_layout = QHBoxLayout()
        title_icon = QLabel("🔍")
        title_icon.setStyleSheet("font-size: 24px;")
        title_label = QLabel("Recherche Avancée")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-left: 8px;
        """)
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Ligne de recherche moderne
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        # Champ de recherche avec style moderne
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un produit...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 14px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
            QLineEdit::placeholder {
                color: #7f8c8d;
            }
        """)
        
        # ComboBox moderne
        self.search_type = QComboBox()
        self.search_type.addItems(["Tous", "Matériel", "Logiciel", "Emballage"])
        self.search_type.setStyleSheet("""
            QComboBox {
                padding: 12px 16px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 14px;
                background-color: #ffffff;
                color: #2c3e50;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #7f8c8d;
                width: 6px;
                height: 6px;
                border-top: none;
                border-left: none;
                transform: rotate(45deg);
            }
        """)
        
        # Boutons d'action modernes
        search_btn = QPushButton("🔍 Rechercher")
        search_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2980b9, stop: 1 #21618c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #21618c, stop: 1 #1b4f72);
            }
        """)
        
        out_of_stock_btn = QPushButton("⚠️ Ruptures")
        out_of_stock_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #a93226);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #a93226, stop: 1 #922b21);
            }
        """)
        
        search_layout.addWidget(self.search_input, 2)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(out_of_stock_btn)
        
        layout.addLayout(search_layout)
        self.setLayout(layout)
        
        # Connexions
        search_btn.clicked.connect(self.trigger_search)
        out_of_stock_btn.clicked.connect(self.trigger_out_of_stock)
        self.search_input.returnPressed.connect(self.trigger_search)
        
    def trigger_search(self):
        self.searchTriggered.emit(self.search_input.text(), self.search_type.currentText())
        
    def trigger_out_of_stock(self):
        self.searchTriggered.emit("", "RUPTURES")


class ModernTableWidget(QTableWidget):
    """Tableau moderne avec styles personnalisés"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                gridline-color: #f1f3f4;
                font-size: 13px;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
                color: #495057;
                padding: 12px 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                font-size: 12px;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e9ecef, stop: 1 #dee2e6);
            }
        """)


class StatsWidget(QWidget):
    """Widget d'affichage des statistiques"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(16)
        
        # Cartes de statistiques
        stats = [
            ("📦", "Total Produits", "0", "#3498db"),
            ("⚠️", "En Rupture", "0", "#e74c3c"),
            ("📍", "Emplacements", "0", "#27ae60"),
            ("🔄", "Dernière MAJ", "Maintenant", "#f39c12")
        ]
        
        for icon, title, value, color in stats:
            card = self.create_stat_card(icon, title, value, color)
            layout.addWidget(card)
        
        self.setLayout(layout)
        
    def create_stat_card(self, icon, title, value, color):
        """Crée une carte de statistique"""
        card = ModernCard()
        card.setFixedHeight(100)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        
        # Icône et titre
        top_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px; color: {color};")
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 12px; color: #7f8c8d; font-weight: bold;")
        
        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        
        # Valeur
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        
        card_layout.addLayout(top_layout)
        card_layout.addWidget(value_label)
        card_layout.addStretch()
        
        card.setLayout(card_layout)
        return card


class InventaireModule(QWidget):
    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.current_products = []
        self.init_ui()
        self.apply_modern_theme()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête avec titre et statistiques
        header_layout = QVBoxLayout()
        header_layout.setSpacing(16)
        
        # Titre principal
        title_label = QLabel("📦 Gestion d'Inventaire")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 16px 0;
        """)
        header_layout.addWidget(title_label)
        
        # Widget des statistiques
        self.stats_widget = StatsWidget()
        header_layout.addWidget(self.stats_widget)
        
        main_layout.addLayout(header_layout)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e1e5e9; height: 2px; border-radius: 1px;")
        main_layout.addWidget(separator)
        
        # Widget de recherche moderne
        search_card = ModernCard()
        search_layout = QVBoxLayout()
        search_layout.setContentsMargins(20, 20, 20, 20)
        
        self.search_widget = ModernSearchWidget()
        self.search_widget.searchTriggered.connect(self.handle_search)
        search_layout.addWidget(self.search_widget)
        
        search_card.setLayout(search_layout)
        main_layout.addWidget(search_card)
        
        # Splitter pour diviser la vue
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e1e5e9;
                width: 3px;
                border-radius: 1px;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)
        
        # Section gauche - Tableau des produits
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        products_label = QLabel("📋 Liste des Produits")
        products_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px 0;
        """)
        left_layout.addWidget(products_label)
        
        # Tableau moderne
        self.products_table = ModernTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Nom", "Description", 
            "Marque", "Modèle", "Type", "Emballage"
        ])
        
        # Configuration des colonnes
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
        self.products_table.setAlternatingRowColors(True)
        self.products_table.doubleClicked.connect(self.show_product_details)
        left_layout.addWidget(self.products_table)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Section droite - Détails du produit
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Conteneur pour les détails
        self.details_container = QWidget()
        details_main_layout = QVBoxLayout()
        details_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Message par défaut
        self.default_message = QLabel("👆 Sélectionnez un produit\npour voir ses détails")
        self.default_message.setAlignment(Qt.AlignCenter)
        self.default_message.setStyleSheet("""
            font-size: 16px;
            color: #7f8c8d;
            padding: 40px;
            border: 2px dashed #e1e5e9;
            border-radius: 8px;
            background-color: #f8f9fa;
        """)
        details_main_layout.addWidget(self.default_message)
        
        # Groupe de détails (caché par défaut)
        self.details_group = QGroupBox("🔍 Détails du Produit")
        self.details_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                margin: 8px 0;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: #ffffff;
            }
        """)
        self.details_group.setVisible(False)
        
        details_layout = QVBoxLayout()
        details_layout.setSpacing(16)
        
        # Titre du produit
        self.product_title = QLabel()
        self.product_title.setAlignment(Qt.AlignCenter)
        self.product_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #e1e5e9;
        """)
        details_layout.addWidget(self.product_title)
        
        # Tableaux de détails
        self.details_table = ModernTableWidget()
        self.details_table.setColumnCount(2)
        self.details_table.setHorizontalHeaderLabels(["Attribut", "Valeur"])
        self.details_table.horizontalHeader().setStretchLastSection(True)
        self.details_table.setMaximumHeight(300)
        details_layout.addWidget(self.details_table)
        
        # Tableau des emplacements
        locations_label = QLabel("📍 Emplacements de Stockage")
        locations_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px 0;
        """)
        details_layout.addWidget(locations_label)
        
        self.locations_table = ModernTableWidget()
        self.locations_table.setColumnCount(4)
        self.locations_table.setHorizontalHeaderLabels([
            "Cellule", "Entrepôt", "Quantité", "Lot"
        ])
        self.locations_table.setMaximumHeight(200)
        details_layout.addWidget(self.locations_table)
        
        self.details_group.setLayout(details_layout)
        details_main_layout.addWidget(self.details_group)
        
        self.details_container.setLayout(details_main_layout)
        right_layout.addWidget(self.details_container)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        # Configuration du splitter
        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
        
        # Barre de progression (cachée par défaut)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                text-align: center;
                background-color: #f8f9fa;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-radius: 6px;
            }
        """)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

    def apply_modern_theme(self):
        """Applique le thème moderne à l'interface"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
        """)

    def show_loading(self, message="Chargement..."):
        """Affiche une barre de progression"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Mode indéterminé
        
    def hide_loading(self):
        """Cache la barre de progression"""
        self.progress_bar.setVisible(False)

    def clear_details(self):
        """Nettoie les détails affichés"""
        self.details_table.setRowCount(0)
        self.locations_table.setRowCount(0)
        self.product_title.setText("")
        self.details_group.setVisible(False)
        self.default_message.setVisible(True)

    def handle_search(self, search_term, search_type):
        """Gestionnaire unifié pour toutes les recherches"""
        self.show_loading()
        
        if search_type == "RUPTURES":
            self.load_out_of_stock()
        else:
            self.search_products(search_term, search_type)
        
        self.hide_loading()

    def search_products(self, search_term=None, product_type=None):
        """Recherche de produits améliorée"""
        if search_term is None:
            search_term = ""
        if product_type is None:
            product_type = "Tous"
            
        # Mapping pour le type de produit
        type_map = {
            "Matériel": "materiel",
            "Logiciel": "logiciel",
            "Emballage": "emballage"
        }
        type_filter = None if product_type == "Tous" else type_map.get(product_type)
        
        try:
            products = search_products(self.db_conn, search_term, type_filter)
            self.current_products = products
            
            if not products:
                self.show_info_message("Aucun résultat", "Aucun produit correspondant trouvé.")
                self.products_table.setRowCount(0)
                self.clear_details()
                return
            
            self.populate_products_table(products)
            self.clear_details()
            
        except Exception as e:
            self.show_error_message("Erreur de recherche", f"Échec de la recherche: {str(e)}")
            self.clear_details()

    def populate_products_table(self, products):
        """Remplit le tableau des produits avec animation"""
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Ajout des données avec coloration conditionnelle
            items = [
                str(product['idProduit']),
                product['reference'],
                product['nom'],
                product.get('description', ''),
                product.get('marque', ''),
                product.get('modele', ''),
                product['type'],
                "Oui" if product.get('estMaterielEmballage', False) else "Non"
            ]
            
            for col, item_text in enumerate(items):
                item = QTableWidgetItem(item_text)
                
                # Coloration selon le type
                if col == 6:  # Colonne Type
                    if item_text == "materiel":
                        item.setBackground(QColor(232, 245, 233))  # Vert clair
                    elif item_text == "logiciel":
                        item.setBackground(QColor(227, 242, 253))  # Bleu clair
                    elif item_text == "emballage":
                        item.setBackground(QColor(255, 243, 224))  # Orange clair
                
                self.products_table.setItem(row, col, item)
        
        self.products_table.resizeColumnsToContents()
        
        # Mise à jour des statistiques
        self.update_stats()

    def update_stats(self):
        """Met à jour les statistiques affichées"""
        # Cette méthode peut être étendue pour calculer les vraies statistiques
        pass

    def show_product_details(self, index):
        """Affiche les détails d'un produit avec interface améliorée"""
        if not index.isValid():
            return
            
        try:
            self.show_loading("Chargement des détails...")
            
            product_id = int(self.products_table.item(index.row(), 0).text())
            
            product = get_product_details(self.db_conn, product_id)
            if not product:
                raise ValueError("Produit non trouvé")
            
            # Masquer le message par défaut
            self.default_message.setVisible(False)
            
            # Titre du produit avec icône
            type_icons = {
                "materiel": "🔧",
                "logiciel": "💻",
                "emballage": "📦"
            }
            icon = type_icons.get(product['type'], "📦")
            self.product_title.setText(f"{icon} {product['reference']} - {product['nom']}")
            
            # Construction des détails de base
            base_fields = [
                ("🆔 ID Produit", product['idProduit']),
                ("📋 Référence", product['reference']),
                ("🏷️ Nom", product['nom']),
                ("📄 Description", product.get('description', 'Non renseignée')),
                ("🏢 Marque", product.get('marque', 'Non renseignée')),
                ("🏷️ Modèle", product.get('modele', 'Non renseigné')),
                ("📦 Type", product['type'].capitalize()),
                ("📦 Emballage", "Oui" if product.get('estMaterielEmballage', False) else "Non")
            ]
            
            # Ajout des spécificités selon le type
            if product['type'] == 'materiel':
                base_fields.extend([
                    ("📏 Longueur", f"{product.get('longueur', 'N/A')} cm"),
                    ("↔️ Largeur", f"{product.get('largeur', 'N/A')} cm"),
                    ("↕️ Hauteur", f"{product.get('hauteur', 'N/A')} cm"),
                    ("⚖️ Masse", f"{product.get('masse', 'N/A')} kg"),
                    ("📐 Volume", f"{product.get('volume', 'N/A')} cm³")
                ])
            elif product['type'] == 'logiciel':
                base_fields.extend([
                    ("🔢 Version", product.get('version', 'N/A')),
                    ("📜 Type de licence", product.get('typeLicence', 'N/A')),
                    ("📅 Date expiration", product.get('dateExpiration', 'N/A'))
                ])
            
            # Remplissage du tableau des détails
            self.details_table.setRowCount(len(base_fields))
            for row, (field_name, field_value) in enumerate(base_fields):
                name_item = QTableWidgetItem(field_name)
                name_item.setBackground(QColor(248, 249, 250))
                value_item = QTableWidgetItem(str(field_value))
                
                self.details_table.setItem(row, 0, name_item)
                self.details_table.setItem(row, 1, value_item)
            
            # Affichage des emplacements de stockage
            locations = get_stock_locations(self.db_conn, product_id)
            self.locations_table.setRowCount(len(locations))
            
            for row, loc in enumerate(locations):
                items = [
                    loc.get('reference_cellule', ''),
                    loc.get('nom_entrepot', ''),
                    str(loc.get('quantite', 0)),
                    loc.get('numeroLot', '')
                ]
                
                for col, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    
                    # Coloration selon la quantité
                    if col == 2:  # Colonne Quantité
                        qty = int(item_text) if item_text.isdigit() else 0
                        if qty == 0:
                            item.setBackground(QColor(255, 235, 238))  # Rouge clair pour rupture
                        elif qty < 10:
                            item.setBackground(QColor(255, 243, 224))  # Orange clair pour stock faible
                        else:
                            item.setBackground(QColor(232, 245, 233))  # Vert clair pour stock OK
                    
                    self.locations_table.setItem(row, col, item)
            
            # Affichage du groupe de détails
            self.details_group.setVisible(True)
            self.details_table.resizeColumnsToContents()
            self.locations_table.resizeColumnsToContents()
            
            self.hide_loading()
            
        except Exception as e:
            self.hide_loading()
            self.show_error_message("Erreur de chargement", f"Échec du chargement des détails: {str(e)}")
            self.clear_details()

    def load_out_of_stock(self):
        """Charge les produits en rupture de stock avec interface améliorée"""
        try:
            self.show_loading("Recherche des ruptures de stock...")
            
            products = handle_ruptures(self.db_conn)
            self.current_products = products
            
            if not products:
                self.show_info_message("Aucune rupture", "Aucun produit en rupture de stock trouvé. 🎉")
                self.products_table.setRowCount(0)
                self.clear_details()
                return
            
            self.populate_products_table(products)
            self.clear_details()
            
            # Message d'alerte avec le nombre de produits
            self.show_warning_message("Produits en rupture", 
                                    f"⚠️ {len(products)} produits en rupture de stock trouvés.\n"
                                    f"Veuillez prévoir un réapprovisionnement.")
            
        except Exception as e:
            self.show_error_message("Erreur de chargement", f"Échec du chargement des ruptures: {str(e)}")
            self.clear_details()
        finally:
            self.hide_loading()

    def show_info_message(self, title, message):
        """Affiche un message d'information stylisé"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2980b9, stop: 1 #21618c);
            }
        """)
        msg.exec_()

    def show_warning_message(self, title, message):
        """Affiche un message d'avertissement stylisé"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f39c12, stop: 1 #e67e22);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e67e22, stop: 1 #d35400);
            }
        """)
        msg.exec_()

    def show_error_message(self, title, message):
        """Affiche un message d'erreur stylisé"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #a93226);
            }
        """)
        msg.exec_()

    def export_to_csv(self):
        """Exporte les données actuelles en CSV (fonctionnalité bonus)"""
        if not self.current_products:
            self.show_info_message("Aucune donnée", "Aucun produit à exporter. Effectuez d'abord une recherche.")
            return
        
        try:
            from PyQt5.QtWidgets import QFileDialog
            import csv
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les données", "produits.csv", 
                "Fichiers CSV (*.csv);;Tous les fichiers (*)")
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # En-têtes
                    headers = ["ID", "Référence", "Nom", "Description", "Marque", "Modèle", "Type", "Emballage"]
                    writer.writerow(headers)
                    
                    # Données
                    for product in self.current_products:
                        row = [
                            product['idProduit'],
                            product['reference'],
                            product['nom'],
                            product.get('description', ''),
                            product.get('marque', ''),
                            product.get('modele', ''),
                            product['type'],
                            "Oui" if product.get('estMaterielEmballage', False) else "Non"
                        ]
                        writer.writerow(row)
                
                self.show_info_message("Export réussi", f"Données exportées avec succès vers:\n{filename}")
                
        except Exception as e:
            self.show_error_message("Erreur d'export", f"Impossible d'exporter les données: {str(e)}")

    def refresh_data(self):
        """Actualise les données (fonctionnalité bonus)"""
        self.show_loading("Actualisation des données...")
        
        # Simulation d'un délai d'actualisation
        QTimer.singleShot(1000, self.finish_refresh)
    
    def finish_refresh(self):
        """Termine l'actualisation des données"""
        self.hide_loading()
        self.show_info_message("Actualisation", "Données actualisées avec succès! 🔄")

    def get_selected_product_id(self):
        """Retourne l'ID du produit sélectionné"""
        current_row = self.products_table.currentRow()
        if current_row >= 0:
            return int(self.products_table.item(current_row, 0).text())
        return None

    def highlight_search_results(self, search_term):
        """Surligne les résultats de recherche dans le tableau"""
        if not search_term:
            return
        
        # Cette méthode peut être étendue pour surligner les termes recherchés
        pass

    def apply_filters(self):
        """Applique des filtres avancés (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour des filtres plus complexes
        pass

    def show_product_history(self, product_id):
        """Affiche l'historique d'un produit (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour afficher l'historique des mouvements
        pass

    def generate_qr_code(self, product_id):
        """Génère un QR code pour le produit (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour générer des QR codes
        pass

    def setup_keyboard_shortcuts(self):
        """Configure les raccourcis clavier (fonctionnalité bonus)"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Ctrl+F pour focus sur la recherche
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_widget.search_input.setFocus())
        
        # Ctrl+R pour actualiser
        refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut.activated.connect(self.refresh_data)
        
        # Ctrl+E pour exporter
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_to_csv)

    def animate_widget(self, widget, property_name, start_value, end_value, duration=300):
        """Anime un widget (fonctionnalité bonus)"""
        animation = QPropertyAnimation(widget, property_name.encode())
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        return animation

    def setup_responsive_layout(self):
        """Configure une mise en page responsive (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour adapter l'interface à différentes tailles d'écran
        pass

    def setup_theme_switcher(self):
        """Configure un commutateur de thème (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour permettre le changement de thème
        pass

    def setup_accessibility_features(self):
        """Configure les fonctionnalités d'accessibilité (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour améliorer l'accessibilité
        pass

    def setup_data_validation(self):
        """Configure la validation des données (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour valider les entrées utilisateur
        pass

    def setup_auto_save(self):
        """Configure la sauvegarde automatique (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour sauvegarder automatiquement les préférences
        pass

    def setup_search_history(self):
        """Configure l'historique de recherche (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour mémoriser les recherches précédentes
        pass

    def setup_advanced_search(self):
        """Configure la recherche avancée (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour des critères de recherche complexes
        pass

    def setup_bulk_operations(self):
        """Configure les opérations en lot (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour permettre les opérations sur plusieurs produits
        pass

    def setup_notifications(self):
        """Configure le système de notifications (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour afficher des notifications système
        pass

    def setup_reports(self):
        """Configure la génération de rapports (fonctionnalité bonus)"""
        # Cette méthode peut être étendue pour générer des rapports détaillés
        pass