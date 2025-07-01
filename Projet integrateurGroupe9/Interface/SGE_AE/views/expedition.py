from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QMessageBox
)

from PyQt5.QtCore import QDate, Qt
from controllers.expedition_controller import (
    handle_create_expedition,  handle_pending_expeditions,
    handle_preparation_expedition, handle_colis_by_bon,
    handle_valider_expedition
)
from views.expedition_detail import ExpeditionDetailWindow
def format_date(dt):
 return dt.strftime("%d/%m/%Y") if dt else "—"

class ExpeditionModule(QWidget):
    def __init__(self, db_conn, user):
        super().__init__()
        self.conn = db_conn
        self.user = user
        self.selected_bon_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Gestion des Expéditions")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Section création
        creation_layout = QHBoxLayout()
        self.ref_input = QLineEdit()
        self.date_input = QDateEdit(QDate.currentDate())
        self.priority_input = QComboBox()
        self.priority_input.addItems(["normal", "élevée", "urgente"])
        create_btn = QPushButton("Créer bon")
        create_btn.clicked.connect(self.create_expedition)

        creation_layout.addWidget(QLabel("Référence:"))
        creation_layout.addWidget(self.ref_input)
        creation_layout.addWidget(QLabel("Date prévue:"))
        creation_layout.addWidget(self.date_input)
        creation_layout.addWidget(QLabel("Priorité:"))
        creation_layout.addWidget(self.priority_input)
        creation_layout.addWidget(create_btn)
        layout.addLayout(creation_layout)

        # Table des bons
        self.bons_table = QTableWidget()
        self.bons_table.setColumnCount(6)
        self.bons_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Date création", "Date prévue", "Priorité", "Statut"
        ])
        self.bons_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.bons_table.cellClicked.connect(self.on_bon_selected)
        layout.addWidget(QLabel("Bons d'expédition en attente :"))
        layout.addWidget(self.bons_table)

        # Section préparation colis
        prep_layout = QHBoxLayout()
        self.prod_id_input = QLineEdit()
        self.qte_input = QLineEdit()
        prepare_btn = QPushButton("Préparer colis")
        prepare_btn.clicked.connect(self.prepare_colis)

        prep_layout.addWidget(QLabel("ID Produit:"))
        prep_layout.addWidget(self.prod_id_input)
        prep_layout.addWidget(QLabel("Quantité:"))
        prep_layout.addWidget(self.qte_input)
        prep_layout.addWidget(prepare_btn)
        layout.addLayout(prep_layout)

        # Résumé des colis
        self.colis_table = QTableWidget()
        self.colis_table.setColumnCount(4)
        self.colis_table.setHorizontalHeaderLabels([
            "ID Colis", "Référence", "Date", "Quantité totale"
        ])
        layout.addWidget(QLabel("Colis associés :"))
        layout.addWidget(self.colis_table)

        # Validation finale
        valider_btn = QPushButton("Valider expédition")
        valider_btn.clicked.connect(self.valider_expedition)
        layout.addWidget(valider_btn)

        self.setLayout(layout)
        self.load_bons()
        detail_btn = QPushButton("Ouvrir détails")
        detail_btn.clicked.connect(self.ouvrir_details)
        layout.addWidget(detail_btn)

    def create_expedition(self):
        ref = self.ref_input.text()
        date_prevue = self.date_input.date().toString("yyyy-MM-dd")
        priorite = self.priority_input.currentText()
        if not ref:
            QMessageBox.warning(self, "Champ requis", "Référence obligatoire")
            return
        try:
            bon_id = handle_create_expedition(
                self.conn, ref, date_prevue, priorite, self.user["idIndividu"]
            )
            QMessageBox.information(self, "Succès", f"Bon #{bon_id} créé")
            self.ref_input.clear()
            self.load_bons()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def load_bons(self):
        try:
            bons =  handle_pending_expeditions(self.conn)
            self.bons_table.setRowCount(len(bons))
            for row, b in enumerate(bons):
                self.bons_table.setItem(row, 0, QTableWidgetItem(str(b["idBon"])))
                self.bons_table.setItem(row, 1, QTableWidgetItem(b["reference"]))
                self.bons_table.setItem(row, 2, QTableWidgetItem(format_date(b["dateCreation"])))
                self.bons_table.setItem(row, 3, QTableWidgetItem(format_date(b["dateExpeditionPrevue"])))
                self.bons_table.setItem(row, 4, QTableWidgetItem(b["priorite"]))
                self.bons_table.setItem(row, 5, QTableWidgetItem(b["statut"]))
            self.bons_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def on_bon_selected(self, row, _):
        self.selected_bon_id = int(self.bons_table.item(row, 0).text())
        self.load_colis()

    def load_colis(self):
        if not self.selected_bon_id:
            return
        try:
            colis = handle_colis_by_bon(self.conn, self.selected_bon_id)
            self.colis_table.setRowCount(len(colis))
            for row, c in enumerate(colis):
                self.colis_table.setItem(row, 0, QTableWidgetItem(str(c["idColis"])))
                self.colis_table.setItem(row, 1, QTableWidgetItem(c["reference"]))
                self.colis_table.setItem(row, 2, QTableWidgetItem(format_date(c["dateCreation"])))
                self.colis_table.setItem(row, 3, QTableWidgetItem(str(c["quantite_totale"])))
            self.colis_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement colis échoué: {str(e)}")

    def prepare_colis(self):
        if not self.selected_bon_id:
            QMessageBox.warning(self, "Sélection requise", "Sélectionnez un bon.")
            return
        try:
            produit_id = int(self.prod_id_input.text())
            quantite = int(self.qte_input.text())
            if quantite <= 0:
                raise ValueError("Quantité invalide.")
            colis_id = handle_preparation_expedition(
                self.conn, self.selected_bon_id, produit_id, quantite
            )
            QMessageBox.information(self, "Colis prêt", f"Colis #{colis_id} préparé.")
            self.prod_id_input.clear()
            self.qte_input.clear()
            self.load_colis()
        except ValueError:
            QMessageBox.warning(self, "Erreur de saisie", "Veuillez entrer des nombres valides.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Préparation échouée : {str(e)}")

    def create_expedition(self):
        ref = self.ref_input.text().strip()
        if not ref:
            QMessageBox.warning(self, "Champ requis", "Référence obligatoire")
            return
        try:
            date_prevue = self.date_input.date().toPyDate()
            priorite = self.priority_input.currentText()
            bon_id = handle_create_expedition(
                self.conn, ref, date_prevue, priorite, self.user["idIndividu"]
            )
            QMessageBox.information(self, "Succès", f"Bon #{bon_id} créé")
            self.ref_input.clear()
            self.load_bons()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    

    # Nouvelle méthode :
    def ouvrir_details(self):
        if not self.selected_bon_id:
            QMessageBox.warning(self, "Sélection requise", "Sélectionnez un bon.")
            return
        try:
            self.detail_window = ExpeditionDetailWindow(self.conn, self.user, self.selected_bon_id)
            self.detail_window.show()
            self.detail_window.raise_()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir la fenêtre de détails : {str(e)}")


    def valider_expedition(self):
        """Valide le bon d'expédition sélectionné (passe à 'en_cours')."""
        try:
            row = self.bons_table.currentRow()  # <-- correction ici
            if row < 0:
                QMessageBox.warning(self, "Sélection", "Veuillez sélectionner un bon d’expédition à valider.")
                return

            bon_id = int(self.bons_table.item(row, 0).text())  # <-- correction ici

            handle_valider_expedition(self.conn, bon_id)

            QMessageBox.information(self, "Succès", f"Bon d’expédition #{bon_id} validé avec succès.")
            self.load_bons()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la validation : {e}")
