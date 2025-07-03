from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QGroupBox, QTableWidget, QTableWidgetItem, QComboBox,
    QPushButton, QDateEdit, QGridLayout, QSizePolicy, QFrame,
    QScrollArea, QApplication, QProgressBar, QSpacerItem,
    QMessageBox  # <-- Ajoute ceci
)
from PyQt5.QtCore import Qt, QTimer, QDate, QThread, pyqtSignal, QThreadPool
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta, date
import logging
import concurrent.futures
import sys
import csv

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

class DataFetcher(QThread):
    data_fetched = pyqtSignal(str, object)
    error_occurred = pyqtSignal(str, str)
    progress_update = pyqtSignal(int)

    def __init__(self, conn, method_name, *args, **kwargs):
        super().__init__()
        self.conn = conn
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.progress_update.emit(0)
            
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
        self.setWindowTitle("Tableau de Bord - Gestion d'Entrepôt")
        self.setWindowIcon(QIcon(':/icons/dashboard.png'))
        
        # Paramètres de fenêtre
        self.setMinimumSize(1200, 800)
        
        self.setup_styles()
        self.init_ui()
        self.start_refresh_timer()

    def setup_styles(self):
        # Palette de couleurs moderne
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f7fa"))
        palette.setColor(QPalette.WindowText, QColor("#2d3748"))
        palette.setColor(QPalette.Base, QColor("#ffffff"))
        palette.setColor(QPalette.AlternateBase, QColor("#edf2f7"))
        palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
        palette.setColor(QPalette.ToolTipText, QColor("#2d3748"))
        palette.setColor(QPalette.Text, QColor("#2d3748"))
        palette.setColor(QPalette.Button, QColor("#4299e1"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        palette.setColor(QPalette.Highlight, QColor("#3182ce"))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)

        # Style global avec QSS
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #2d3748;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 1.5ex;
                padding: 12px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            
            QLabel#header_label {
                font-size: 22px;
                font-weight: 600;
                color: #2d3748;
                padding: 8px 0;
            }
            
            QLabel#summary_label {
                font-size: 15px;
                color: #4a5568;
                margin-bottom: 16px;
            }
            
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                gridline-color: #e2e8f0;
                background-color: white;
                selection-background-color: #bee3f8;
                alternate-background-color: #f8fafc;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::horizontalHeader {
                background-color: #4299e1;
                color: white;
                font-weight: 600;
                padding: 8px;
                border-radius: 0;
            }
            
            QPushButton {
                background-color: #4299e1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #3182ce;
            }
            
            QPushButton:pressed {
                background-color: #2b6cb0;
            }
            
            QComboBox, QDateEdit {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px;
                min-height: 28px;
                background-color: white;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #e2e8f0;
            }
            
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                text-align: center;
                color: white;
                background-color: #edf2f7;
                height: 20px;
            }
            
            QProgressBar::chunk {
                background-color: #48bb78;
                border-radius: 5px;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            .critical-indicator {
                background-color: #f56565;
                border-radius: 4px;
                padding: 2px 6px;
                color: white;
                font-weight: 600;
            }
            
            .warning-indicator {
                background-color: #ed8936;
                border-radius: 4px;
                padding: 2px 6px;
                color: white;
                font-weight: 600;
            }
            
            .success-indicator {
                background-color: #48bb78;
                border-radius: 4px;
                padding: 2px 6px;
                color: white;
                font-weight: 600;
            }
        """)

    def init_ui(self):
        # Layout principal
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.setLayout(self.main_layout)

        # En-tête
        self.init_header()
        
        # Barre de progression
        self.init_progress_bar()
        
        # Contenu principal avec scroll
        self.init_scroll_area()
        
        # Chargement initial des données
        self.refresh_data()

    def init_header(self):
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_widget.setLayout(header_layout)
        
        # Titre principal
        self.header_label = QLabel(f"Tableau de Bord - Bienvenue, {self.user.get('nom', 'Utilisateur')}")
        self.header_label.setObjectName("header_label")
        
        # Sous-titre avec date
        self.subheader_label = QLabel(datetime.now().strftime("%A %d %B %Y - %H:%M"))
        self.subheader_label.setStyleSheet("color: #718096; font-size: 14px;")
        
        # Statistiques sommaires
        self.stats_summary = QLabel()
        self.stats_summary.setObjectName("summary_label")
        
        header_layout.addWidget(self.header_label)
        header_layout.addWidget(self.subheader_label)
        header_layout.addWidget(self.stats_summary)
        
        self.main_layout.addWidget(header_widget)

    def init_progress_bar(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        self.main_layout.addWidget(self.progress_bar)

    def init_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(20)
        self.scroll_content.setLayout(self.scroll_layout)
        
        # Section des indicateurs visuels
        self.init_visual_indicators()
        
        # Section des tableaux
        self.init_data_tables()
        
        # Section des mouvements
        self.init_movements_section()
        
        # Ajouter un espace flexible à la fin
        self.scroll_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

    def init_visual_indicators(self):
        # Conteneur pour les indicateurs visuels
        indicators_container = QWidget()
        indicators_layout = QVBoxLayout()
        indicators_container.setLayout(indicators_layout)
        
        # Titre de section
        section_title = QLabel("Indicateurs Clés")
        section_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #2d3748;")
        indicators_layout.addWidget(section_title)
        
        # Grille pour les graphiques
        graphs_grid = QGridLayout()
        graphs_grid.setSpacing(15)
        
        # Graphique d'occupation
        self.occupation_figure = plt.figure(figsize=(8, 4))
        self.occupation_canvas = FigureCanvas(self.occupation_figure)
        graphs_grid.addWidget(self.occupation_canvas, 0, 0)
        
        # Graphique historique des ruptures
        self.rupture_history_figure = plt.figure(figsize=(8, 4))
        self.rupture_history_canvas = FigureCanvas(self.rupture_history_figure)
        graphs_grid.addWidget(self.rupture_history_canvas, 0, 1)
        
        indicators_layout.addLayout(graphs_grid)
        self.scroll_layout.addWidget(indicators_container)

    def init_data_tables(self):
        # Conteneur pour les tableaux
        tables_container = QWidget()
        tables_layout = QVBoxLayout()
        tables_container.setLayout(tables_layout)
        
        # Titre de section
        section_title = QLabel("Statistiques d'Entrepôt")
        section_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #2d3748;")
        tables_layout.addWidget(section_title)
        
        # Grille pour les tableaux
        tables_grid = QGridLayout()
        tables_grid.setSpacing(15)
        
        # Tableaux avec indicateurs visuels
        self.tables = {}
        self.add_table("Produits en rupture", 0, 0, critical=True)
        self.add_table("Produits jamais stockés", 0, 1)
        self.add_table("Cellules vides", 1, 0)
        self.add_table("Produits expirant bientôt", 1, 1, warning=True)
        self.add_table("Demandes d'approvisionnement", 2, 0)
        self.add_table("Expéditions terminées", 2, 1)
        
        tables_layout.addLayout(tables_grid)
        self.scroll_layout.addWidget(tables_container)

    def init_movements_section(self):
        self.movements_container = QGroupBox("Historique des Mouvements")
        movements_layout = QVBoxLayout()
        self.movements_container.setLayout(movements_layout)
        
        # Barre de filtres
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)
        
        # Sélecteur de produit
        self.product_combo = QComboBox()
        self.product_combo.setPlaceholderText("Sélectionner un produit")
        self.product_combo.setMinimumWidth(200)
        
        # Sélecteurs de date
        self.date_start = QDateEdit(calendarPopup=True)
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setDate(QDate.currentDate().addMonths(-1))
        
        self.date_end = QDateEdit(calendarPopup=True)
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setDate(QDate.currentDate())
        
        # Sélecteur de type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Tous types", "Entrée", "Sortie"])
        
        # Bouton de rafraîchissement
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_btn.clicked.connect(self.refresh_mouvements)
        
        # Ajout des widgets au layout
        filters_layout.addWidget(QLabel("Produit:"))
        filters_layout.addWidget(self.product_combo)
        filters_layout.addWidget(QLabel("Du:"))
        filters_layout.addWidget(self.date_start)
        filters_layout.addWidget(QLabel("Au:"))
        filters_layout.addWidget(self.date_end)
        filters_layout.addWidget(QLabel("Type:"))
        filters_layout.addWidget(self.type_combo)
        filters_layout.addWidget(refresh_btn)
        filters_layout.addStretch()
        
        movements_layout.addLayout(filters_layout)
        
        # Tableau des mouvements
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(7)
        self.movements_table.setHorizontalHeaderLabels([
            "Type", "Référence", "Date", "Quantité", "N° Lot", "Cellule", "Commentaire"
        ])
        self.movements_table.setSortingEnabled(True)
        self.movements_table.verticalHeader().setVisible(False)
        movements_layout.addWidget(self.movements_table)
        
        self.scroll_layout.addWidget(self.movements_container)
        
        # Charger les produits
        self.load_products()

    def add_table(self, title, row, col, critical=False, warning=False):
        container = QGroupBox(title)
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Indicateur de statut
        status_indicator = QLabel()
        status_indicator.setAlignment(Qt.AlignRight)
        status_indicator.setFixedHeight(20)
        layout.addWidget(status_indicator)

        # Tableau
        table = QTableWidget()
        table.setColumnCount(3)
        table.verticalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)

        # Bouton Export CSV
        export_btn = QPushButton("Exporter CSV")
        export_btn.clicked.connect(lambda: self.export_table_to_csv(title))
        layout.addWidget(export_btn)

        # Stocker la référence
        self.tables[title] = {
            "widget": container,
            "table": table,
            "status": status_indicator
        }

        # Style selon le type
        if critical:
            container.setStyleSheet("QGroupBox { border-left: 4px solid #f56565; }")
        elif warning:
            container.setStyleSheet("QGroupBox { border-left: 4px solid #ed8936; }")
        else:
            container.setStyleSheet("QGroupBox { border-left: 4px solid #4299e1; }")

    def export_table_to_csv(self, title):
        """Exporte le tableau donné en CSV (sans ui_utils)"""
        table_info = self.tables.get(title)
        if not table_info:
            return
        table = table_info["table"]
        data = []
        for row in range(table.rowCount()):
            row_data = {}
            for col in range(table.columnCount()):
                header_item = table.horizontalHeaderItem(col)
                header = header_item.text() if header_item else f"Colonne {col+1}"
                item = table.item(row, col)
                row_data[header] = item.text() if item else ""
            data.append(row_data)
        if not data:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return

        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en CSV",
            f"{title.replace(' ', '_').lower()}_{date.today().strftime('%Y%m%d')}.csv",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=data[0].keys(), delimiter=';')
                    writer.writeheader()
                    writer.writerows(data)
                QMessageBox.information(self, "Export", "Exportation réussie !")
            except Exception as e:
                QMessageBox.warning(self, "Export", f"Erreur lors de l'export : {e}")

    def start_refresh_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(300000)  # 5 minutes

    def refresh_data(self):
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        # Mettre à jour l'heure dans l'en-tête
        self.subheader_label.setText(datetime.now().strftime("%A %d %B %Y - %H:%M"))
        
        # Charger les données
        self.fetch_data_in_thread("occupation_cellules")
        self.fetch_data_in_thread("ruptures", "Produits en rupture")
        self.fetch_data_in_thread("produits_non_stockes", "Produits jamais stockés")
        self.fetch_data_in_thread("cellules_vides", "Cellules vides")
        self.fetch_data_in_thread("expirations", "Produits expirant bientôt")
        self.fetch_data_in_thread("demandes_approvisionnement", "Demandes d'approvisionnement")
        self.fetch_data_in_thread("expeditions_terminées", "Expéditions terminées")
        
        # Historique des ruptures (6 derniers mois)
        end_date = QDate.currentDate().toPyDate()
        start_date = (QDate.currentDate().addMonths(-6)).toPyDate()
        self.fetch_data_in_thread("ruptures_history", start_date, end_date)

    def fetch_data_in_thread(self, method_name, *args):
        worker = DataFetcher(self.conn, method_name, *args)
        worker.data_fetched.connect(self.handle_fetched_data)
        worker.error_occurred.connect(self.handle_fetch_error)
        worker.progress_update.connect(self.update_progress)
        QThreadPool.globalInstance().start(worker)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value >= 100:
            self.progress_bar.hide()

    def handle_fetched_data(self, method_name, data):
        try:
            if method_name == "occupation_cellules":
                self.update_occupation_chart(data)
                self.update_summary_stats(data)
            elif method_name == "ruptures":
                self.update_table_data("Produits en rupture", data)
            elif method_name == "produits_non_stockes":
                self.update_table_data("Produits jamais stockés", data)
            elif method_name == "cellules_vides":
                self.update_table_data("Cellules vides", data)
            elif method_name == "expirations":
                self.update_table_data("Produits expirant bientôt", data)
            elif method_name == "demandes_approvisionnement":
                self.update_table_data("Demandes d'approvisionnement", data)
            elif method_name == "expeditions_terminées":
                self.update_table_data("Expéditions terminées", data)
            elif method_name == "ruptures_history":
                self.update_rupture_history_chart(data)
            elif method_name == "all_produits":
                self.populate_product_combo(data)
        except Exception as e:
            logger.error(f"Erreur traitement données {method_name}: {e}")

    def handle_fetch_error(self, method_name, error_msg):
        logger.error(f"Erreur récupération {method_name}: {error_msg}")
        # Afficher un message d'erreur dans l'interface si nécessaire

    def update_occupation_chart(self, data):
        self.occupation_figure.clear()
        ax = self.occupation_figure.add_subplot(111)
        
        if data:
            labels = [d['reference'] for d in data]
            values = [d['taux_occupation'] for d in data]
            
            bars = ax.bar(labels, values, color='#48bb78')
            ax.set_title("Taux d'Occupation des Cellules", pad=20)
            ax.set_ylabel("Taux d'occupation (%)")
            
            # Ajouter les valeurs sur les barres
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom')
            
            # Rotation des étiquettes
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Style
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   color='gray')
            ax.set_title("Taux d'Occupation des Cellules", pad=20)
        
        self.occupation_figure.tight_layout()
        self.occupation_canvas.draw()

    def update_rupture_history_chart(self, data):
        self.rupture_history_figure.clear()
        ax = self.rupture_history_figure.add_subplot(111)
        
        if data:
            dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
            counts = [d['count'] for d in data]
            
            ax.plot(dates, counts, marker='o', linestyle='-', color='#f56565', linewidth=2)
            ax.set_title("Historique des Ruptures de Stock", pad=20)
            ax.set_ylabel("Nombre de ruptures")
            
            # Format des dates
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %Y'))
            
            # Style
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible',
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   color='gray')
            ax.set_title("Historique des Ruptures de Stock", pad=20)
        
        self.rupture_history_figure.tight_layout()
        self.rupture_history_canvas.draw()

    def update_table_data(self, title, data):
        table_info = self.tables.get(title)
        if not table_info:
            return
            
        table = table_info["table"]
        status_label = table_info["status"]
        
        # Mettre à jour le tableau
        if data:
            headers = list(data[0].keys())
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setRowCount(len(data))
            
            for row_idx, row_data in enumerate(data):
                for col_idx, (key, value) in enumerate(row_data.items()):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_idx, col_idx, item)
            
            # Mettre à jour l'indicateur de statut
            count = len(data)
            if title == "Produits en rupture":
                status_label.setText(f"<span class='critical-indicator'>{count} rupture(s)</span>")
            elif title == "Produits expirant bientôt":
                status_label.setText(f"<span class='warning-indicator'>{count} produit(s)</span>")
            else:
                status_label.setText(f"<span class='success-indicator'>{count} élément(s)</span>")
        else:
            table.setRowCount(0)
            status_label.setText("<span style='color:#718096;'>Aucune donnée</span>")
        
        table.resizeColumnsToContents()

    def update_summary_stats(self, data):
        if data:
            nb_cellules = len(data)
            taux_moyen = sum(d['taux_occupation'] for d in data) / nb_cellules if nb_cellules else 0
            
            stats_text = f"""
                <div style="background-color: #ffffff; border-radius: 8px; padding: 12px;">
                    <table width="100%">
                        <tr>
                            <td style="text-align: center; border-right: 1px solid #e2e8f0;">
                                <div style="font-size: 24px; color: #4299e1; font-weight: 600;">{nb_cellules}</div>
                                <div style="font-size: 14px; color: #718096;">Cellules</div>
                            </td>
                            <td style="text-align: center; border-right: 1px solid #e2e8f0;">
                                <div style="font-size: 24px; color: #4299e1; font-weight: 600;">{taux_moyen:.1f}%</div>
                                <div style="font-size: 14px; color: #718096;">Occupation moyenne</div>
                            </td>
                            <td style="text-align: center;">
                                <div style="font-size: 24px; color: #4299e1; font-weight: 600;">{len(self.tables['Produits en rupture']['table'].rowCount())}</div>
                                <div style="font-size: 14px; color: #718096;">Produits en rupture</div>
                            </td>
                        </tr>
                    </table>
                </div>
            """
            self.stats_summary.setText(stats_text)

    def load_products(self):
        self.fetch_data_in_thread("all_produits")

    def populate_product_combo(self, products):
        self.product_combo.clear()
        self.product_combo.addItem("Tous les produits", None)
        
        for product in products:
            self.product_combo.addItem(
                f"{product.get('nom', 'N/A')} (ID: {product.get('idProduit', 'N/A')})", 
                product.get('idProduit')
            )

    def refresh_mouvements(self):
        product_id = self.product_combo.currentData()
        date_start = self.date_start.date().toPyDate()
        date_end = self.date_end.date().toPyDate()
        movement_type = self.type_combo.currentText()
        
        if movement_type == "Tous types":
            movement_type = ""
        
        self.fetch_data_in_thread("mouvements_produit", product_id, date_start, date_end, movement_type)

    def update_mouvements_table(self, data):
        self.movements_table.setRowCount(len(data))
        
        if data:
            headers = list(data[0].keys())
            self.movements_table.setColumnCount(len(headers))
            self.movements_table.setHorizontalHeaderLabels(headers)
            
            for row_idx, row_data in enumerate(data):
                for col_idx, (key, value) in enumerate(row_data.items()):
                    item = QTableWidgetItem(str(value))
                    
                    # Alignement et style selon le type de donnée
                    if key.lower() in ['quantite', 'montant']:
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    elif key.lower() == 'date':
                        item.setTextAlignment(Qt.AlignCenter)
                    
                    self.movements_table.setItem(row_idx, col_idx, item)
        else:
            self.movements_table.setColumnCount(1)
            self.movements_table.setHorizontalHeaderLabels(["Aucun mouvement trouvé"])
        
        self.movements_table.resizeColumnsToContents()

    def closeEvent(self, event):
        QThreadPool.globalInstance().waitForDone()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configuration fictive pour le test
    class MockUser:
        def get(self, key, default):
            return "Admin" if key == "nom" else default
    
    dashboard = DashboardModule(None, MockUser())
    dashboard.show()
    sys.exit(app.exec_())