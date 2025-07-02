from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QGroupBox, QTableWidget, QTableWidgetItem, QComboBox,
    QPushButton, QDateEdit, QGridLayout, QSizePolicy, QFrame,
    QScrollArea, QApplication, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import logging
import concurrent.futures # Pour le pool de threads

from models.product_model import get_all_products
from controllers.dashboard_controller import (
    handle_occupation_cellules,
    handle_ruptures,
    handle_produits_non_stockes,
    handle_cellules_vides,
    handle_expirations,
    handle_ruptures_history,
    handle_expeditions_terminées,
    handle_demandes_approvisionnement,
    handle_mouvements_produit,
)

logger = logging.getLogger(__name__)

# --- Threading pour la récupération des données ---
class DataFetcher(QThread):
    data_fetched = pyqtSignal(str, object) # Signal pour émettre les données récupérées
    error_occurred = pyqtSignal(str, str) # Signal pour les erreurs
    progress_update = pyqtSignal(int) # Signal pour la progression

    def __init__(self, conn, method_name, *args, **kwargs):
        super().__init__()
        self.conn = conn
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.progress_update.emit(0)
            # Simuler le travail pour les mises à jour de progression si nécessaire, ex: time.sleep()
            if self.method_name == "occupation_cellules":
                data = handle_occupation_cellules(self.conn)
            elif self.method_name == "ruptures":
                data = handle_ruptures(self.conn)
            elif self.method_name == "produits_non_stockes":
                data = handle_produits_non_stockes(self.conn)
            elif self.method_name == "cellules_vides":
                data = handle_cellules_vides(self.conn)
            elif self.method_name == "expirations":
                data = handle_expirations(self.conn)
            elif self.method_name == "demandes_approvisionnement":
                data = handle_demandes_approvisionnement(self.conn)
            elif self.method_name == "expeditions_terminées":
                data = handle_expeditions_terminées(self.conn)
            elif self.method_name == "mouvements_produit":
                data = handle_mouvements_produit(self.conn, *self.args)
            elif self.method_name == "ruptures_history":
                data = handle_ruptures_history(self.conn, *self.args)
            elif self.method_name == "all_produits":
                data = get_all_products(self.conn)
            else:
                raise ValueError(f"Nom de méthode inconnu : {self.method_name}")

            self.data_fetched.emit(self.method_name, data)
            self.progress_update.emit(100)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données pour {self.method_name} : {e}", exc_info=True)
            self.error_occurred.emit(self.method_name, str(e))
            self.progress_update.emit(100)


class DashboardModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.setWindowTitle("Tableau de Bord - Vue d'ensemble")
        
        self.setup_styles() # Appliquer le style professionnel
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=5) # Gérer les threads

        self.init_ui()
        self.start_refresh_timer() # Démarrer le minuteur pour l'actualisation périodique

    def setup_styles(self):
        # Palette de couleurs professionnelle
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#F0F2F5")) # Arrière-plan gris clair
        palette.setColor(QPalette.WindowText, QColor("#333333")) # Texte gris foncé
        palette.setColor(QPalette.Base, QColor("#FFFFFF")) # Blanc pour les champs de saisie/tables
        palette.setColor(QPalette.AlternateBase, QColor("#E0E6ED")) # Légèrement plus foncé pour les lignes alternées
        palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
        palette.setColor(QPalette.ToolTipText, QColor("#333333"))
        palette.setColor(QPalette.Text, QColor("#333333"))
        palette.setColor(QPalette.Button, QColor("#007BFF")) # Bleu pour les boutons
        palette.setColor(QPalette.ButtonText, QColor("#FFFFFF")) # Texte blanc sur les boutons
        palette.setColor(QPalette.Highlight, QColor("#0056b3")) # Bleu plus foncé pour la surbrillance
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        self.setPalette(palette)

        # Paramètres de police globaux
        font = QFont("Segoe UI", 10) # Police moderne et propre
        self.setFont(font)

        # Style de widget spécifique avec QSS
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #0056b3; /* Bleu plus foncé pour les titres de groupe de boîtes */
                border: 1px solid #C0C5CC;
                border-radius: 5px;
                margin-top: 1ex; /* Espace pour le titre */
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: #0056b3;
            }
            QLabel#header_label {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50; /* Bleu/gris encore plus foncé pour l'en-tête */
                padding-bottom: 10px;
            }
            QLabel#summary_label {
                font-size: 14px;
                font-weight: bold;
                color: #555555;
                margin-bottom: 15px;
            }
            QTableWidget {
                border: 1px solid #C0C5CC;
                gridline-color: #D3D8DF;
                background-color: #FFFFFF;
                selection-background-color: #AACCFF;
                alternate-background-color: #F8F9FA;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::horizontalHeader {
                background-color: #007BFF;
                color: #FFFFFF;
                font-weight: bold;
                padding: 5px;
            }
            QTableWidget::verticalHeader {
                background-color: #F0F2F5;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QComboBox, QDateEdit {
                border: 1px solid #C0C5CC;
                border-radius: 3px;
                padding: 5px;
                background-color: #FFFFFF;
            }
            QFrame { /* Pour les icônes colorées */
                border-radius: 5px;
            }
            QProgressBar {
                text-align: center;
                color: #FFFFFF;
                background-color: #E0E6ED;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50; /* Vert pour la progression */
                border-radius: 5px;
            }
        """)

    def init_ui(self):
        # En-tête principal
        self.label_header = QLabel(f"Bienvenue {self.user.get('nom', '')} - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        self.label_header.setObjectName("header_label")
        self.layout.addWidget(self.label_header, alignment=Qt.AlignCenter)

        # Statistiques récapitulatives
        self.stats_summary = QLabel()
        self.stats_summary.setObjectName("summary_label")
        self.layout.addWidget(self.stats_summary, alignment=Qt.AlignCenter)

        # Barre de progression pour le chargement
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide() # Cacher jusqu'à ce que le chargement commence
        self.layout.addWidget(self.progress_bar)

        # Zone de défilement pour le contenu principal
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_area.setWidget(self.scroll_content_widget)
        self.layout.addWidget(self.scroll_area)

        # Section graphique
        self.graph_group = QGroupBox("Indicateurs Clés & Graphiques")
        self.graph_layout = QGridLayout()
        self.graph_group.setLayout(self.graph_layout)
        self.scroll_content_layout.addWidget(self.graph_group)

        # Graphique d'occupation des cellules
        self.occupation_figure = plt.figure(figsize=(6, 3))
        self.occupation_canvas = FigureCanvas(self.occupation_figure)
        self.graph_layout.addWidget(QLabel("Taux de remplissage global"), 0, 0, alignment=Qt.AlignCenter)
        self.graph_layout.addWidget(self.occupation_canvas, 1, 0)
        
        # Graphique de l'historique des ruptures
        self.rupture_history_figure = plt.figure(figsize=(6, 3))
        self.rupture_history_canvas = FigureCanvas(self.rupture_history_figure)
        self.graph_layout.addWidget(QLabel("Historique des ruptures"), 0, 1, alignment=Qt.AlignCenter)
        self.graph_layout.addWidget(self.rupture_history_canvas, 1, 1)

        # Section des tableaux
        self.tables = {}
        self.data_grid = QGridLayout()
        
        self.add_table("Produits en rupture", 0, 0, critical=True)
        self.add_table("Produits jamais stockés", 0, 1)
        self.add_table("Cellules vides", 1, 0)
        self.add_table("Produits expirant bientôt", 1, 1, warning=True)
        self.add_table("Demandes d'approvisionnement", 2, 0)
        self.add_table("Expéditions terminées", 2, 1)

        self.scroll_content_layout.addLayout(self.data_grid)

        self.init_mouvements_section()

        # Chargement initial des données
        self.refresh_data()

    def add_table(self, title, row, col, critical=False, warning=False):
        box = QGroupBox()
        vbox = QVBoxLayout()
        box.setLayout(vbox)
        box.setTitle(title) # Définir le titre pour QGroupBox

        header_layout = QHBoxLayout()
        icon = QLabel()
        icon.setFixedSize(10, 10) # Icône carrée
        icon.setStyleSheet("background-color: green; border-radius: 5px;")
        icon.setObjectName(f"icon_{title.replace(' ', '_').lower()}") # Nom d'objet unique pour le style
        header_layout.addWidget(icon)
        header_layout.addStretch(1) # Pousser l'icône vers la gauche

        # Pas besoin d'un QLabel séparé pour le titre à l'intérieur de la boîte si le titre de QGroupBox est utilisé

        table = QTableWidget()
        table.setColumnCount(3) # Par défaut, sera ajusté par update_table
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setEditTriggers(QTableWidget.NoEditTriggers) # Rendre les tables en lecture seule
        table.setAlternatingRowColors(True) # Améliorer la lisibilité

        vbox.addLayout(header_layout) # Ajouter l'icône en haut
        vbox.addWidget(table)

        self.tables[title] = table
        self.data_grid.addWidget(box, row, col)

    def start_refresh_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5 * 60 * 1000)  # Toutes les 5 minutes

    def refresh_data(self):
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.label_header.setText(f"Bienvenue {self.user.get('nom', '')} - {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Utiliser un pool de threads pour la récupération concurrente des données
        self.fetch_data_in_thread("occupation_cellules")
        self.fetch_data_in_thread("ruptures", "Produits en rupture")
        self.fetch_data_in_thread("produits_non_stockes", "Produits jamais stockés")
        self.fetch_data_in_thread("cellules_vides", "Cellules vides")
        self.fetch_data_in_thread("expirations", "Produits expirant bientôt")
        self.fetch_data_in_thread("demandes_approvisionnement", "Demandes d'approvisionnement")
        self.fetch_data_in_thread("expeditions_terminées", "Expéditions terminées")
        
        # Récupérer les données pour le graphique de l'historique des ruptures (ex: les 6 derniers mois)
        end_date = QDate.currentDate().toPyDate()
        start_date = (QDate.currentDate().addMonths(-6)).toPyDate()
        self.fetch_data_in_thread("ruptures_history", start_date, end_date)

        self.load_produits_ids_threaded() # Charger les produits dans un thread

    def fetch_data_in_thread(self, method_name, *args):
        worker = DataFetcher(self.conn, method_name, *args)
        worker.data_fetched.connect(self.handle_fetched_data)
        worker.error_occurred.connect(self.handle_fetch_error)
        worker.progress_update.connect(self.update_progress)
        self.thread_pool.submit(worker.run) # Soumettre au pool de threads

    def update_progress(self, value):
        current_value = self.progress_bar.value()
        # Incrémenter d'une petite quantité à chaque fois, ou calculer en fonction du nombre de tâches
        # Par exemple, pour 9 tâches, chaque tâche réussie incrémente de 100 // 9
        if value == 100: # Si une tâche est terminée
            self.progress_bar.setValue(current_value + (100 // 9)) # Environ pour 9 tâches initiales
            if self.progress_bar.value() >= 100:
                self.progress_bar.hide()
        # Vous pouvez affiner cette logique pour un suivi plus précis si vous avez un nombre exact de tâches

    def handle_fetched_data(self, method_name, data):
        try:
            if method_name == "occupation_cellules":
                self.update_occupation_chart(data)
                self.update_summary_stats(data)
            elif method_name == "ruptures":
                self.update_table("Produits en rupture", data)
            elif method_name == "produits_non_stockes":
                self.update_table("Produits jamais stockés", data)
            elif method_name == "cellules_vides":
                self.update_table("Cellules vides", data)
            elif method_name == "expirations":
                self.update_table("Produits expirant bientôt", data)
            elif method_name == "demandes_approvisionnement":
                self.update_table("Demandes d'approvisionnement", data)
            elif method_name == "expeditions_terminées":
                self.update_table("Expéditions terminées", data)
            elif method_name == "mouvements_produit":
                self.update_mouvements_table(data)
            elif method_name == "ruptures_history":
                self.update_rupture_history_chart(data)
            elif method_name == "all_produits":
                self.populate_produit_id_combo(data)
            
            # La barre de progression est masquée par update_progress lorsque la valeur atteint 100
            # Mais assurez-vous qu'elle est toujours masquée même en cas de problème de progression
            if self.progress_bar.value() >= 90:
                self.progress_bar.hide()

        except Exception as e:
            logger.error(f"Erreur lors du traitement des données récupérées pour {method_name} : {e}", exc_info=True)
        finally:
            # Assurez-vous que la barre de progression se cache même en cas de succès/échec partiel
            if self.progress_bar.isVisible() and self.progress_bar.value() < 100:
                self.progress_bar.setValue(100) # Assurer qu'elle est à 100% avant de cacher
                self.progress_bar.hide()


    def handle_fetch_error(self, method_name, error_message):
        logger.error(f"Échec de la récupération des données pour {method_name} : {error_message}")
        self.progress_bar.hide() # Cacher la barre de progression en cas d'erreur

    def update_occupation_chart(self, data):
        self.occupation_figure.clear()
        ax = self.occupation_figure.add_subplot(111)

        labels = [d['reference'] for d in data]
        values = [d['taux_occupation'] for d in data]

        ax.bar(labels, values, color='#4CAF50') # Barres vertes
        ax.set_title("Occupation des cellules", fontsize=12)
        ax.set_ylabel("% Occupation", fontsize=10)
        
        # --- DÉBUT DE LA CORRECTION ---
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment('right')
        # --- FIN DE LA CORRECTION ---

        ax.tick_params(axis='y', labelsize=8)
        self.occupation_figure.tight_layout() # Ajuster la mise en page pour éviter le chevauchement des étiquettes
        self.occupation_canvas.draw()

    def update_rupture_history_chart(self, data):
        self.rupture_history_figure.clear()
        ax = self.rupture_history_figure.add_subplot(111)

        # En supposant que les données sont une liste de dictionnaires comme {'date': 'AAAA-MM-JJ', 'count': N}
        # Si la fonction handle_ruptures_history n'est pas implémentée, cette section utilisera des données vides.
        if data:
            dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
            counts = [d['count'] for d in data]

            ax.plot(dates, counts, marker='o', linestyle='-', color='#FF5733') # Ligne orange/rouge
            ax.set_title("Historique des ruptures", fontsize=12)
            ax.set_xlabel("Date", fontsize=10)
            ax.set_ylabel("Nombre de ruptures", fontsize=10)
            
            # --- DÉBUT DE LA CORRECTION ---
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            for label in ax.get_xticklabels():
                label.set_horizontalalignment('right')
            # --- FIN DE LA CORRECTION ---

            ax.tick_params(axis='y', labelsize=8)
            self.rupture_history_figure.autofmt_xdate() # Formater joliment les dates
        else:
            ax.set_title("Historique des ruptures (données non disponibles)", fontsize=12, color='gray')
            ax.text(0.5, 0.5, 'Pas de données à afficher', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, color='gray')

        self.rupture_history_figure.tight_layout()
        self.rupture_history_canvas.draw()


    def update_table(self, title, data):
        table = self.tables[title]
        
        # Déterminer les en-têtes de colonne en fonction du premier élément des données, si disponible
        if data:
            headers = list(data[0].keys())
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
        else:
            table.setColumnCount(3) # Par défaut s'il n'y a pas de données
            # Exemple d'en-têtes par défaut, à adapter à chaque tableau si nécessaire
            if title == "Produits en rupture":
                table.setHorizontalHeaderLabels(["ID Produit", "Nom Produit", "Quantité Manquante"])
            elif title == "Produits expirant bientôt":
                table.setHorizontalHeaderLabels(["ID Produit", "Nom Produit", "Date Expiration"])
            else:
                table.setHorizontalHeaderLabels(["Col. 1", "Col. 2", "Col. 3"])

        table.setRowCount(len(data))
        for i, row in enumerate(data):
            # S'assurer que l'ordre des valeurs correspond aux en-têtes définis
            for j, value in enumerate(row.values()):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter) # Centrer le texte dans les cellules du tableau
                table.setItem(i, j, item)
        
        table.resizeColumnsToContents() # Ajuster la largeur des colonnes au contenu
        table.horizontalHeader().setStretchLastSection(True) # Faire en sorte que la dernière colonne s'étire

        icon = self.findChild(QLabel, f"icon_{title.replace(' ', '_').lower()}")
        if icon:
            if len(data) == 0:
                icon.setStyleSheet("background-color: green; border-radius: 5px;")
            elif (title == "Produits en rupture" or title == "Produits expirant bientôt") and len(data) > 0:
                # Logique pour rouge/orange basée sur la quantité de données de rupture/expiration
                # Par exemple, si plus de 5 ruptures est critique, entre 1 et 5 est un avertissement
                if len(data) <= 2: # Peu de ruptures/expirations = orange
                    icon.setStyleSheet("background-color: orange; border-radius: 5px;")
                else: # Beaucoup de ruptures/expirations = rouge
                    icon.setStyleSheet("background-color: red; border-radius: 5px;")
            # Couleur par défaut pour les autres tableaux qui n'ont pas d'état critique/avertissement
            else:
                icon.setStyleSheet("background-color: #007BFF; border-radius: 5px;") # Bleu pour neutre

    def update_summary_stats(self, occupation_data):
        try:
            nb_cellules = len(occupation_data)
            taux_moyen = sum([c['taux_occupation'] for c in occupation_data]) / nb_cellules if nb_cellules else 0
            self.stats_summary.setText(
                f"Nombre de cellules : <span style='color:#007BFF;'>{nb_cellules}</span> | Taux d'occupation moyen : <span style='color:#007BFF;'>{round(taux_moyen, 2)}%</span>"
            )
        except Exception as e:
            logger.warning(f"Erreur update_summary_stats : {e}")

    def init_mouvements_section(self):
        self.mouvements_box = QGroupBox("Historique des Mouvements de produit")
        vbox = QVBoxLayout()

        filter_layout = QHBoxLayout()
        self.produit_id_combo = QComboBox()
        self.date_debut = QDateEdit(calendarPopup=True)
        self.date_fin = QDateEdit(calendarPopup=True)
        self.type_combo = QComboBox()

        self.date_debut.setDate(QDate.currentDate().addMonths(-1))
        self.date_fin.setDate(QDate.currentDate())

        self.type_combo.addItems(["Tous", "Entrée", "Sortie"])
        filter_layout.addWidget(QLabel("Produit:"))
        filter_layout.addWidget(self.produit_id_combo)
        filter_layout.addWidget(QLabel("Du:"))
        filter_layout.addWidget(self.date_debut)
        filter_layout.addWidget(QLabel("Au:"))
        filter_layout.addWidget(self.date_fin)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_combo)

        btn_refresh = QPushButton("Filtrer Mouvements")
        btn_refresh.clicked.connect(self.refresh_mouvements)
        filter_layout.addWidget(btn_refresh)

        vbox.addLayout(filter_layout)
        
        self.mouvements_table = QTableWidget()
        self.mouvements_table.setColumnCount(7) # Nombre de colonnes initial
        self.mouvements_table.setHorizontalHeaderLabels(['Type', 'Référence Bon', 'Date', 'Quantité', 'Lot', 'Cellule', 'Description'])
        self.mouvements_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.mouvements_table.setAlternatingRowColors(True)
        vbox.addWidget(self.mouvements_table)

        self.mouvements_box.setLayout(vbox)
        self.scroll_content_layout.addWidget(self.mouvements_box)

        # Chargement initial des IDs de produit
        self.load_produits_ids_threaded()

    def load_produits_ids_threaded(self):
        self.fetch_data_in_thread("all_produits")

    def populate_produit_id_combo(self, produits):
        try:
            self.produit_id_combo.clear()
            self.produit_id_combo.addItem("Sélectionner un produit", None) # Ajouter une option par défaut "sélectionner tout" ou similaire
            for p in produits:
                self.produit_id_combo.addItem(f"{p.get('nom', 'N/A')} (ID: {p.get('idProduit', 'N/A')})", p.get('idProduit'))
        except Exception as e:
            logger.error(f"Erreur lors du peuplement des produits dans le combo : {e}")


    def refresh_mouvements(self):
        produit_id = self.produit_id_combo.currentData()
        if produit_id is None: 
            self.mouvements_table.setRowCount(0)
            return

        date_debut = self.date_debut.date().toPyDate()
        date_fin = self.date_fin.date().toPyDate()
        type_mouvement = self.type_combo.currentText()
        if type_mouvement == "Tous":
            type_mouvement = "" # Passer une chaîne vide au contrôleur pour récupérer tous les types

        self.fetch_data_in_thread("mouvements_produit", produit_id, date_debut, date_fin, type_mouvement)

    def update_mouvements_table(self, mouvements):
        self.mouvements_table.setRowCount(len(mouvements))
        if mouvements:
            headers = list(mouvements[0].keys())
            self.mouvements_table.setColumnCount(len(headers))
            self.mouvements_table.setHorizontalHeaderLabels(headers)
        else:
            self.mouvements_table.setColumnCount(7)
            self.mouvements_table.setHorizontalHeaderLabels(['Type', 'Référence Bon', 'Date', 'Quantité', 'Lot', 'Cellule', 'Description'])


        for i, m in enumerate(mouvements):
            # S'assurer que l'ordre des clés correspond aux en-têtes de colonne définis si les données arrivent dans un ordre variable
            for j, key in enumerate(['type', 'reference_bon', 'date', 'quantite', 'lot', 'cellule', 'description']):
                item = QTableWidgetItem(str(m.get(key, 'N/A')))
                item.setTextAlignment(Qt.AlignCenter)
                self.mouvements_table.setItem(i, j, item)
        self.mouvements_table.resizeColumnsToContents()
        self.mouvements_table.horizontalHeader().setStretchLastSection(True) # Faire en sorte que la dernière colonne s'étire

    def closeEvent(self, event):
        # Arrêter le pool de threads gracieusement lorsque le widget se ferme
        self.thread_pool.shutdown(wait=True)
        super().closeEvent(event)

