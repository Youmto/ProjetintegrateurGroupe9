from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QCheckBox,
    QMessageBox, QFileDialog, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from controllers.product_controller import (
    handle_get_all_products, handle_add_product, handle_update_product
)
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
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Section formulaire
        form_group = QGroupBox("Informations du produit")
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)

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
        self.emballage_input = QCheckBox("Est un matériel d'emballage")

        # Ajouter les champs au layout en grille
        fields = [
            ("ID", self.id_input),
            ("Référence *", self.ref_input),
            ("Nom *", self.nom_input),
            ("Description", self.desc_input),
            ("Marque", self.marque_input),
            ("Modèle", self.modele_input),
            ("Type", self.type_input),
            ("", self.emballage_input),
        ]

        for i, (label, widget) in enumerate(fields):
            if label:
                form_layout.addWidget(QLabel(label), i, 0)
            form_layout.addWidget(widget, i, 1)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # Table des produits
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Nom", "Description",
            "Marque", "Modèle", "Type", "Emballage"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.select_product)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.table)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(self.add_product)

        edit_btn = QPushButton("Modifier")
        edit_btn.clicked.connect(self.edit_product)

        clear_btn = QPushButton("Réinitialiser")
        clear_btn.clicked.connect(self.clear_form)

        export_btn = QPushButton("Exporter en CSV")
        export_btn.clicked.connect(self.export_to_csv)

        for btn in [add_btn, edit_btn, clear_btn, export_btn]:
            btn.setMinimumWidth(120)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def clear_form(self):
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
        data = handle_get_all_products(self.conn)
        self.table.setRowCount(len(data))

        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["idProduit"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["reference"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["nom"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["description"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(item["marque"] or ""))
            self.table.setItem(row, 5, QTableWidgetItem(item["modele"] or ""))
            self.table.setItem(row, 6, QTableWidgetItem(item["type"]))
            self.table.setItem(row, 7, QTableWidgetItem("Oui" if item["estMaterielEmballage"] else "Non"))

        self.table.resizeColumnsToContents()

    def select_product(self, row, _):
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
        if not self.ref_input.text().strip() or not self.nom_input.text().strip():
            raise ValueError("Les champs Référence et Nom sont obligatoires.")

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
        try:
            data = self.get_form_data()
            handle_add_product(self.conn, data)
            QMessageBox.information(self, "Succès", "Produit ajouté avec succès.")
            self.clear_form()
            self.load_products()
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def edit_product(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un produit à modifier.")
            return

        try:
            data = self.get_form_data()
            handle_update_product(self.conn, self.selected_id, data)
            QMessageBox.information(self, "Succès", "Produit modifié avec succès.")
            self.clear_form()
            self.load_products()
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def export_to_csv(self):
        """Exporte les produits vers un fichier CSV sans ui_utils"""
        data = []
        for row in range(self.table.rowCount()):
            row_data = {}
            for col in range(self.table.columnCount()):
                header = self.table.horizontalHeaderItem(col).text()
                row_data[header] = self.table.item(row, col).text()
            data.append(row_data)
        if not data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en CSV",
            "produits.csv",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)",
            options=options
        )
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                QMessageBox.information(self, "Export", "Exportation réussie !")
            except Exception as e:
                QMessageBox.warning(self, "Export", f"Erreur lors de l'export : {e}")