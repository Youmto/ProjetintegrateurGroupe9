from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout, QHeaderView
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

        # Appliquer une feuille de style professionnelle
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f9fa;
                color: #2c3e50;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 13px;
            }
            QLabel#titleLabel {
                font-size: 20px;
                font-weight: 700;
                color: #34495e;
                margin-bottom: 15px;
            }
            QLabel#sectionLabel {
                font-weight: 600;
                font-size: 15px;
                margin-top: 20px;
                margin-bottom: 10px;
                color: #2980b9;
                border-bottom: 2px solid #2980b9;
                padding-bottom: 3px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
                alternate-background-color: #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #2980b9;
                color: white;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: 600;
                padding: 4px;
                border: none;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: 600;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c5980;
            }
            QHBoxLayout {
                spacing: 15px;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel(f"Colis associés au bon #{self.expedition_id}")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Table des colis
        self.colis_table = QTableWidget()
        self.colis_table.setColumnCount(4)
        self.colis_table.setHorizontalHeaderLabels(["ID Colis", "Référence", "Date création", "Statut"])
        self.colis_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.colis_table.setAlternatingRowColors(True)
        self.colis_table.horizontalHeader().setStretchLastSection(True)
        self.colis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.colis_table.doubleClicked.connect(self.show_contenu_colis)
        layout.addWidget(QLabel("Colis préparés :"))
        layout.addWidget(self.colis_table)

        # Résumé contenu colis
        resume_label = QLabel("Résumé du contenu du colis")
        resume_label.setObjectName("sectionLabel")
        layout.addWidget(resume_label)

        self.resume_table = QTableWidget()
        self.resume_table.setColumnCount(4)
        self.resume_table.setHorizontalHeaderLabels(["Lot", "Date prod.", "Qté", "Date exp."])
        self.resume_table.setAlternatingRowColors(True)
        self.resume_table.horizontalHeader().setStretchLastSection(True)
        self.resume_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.resume_table)

        # Rapports d'exception
        exceptions_label = QLabel("Rapports d'exception")
        exceptions_label.setObjectName("sectionLabel")
        layout.addWidget(exceptions_label)

        self.exceptions_table = QTableWidget()
        self.exceptions_table.setColumnCount(3)
        self.exceptions_table.setHorizontalHeaderLabels(["Date", "Type", "Description"])
        self.exceptions_table.setAlternatingRowColors(True)
        self.exceptions_table.horizontalHeader().setStretchLastSection(True)
        self.exceptions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.exceptions_table)

        # Boutons d'action
        btns = QHBoxLayout()
        btns.setSpacing(20)

        valider_btn = QPushButton("✅ Valider l'expédition")
        valider_btn.clicked.connect(self.valider_expedition)
        btns.addWidget(valider_btn)

        pdf_btn = QPushButton("📄 Générer le bordereau PDF")
        pdf_btn.clicked.connect(self.generer_pdf)
        btns.addWidget(pdf_btn)

        refresh_btn = QPushButton("🔄 Rafraîchir")
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
            else:
                self.resume_table.setRowCount(0)
                self.exceptions_table.setRowCount(0)

            exceptions = handle_get_exceptions(self.conn, self.expedition_id)
            self.exceptions_table.setRowCount(len(exceptions))
            for row, ex in enumerate(exceptions):
                self.exceptions_table.setItem(row, 0, QTableWidgetItem(format_date(ex['date'])))
                self.exceptions_table.setItem(row, 1, QTableWidgetItem(ex.get('type', '—')))
                self.exceptions_table.setItem(row, 2, QTableWidgetItem(ex['description']))

            self.exceptions_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement échoué : {e}")

    def show_contenu_colis(self):
        try:
            row = self.colis_table.currentRow()
            if row < 0:
                self.resume_table.setRowCount(0)
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
