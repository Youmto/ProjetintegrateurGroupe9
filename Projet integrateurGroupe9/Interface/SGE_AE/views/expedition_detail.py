from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from controllers.expedition_controller import (
    handle_get_colis_by_bon,
    handle_get_contenu_colis,
    handle_get_exceptions,
    handle_valider_expedition,
    handle_generer_bordereau_pdf,
)
import os

def format_date(dt):
    return dt.strftime("%d/%m/%Y") if dt else "—"

class ExpeditionDetailWindow(QWidget):
    def __init__(self, db_conn, user, expedition_id):
        super().__init__()
        self.conn = db_conn
        self.user = user
        self.expedition_id = expedition_id
        self.setWindowTitle(f"Détail de l'expédition #{expedition_id}")
        self.setMinimumSize(950, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel(f"Colis associés au bon #{self.expedition_id}")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.colis_table = QTableWidget()
        self.colis_table.setColumnCount(4)
        self.colis_table.setHorizontalHeaderLabels(["ID Colis", "Référence", "Date création", "Statut"])
        self.colis_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.colis_table.doubleClicked.connect(self.show_contenu_colis)
        layout.addWidget(QLabel("Colis préparés :"))
        layout.addWidget(self.colis_table)

        self.resume_label = QLabel("Résumé du contenu du colis")
        self.resume_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(self.resume_label)

        self.resume_table = QTableWidget()
        self.resume_table.setColumnCount(4)
        self.resume_table.setHorizontalHeaderLabels(["Lot", "Date prod.", "Qté", "Date exp."])
        layout.addWidget(self.resume_table)

        self.exceptions_label = QLabel("Rapports d'exception")
        self.exceptions_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(self.exceptions_label)

        self.exceptions_table = QTableWidget()
        self.exceptions_table.setColumnCount(3)
        self.exceptions_table.setHorizontalHeaderLabels(["Date", "Type", "Description"])
        layout.addWidget(self.exceptions_table)

        # Boutons
        btns = QHBoxLayout()
        valider_btn = QPushButton("Valider l'expédition")
        valider_btn.clicked.connect(self.valider_expedition)
        btns.addWidget(valider_btn)

        pdf_btn = QPushButton("Générer le bordereau PDF")
        pdf_btn.clicked.connect(self.generer_pdf)
        btns.addWidget(pdf_btn)

        refresh_btn = QPushButton("Rafraîchir")
        refresh_btn.clicked.connect(self.load_data)
        btns.addWidget(refresh_btn)

        layout.addLayout(btns)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        try:
            colis_list = handle_get_colis_by_bon(self.conn, self.expedition_id)
            self.colis_table.setRowCount(len(colis_list))

            for row, colis in enumerate(colis_list):
                self.colis_table.setItem(row, 0, QTableWidgetItem(str(colis['idColis'])))
                self.colis_table.setItem(row, 1, QTableWidgetItem(colis['reference']))
                self.colis_table.setItem(row, 2, QTableWidgetItem(format_date(colis['dateCreation'])))
                self.colis_table.setItem(row, 3, QTableWidgetItem(colis['statut']))
            self.colis_table.resizeColumnsToContents()

            if colis_list:
                self.colis_table.selectRow(0)
                self.show_contenu_colis()

            exceptions = handle_get_exceptions(self.conn, self.expedition_id)
            self.exceptions_table.setRowCount(len(exceptions))
            for row, ex in enumerate(exceptions):
                self.exceptions_table.setItem(row, 0, QTableWidgetItem(format_date(ex['date'])))
                self.exceptions_table.setItem(row, 1, QTableWidgetItem(ex.get('type', '—')))
                self.exceptions_table.setItem(row, 2, QTableWidgetItem(ex['description']))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement échoué : {e}")

    def show_contenu_colis(self):
        try:
            row = self.colis_table.currentRow()
            if row < 0:
                return
            id_colis = int(self.colis_table.item(row, 0).text())
            contenu = handle_get_contenu_colis(self.conn, id_colis)
            self.resume_table.setRowCount(len(contenu))
            for r, item in enumerate(contenu):
                self.resume_table.setItem(r, 0, QTableWidgetItem(item.get('numeroLot', '')))
                self.resume_table.setItem(r, 1, QTableWidgetItem(format_date(item.get('dateProduction'))))
                self.resume_table.setItem(r, 2, QTableWidgetItem(str(item.get('quantite'))))
                self.resume_table.setItem(r, 3, QTableWidgetItem(format_date(item.get('dateExpiration'))))
            self.resume_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'affichage du contenu : {str(e)}")

    def valider_expedition(self):
        try:
            handle_valider_expedition(self.conn, self.expedition_id)
            QMessageBox.information(self, "Succès", "Expédition validée avec succès.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de validation : {str(e)}")

    def generer_pdf(self):
        try:
            file_path = handle_generer_bordereau_pdf(self.conn, self.expedition_id)
            if os.path.exists(file_path):
                QMessageBox.information(self, "PDF généré", f"Bordereau enregistré sous :\n{file_path}")
                # Optionnel : os.startfile(file_path) pour ouvrir le fichier directement sur Windows
            else:
                raise FileNotFoundError("Le fichier n'a pas été généré correctement.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur génération PDF : {str(e)}")