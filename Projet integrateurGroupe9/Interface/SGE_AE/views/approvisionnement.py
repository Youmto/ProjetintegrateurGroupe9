from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QSpinBox, QDateEdit, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QDate
from controllers.approvisionnement_controller import (
    charger_produits_a_approvisionner, ajouter_demande_approvisionnement
)

class ApprovisionnementWindow(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user  # Doit contenir idOrganisation (non utilisé ici car fixé à 1)

        self.setWindowTitle("Approvisionner l'entrepôt")
        self.resize(800, 400)

        self.layout = QVBoxLayout(self)

        # Table des produits
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Bouton de validation
        self.btn_valider = QPushButton("Valider l'approvisionnement sélectionné")
        self.btn_valider.clicked.connect(self.valider_approvisionnement)
        self.layout.addWidget(self.btn_valider)

        self.charger_table()

    def charger_table(self):
        produits = charger_produits_a_approvisionner(self.conn)

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Quantité actuelle", "Quantité à approvisionner", "Date prévue"
        ])
        self.table.setRowCount(len(produits))

        for row, produit in enumerate(produits):
            id_produit = str(produit[0])
            nom_produit = produit[1]
            quantite_actuelle = str(produit[2] if produit[2] is not None else 0)

            # ID Produit (non éditable)
            item_id = QTableWidgetItem(id_produit)
            item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item_id)

            # Nom Produit (non éditable)
            item_nom = QTableWidgetItem(nom_produit)
            item_nom.setFlags(item_nom.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, item_nom)

            # Quantité actuelle (non éditable)
            item_qte = QTableWidgetItem(quantite_actuelle)
            item_qte.setFlags(item_qte.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, item_qte)

            # Champ quantité à approvisionner
            spin_quantite = QSpinBox()
            spin_quantite.setRange(0, 10000)
            spin_quantite.setValue(0)
            self.table.setCellWidget(row, 3, spin_quantite)

            # Champ date de livraison
            date_edit = QDateEdit()
            date_edit.setDate(QDate.currentDate())
            date_edit.setCalendarPopup(True)
            self.table.setCellWidget(row, 4, date_edit)

        # Ajustement auto de la largeur des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def valider_approvisionnement(self):
        id_organisation = 1  # ✅ Ajustement : Organisation fixée à 1 (entrepôt)

        any_approvisionnement = False

        for row in range(self.table.rowCount()):
            try:
                id_produit = int(self.table.item(row, 0).text())
                quantite = self.table.cellWidget(row, 3).value()
                date = self.table.cellWidget(row, 4).date().toPyDate()

                if quantite > 0:
                    ajouter_demande_approvisionnement(
                        self.conn, id_produit, quantite, date, id_organisation
                    )
                    any_approvisionnement = True
            except Exception as e:
                QMessageBox.warning(
                    self, "Erreur",
                    f"Échec pour le produit {id_produit} : {str(e)}"
                )

        if any_approvisionnement:
            QMessageBox.information(
                self, "Succès", "Les approvisionnements ont été enregistrés avec succès."
            )
            self.close()
        else:
            QMessageBox.information(
                self, "Aucun approvisionnement",
                "Aucun produit avec une quantité supérieure à 0 n'a été sélectionné."
            )
