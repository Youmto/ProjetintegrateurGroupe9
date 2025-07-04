from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout, QHeaderView, QSpacerItem, QSizePolicy, QFrame # Added QFrame for ModernCard
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont 
import os


class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(15, 15, 15, 15)
        self.setMinimumHeight(120)

        

        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)

# Pas besoin de redéfinir ModernTableWidget en entier si elle est déjà dans le même fichier
# ou importée depuis un fichier d'utilitaires commun. Assurez-vous simplement qu'elle est disponible.
class ModernTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                selection-background-color: #E3F2FD; /* Bleu clair */
                selection-color: #212121;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #212121;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                color: #424242;
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
            }
            QTableWidget::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #388E3C;
            }
            QTableWidget::indicator:unchecked {
                background-color: #E0E0E0;
                border: 1px solid #9E9E9E;
            }
        """)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)


# Importations des contrôleurs existants
from controllers.expedition_controller import (
    handle_get_colis_by_bon,
    handle_get_contenu_colis,
    handle_get_exceptions,
    handle_valider_expedition,
    handle_generer_bordereau_pdf,
)

def format_date(dt):
    """Formate un objet datetime en chaîne de caractères JJ/MM/AAAA HH:MM:SS."""
    return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else "—" # Inclure l'heure pour plus de détails

class ExpeditionDetailWindow(QWidget):
    # Définit un signal pour notifier le parent lorsque la fenêtre est fermée ou que les données changent
    # Utilisez 'finished' pour QDialogs, mais pour QWidget, un signal personnalisé est préférable
    data_changed = pyqtSignal()
    
    def __init__(self, db_conn, user, expedition_id):
        """
        Initialise la fenêtre de détail de l'expédition.

        Args:
            db_conn: La connexion à la base de données.
            user: L'utilisateur actuel.
            expedition_id: L'ID du bon d'expédition à afficher.
        """
        super().__init__()
        self.conn = db_conn
        self.user = user
        self.expedition_id = expedition_id
        self.setWindowTitle(f"Détail de l'expédition #{expedition_id}")
        self.setMinimumSize(1000, 700) # Fenêtre légèrement plus grande

        self.apply_modern_theme() # Applique la nouvelle feuille de style professionnelle
        self.init_ui()
        self.load_data() # Chargement initial des données

    def apply_modern_theme(self):
        """Applique les styles CSS modernes aux widgets."""
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA; /* Arrière-plan clair */
                color: #212121;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QLabel#mainTitle {
                font-size: 26px;
                font-weight: bold;
                color: #2C3E50; /* Gris-bleu plus foncé */
                margin-bottom: 20px;
                padding-bottom: 5px;
                border-bottom: 2px solid #D1D8DD; /* Séparateur subtil */
            }
            QLabel#sectionHeader {
                font-size: 18px;
                font-weight: bold;
                color: #34495E; /* Un autre gris-bleu foncé */
                margin-top: 20px;
                margin-bottom: 10px;
                padding-left: 5px;
                border-left: 5px solid #00BCD4; /* Accent sarcelle */
            }
            QPushButton {
                background-color: #00BCD4; /* Sarcelle */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 18px;
                border: none;
                min-width: 160px; /* Boutons plus larges */
            }
            QPushButton:hover {
                background-color: #4DD0E1;
            }
            QPushButton:pressed {
                background-color: #0097A7;
            }
            QPushButton#validateButton {
                background-color: #4CAF50; /* Vert pour la validation */
            }
            QPushButton#validateButton:hover {
                background-color: #66BB6A;
            }
            QPushButton#validateButton:pressed {
                background-color: #388E3C;
            }
            QPushButton#pdfButton {
                background-color: #FF9800; /* Orange pour le PDF */
            }
            QPushButton#pdfButton:hover {
                background-color: #FFB74D;
            }
            QPushButton#pdfButton:pressed {
                background-color: #FB8C00;
            }
            QPushButton#refreshButton {
                background-color: #607D8B; /* Gris-bleu pour le rafraîchissement */
            }
            QPushButton#refreshButton:hover {
                background-color: #78909C;
            }
            QPushButton#refreshButton:pressed {
                background-color: #455A64;
            }
            QMessageBox {
                background-color: #FFFFFF;
                color: #212121;
            }
            QMessageBox QPushButton {
                background-color: #42A5F5;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
        """)

    def init_ui(self):
        """Initialise l'interface utilisateur de la fenêtre."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # --- Titre Principal ---
        title_label = QLabel(f"Détail du Bon d'Expédition #{self.expedition_id}")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Section Liste des colis ---
        colis_card = ModernCard()
        colis_layout = QVBoxLayout(colis_card)
        
        colis_header = QLabel("📦 Colis Associés")
        colis_header.setObjectName("sectionHeader")
        colis_layout.addWidget(colis_header)

        self.colis_table = ModernTableWidget()
        self.colis_table.setColumnCount(4)
        self.colis_table.setHorizontalHeaderLabels(["ID Colis", "Référence", "Date création", "Statut"])
        self.colis_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.colis_table.setSelectionMode(QTableWidget.SingleSelection) # N'autorise qu'une seule sélection
        # self.colis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Supprimé, utiliser stretch last
        self.colis_table.doubleClicked.connect(self.show_contenu_colis)
        colis_layout.addWidget(self.colis_table)
        main_layout.addWidget(colis_card)

        # --- Section Résumé du Contenu du Colis ---
        resume_card = ModernCard()
        resume_layout = QVBoxLayout(resume_card)

        resume_header = QLabel("📋 Contenu du Colis Sélectionné")
        resume_header.setObjectName("sectionHeader")
        resume_layout.addWidget(resume_header)

        self.resume_table = ModernTableWidget()
        self.resume_table.setColumnCount(4)
        self.resume_table.setHorizontalHeaderLabels(["Lot", "Date prod.", "Qté", "Date exp."])
        # self.resume_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Supprimé
        resume_layout.addWidget(self.resume_table)
        main_layout.addWidget(resume_card)

        # --- Section Rapports d'Exception ---
        exceptions_card = ModernCard()
        exceptions_layout = QVBoxLayout(exceptions_card)

        exceptions_header = QLabel("⚠️ Rapports d'Exception")
        exceptions_header.setObjectName("sectionHeader")
        exceptions_layout.addWidget(exceptions_header)

        self.exceptions_table = ModernTableWidget()
        self.exceptions_table.setColumnCount(3)
        self.exceptions_table.setHorizontalHeaderLabels(["Date", "Type", "Description"])
        # self.exceptions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Supprimé
        exceptions_layout.addWidget(self.exceptions_table)
        main_layout.addWidget(exceptions_card)

        # --- Boutons d'Action ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15) # Ajuste l'espacement entre les boutons

        valider_btn = QPushButton("✅ Valider l'expédition")
        valider_btn.setObjectName("validateButton") # Nom d'objet spécifique pour le style
        valider_btn.clicked.connect(self.valider_expedition)
        button_layout.addWidget(valider_btn)

        pdf_btn = QPushButton("📄 Générer Bordereau PDF")
        pdf_btn.setObjectName("pdfButton") # Nom d'objet spécifique pour le style
        pdf_btn.clicked.connect(self.generer_pdf)
        button_layout.addWidget(pdf_btn)

        refresh_btn = QPushButton("🔄 Rafraîchir les Données")
        refresh_btn.setObjectName("refreshButton") # Nom d'objet spécifique pour le style
        refresh_btn.clicked.connect(self.load_data)
        button_layout.addWidget(refresh_btn)
        
        # Ajoute un espace flexible pour pousser les boutons au centre ou à droite, ou les laisser groupés
        button_layout.addStretch() 

        main_layout.addLayout(button_layout)
        
        # Ajoute un espace flexible final pour pousser tout le contenu vers le haut, si désiré
        main_layout.addStretch()

    def load_expedition_data(self, new_expedition_id):
        """
        Méthode pour charger de nouvelles données d'expédition si la fenêtre est réutilisée.

        Args:
            new_expedition_id: Le nouvel ID du bon d'expédition à charger.
        """
        self.expedition_id = new_expedition_id
        self.setWindowTitle(f"Détail de l'expédition #{self.expedition_id}")
        self.load_data()

    def load_data(self):
        """Charge toutes les données pour le détail de l'expédition."""
        try:
            # Charger la liste des colis
            colis_list = handle_get_colis_by_bon(self.conn, self.expedition_id)
            self.colis_table.setRowCount(len(colis_list))

            for row, colis in enumerate(colis_list):
                self.colis_table.setItem(row, 0, QTableWidgetItem(str(colis['idColis'])))
                self.colis_table.setItem(row, 1, QTableWidgetItem(colis['reference']))
                self.colis_table.setItem(row, 2, QTableWidgetItem(format_date(colis['dateCreation'])))
                self.colis_table.setItem(row, 3, QTableWidgetItem(colis['statut']))
            self.colis_table.resizeColumnsToContents()

            # Sélectionne le premier colis si disponible et charge son contenu
            if colis_list:
                self.colis_table.selectRow(0) # Sélectionne la première ligne
                self.show_contenu_colis()
            else:
                self.resume_table.setRowCount(0) # Efface la table de résumé si aucun colis
                QMessageBox.information(self, "Information", "Aucun colis associé à ce bon d'expédition.")

            # Charger les exceptions
            exceptions = handle_get_exceptions(self.conn, self.expedition_id)
            self.exceptions_table.setRowCount(len(exceptions))
            for row, ex in enumerate(exceptions):
                self.exceptions_table.setItem(row, 0, QTableWidgetItem(format_date(ex['date'])))
                self.exceptions_table.setItem(row, 1, QTableWidgetItem(ex.get('type', 'Non spécifié'))) # Gère le type manquant
                self.exceptions_table.setItem(row, 2, QTableWidgetItem(ex['description']))
            self.exceptions_table.resizeColumnsToContents()
            
            self.data_changed.emit() # Émet le signal après le chargement/rafraîchissement des données

        except Exception as e:
            QMessageBox.critical(self, "Erreur de chargement", f"Impossible de charger les détails de l'expédition:\n{e}")

    def show_contenu_colis(self):
        """Affiche le contenu du colis sélectionné."""
        try:
            row = self.colis_table.currentRow()
            if row < 0:
                self.resume_table.setRowCount(0) # Efface si rien n'est sélectionné
                return

            id_colis = int(self.colis_table.item(row, 0).text())
            contenu = handle_get_contenu_colis(self.conn, id_colis)
            self.resume_table.setRowCount(len(contenu))
            for r, item in enumerate(contenu):
                self.resume_table.setItem(r, 0, QTableWidgetItem(item.get('numeroLot', '—')))
                self.resume_table.setItem(r, 1, QTableWidgetItem(format_date(item.get('dateProduction'))))
                self.resume_table.setItem(r, 2, QTableWidgetItem(str(item.get('quantite', '—'))))
                self.resume_table.setItem(r, 3, QTableWidgetItem(format_date(item.get('dateExpiration'))))
            self.resume_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'affichage du contenu du colis:\n{str(e)}")

    def valider_expedition(self):
        """Valide l'expédition."""
        try:
            # Vous pouvez ajouter une boîte de dialogue de confirmation ici
            reply = QMessageBox.question(self, "Confirmer Validation", 
                                         f"Êtes-vous sûr de vouloir valider l'expédition #{self.expedition_id} ?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

            handle_valider_expedition(self.conn, self.expedition_id)
            QMessageBox.information(self, "Succès", f"L'expédition #{self.expedition_id} a été validée avec succès.")
            self.load_data() # Rafraîchit les données pour refléter le changement de statut
            self.data_changed.emit() # Notifie le parent que les données ont changé
        except Exception as e:
            QMessageBox.critical(self, "Erreur de validation", f"Échec de la validation de l'expédition :\n{str(e)}")

    def generer_pdf(self):
        """Génère le bordereau PDF."""
        try:
            file_path = handle_generer_bordereau_pdf(self.conn, self.expedition_id)
            if os.path.exists(file_path):
                QMessageBox.information(self, "PDF Généré", f"Le bordereau PDF a été enregistré sous :\n{file_path}")
                # Optionnel : Ouvrir le fichier automatiquement pour l'utilisateur
                # import sys, subprocess # Décommentez ces lignes si vous utilisez ceci
                # if sys.platform == "win32":
                #     os.startfile(file_path)
                # elif sys.platform == "darwin":
                #     subprocess.call(["open", file_path])
                # else: # linux
                #     subprocess.call(["xdg-open", file_path])
            else:
                raise FileNotFoundError("Le fichier PDF n'a pas été généré correctement. Veuillez vérifier les logs.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur PDF", f"Erreur lors de la génération du bordereau PDF :\n{str(e)}")

    # Surcharge de closeEvent pour émettre un signal lorsque la fenêtre est fermée
    def closeEvent(self, event):
        """
        Gère l'événement de fermeture de la fenêtre.
        Émet le signal data_changed avant de fermer.
        """
        self.data_changed.emit()
        super().closeEvent(event)