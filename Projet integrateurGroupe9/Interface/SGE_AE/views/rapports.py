# views/alertes.py
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

class  RapportsModule(QWidget):
    """Vue dédiée à l'affichage et l'export des alertes"""
    
    def __init__(self, conn,user):
        self.user = user
        super().__init__()
        self.conn = conn
        self.data = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout()

        # Configuration des contrôles
        self.setup_controls(layout)
        
        # Configuration de la table
        self.table = QTableWidget()
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
            ("Exporter CSV", self.export_csv),
            ("Exporter PDF", self.export_pdf),
            ("Afficher graphique", self.show_chart)
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

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

        self.data = controller_map.get(mode, lambda: [])()
        self.update_table()

    def update_table(self):
        """Met à jour l'affichage tabulaire"""
        if not self.data:
            QMessageBox.information(self, "Alerte", "Aucune donnée trouvée.")
            self.table.clear()
            return

        self.table.setRowCount(len(self.data))
        self.table.setColumnCount(len(self.data[0]))
        self.table.setHorizontalHeaderLabels(list(self.data[0].keys()))

        for row, item in enumerate(self.data):
            for col, val in enumerate(item.values()):
                self.table.setItem(row, col, QTableWidgetItem(str(val)))
        
        self.table.resizeColumnsToContents()

    def export_csv(self):
        """Exporte les données au format CSV"""
        if not self.data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exporter vers CSV", 
            "alertes.csv", 
            "CSV Files (*.csv)"
        )
        
        if not path:
            return

        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)
            QMessageBox.information(self, "Export", f"Exporté avec succès vers {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export", str(e))

    def export_pdf(self):
        """Génère un rapport PDF"""
        if not self.data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter vers PDF",
            "alertes.pdf",
            "PDF Files (*.pdf)"
        )

        if not path:
            return

        try:
            self.generate_pdf_report(path)
            QMessageBox.information(self, "Export", f"PDF exporté avec succès: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export PDF", str(e))

    def generate_pdf_report(self, path):
        """Génère le contenu PDF"""
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        
        # En-tête
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, height - 2*cm, f"{self.mode_selector.currentText()}")
        
        # Contenu
        c.setFont("Helvetica", 10)
        y_position = height - 3*cm
        headers = list(self.data[0].keys())
        col_width = 3*cm
        
        # Dessin des en-têtes
        for i, header in enumerate(headers):
            c.drawString(2*cm + i*col_width, y_position, header)
        
        y_position -= 0.5*cm
        
        # Dessin des données
        for row in self.data:
            for i, value in enumerate(row.values()):
                c.drawString(2*cm + i*col_width, y_position, str(value))
            
            y_position -= 0.5*cm
            if y_position < 2*cm:
                c.showPage()
                y_position = height - 2*cm
        
        c.save()

    def show_chart(self):
        """Affiche une visualisation graphique"""
        if not self.data:
            QMessageBox.warning(self, "Graphique", "Aucune donnée à afficher")
            return

        mode = self.mode_selector.currentText()
        plt.figure(figsize=(10, 6))
        
        if mode == "Produits expirant bientôt":
            self.plot_expiration_chart()
        elif mode == "Occupation des cellules":
            self.plot_occupation_chart()
        elif mode == "Produits en rupture":
            self.plot_rupture_chart()
        else:
            QMessageBox.information(self, "Graphique", "Pas de graphique défini pour ce type.")
            return
        
        plt.tight_layout()
        plt.show()

    def plot_expiration_chart(self):
        """Génère le graphique des expirations"""
        noms = [item['nom'] for item in self.data]
        jours = [item['jours_restants'] for item in self.data]
        plt.barh(noms, jours, color='orange')
        plt.xlabel("Jours restants")
        plt.title("Produits expirant bientôt")

    def plot_occupation_chart(self):
        """Génère le graphique d'occupation"""
        noms = [item['reference'] for item in self.data]
        taux = [item['pourcentage_occupation'] for item in self.data]
        plt.barh(noms, taux, color='teal')
        plt.xlabel("% Occupation")
        plt.title("Occupation des cellules")

    def plot_rupture_chart(self):
        """Génère le graphique des ruptures"""
        noms = [item['nom'] for item in self.data]
        plt.bar(noms, [1]*len(noms), color='red')
        plt.title("Produits en rupture")