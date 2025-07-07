from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSpinBox, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QHBoxLayout, QComboBox,
    QHeaderView, QFrame, QGraphicsDropShadowEffect,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

# Vos imports originaux pour les contrôleurs
from controllers.supervision_controller import (
    handle_expirations,
    handle_ruptures,
    handle_occupation_cellules,
    handle_produits_non_stockes,
    handle_cellules_vides
)
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
from datetime import date
from matplotlib.ticker import MaxNLocator

# --- Composants d'IU Modernes Réutilisables ---

class ModernCard(QFrame):
    """Carte moderne avec effet d'ombre, réutilisable pour les sections."""
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
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
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
                gridline-color: #f1f3f4;
                font-size: 13px;
                color: #2c3e50;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
                color: #495057;
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
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)


# --- Fonctions utilitaires intégrées (étaient dans charts.py et ui_utils.py) ---

def plot_expiration(data, jours):
    sorted_data = sorted(data, key=lambda x: x['jours_restants'])
    noms = [item['nom'] for item in sorted_data]
    jours_list = [item['jours_restants'] for item in sorted_data]

    bars = plt.barh(noms, jours_list, color='orange')
    plt.xlabel("Jours restants")
    plt.title(f"Produits expirant dans moins de {jours} jours")

    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                 f'{int(width)}', ha='left', va='center')

def plot_occupation(data):
    sorted_data = sorted(data, key=lambda x: x['pourcentage_occupation'])
    noms = [item['reference'] for item in sorted_data]
    taux = [item['pourcentage_occupation'] for item in sorted_data]

    bars = plt.barh(noms, taux, color='teal')
    plt.xlabel("% Occupation")
    plt.title("Occupation des cellules")
    plt.xlim(0, 100)

    for bar in bars:
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2,
                 f'{width:.1f}%', ha='left', va='center')

def plot_rupture(data):
    noms = [item['nom'] for item in data if 'nom' in item]
    plt.bar(noms, [1]*len(noms), color='red')
    plt.title("Produits en rupture de stock")
    plt.yticks([])
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    for i, nom in enumerate(noms):
        plt.text(i, 0.5, nom, ha='center', va='center', rotation=90, color='white')
    plt.xticks(rotation=45)

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


