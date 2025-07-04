from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QGroupBox, QTableWidget, QTableWidgetItem, QComboBox,
    QPushButton, QDateEdit, QGridLayout, QSizePolicy, QFrame,
    QScrollArea, QApplication, QProgressBar, QTabWidget,
    QSpacerItem, QLineEdit, QSlider, QMessageBox, QInputDialog 
)
from PyQt5.QtCore import Qt, QTimer, QDate, QThread, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QStandardItemModel, QStandardItem
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta, date 
import logging
import concurrent.futures
import csv
import os

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

# --- Widget de Notification (Toast/SnackBar) ---
class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("")
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(52, 152, 219, 0.9);
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid rgba(41, 128, 185, 0.8);
            }
        """)
        self.layout.addWidget(self.label)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_animation)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)

    def show_notification(self, message: str, duration: int = 3000):
        self.label.setText(message)
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(parent_rect.x() + (parent_rect.width() - self.width()) // 2,
                      parent_rect.y() + parent_rect.height() - self.height() - 20)
        
        self.setWindowOpacity(0.0)
        self.show()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        self.timer.start(duration)

    def hide_animation(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()
        self.animation.finished.connect(self.hide)


# --- Threading pour la récupération des données ---
class DataFetcher(QThread):
    data_fetched = pyqtSignal(str, object)
    error_occurred = pyqtSignal(str, str)
    progress_update = pyqtSignal(str, int)

    def __init__(self, conn, method_name, *args, **kwargs):
        super().__init__()
        self.conn = conn
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.progress_update.emit(self.method_name, 0)
            
            data = None
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
            self.progress_update.emit(self.method_name, 100)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données pour {self.method_name} : {e}", exc_info=True)
            self.error_occurred.emit(self.method_name, str(e))
            self.progress_update.emit(self.method_name, 100)


class DashboardModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.setWindowTitle("Tableau de Bord - Gestion d'Entrepôt")
        self.threads = {}
        self.pending_fetches = 0

        self.ruptures_data = []
        self.cellules_vides_data = []
        self.occupation_data = []

        self.setup_styles()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=5)

        self.init_ui()
        self.start_refresh_timer()

        self.notification_widget = NotificationWidget(self)

    def setup_styles(self):
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#E9EEF6"))
        palette.setColor(QPalette.WindowText, QColor("#2C3E50"))
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.AlternateBase, QColor("#F8FAFC"))
        palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
        palette.setColor(QPalette.ToolTipText, QColor("#333333"))
        palette.setColor(QPalette.Text, QColor("#333333"))
        palette.setColor(QPalette.Button, QColor("#3498DB"))
        palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Highlight, QColor("#2980B9"))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        self.setPalette(palette)

        font = QFont("Arial", 10)
        self.setFont(font)

        self.setStyleSheet("""
            QWidget {
                background-color: #E9EEF6;
                color: #2C3E50;
            }
            QGroupBox {
                font-weight: bold;
                color: #2980B9;
                border: 1px solid #D1D9E6;
                border-radius: 8px;
                margin-top: 2ex;
                padding: 15px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #2980B9;
                font-size: 14px;
            }
            QGroupBox::title[style*="red"] { color: red; }
            QGroupBox::title[style*="orange"] { color: orange; }
            QGroupBox::title[style*="green"] { color: green; }

            QLabel#header_label {
                font-size: 24px;
                font-weight: bold;
                color: #1A2E44;
                padding-bottom: 15px;
            }
            QLabel#summary_label {
                font-size: 16px;
                font-weight: bold;
                color: #4A6572;
                margin-bottom: 20px;
            }
            QTableWidget {
                border: 1px solid #D1D9E6;
                gridline-color: #E0E6ED;
                background-color: #FFFFFF;
                selection-background-color: #B3D9FF;
                alternate-background-color: #F8FAFC;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::horizontalHeader {
                background-color: #3498DB;
                color: #FFFFFF;
                font-weight: bold;
                padding: 8px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTableWidget::verticalHeader {
                background-color: #E9EEF6;
                border: none;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
            QComboBox, QDateEdit, QLineEdit {
                border: 1px solid #D1D9E6;
                border-radius: 5px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
            }
            QFrame#card_frame {
                background-color: #FFFFFF;
                border: 1px solid #D1D9E6;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel#card_title {
                font-size: 14px;
                font-weight: bold;
                color: #555555;
            }
            QLabel#card_value {
                font-size: 24px;
                font-weight: bold;
                color: #3498DB;
                margin-top: 5px;
            }
            QFrame#card_frame.alert {
                background-color: #FFEBEE;
                border: 1px solid #EF5350;
            }
            QLabel#card_value.alert {
                color: #D32F2F;
            }
            QFrame#card_frame.warning {
                background-color: #FFF3E0;
                border: 1px solid #FF9800;
            }
            QLabel#card_value.warning {
                color: #EF6C00;
            }
            QFrame#card_frame.ok {
                background-color: #E8F5E9;
                border: 1px solid #4CAF50;
            }
            QLabel#card_value.ok {
                color: #2E7D32;
            }

            QProgressBar {
                text-align: center;
                color: #FFFFFF;
                background-color: #D1D9E6;
                border-radius: 5px;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x0:0, y0:0, x1:1, y1:0, stop:0 #2ECC71, stop:1 #27AE60);
                border-radius: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #D1D9E6;
                border-top: none;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background: #E0E6ED;
                border: 1px solid #D1D9E6;
                border-bottom-color: #D1D9E6;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 100px;
                padding: 10px 15px;
                color: #555555;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                border-bottom-color: #FFFFFF;
                color: #3498DB;
            }
            QTabBar::tab:hover {
                background: #D1D9E6;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #F0F0F0;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498DB;
                border: 1px solid #3498DB;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #2980B9;
                border: 1px solid #2980B9;
                height: 8px;
                border-radius: 4px;
            }
        """)

    def init_ui(self):
        self.label_header = QLabel(f"Bienvenue {self.user.get('nom', 'Utilisateur')} - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        self.label_header.setObjectName("header_label")
        self.label_header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_header)

        self.stats_summary_layout = QHBoxLayout()
        # --- START CHANGE for responsive cards ---
        self.card_total_cells = self.create_info_card("Total Cellules", "N/A") 
        self.card_avg_occupation = self.create_info_card("Taux d'Occupation Moyen", "N/A%")
        self.card_alerts = self.create_info_card("État du Stock", "Tout est OK")
        
        self.stats_summary_layout.addStretch(1)
        self.stats_summary_layout.addWidget(self.card_total_cells)
        self.stats_summary_layout.addSpacing(20) # Added spacing
        self.stats_summary_layout.addWidget(self.card_avg_occupation)
        self.stats_summary_layout.addSpacing(20) # Added spacing
        self.stats_summary_layout.addWidget(self.card_alerts)
        self.stats_summary_layout.addStretch(1)
        # --- END CHANGE for responsive cards ---
        self.layout.addLayout(self.stats_summary_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Chargement des données... %p%")
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.overview_tab = QWidget()
        self.overview_layout = QVBoxLayout(self.overview_tab)
        self.tab_widget.addTab(self.overview_tab, "Vue d'ensemble")

        self.reports_tab = QWidget()
        self.reports_layout = QVBoxLayout(self.reports_tab)
        self.tab_widget.addTab(self.reports_tab, "Rapports Détaillés")

        self.mouvements_tab = QWidget()
        self.mouvements_layout = QVBoxLayout(self.mouvements_tab)
        self.tab_widget.addTab(self.mouvements_tab, "Historique des Mouvements")

        self.init_overview_tab()
        self.init_reports_tab()
        self.init_mouvements_section()

        self.show_startup_progress()
        QTimer.singleShot(100, self.refresh_data)

    def show_startup_progress(self):
        self.startup_splash = QWidget()
        self.startup_splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        splash_layout = QVBoxLayout(self.startup_splash)
        
        splash_label = QLabel("Chargement du Tableau de Bord...")
        splash_label.setFont(QFont("Arial", 16, QFont.Bold))
        splash_label.setAlignment(Qt.AlignCenter)
        splash_label.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")

        self.startup_progress_bar = QProgressBar()
        self.startup_progress_bar.setRange(0, 100)
        self.startup_progress_bar.setValue(0)
        self.startup_progress_bar.setTextVisible(True)
        self.startup_progress_bar.setFormat("Initialisation: %p%")
        self.startup_progress_bar.setStyleSheet("""
            QProgressBar {
                text-align: center;
                color: #FFFFFF;
                background-color: #D1D9E6;
                border-radius: 5px;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x0:0, y0:0, x1:1, y1:0, stop:0 #3498DB, stop:1 #2980B9);
                border-radius: 5px;
            }
        """)

        splash_layout.addWidget(splash_label)
        splash_layout.addWidget(self.startup_progress_bar)
        splash_layout.setContentsMargins(50, 50, 50, 50)
        self.startup_splash.setStyleSheet("background-color: #E9EEF6; border-radius: 10px; border: 1px solid #D1D9E6;")
        self.startup_splash.show()
        self.startup_splash.adjustSize()
        desktop_geo = QApplication.desktop().availableGeometry()
        x = (desktop_geo.width() - self.startup_splash.width()) // 2
        y = (desktop_geo.height() - self.startup_splash.height()) // 2
        self.startup_splash.move(x, y)

    def hide_startup_progress(self):
        if hasattr(self, 'startup_splash') and self.startup_splash.isVisible():
            self.startup_splash.close()
            del self.startup_splash
            del self.startup_progress_bar
        self.notification_widget.show_notification("Données du tableau de bord actualisées !")


    def create_info_card(self, title, value):
        frame = QFrame()
        frame.setObjectName("card_frame")
        # --- START CHANGE for card sizing ---
        frame.setMinimumSize(250, 100) # Increased minimum width
        frame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed) # Allow horizontal expansion
        # --- END CHANGE for card sizing ---
        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setObjectName("card_title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True) # Allow text wrapping
        
        value_label = QLabel(value)
        value_label.setObjectName("card_value")
        value_label.setAlignment(Qt.AlignCenter)
        
        vbox.addWidget(title_label)
        vbox.addWidget(value_label)
        return frame

    def init_overview_tab(self):
        self.graph_group = QGroupBox("Indicateurs Clés & Graphiques")
        self.graph_layout = QGridLayout()
        self.graph_group.setLayout(self.graph_layout)
        self.overview_layout.addWidget(self.graph_group)

        # --- START CHANGE for occupation chart layout ---
        # Container for the left graph (Occupation) and its controls
        occupation_chart_container = QVBoxLayout()
        
        self.occupation_slider_label = QLabel("Filtrer occupation > 0%")
        self.occupation_slider_label.setAlignment(Qt.AlignCenter) # Center align label
        occupation_chart_container.addWidget(self.occupation_slider_label)

        self.occupation_slider = QSlider(Qt.Horizontal)
        self.occupation_slider.setRange(0, 100)
        self.occupation_slider.setValue(0)
        self.occupation_slider.setSingleStep(1) # Finer step control
        self.occupation_slider.setTickInterval(10)
        self.occupation_slider.setTickPosition(QSlider.TicksBelow)
        self.occupation_slider.valueChanged.connect(self.update_occupation_chart_filtered)
        occupation_chart_container.addWidget(self.occupation_slider)

        self.occupation_figure = plt.figure(figsize=(6, 3), facecolor='#E9EEF6')
        self.occupation_canvas = FigureCanvas(self.occupation_figure)
        occupation_chart_container.addWidget(self.occupation_canvas)
        
        # Add a stretch to ensure content is aligned properly if container grows
        occupation_chart_container.addStretch()

        self.graph_layout.addWidget(QLabel("Taux de remplissage global"), 0, 0, alignment=Qt.AlignCenter)
        self.graph_layout.addLayout(occupation_chart_container, 1, 0)
        # --- END CHANGE for occupation chart layout ---

        # --- START CHANGE for rupture history chart layout (for consistency) ---
        rupture_history_container = QVBoxLayout()

        self.rupture_period_combo = QComboBox()
        self.rupture_period_combo.addItems(["Dernière semaine", "Dernier mois", "3 derniers mois", "6 derniers mois", "Dernière année"])
        self.rupture_period_combo.setCurrentText("6 derniers mois")
        self.rupture_period_combo.currentIndexChanged.connect(self.refresh_ruptures_history_chart)
        rupture_history_container.addWidget(self.rupture_period_combo)
        rupture_history_container.addStretch() # Push combo up if container grows

        self.rupture_history_figure = plt.figure(figsize=(6, 3), facecolor='#E9EEF6')
        self.rupture_history_canvas = FigureCanvas(self.rupture_history_figure)
        rupture_history_container.addWidget(self.rupture_history_canvas)

        self.graph_layout.addWidget(QLabel("Historique des ruptures"), 0, 1, alignment=Qt.AlignCenter)
        self.graph_layout.addLayout(rupture_history_container, 1, 1)
        # --- END CHANGE for rupture history chart layout ---

        self.overview_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def init_reports_tab(self):
        self.data_grid = QGridLayout()
        self.reports_layout.addLayout(self.data_grid)
        self.tables = {}

        self.add_table(self.data_grid, "Produits en rupture", 0, 0, critical=True)
        self.add_table(self.data_grid, "Produits jamais stockés", 0, 1)
        self.add_table(self.data_grid, "Cellules vides", 1, 0)
        self.add_table(self.data_grid, "Produits expirant bientôt", 1, 1, warning=True)
        self.add_table(self.data_grid, "Demandes d'approvisionnement", 2, 0)
        self.add_table(self.data_grid, "Expéditions terminées", 2, 1)

        self.reports_layout.addStretch(1)

    def add_table(self, parent_layout, title, row, col, critical=False, warning=False):
        box = QGroupBox()
        vbox = QVBoxLayout()
        box.setLayout(vbox)
        box.setTitle(title)

        search_layout = QHBoxLayout()
        search_label = QLabel("Rechercher:")
        search_input = QLineEdit()
        search_input.setPlaceholderText(f"Rechercher dans {title}...")
        search_input.textChanged.connect(lambda text, t=title: self.filter_table(t, text))
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input)
        vbox.addLayout(search_layout)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setMinimumHeight(200)
        
        vbox.addWidget(table)

        export_btn = QPushButton("Exporter CSV")
        export_btn.clicked.connect(lambda: self.export_table_to_csv(title))
        vbox.addWidget(export_btn)


        self.tables[title] = table
        parent_layout.addWidget(box, row, col)
        parent_layout.setColumnStretch(col, 1)
        parent_layout.setRowStretch(row, 1)

    def start_refresh_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5 * 60 * 1000)

    def refresh_data(self):
        if not hasattr(self, 'startup_splash') or not self.startup_splash.isVisible():
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Chargement des données... %p%")
            self.notification_widget.show_notification("Actualisation des données en cours...")

        self.label_header.setText(f"Bienvenue {self.user.get('nom', 'Utilisateur')} - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        self.pending_fetches = 0
        
        tasks = [
            ("occupation_cellules", None),
            ("ruptures", "Produits en rupture"),
            ("produits_non_stockes", "Produits jamais stockés"),
            ("cellules_vides", "Cellules vides"),
            ("expirations", "Produits expirant bientôt"),
            ("demandes_approvisionnement", "Demandes d'approvisionnement"),
            ("expeditions_terminées", "Expéditions terminées"),
        ]
        
        self.refresh_ruptures_history_chart()

        if self.produit_id_combo.count() <= 1:
            tasks.append(("all_produits", None))

        self.pending_fetches = len(tasks)
        self.progress_bar.setRange(0, self.pending_fetches)
        if hasattr(self, 'startup_progress_bar'):
             self.startup_progress_bar.setRange(0, self.pending_fetches)


        for task_info in tasks:
            method_name = task_info[0]
            args = task_info[1:] if len(task_info) > 1 else ()
            self.fetch_data_in_thread(method_name, *args)

    def fetch_data_in_thread(self, method_name, *args):
        if method_name in self.threads and self.threads[method_name].isRunning():
            logger.warning(f"Un thread pour '{method_name}' est déjà en cours. Sauter la nouvelle requête.")
            return

        worker = DataFetcher(self.conn, method_name, *args)
        worker.data_fetched.connect(self.handle_fetched_data)
        worker.error_occurred.connect(self.handle_fetch_error)
        worker.progress_update.connect(self.update_single_task_progress)
        
        self.threads[method_name] = worker
        worker.start()

    def update_single_task_progress(self, method_name, value):
        if value == 100:
            if hasattr(self, 'startup_progress_bar') and self.startup_progress_bar.isVisible():
                current_progress = self.startup_progress_bar.value()
                if current_progress < self.startup_progress_bar.maximum():
                    self.startup_progress_bar.setValue(current_progress + 1)
            else:
                current_progress = self.progress_bar.value()
                if current_progress < self.progress_bar.maximum():
                    self.progress_bar.setValue(current_progress + 1)
            
            if (hasattr(self, 'startup_progress_bar') and self.startup_progress_bar.value() >= self.startup_progress_bar.maximum()) or \
               (not hasattr(self, 'startup_progress_bar') and self.progress_bar.value() >= self.progress_bar.maximum() and self.progress_bar.isVisible()):
                if hasattr(self, 'startup_splash') and self.startup_splash.isVisible():
                    self.hide_startup_progress()
                else:
                    self.progress_bar.hide()
                    self.notification_widget.show_notification("Données du tableau de bord actualisées !")


    def handle_fetched_data(self, method_name, data):
        try:
            if method_name == "occupation_cellules":
                self.occupation_data = data if data is not None else []
                self.update_occupation_chart_filtered()
                total_cellules = len(self.occupation_data) 
                self.card_total_cells.findChild(QLabel, "card_value").setText(str(total_cellules))
                self.update_summary_cards(data)
            elif method_name == "ruptures":
                self.ruptures_data = data if data is not None else []
                self.update_table("Produits en rupture", data)
                self.update_alert_card()
            elif method_name == "produits_non_stockes":
                self.update_table("Produits jamais stockés", data)
            elif method_name == "cellules_vides":
                self.cellules_vides_data = data if data is not None else []
                self.update_table("Cellules vides", data)
                self.update_alert_card()
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
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement des données récupérées pour {method_name} : {e}", exc_info=True)
        finally:
            if method_name in self.threads:
                del self.threads[method_name]

    def handle_fetch_error(self, method_name, error_message):
        logger.error(f"Échec de la récupération des données pour {method_name} : {error_message}")
        QMessageBox.warning(self, "Erreur de Chargement", f"Impossible de charger les données pour {method_name}:\n{error_message}")
        if method_name in self.threads:
            del self.threads[method_name]
        
        self.update_single_task_progress(method_name, 100)


    def update_occupation_chart(self, data_to_plot):
        self.occupation_figure.clear()
        ax = self.occupation_figure.add_subplot(111)

        # --- START CHANGE for degenerate data handling ---
        # Check for meaningful data (e.g., at least one non-zero occupation)
        has_meaningful_data = data_to_plot and any(d.get('taux_occupation', 0) > 0 for d in data_to_plot)

        if has_meaningful_data:
            labels = [d['reference'] for d in data_to_plot]
            values = [d['taux_occupation'] for d in data_to_plot]

            ax.bar(labels, values, color='#4CAF50')
            ax.set_title("Occupation des cellules", fontsize=12, color='#333333')
            ax.set_ylabel("% Occupation", fontsize=10, color='#555555')
            ax.set_xlabel("Référence Cellule", fontsize=10, color='#555555')
            
            ax.tick_params(axis='x', rotation=45, labelsize=8, colors='#555555')
            ax.tick_params(axis='y', labelsize=8, colors='#555555')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            try:
                self.occupation_figure.tight_layout() 
            except Exception as e:
                logger.warning(f"Impossible d'appliquer tight_layout à occupation_chart: {e}. Utilisant subplots_adjust.")
                # Manual adjustment if tight_layout fails
                self.occupation_figure.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.25) # Increased bottom
        elif data_to_plot and all(d.get('taux_occupation', 0) == 0 for d in data_to_plot):
            # Specific message if all data is present but all occupations are 0
            ax.set_title("Occupation des cellules", fontsize=12, color='#333333')
            ax.text(0.5, 0.5, 'Toutes les cellules sont vides (0% occupation)', 
                    horizontalalignment='center', verticalalignment='center', 
                    transform=ax.transAxes, color='gray')
        else:
            # Message for truly no data after filtering
            ax.set_title("Occupation des cellules (pas de données)", fontsize=12, color='gray')
            ax.text(0.5, 0.5, 'Aucune donnée d\'occupation de cellule disponible\n(ajustez le filtre si besoin)', 
                    horizontalalignment='center', verticalalignment='center', 
                    transform=ax.transAxes, color='gray')
        # --- END CHANGE for degenerate data handling ---

        self.occupation_canvas.draw()

    def update_occupation_chart_filtered(self):
        threshold = self.occupation_slider.value()
        self.occupation_slider_label.setText(f"Filtrer occupation > {threshold}%")
        
        filtered_data = [d for d in self.occupation_data if d.get('taux_occupation', 0) >= threshold]
        self.update_occupation_chart(filtered_data)


    def refresh_ruptures_history_chart(self):
        period = self.rupture_period_combo.currentText()
        end_date = QDate.currentDate().toPyDate()
        start_date = QDate.currentDate().toPyDate()

        if period == "Dernière semaine":
            start_date = (QDate.currentDate().addDays(-7)).toPyDate()
        elif period == "Dernier mois":
            start_date = (QDate.currentDate().addMonths(-1)).toPyDate()
        elif period == "3 derniers mois":
            start_date = (QDate.currentDate().addMonths(-3)).toPyDate()
        elif period == "6 derniers mois":
            start_date = (QDate.currentDate().addMonths(-6)).toPyDate()
        elif period == "Dernière année":
            start_date = (QDate.currentDate().addYears(-1)).toPyDate()
        
        self.fetch_data_in_thread("ruptures_history", start_date, end_date)


    def update_rupture_history_chart(self, data):
        self.rupture_history_figure.clear()
        ax = self.rupture_history_figure.add_subplot(111)

        if data:
            sorted_data = sorted(data, key=lambda x: x['date'])
            dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in sorted_data]
            counts = [d['count'] for d in sorted_data]

            ax.plot(dates, counts, marker='o', linestyle='-', color='#E74C3C', linewidth=2)
            ax.set_title("Historique des ruptures", fontsize=12, color='#333333')
            ax.set_xlabel("Date", fontsize=10, color='#555555')
            ax.set_ylabel("Nombre de ruptures", fontsize=10, color='#555555')
            
            ax.tick_params(axis='x', rotation=45, labelsize=8, colors='#555555')
            ax.tick_params(axis='y', labelsize=8, colors='#555555')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            self.rupture_history_figure.autofmt_xdate()
            self.rupture_history_figure.tight_layout()
        else:
            ax.set_title("Historique des ruptures (pas de données)", fontsize=12, color='gray')
            ax.text(0.5, 0.5, 'Pas de données d\'historique de rupture à afficher', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, color='gray')

        self.rupture_history_canvas.draw()

    def update_table(self, title, data):
        table = self.tables[title]
        
        table.model_data = data 

        if data:
            headers = list(data[0].keys())
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
        else:
            if title == "Produits en rupture":
                table.setColumnCount(3)
                table.setHorizontalHeaderLabels(["ID Produit", "Nom Produit", "Quantité Manquante"])
            elif title == "Produits expirant bientôt":
                table.setColumnCount(3)
                table.setHorizontalHeaderLabels(["ID Produit", "Nom Produit", "Date Expiration"])
            elif title == "Produits jamais stockés":
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(["ID Produit", "Nom Produit"])
            elif title == "Cellules vides":
                table.setColumnCount(1)
                table.setHorizontalHeaderLabels(["Référence Cellule"])
            elif title == "Demandes d'approvisionnement":
                table.setColumnCount(4)
                table.setHorizontalHeaderLabels(["ID Demande", "Produit", "Quantité", "Statut"])
            elif title == "Expéditions terminées":
                table.setColumnCount(4)
                table.setHorizontalHeaderLabels(["ID Expédition", "Date", "Destination", "Statut"])
            else:
                table.setColumnCount(3)
                table.setHorizontalHeaderLabels(["Col. 1", "Col. 2", "Col. 3"])

        table.setRowCount(len(data))
        for i, row_data in enumerate(data):
            for j, value in enumerate(row_data.values()):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)

                if title == "Produits en rupture" and row_data.get('quantite_manquante', 0) > 0:
                    item.setBackground(QColor("#FFCDD2"))
                    item.setToolTip("Produit en rupture de stock critique")
                elif title == "Produits expirant bientôt":
                    expiration_date = row_data.get('date_expiration')
                    if expiration_date:
                        exp_date = expiration_date 
                        if isinstance(exp_date, date) and exp_date < (QDate.currentDate().toPyDate() + timedelta(days=30)):
                            item.setBackground(QColor("#FFE0B2"))
                            item.setToolTip("Produit expirant bientôt")
        
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)

        group_box = table.parent().parent()
        if group_box:
            group_box.setStyleSheet(group_box.styleSheet().split("QGroupBox::title {")[0] + " QGroupBox::title { color: #2980B9; }")

            if title == "Produits en rupture" or title == "Produits expirant bientôt":
                if len(data) > 2:
                    group_box.setStyleSheet(group_box.styleSheet() + " QGroupBox::title { color: red; }")
                elif 0 < len(data) <= 2:
                    group_box.setStyleSheet(group_box.styleSheet() + " QGroupBox::title { color: orange; }")
                else:
                    group_box.setStyleSheet(group_box.styleSheet() + " QGroupBox::title { color: green; }")


    def filter_table(self, title, text):
        table = self.tables[title]
        original_data = table.model_data 

        table.setRowCount(0)

        if not text:
            filtered_data = original_data
        else:
            filtered_data = []
            search_text = text.lower()
            for row_data in original_data:
                for value in row_data.values():
                    if search_text in str(value).lower():
                        filtered_data.append(row_data)
                        break

        table.setRowCount(len(filtered_data))
        for i, row_data in enumerate(filtered_data):
            for j, value in enumerate(row_data.values()):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)
                if title == "Produits en rupture" and row_data.get('quantite_manquante', 0) > 0:
                    item.setBackground(QColor("#FFCDD2"))
                elif title == "Produits expirant bientôt":
                    expiration_date = row_data.get('date_expiration')
                    if expiration_date:
                        exp_date = expiration_date
                        if isinstance(exp_date, date) and exp_date < (QDate.currentDate().toPyDate() + timedelta(days=30)):
                            item.setBackground(QColor("#FFE0B2"))
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)


    def export_table_to_csv(self, title):
        table = self.tables[title] if title != "Historique des Mouvements" else self.mouvements_table

        if not hasattr(table, 'model_data') or not table.model_data:
            QMessageBox.information(self, "Export CSV", "Aucune donnée à exporter.")
            return

        headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        data_to_export = table.model_data

        file_name, ok = QInputDialog.getText(self, "Nom du fichier CSV", "Nom du fichier CSV (sans extension .csv):", text=f"{title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if not ok or not file_name:
            return

        file_path = f"{file_name}.csv"

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(headers)
                for row_data_dict in data_to_export:
                    if title == "Historique des Mouvements":
                        ordered_keys = ['type', 'reference_bon', 'date', 'quantite', 'lot', 'cellule', 'description']
                        row_values = [row_data_dict.get(key, '') for key in ordered_keys]
                    else:
                        row_values = []
                        for h in headers:
                            key_found = None
                            for k in row_data_dict.keys():
                                if h.replace(' ', '').lower() == k.lower() or \
                                   h.replace(' ', '_').lower() == k.lower() or \
                                   h.replace(' ', '').lower() == k.replace('_', '').lower():
                                    key_found = k
                                    break
                            row_values.append(row_data_dict.get(key_found, ''))

            self.notification_widget.show_notification(f"Exporté avec succès vers {os.path.abspath(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'Exportation", f"Impossible d'exporter les données : {e}")
            logger.error(f"Erreur lors de l'exportation CSV de '{title}' : {e}", exc_info=True)


    def update_summary_cards(self, occupation_data):
        try:
            self.occupation_data = occupation_data if occupation_data is not None else []
            
            total_cellules = len(self.occupation_data) 
            
            nb_cellules_occupees = sum(1 for c in self.occupation_data if c.get('taux_occupation', 0) > 0)
            
            taux_moyen = (sum([c['taux_occupation'] for c in self.occupation_data]) / total_cellules) if total_cellules else 0

            self.card_total_cells.findChild(QLabel, "card_value").setText(str(total_cellules))
            self.card_avg_occupation.findChild(QLabel, "card_value").setText(f"{round(taux_moyen, 2)}%")
            
            self.update_alert_card()

        except Exception as e:
            logger.warning(f"Erreur update_summary_cards : {e}")

    def update_alert_card(self):
        alert_value_label = self.card_alerts.findChild(QLabel, "card_value")
        alert_frame = self.card_alerts

        num_ruptures = len(self.ruptures_data)
        num_cellules_vides = len(self.cellules_vides_data)

        total_cellules = len(self.occupation_data) 
        num_cellules_pleines = total_cellules - num_cellules_vides
        
        alert_frame.setProperty("class", "")
        alert_value_label.setProperty("class", "")
        alert_frame.style().unpolish(alert_frame)
        alert_value_label.style().unpolish(alert_value_label)


        if num_ruptures > 0:
            alert_value_label.setText(f"{num_ruptures} ruptures")
            alert_frame.setProperty("class", "alert")
            alert_value_label.setProperty("class", "alert")
            self.notification_widget.show_notification(f"Alerte : {num_ruptures} produits en rupture de stock critique !")
        elif total_cellules > 0 and num_cellules_pleines > (0.8 * total_cellules):
            alert_value_label.setText(f"Entrepôt plein ({num_cellules_pleines}/{total_cellules})")
            alert_frame.setProperty("class", "warning")
            alert_value_label.setProperty("class", "warning")
            self.notification_widget.show_notification(f"Avertissement : {num_cellules_pleines} cellules occupées, l'entrepôt est presque plein.")
        else:
            alert_value_label.setText("Tout est OK")
            alert_frame.setProperty("class", "ok")
            alert_value_label.setProperty("class", "ok")

        alert_frame.style().polish(alert_frame)
        alert_value_label.style().polish(alert_value_label)


    def init_mouvements_section(self):
        self.mouvements_box = QGroupBox("Filtrer les Mouvements de Stock")
        vbox = QVBoxLayout()

        filter_layout = QGridLayout()
        filter_layout.setSpacing(10)

        self.produit_id_combo = QComboBox()
        self.date_debut = QDateEdit(calendarPopup=True)
        self.date_fin = QDateEdit(calendarPopup=True)
        self.type_combo = QComboBox()

        self.date_debut.setDate(QDate.currentDate().addMonths(-1))
        self.date_fin.setDate(QDate.currentDate())

        self.type_combo.addItems(["Tous", "Entrée", "Sortie"])
        
        filter_layout.addWidget(QLabel("Produit:"), 0, 0)
        filter_layout.addWidget(self.produit_id_combo, 0, 1)
        filter_layout.addWidget(QLabel("Date début:"), 1, 0)
        filter_layout.addWidget(self.date_debut, 1, 1)
        filter_layout.addWidget(QLabel("Date fin:"), 2, 0)
        filter_layout.addWidget(self.date_fin, 2, 1)
        filter_layout.addWidget(QLabel("Type de mouvement:"), 0, 2)
        filter_layout.addWidget(self.type_combo, 0, 3)

        btn_refresh = QPushButton("Appliquer Filtres")
        btn_refresh.clicked.connect(self.refresh_mouvements)
        filter_layout.addWidget(btn_refresh, 1, 3, 2, 1)

        vbox.addLayout(filter_layout)
        vbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        search_mouvements_layout = QHBoxLayout()
        search_mouvements_label = QLabel("Rechercher:")
        self.search_mouvements_input = QLineEdit()
        self.search_mouvements_input.setPlaceholderText("Rechercher dans les mouvements...")
        self.search_mouvements_input.textChanged.connect(self.filter_mouvements_table)
        search_mouvements_layout.addWidget(search_mouvements_label)
        search_mouvements_layout.addWidget(self.search_mouvements_input)
        vbox.addLayout(search_mouvements_layout)


        self.mouvements_table = QTableWidget()
        self.mouvements_table.setColumnCount(7)
        self.mouvements_table.setHorizontalHeaderLabels(['Type', 'Référence Bon', 'Date', 'Quantité', 'Lot', 'Cellule', 'Description'])
        self.mouvements_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.mouvements_table.setAlternatingRowColors(True)
        self.mouvements_table.setMinimumHeight(300)
        vbox.addWidget(self.mouvements_table)

        export_mouvements_btn = QPushButton("Exporter Mouvements CSV")
        export_mouvements_btn.clicked.connect(lambda: self.export_table_to_csv("Historique des Mouvements"))
        vbox.addWidget(export_mouvements_btn)


        self.mouvements_box.setLayout(vbox)
        self.mouvements_layout.addWidget(self.mouvements_box)
        self.mouvements_layout.addStretch(1)

        self.load_produits_ids_threaded()


    def load_produits_ids_threaded(self):
        self.fetch_data_in_thread("all_produits")

    def populate_produit_id_combo(self, produits):
        try:
            self.produit_id_combo.clear()
            self.produit_id_combo.addItem("Tous les produits", None)
            sorted_produits = sorted(produits, key=lambda p: p.get('nom', ''))
            for p in sorted_produits:
                self.produit_id_combo.addItem(f"{p.get('nom', 'N/A')} (ID: {p.get('idProduit', 'N/A')})", p.get('idProduit'))
        except Exception as e:
            logger.error(f"Erreur lors du peuplement des produits dans le combo : {e}")

    def refresh_mouvements(self):
        produit_id = self.produit_id_combo.currentData()
        
        date_debut = self.date_debut.date().toPyDate()
        date_fin = self.date_fin.date().toPyDate()
        type_mouvement = self.type_combo.currentText()
        if type_mouvement == "Tous":
            type_mouvement = ""

        self.fetch_data_in_thread("mouvements_produit", produit_id, date_debut, date_fin, type_mouvement)

    def update_mouvements_table(self, mouvements):
        self.mouvements_table.model_data = mouvements if mouvements is not None else []
        self.filter_mouvements_table(self.search_mouvements_input.text())

    def filter_mouvements_table(self, text):
        table = self.mouvements_table
        original_data = table.model_data if hasattr(table, 'model_data') else []

        table.setRowCount(0)

        if not text:
            filtered_data = original_data
        else:
            filtered_data = []
            search_text = text.lower()
            for row_data in original_data:
                match_found = False
                for key in ['type', 'reference_bon', 'date', 'quantite', 'lot', 'cellule', 'description']:
                    if search_text in str(row_data.get(key, '')).lower():
                        match_found = True
                        break
                if match_found:
                    filtered_data.append(row_data)

        table.setRowCount(len(filtered_data))
        for i, m in enumerate(filtered_data):
            for j, key in enumerate(['type', 'reference_bon', 'date', 'quantite', 'lot', 'cellule', 'description']):
                item = QTableWidgetItem(str(m.get(key, 'N/A')))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)
        self.mouvements_table.resizeColumnsToContents()
        self.mouvements_table.horizontalHeader().setStretchLastSection(True)


    def closeEvent(self, event):
        self.timer.stop()
        self.thread_pool.shutdown(wait=True)
        if self.notification_widget.isVisible():
            self.notification_widget.hide()
        super().closeEvent(event)