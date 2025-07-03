from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSpinBox, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QHBoxLayout, QComboBox
)
from PyQt5.QtCore import Qt
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


class RapportsModule(QWidget):
    """Vue dédiée à l'affichage et l'export des alertes"""
    
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.data = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout()

        # Configuration des contrôles
        self.setup_controls(layout)
        
        # Configuration de la table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.setMinimumSize(800, 600)

    def setup_controls(self, layout):
        """Configure les éléments interactifs"""
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "Produits expirant bientôt",
            "Produits en rupture",
            "Occupation des cellules",
            "Produits jamais stockés",
            "Cellules vides"
        ])
        layout.addWidget(QLabel("Type d'alerte :"))
        layout.addWidget(self.mode_selector)

        self.jours = QSpinBox()
        self.jours.setRange(1, 365)
        self.jours.setValue(30)
        layout.addWidget(QLabel("Délai (jours) pour expiration :"))
        layout.addWidget(self.jours)

        btn_layout = QHBoxLayout()
        buttons = [
            ("Rechercher", self.load_data),
            ("Effacer", self.clear_table),
            ("Exporter CSV", self.export_csv),
            ("Exporter PDF", self.export_pdf),
            ("Afficher graphique", self.show_chart)
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

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
        """Exporte les données au format CSV (sans ui_utils)"""
        if not self.data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter vers CSV",
            f"alertes_{date.today().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys(), delimiter=';')
                writer.writeheader()
                writer.writerows(self.data)
            QMessageBox.information(self, "Export", f"Exporté avec succès vers {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export", f"Erreur lors de l'export CSV : {str(e)}")

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
        
        # En-tête
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, height - 2*cm, f"{self.mode_selector.currentText()} - {date.today().strftime('%d/%m/%Y')}")
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, height - 2.5*cm, f"Généré par : {self.user.get('nom', 'Utilisateur inconnu')}")
        
        # Contenu
        c.setFont("Helvetica", 10)
        y_position = height - 3.5*cm
        headers = list(self.data[0].keys())
        col_width = 3*cm
        
        # Dessin des en-têtes
        for i, header in enumerate(headers):
            c.drawString(2*cm + i*col_width, y_position, header)
        
        y_position -= 0.7*cm
        c.line(2*cm, y_position + 0.2*cm, 2*cm + len(headers)*col_width, y_position + 0.2*cm)
        y_position -= 0.5*cm
        
        # Dessin des données
        for row_idx, row in enumerate(self.data):
            for i, header in enumerate(headers):
                c.drawString(2*cm + i*col_width, y_position, str(row.get(header, '')))
            
            y_position -= 0.7*cm
            if y_position < 2*cm and row_idx < len(self.data) - 1:
                # Pied de page
                c.setFont("Helvetica", 8)
                c.drawString(2*cm, 1.5*cm, f"Page {page_num}")
                c.showPage()
                page_num += 1
                y_position = height - 2*cm
                
                # Nouvelle page
                c.setFont("Helvetica-Bold", 14)
                c.drawString(2*cm, height - 2*cm, f"{self.mode_selector.currentText()} (suite)")
                c.setFont("Helvetica", 10)
                y_position = height - 3*cm
                
                # Réafficher les en-têtes
                for i, header in enumerate(headers):
                    c.drawString(2*cm + i*col_width, y_position, header)
                y_position -= 0.7*cm
                c.line(2*cm, y_position + 0.2*cm, 2*cm + len(headers)*col_width, y_position + 0.2*cm)
                y_position -= 0.5*cm
        
        # Pied de page final
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, 1.5*cm, f"Page {page_num}")
        c.save()

    def show_chart(self):
        """Affiche une visualisation graphique"""
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
            return

        plt.tight_layout()
        plt.show()

    def plot_expiration_chart(self):
        """Génère le graphique des expirations"""
        # Tri des données par jours restants
        sorted_data = sorted(self.data, key=lambda x: x['jours_restants'])
        noms = [item['nom'] for item in sorted_data]
        jours = [item['jours_restants'] for item in sorted_data]
        
        bars = plt.barh(noms, jours, color='orange')
        plt.xlabel("Jours restants")
        plt.title(f"Produits expirant dans moins de {self.jours.value()} jours")
        
        # Ajout des valeurs sur les barres
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}', ha='left', va='center')

    def plot_occupation_chart(self):
        """Génère le graphique d'occupation"""
        # Tri des données par pourcentage
        sorted_data = sorted(self.data, key=lambda x: x['pourcentage_occupation'])
        noms = [item['reference'] for item in sorted_data]
        taux = [item['pourcentage_occupation'] for item in sorted_data]
        
        bars = plt.barh(noms, taux, color='teal')
        plt.xlabel("% Occupation")
        plt.title("Occupation des cellules")
        plt.xlim(0, 100)
        
        # Ajout des valeurs sur les barres
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 1, bar.get_y() + bar.get_height()/2,
                    f'{width:.1f}%', ha='left', va='center')

    def plot_rupture_chart(self):
        """Génère le graphique des ruptures"""
        noms = [item['nom'] for item in self.data if 'nom' in item]
        plt.bar(noms, [1]*len(noms), color='red')
        plt.title("Produits en rupture de stock")
        plt.yticks([])  # Masquer l'axe Y
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

        # Ajout des labels sur les barres
        for i, nom in enumerate(noms):
            plt.text(i, 0.5, nom, ha='center', va='center', rotation=90, color='white')

        plt.xticks(rotation=45)  # optionnel si beaucoup de produits
# fichiers utilitaires a creer: charts.py et ui_utils.py

# charts.py
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

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

# ui_utils.py
import csv
from datetime import date
from PyQt5.QtWidgets import QFileDialog, QMessageBox

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