class RapportsModule(QWidget):
    """Vue dédiée à l'affichage et l'export des alertes"""
    
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.data = None
        self.setWindowTitle("📊 Module de Rapports & Alertes")
        self.setMinimumSize(950, 700)
        self.init_ui()
        self.apply_modern_theme()

    def init_ui(self):
        """Initialise l'interface utilisateur avec un design moderne"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # --- Section En-tête ---
        header_layout = QHBoxLayout()
        title_label = QLabel("📊 Rapports et Supervision du Stock")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
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

        controls_title = QLabel("⚙️ Options de Filtrage et Actions")
        controls_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #34495e;")
        controls_layout.addWidget(controls_title)

        # Layout pour les SpinBox et ComboBox
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)

        type_label = QLabel("Type de rapport :")
        type_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #555;")
        input_layout.addWidget(type_label)
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "Produits expirant bientôt",
            "Produits en rupture",
            "Occupation des cellules",
            "Produits jamais stockés",
            "Cellules vides"
        ])
        self.mode_selector.setStyleSheet("""
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
                /* Si vous avez des icônes pour les flèches, mettez le chemin ici */
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
        input_layout.addWidget(self.mode_selector)

        input_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        days_label = QLabel("Délai (jours) pour expiration :")
        days_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #555;")
        input_layout.addWidget(days_label)
        self.jours = QSpinBox()
        self.jours.setRange(1, 365)
        self.jours.setValue(30)
        self.jours.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 8px 10px;
                background: #fdfefe;
                color: #333;
                font-size: 14px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
                border: none;
                background: #f0f0f0;
                border-left: 1px solid #dcdfe6;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                /* Si vous avez des icônes pour les flèches, mettez le chemin ici */
                /* image: url(path/to/arrow_up.png); */
                width: 12px;
                height: 12px;
            }
            QSpinBox::down-button {
                border-top-right-radius: 0;
                border-bottom-right-radius: 0;
                border-bottom-left-radius: 6px;
                border-top-left-radius: 6px;
            }
        """)
        input_layout.addWidget(self.jours)
        input_layout.addStretch()

        controls_layout.addLayout(input_layout)

        # Layout des boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        buttons_config = [
            ("Rechercher", "🔍", self.load_data, "#3498db"),
            ("Effacer", "🗑️", self.clear_table, "#e74c3c"),
            ("Exporter CSV", "📄", self.export_csv, "#2ecc71"),
            ("Exporter PDF", "📜", self.export_pdf, "#e67e22"),
            ("Afficher graphique", "📈", self.show_chart, "#9b59b6")
        ]
        
        for text, icon, callback, color in buttons_config:
            btn = QPushButton(f"{icon} {text}")
            btn.clicked.connect(callback)
            # IMPORTANT: Removed 'transform' properties
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                    min-width: 120px;
                }}
                QPushButton:hover {{
                    background-color: {color[:-2]}a0; /* Slightly darker on hover */
                }}
                QPushButton:pressed {{
                    background-color: {color[:-2]}b0; /* Even darker on press */
                }}
            """)
            btn_layout.addWidget(btn)

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

        self.table = ModernTableWidget()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.table)
        
        table_card.setLayout(table_layout)
        main_layout.addWidget(table_card)
        
        main_layout.addStretch()

        self.setLayout(main_layout)

    def apply_modern_theme(self):
        """Applique le thème moderne général à la fenêtre."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #333;
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

    def clear_table(self):
        """Efface les résultats affichés"""
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.data = None

    def load_data(self):
        """Charge les données via le contrôleur"""
        mode = self.mode_selector.currentText()
        controller_map = {
            "Produits expirant bientôt": lambda: handle_expirations(self.conn, self.jours.value()),
            "Produits en rupture": lambda: handle_ruptures(self.conn),
            "Occupation des cellules": lambda: handle_occupation_cellules(self.conn),
            "Produits jamais stockés": lambda: handle_produits_non_stockes(self.conn),
            "Cellules vides": lambda: handle_cellules_vides(self.conn)
        }

        try:
            self.data = controller_map.get(mode, lambda: [])()
            if not self.data:
                QMessageBox.information(self, "Information", "Aucune donnée trouvée.")
            self.update_table()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {str(e)}")

    def update_table(self):
        """Met à jour l'affichage tabulaire"""
        if not self.data:
            self.clear_table()
            return

        self.table.setRowCount(len(self.data))
        self.table.setColumnCount(len(self.data[0]))
        self.table.setHorizontalHeaderLabels(list(self.data[0].keys()))

        for row, item in enumerate(self.data):
            for col, (key, val) in enumerate(item.items()):
                self.table.setItem(row, col, QTableWidgetItem(str(val)))
        
        self.table.resizeColumnsToContents()

    def export_csv(self):
        """Exporte les données au format CSV."""
        if not self.data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return
        
        export_table_to_csv_dict(self, self.data, filename_prefix=self.mode_selector.currentText().replace(" ", "_").lower())


    def export_pdf(self):
        """Génère un rapport PDF"""
        if not self.data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter vers PDF",
            f"alertes_{date.today().strftime('%Y%m%d')}.pdf",
            "PDF Files (*.pdf)"
        )

        if not path:
            return

        try:
            self.generate_pdf_report(path)
            QMessageBox.information(self, "Export", f"PDF exporté avec succès: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export PDF", f"Erreur lors de l'export PDF : {str(e)}")

    def generate_pdf_report(self, path):
        """Génère le contenu PDF"""
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        page_num = 1
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, height - 2*cm, f"{self.mode_selector.currentText()} - {date.today().strftime('%d/%m/%Y')}")
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, height - 2.5*cm, f"Généré par : {self.user.get('nom', 'Utilisateur inconnu')}")
        
        c.setFont("Helvetica", 10)
        y_position = height - 3.5*cm
        headers = list(self.data[0].keys())
        col_width = (width - 4*cm) / len(headers) 
        
        for i, header in enumerate(headers):
            c.drawString(2*cm + i*col_width, y_position, header)
        
        y_position -= 0.7*cm
        c.line(2*cm, y_position + 0.2*cm, 2*cm + len(headers)*col_width, y_position + 0.2*cm)
        y_position -= 0.5*cm
        
        for row_idx, row in enumerate(self.data):
            for i, header in enumerate(headers):
                c.drawString(2*cm + i*col_width, y_position, str(row.get(header, '')))
            
            y_position -= 0.7*cm
            if y_position < 2*cm and row_idx < len(self.data) - 1:
                c.setFont("Helvetica", 8)
                c.drawString(2*cm, 1.5*cm, f"Page {page_num}")
                c.showPage()
                page_num += 1
                y_position = height - 2*cm
                
                c.setFont("Helvetica-Bold", 14)
                c.drawString(2*cm, height - 2*cm, f"{self.mode_selector.currentText()} (suite)")
                c.setFont("Helvetica", 10)
                y_position = height - 3*cm
                
                for i, header in enumerate(headers):
                    c.drawString(2*cm + i*col_width, y_position, header)
                y_position -= 0.7*cm
                c.line(2*cm, y_position + 0.2*cm, 2*cm + len(headers)*col_width, y_position + 0.2*cm)
                y_position -= 0.5*cm
        
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, 1.5*cm, f"Page {page_num}")
        c.save()

    def show_chart(self):
        """Affiche une visualisation graphique."""
        if not self.data:
            QMessageBox.warning(self, "Graphique", "Aucune donnée à afficher")
            return

        mode = self.mode_selector.currentText()
        plt.figure(figsize=(10, 6))
        plt.style.use('ggplot')

        if mode == "Produits expirant bientôt":
            plot_expiration(self.data, self.jours.value())
        elif mode == "Occupation des cellules":
            plot_occupation(self.data)
        elif mode == "Produits en rupture":
            plot_rupture(self.data)
        else:
            QMessageBox.information(self, "Graphique", "Pas de graphique défini pour ce type.")
            plt.close() 
            return

        try:
            plt.show(block=False) 
        except Exception as e:
           
            QMessageBox.critical(self, "Erreur Graphique", f"Erreur lors de l'affichage du graphique : {str(e)}\n"
                                                           "Veuillez fermer toutes les fenêtres de graphique existantes.")
            plt.close('all')