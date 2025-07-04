from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QPushButton, 
    QLabel, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHBoxLayout, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from controllers.supervision_controller import (
    handle_occupation_cellules, handle_ruptures,
    handle_produits_non_stockes, handle_cellules_vides,
    handle_expeditions_terminées
)
from controllers.approvisionnement_controller import  handle_demandes_approvisionnement 
import csv
from datetime import date

class SupervisionModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.current_data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Sélection du rapport
        self.select = QComboBox()
        self.select.addItems([
            "Occupation des cellules",
            "Produits jamais stockés",
            "Ruptures de stock",
            "Cellules vides",
            "Expéditions terminées",
            "Demandes d'approvisionnement" 
        ])
        layout.addWidget(QLabel("Sélection du rapport de supervision:"))
        layout.addWidget(self.select)

        # Boutons
        btn_layout = QHBoxLayout()
        
        show_btn = QPushButton("Afficher")
        show_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(show_btn)
        
        self.export_btn = QPushButton("Exporter CSV")
        self.export_btn.clicked.connect(self.export_csv)
        self.export_btn.setEnabled(False)
        btn_layout.addWidget(self.export_btn)

        
        layout.addLayout(btn_layout)

        # Zone d'information
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-style: italic; color: #555;")
        layout.addWidget(self.info_label)

        # Tableau
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.setMinimumSize(800, 500)

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
              
                "Demandes d'approvisionnement": handle_demandes_approvisionnement  # <- ajout ici


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

            # Info
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
                         
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {str(e)}")
            self.export_btn.setEnabled(False)


    def update_info_label(self, data, label_text, condition=None):
        """Met à jour le label d'information avec le nombre d'éléments"""
        count = len(data)
        if condition:
            filtered_count = sum(1 for item in data if condition(item))
            self.info_label.setText(f"{count} éléments trouvés ({filtered_count} {label_text})")
        else:
            self.info_label.setText(f"{count} {label_text} trouvés")

    def export_csv(self):
        """Exporte les données au format CSV"""
        if not self.current_data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exporter vers CSV", 
            f"supervision_{date.today().strftime('%Y%m%d')}.csv", 
            "CSV Files (*.csv)"
        )
        
        if not path:
            return

        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.current_data[0].keys(), delimiter=';')
                writer.writeheader()
                writer.writerows(self.current_data)
            QMessageBox.information(self, "Export", f"Exporté avec succès vers {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export", f"Erreur lors de l'export : {str(e)}")