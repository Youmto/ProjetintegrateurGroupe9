from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout
)
from controllers.expedition_controller import handle_annulation_colis, handle_colis_prets

class ExpeditionDetailWindow(QWidget):
    def __init__(self, db_conn, user, expedition_id):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.expedition_id = expedition_id
        self.setWindowTitle(f"Colis pour Bon #{expedition_id}")
        self.setMinimumSize(800, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel(f"Colis liés au bon #{self.expedition_id}")
        self.title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.title)

        self.colis_table = QTableWidget()
        self.colis_table.setColumnCount(7)
        self.colis_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Date création", "Bon d’expédition",
            "Date prévue", "Nb lots", "Quantité totale"
        ])
        layout.addWidget(self.colis_table)

        btns = QHBoxLayout()
        annuler_btn = QPushButton("Annuler colis sélectionné")
        annuler_btn.clicked.connect(self.annuler_colis_selectionne)
        btns.addWidget(annuler_btn)

        refresh_btn = QPushButton("Rafraîchir")
        refresh_btn.clicked.connect(self.charger_colis_prets)
        btns.addWidget(refresh_btn)

        layout.addLayout(btns)
        self.setLayout(layout)

        self.charger_colis_prets()

    def annuler_colis_selectionne(self):
        selected_row = self.colis_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un colis à annuler.")
            return

        colis_id = int(self.colis_table.item(selected_row, 0).text())
        try:
            handle_annulation_colis(self.db_conn, colis_id)
            QMessageBox.information(self, "Succès", f"Colis #{colis_id} annulé.")
            self.charger_colis_prets()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de l'annulation : {str(e)}")

    def charger_colis_prets(self):
        try:
            data = handle_colis_prets(self.db_conn, self.expedition_id)
            self.colis_table.setRowCount(len(data))
            for row, item in enumerate(data):
                self.colis_table.setItem(row, 0, QTableWidgetItem(str(item['idColis'])))
                self.colis_table.setItem(row, 1, QTableWidgetItem(item['reference']))
                self.colis_table.setItem(row, 2, QTableWidgetItem(item['date_creation'].strftime("%d/%m/%Y")))
                self.colis_table.setItem(row, 3, QTableWidgetItem(item['bon_expedition']))
                self.colis_table.setItem(row, 4, QTableWidgetItem(item['date_expedition_prevue'].strftime("%d/%m/%Y")))
                self.colis_table.setItem(row, 5, QTableWidgetItem(str(item['nb_lots'])))
                self.colis_table.setItem(row, 6, QTableWidgetItem(str(item['quantite_totale'])))
            self.colis_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les colis : {str(e)}")
