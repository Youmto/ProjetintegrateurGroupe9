from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QCheckBox, QMessageBox
)
from controllers.product_controller import handle_get_all_products, handle_add_product, handle_update_product

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
        self.ref_input = QLineEdit()
        self.nom_input = QLineEdit()
        self.desc_input = QLineEdit()
        self.marque_input = QLineEdit()
        self.modele_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["logiciel", "materiel"])
        self.emballage_input = QCheckBox("Emballage ?")

        for label, widget in [
            ("ID", self.id_input), 
            ("Référence", self.ref_input), ("Nom", self.nom_input),
            ("Description", self.desc_input), ("Marque", self.marque_input),
            ("Modèle", self.modele_input), ("Type", self.type_input)
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
        self.table.cellClicked.connect(self.select_product)
        layout.addWidget(self.table)

        # Boutons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(self.add_product)
        edit_btn = QPushButton("Modifier")
        edit_btn.clicked.connect(self.edit_product)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_products(self):
        data = handle_get_all_products(self.conn)
        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["idproduit"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["reference"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["nom"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["description"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(item["marque"] or ""))
            self.table.setItem(row, 5, QTableWidgetItem(item["modele"] or ""))
            self.table.setItem(row, 6, QTableWidgetItem(item["type"]))
            self.table.setItem(row, 7, QTableWidgetItem("Oui" if item["estmaterielemballage"] else "Non"))

    def select_product(self, row, _):
        self.selected_id = int(self.table.item(row, 0).text())
        self.ref_input.setText(self.table.item(row, 1).text())
        self.nom_input.setText(self.table.item(row, 2).text())
        self.desc_input.setText(self.table.item(row, 3).text())
        self.marque_input.setText(self.table.item(row, 4).text())
        self.modele_input.setText(self.table.item(row, 5).text())
        self.type_input.setCurrentText(self.table.item(row, 6).text())
        self.emballage_input.setChecked(self.table.item(row, 7).text() == "Oui")

    def get_form_data(self):
        return {
            "reference": self.ref_input.text(),
            "nom": self.nom_input.text(),
            "description": self.desc_input.text(),
            "marque": self.marque_input.text(),
            "modele": self.modele_input.text(),
            "type": self.type_input.currentText(),
            "estMaterielEmballage": self.emballage_input.isChecked()
        }

    def add_product(self):
        try:
            handle_add_product(self.conn, self.get_form_data())
            QMessageBox.information(self, "Ajout", "Produit ajouté")
            self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def edit_product(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Sélection", "Aucun produit sélectionné")
            return
        try:
            handle_update_product(self.conn, self.selected_id, self.get_form_data())
            QMessageBox.information(self, "Modification", "Produit modifié")
            self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
