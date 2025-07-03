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
        self.user = user

        self.setWindowTitle("📦 Approvisionner l'entrepôt")
        self.resize(850, 450)

        self.layout = QVBoxLayout(self)

        # Table stylisée
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Bouton stylé avec emoji
        self.btn_valider = QPushButton("✅ Valider l'approvisionnement sélectionné")
        self.btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-weight: bold;
                border-radius: 7px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        self.btn_valider.clicked.connect(self.valider_approvisionnement)
        self.layout.addWidget(self.btn_valider)

        self.charger_table()

        # Style global pour la table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fdfefe;
                alternate-background-color: #ecf0f1;
                font-size: 13px;
                gridline-color: #dcdde1;
            }
            QHeaderView::section {
                background-color: #2980b9;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        self.table.setAlternatingRowColors(True)

    def charger_table(self):
        produits = charger_produits_a_approvisionner(self.conn)

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom du produit", "Quantité actuelle", "Quantité à approvisionner", "Date prévue"
        ])
        self.table.setRowCount(len(produits))

        for row, produit in enumerate(produits):
            id_produit = str(produit[0])
            nom_produit = produit[1]
            quantite_actuelle = str(produit[2] if produit[2] is not None else 0)

            # ID Produit non éditable
            item_id = QTableWidgetItem(id_produit)
            item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item_id)

            # Nom Produit non éditable
            item_nom = QTableWidgetItem(nom_produit)
            item_nom.setFlags(item_nom.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, item_nom)

            # Quantité actuelle non éditable
            item_qte = QTableWidgetItem(quantite_actuelle)
            item_qte.setFlags(item_qte.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, item_qte)

            # SpinBox quantité à approvisionner avec focus visible
            spin_quantite = QSpinBox()
            spin_quantite.setRange(0, 10000)
            spin_quantite.setValue(0)
            spin_quantite.setStyleSheet("""
                QSpinBox {
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 3px 8px;
                    font-size: 13px;
                }
                QSpinBox:focus {
                    border-color: #2980b9;
                    background-color: #eaf4fc;
                }
            """)
            self.table.setCellWidget(row, 3, spin_quantite)

            # DateEdit avec popup calendrier et style
            date_edit = QDateEdit()
            date_edit.setDate(QDate.currentDate())
            date_edit.setCalendarPopup(True)
            date_edit.setStyleSheet("""
                QDateEdit {
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 3px 6px;
                    font-size: 13px;
                }
                QDateEdit:focus {
                    border-color: #2980b9;
                    background-color: #eaf4fc;
                }
            """)
            self.table.setCellWidget(row, 4, date_edit)

        # Ajustement des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def valider_approvisionnement(self):
        id_organisation = 1  # Organisation fixe

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
                    self, "⚠️ Erreur",
                    f"Échec pour le produit {id_produit} : {str(e)}"
                )

        if any_approvisionnement:
            QMessageBox.information(
                self, "🎉 Succès",
                "Les approvisionnements ont été enregistrés avec succès."
            )
            self.charger_table()
            self.table.scrollToTop()
        else:
            QMessageBox.information(
                self, "ℹ️ Aucun approvisionnement",
                "Aucun produit avec une quantité supérieure à 0 n'a été sélectionné."
            )
