from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, 
    QCheckBox, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from controllers.product_controller import handle_get_all_products, handle_add_product, handle_update_product
import csv

class ProduitsModule(QWidget):
    def __init__(self, conn, user=None):
        super().__init__()
        self.conn = conn
        self.user = user
        self.selected_id = None
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        # Formulaire
        form_layout = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        self.id_input.setPlaceholderText("Auto-généré")
        self.ref_input = QLineEdit()
        self.nom_input = QLineEdit()
        self.desc_input = QLineEdit()
        self.marque_input = QLineEdit()
        self.modele_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["logiciel", "materiel"])
        self.emballage_input = QCheckBox("Matériel d'emballage ?")

        for label, widget in [
            ("ID", self.id_input), 
            ("Référence*", self.ref_input), 
            ("Nom*", self.nom_input),
            ("Description", self.desc_input), 
            ("Marque", self.marque_input),
            ("Modèle", self.modele_input), 
            ("Type", self.type_input)
        ]:
            box = QVBoxLayout()
            box.addWidget(QLabel(label))
            box.addWidget(widget)
            form_layout.addLayout(box)

        form_layout.addWidget(self.emballage_input)
        layout.addLayout(form_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Nom", "Description", "Marque", "Modèle", "Type", "Emballage"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.select_product)
        layout.addWidget(self.table)

        # Boutons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(self.add_product)
        edit_btn = QPushButton("Modifier")
        edit_btn.clicked.connect(self.edit_product)
        clear_btn = QPushButton("Nouveau")
        clear_btn.clicked.connect(self.clear_form)
        export_btn = QPushButton("Exporter CSV")
        export_btn.clicked.connect(self.export_to_csv)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(export_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def clear_form(self):
        """Réinitialise le formulaire"""
        self.selected_id = None
        self.id_input.clear()
        self.ref_input.clear()
        self.nom_input.clear()
        self.desc_input.clear()
        self.marque_input.clear()
        self.modele_input.clear()
        self.type_input.setCurrentIndex(0)
        self.emballage_input.setChecked(False)
        self.table.clearSelection()

    def load_products(self):
        """Charge tous les produits dans la table"""
        data = handle_get_all_products(self.conn)
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["idProduit"])))  # Correction de la casse
            self.table.setItem(row, 1, QTableWidgetItem(item["reference"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["nom"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["description"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(item["marque"] or ""))
            self.table.setItem(row, 5, QTableWidgetItem(item["modele"] or ""))
            self.table.setItem(row, 6, QTableWidgetItem(item["type"]))
            self.table.setItem(row, 7, QTableWidgetItem("Oui" if item["estMaterielEmballage"] else "Non"))
        
        self.table.resizeColumnsToContents()

    def select_product(self, row, _):
        """Remplit le formulaire avec le produit sélectionné"""
        self.selected_id = int(self.table.item(row, 0).text())
        self.id_input.setText(str(self.selected_id))
        self.ref_input.setText(self.table.item(row, 1).text())
        self.nom_input.setText(self.table.item(row, 2).text())
        self.desc_input.setText(self.table.item(row, 3).text())
        self.marque_input.setText(self.table.item(row, 4).text())
        self.modele_input.setText(self.table.item(row, 5).text())
        self.type_input.setCurrentText(self.table.item(row, 6).text())
        self.emballage_input.setChecked(self.table.item(row, 7).text() == "Oui")

    def get_form_data(self):
        """Valide et retourne les données du formulaire"""
        if not self.ref_input.text().strip() or not self.nom_input.text().strip():
            raise ValueError("Les champs Référence et Nom sont obligatoires")
            
        return {
            "reference": self.ref_input.text().strip(),
            "nom": self.nom_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "marque": self.marque_input.text().strip(),
            "modele": self.modele_input.text().strip(),
            "type": self.type_input.currentText(),
            "estMaterielEmballage": self.emballage_input.isChecked()
        }

    def add_product(self):
        """Ajoute un nouveau produit"""
        try:
            product_data = self.get_form_data()
            handle_add_product(self.conn, product_data)
            QMessageBox.information(self, "Succès", "Produit ajouté avec succès")
            self.clear_form()
            self.load_products()
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def edit_product(self):
        """Modifie un produit existant"""
        if self.selected_id is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit à modifier")
            return
            
        try:
            product_data = self.get_form_data()
            handle_update_product(self.conn, self.selected_id, product_data)
            QMessageBox.information(self, "Succès", "Produit modifié avec succès")
            self.clear_form()
            self.load_products()
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def export_to_csv(self):
        """Exporte les produits vers un fichier CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les produits", "", "Fichiers CSV (*.csv)")
            
            if not filename:
                return
                
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # En-têtes
                headers = [self.table.horizontalHeaderItem(i).text() 
                          for i in range(self.table.columnCount())]
                writer.writerow(headers)
                
                # Données
                for row in range(self.table.rowCount()):
                    row_data = [
                        self.table.item(row, col).text() 
                        for col in range(self.table.columnCount())
                    ]
                    writer.writerow(row_data)
                    
            QMessageBox.information(self, "Export réussi", 
                                   "Les produits ont été exportés avec succès")
                                   
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de l'export : {str(e)}")