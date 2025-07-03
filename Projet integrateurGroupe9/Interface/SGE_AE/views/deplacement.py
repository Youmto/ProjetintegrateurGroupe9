from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from controllers.deplacement_controller import handle_deplacement
from models.stock_model import get_cellule_details, get_product_details


class DeplacementModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("📦 Déplacement de lots")
        self.setMinimumWidth(400)
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setFormAlignment(Qt.AlignCenter)
        layout.setVerticalSpacing(15)

        # Style global de la fenêtre
        self.setStyleSheet("""
            QWidget {
                background-color: #f9faff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit, QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 6px 8px;
                background: white;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #2980b9;
                background: #eaf4fc;
            }
            QPushButton {
                background-color: #2980b9;
                color: white;
                border-radius: 7px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)

        # Champs avec placeholders et emojis
        self.lot_input = QLineEdit()
        self.lot_input.setPlaceholderText("Ex: 12345")
        self.src_cellule_input = QLineEdit()
        self.src_cellule_input.setPlaceholderText("Ex: 10")
        self.dest_cellule_input = QLineEdit()
        self.dest_cellule_input.setPlaceholderText("Ex: 20")
        self.quantite_input = QSpinBox()
        self.quantite_input.setRange(1, 100_000)
        self.quantite_input.setValue(1)

        layout.addRow("📄 ID du lot :", self.lot_input)
        layout.addRow("📍 Cellule source :", self.src_cellule_input)
        layout.addRow("🏁 Cellule destination :", self.dest_cellule_input)
        layout.addRow("🔢 Quantité à déplacer :", self.quantite_input)

        self.btn_deplacer = QPushButton("🚚 Exécuter le déplacement")
        self.btn_deplacer.clicked.connect(self.effectuer_deplacement)
        layout.addRow(self.btn_deplacer)

        self.setLayout(layout)

    def clear_fields(self):
        self.lot_input.clear()
        self.src_cellule_input.clear()
        self.dest_cellule_input.clear()
        self.quantite_input.setValue(1)

    def effectuer_deplacement(self):
        try:
            # Validation simple des entrées
            if not (self.lot_input.text().isdigit() and
                    self.src_cellule_input.text().isdigit() and
                    self.dest_cellule_input.text().isdigit()):
                QMessageBox.warning(self, "⚠️ Entrée invalide", 
                    "Tous les champs doivent contenir des entiers valides.")
                return

            id_lot = int(self.lot_input.text())
            cellule_src = int(self.src_cellule_input.text())
            cellule_dest = int(self.dest_cellule_input.text())
            quantite = self.quantite_input.value()
            responsable_id = self.user['idIndividu']

            # 🔍 Récupération infos cellule destination
            cellule_info = get_cellule_details(self.conn, cellule_dest)

            # 🔍 Récupérer info produit via lot
            from models.stock_model import get_lot_info
            lot_info = get_lot_info(self.conn, id_lot)
            id_produit = lot_info['idProduit']

            produit = get_product_details(self.conn, id_produit)

            # 💥 Vérif capacité cellule
            reste_capacite = cellule_info["capacite_max"] - cellule_info["quantite_totale"]
            if quantite > reste_capacite:
                QMessageBox.warning(self, "🚫 Capacité insuffisante",
                    f"La cellule ne peut accueillir que {reste_capacite} unités.")
                return

            # 💥 Vérif volume si matériel
            if produit["type"] == "materiel":
                volume_unit = produit.get("volume", 0)
                volume_total = volume_unit * quantite
                if volume_total > cellule_info["volume_restant"]:
                    QMessageBox.warning(self, "🚫 Volume insuffisant",
                        f"La cellule ne peut contenir que {cellule_info['volume_restant']} cm³ restants.")
                    return

            # ✅ Appel déplacement
            success = handle_deplacement(self.conn, id_lot, cellule_src, cellule_dest, quantite, responsable_id)
            if success:
                QMessageBox.information(self, "✅ Succès", f"Le lot {id_lot} a été déplacé avec succès.")
                self.clear_fields()
            else:
                QMessageBox.warning(self, "❌ Échec", "Le déplacement n'a pas pu être effectué.")

        except Exception as e:
            QMessageBox.critical(self, "🔥 Erreur", f"Erreur lors du déplacement :\n{str(e)}")
