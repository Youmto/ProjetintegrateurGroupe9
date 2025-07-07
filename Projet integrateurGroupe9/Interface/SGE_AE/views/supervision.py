from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QFileDialog,
    QHeaderView, QFrame, QGraphicsDropShadowEffect, # Ajouté pour les composants UI modernes
    QSpacerItem, QSizePolicy # Ajouté pour des layouts flexibles
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont # Ajouté pour le style personnalisé

# Vos imports originaux pour les contrôleurs
from controllers.supervision_controller import (
    handle_occupation_cellules, handle_ruptures,
    handle_produits_non_stockes, handle_cellules_vides,
    handle_expeditions_terminées
)
from controllers.approvisionnement_controller import handle_demandes_approvisionnement
import csv
from datetime import date

# --- Composants d'IU Modernes Réutilisables (Copie de RapportsModule pour la cohérence) ---

class ModernCard(QFrame):
    """Carte moderne avec effet d'ombre, réutilisable pour les sections."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff; /* Fond blanc */
                border-radius: 12px; /* Coins arrondis */
                border: 1px solid #e1e5e9; /* Bordure subtile gris clair */
            }
            QFrame:hover {
                border: 1px solid #3498db; /* Bordure bleue au survol */
                background-color: #f8f9fa; /* Fond légèrement plus clair au survol */
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20) # Douceur de l'ombre
        shadow.setColor(QColor(0, 0, 0, 40)) # Noir, 40 alpha (transparence)
        shadow.setOffset(0, 4) # Décalage de l'ombre (x, y)
        self.setGraphicsEffect(shadow)

class ModernTableWidget(QTableWidget):
    """Tableau moderne avec des styles personnalisés."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                gridline-color: #f1f3f4; /* Lignes entre les cellules */
                font-size: 13px;
                color: #2c3e50; /* Texte gris foncé */
                selection-background-color: #e3f2fd; /* Bleu clair à la sélection */
                selection-color: #1976d2; /* Texte bleu plus foncé à la sélection */
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa; /* Effet de survol subtil */
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef); /* Dégradé pour l'en-tête */
                color: #495057; /* Couleur du texte de l'en-tête */
                padding: 10px 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                font-size: 12px;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e9ecef, stop: 1 #dee2e6);
            }
        """)
        self.setAlternatingRowColors(True) # Maintient les couleurs de ligne alternées
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)

# --- Fonction utilitaire pour l'export CSV (copie de RapportsModule pour la cohérence) ---
def export_table_to_csv_dict(parent_widget, data, filename_prefix="export"):
    path, _ = QFileDialog.getSaveFileName(
        parent_widget,
        "Exporter vers CSV",
        f"{filename_prefix}_{date.today().strftime('%Y%m%d')}.csv",
        "CSV Files (*.csv)"
    )
    if not path:
        return

    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(data)
        QMessageBox.information(parent_widget, "Export", f"Exporté avec succès vers {path}")
    except Exception as e:
        QMessageBox.critical(parent_widget, "Erreur export", f"Erreur lors de l'export CSV : {str(e)}")


class SupervisionModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.current_data = None
        self.setWindowTitle("🔍 Module de Supervision du Stock") # Titre de fenêtre amélioré
        self.setMinimumSize(950, 700) # Taille de fenêtre légèrement plus grande
        self.init_ui()
        self.apply_modern_theme() # Applique le thème général

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30) # Marges plus généreuses
        main_layout.setSpacing(25) # Espacement accru entre les sections majeures
        
        # --- Section En-tête ---
        header_layout = QHBoxLayout()
        title_label = QLabel("📊 Rapports de Supervision du Stock")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50; /* Couleur de titre plus foncée */
            padding-bottom: 10px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # --- Séparateur ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e1e5e9; height: 2px; border-radius: 1px;")
        main_layout.addWidget(separator)

        # --- Section Contrôles (à l'intérieur d'une ModernCard) ---
        controls_card = ModernCard()
        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setSpacing(15)

        controls_title = QLabel("⚙️ Options de Rapports")
        controls_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #34495e;")
        controls_layout.addWidget(controls_title)

        # Layout pour la sélection du rapport
        report_selection_layout = QHBoxLayout()
        report_selection_label = QLabel("Sélection du rapport de supervision :")
        report_selection_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #555;")
        report_selection_layout.addWidget(report_selection_label)

        self.select = QComboBox()
        self.select.addItems([
            "Occupation des cellules",
            "Produits jamais stockés",
            "Ruptures de stock",
            "Cellules vides",
            "Expéditions terminées",
            "Demandes d'approvisionnement"
        ])
        self.select.setStyleSheet("""
            QComboBox {
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 8px 15px;
                background: #fdfefe;
                color: #333;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border-left: 1px solid #dcdfe6;
                width: 30px;
            }
            QComboBox::down-arrow {
                /* image: url(path/to/arrow_down.png); */
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                background-color: #ffffff;
                selection-background-color: #e3f2fd;
                color: #333;
            }
        """)
        report_selection_layout.addWidget(self.select)
        report_selection_layout.addStretch() # Pousse le ComboBox vers la gauche
        controls_layout.addLayout(report_selection_layout)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # Bouton Afficher
        show_btn = QPushButton("📊 Afficher le rapport")
        show_btn.clicked.connect(self.load_data)
        show_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)
        btn_layout.addWidget(show_btn)
        
        # Bouton Exporter CSV
        self.export_btn = QPushButton("📄 Exporter CSV")
        self.export_btn.clicked.connect(self.export_csv)
        self.export_btn.setEnabled(False) # Désactivé par défaut
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219d53;
            }
            QPushButton:disabled {
                background-color: #a2d9c4;
                color: #f0f0f0;
            }
        """)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch() # Pousse les boutons vers la gauche

        controls_layout.addLayout(btn_layout)
        controls_card.setLayout(controls_layout)
        main_layout.addWidget(controls_card)

        # --- Section Tableau (à l'intérieur d'une ModernCard) ---
        table_card = ModernCard()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)

        table_title = QLabel("📋 Résultats du Rapport")
        table_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #34495e;")
        table_layout.addWidget(table_title)

        # Zone d'information (maintenant intégrée dans la carte du tableau)
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-style: italic; color: #555; font-size: 14px;")
        table_layout.addWidget(self.info_label)

        # Utilise ModernTableWidget
        self.table = ModernTableWidget()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # Étire toutes les colonnes par défaut
        table_layout.addWidget(self.table)
        
        table_card.setLayout(table_layout)
        main_layout.addWidget(table_card)
        
        main_layout.addStretch() # Pousse tout vers le haut

        self.setLayout(main_layout)

    def apply_modern_theme(self):
        """Applique le thème moderne général à la fenêtre."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa; /* Fond clair pour la fenêtre */
                font-family: 'Segoe UI', Arial, sans-serif; /* Police moderne */
                color: #333; /* Couleur de texte par défaut */
            }
            QLabel {
                color: #333;
            }
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
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

    def load_data(self):
        try:
            option = self.select.currentText()
            self.current_data = None
            self.info_label.clear()

            controller_map = {
                "Occupation des cellules": handle_occupation_cellules,
                "Produits jamais stockés": handle_produits_non_stockes,
                "Ruptures de stock": handle_ruptures,
                "Cellules vides": handle_cellules_vides,
                "Expéditions terminées": handle_expeditions_terminées,
                "Demandes d'approvisionnement": handle_demandes_approvisionnement
            }

            handler = controller_map.get(option)
            if not handler:
                QMessageBox.warning(self, "Erreur", "Type de rapport non reconnu.")
                return

            data = handler(self.conn)
            self.current_data = data

            if not data:
                self.info_label.setText("Aucune donnée disponible pour ce rapport.")
                self.table.clear()
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                self.export_btn.setEnabled(False)
                return

            headers = list(data[0].keys())
            self.table.clear()
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(data))

            for row, item in enumerate(data):
                for col, header in enumerate(headers):
                    value = item.get(header, "")
                    item_widget = QTableWidgetItem(str(value))

                    # Colorisation conditionnelle
                    if option == "Occupation des cellules" and header == "pourcentage_occupation":
                        try:
                            percent = float(value)
                            item_widget = QTableWidgetItem(f"{percent:.1f}%")
                            if percent > 80:
                                item_widget.setBackground(QColor(255, 200, 200))  # Rouge clair
                            elif percent > 60:
                                item_widget.setBackground(QColor(255, 255, 200))  # Jaune clair
                        except ValueError:
                            pass  # Ignore if not convertible
                    
                    self.table.setItem(row, col, item_widget)

            self.table.resizeColumnsToContents()
            self.export_btn.setEnabled(True)

            # Mise à jour de l'info
            if option == "Occupation des cellules":
                self.update_info_label(data, "cellules chargées à plus de 80%", lambda x: float(x.get('pourcentage_occupation', 0)) > 80)
            elif option == "Produits jamais stockés":
                self.update_info_label(data, "produits jamais stockés")
            elif option == "Ruptures de stock":
                self.update_info_label(data, "produits en rupture")
            elif option == "Cellules vides":
                self.update_info_label(data, "cellules vides")
            elif option == "Expéditions terminées":
                self.update_info_label(data, "expéditions terminées")
            elif option == "Demandes d'approvisionnement":
                self.update_info_label(data, "demandes d'approvisionnement")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {str(e)}")
            self.export_btn.setEnabled(False)

    def update_info_label(self, data, label_text, condition=None):
        """Met à jour le label d'information avec le nombre d'éléments"""
        count = len(data)
        if condition:
            filtered_count = sum(1 for item in data if condition(item))
            self.info_label.setText(f"**{count}** éléments trouvés ({filtered_count} {label_text})") # Texte plus lisible
        else:
            self.info_label.setText(f"**{count}** {label_text} trouvés") # Texte plus lisible

    def export_csv(self):
        """Exporte les données au format CSV (utilise la fonction utilitaire intégrée)"""
        if not self.current_data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return
        # Appel direct de la fonction utilitaire
        export_table_to_csv_dict(self, self.current_data, filename_prefix=self.select.currentText().replace(" ", "_").lower())