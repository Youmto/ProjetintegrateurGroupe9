from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QMessageBox, QSplitter, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import QDate, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont
import datetime

# --- Re-use ModernCard, StatsWidget, create_stat_card, ModernTableWidget from ReceptionModule ---
# Ensure these classes are defined in the same file or imported from a common utilities file.

# Assuming you have these defined in this file or a shared module:

class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(15, 15, 15, 15)
        self.setMinimumHeight(120) # Give it a bit more minimum height

        self.initial_shadow = QGraphicsDropShadowEffect(self)
        self.initial_shadow.setBlurRadius(20)
        self.initial_shadow.setXOffset(0)
        self.initial_shadow.setYOffset(5)
        self.initial_shadow.setColor(QColor(0, 0, 0, 30))
        
        self.hover_blur_radius = 35
        self.hover_y_offset = 10
        self.hover_shadow_color = QColor(0, 0, 0, 60)

        self.setGraphicsEffect(self.initial_shadow)

        self.blur_animation = QPropertyAnimation(self.initial_shadow, b"blurRadius")
        self.blur_animation.setDuration(200)
        self.blur_animation.setEasingCurve(QEasingCurve.OutQuad)

        self.offset_animation = QPropertyAnimation(self.initial_shadow, b"yOffset")
        self.offset_animation.setDuration(200)
        self.offset_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)

    def enterEvent(self, event):
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #B0D8FF;
            }
        """)
        self.blur_animation.setStartValue(self.initial_shadow.blurRadius())
        self.blur_animation.setEndValue(self.hover_blur_radius)
        self.blur_animation.start()

        self.offset_animation.setStartValue(self.initial_shadow.yOffset())
        self.offset_animation.setEndValue(self.hover_y_offset)
        self.offset_animation.start()

        self.initial_shadow.setColor(self.hover_shadow_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)
        self.blur_animation.setStartValue(self.initial_shadow.blurRadius())
        self.blur_animation.setEndValue(20)
        self.blur_animation.start()

        self.offset_animation.setStartValue(self.initial_shadow.yOffset())
        self.offset_animation.setEndValue(5)
        self.offset_animation.start()

        self.initial_shadow.setColor(QColor(0, 0, 0, 30))
        super().leaveEvent(event)

class StatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)
        self.card_value_labels = {}

    def add_card(self, card_widget, title_key):
        self.layout.addWidget(card_widget)
        value_label = card_widget.findChild(QLabel, f"{title_key}_value")
        if value_label:
            self.card_value_labels[title_key] = value_label

    def update_card_value(self, title_key, value):
        if title_key in self.card_value_labels:
            self.card_value_labels[title_key].setText(str(value))
        else:
            print(f"Erreur: La carte '{title_key}' n'a pas été trouvée pour la mise à jour.")

def create_stat_card(icon, title, value, color):
    card = ModernCard()
    # card.setFixedHeight(100) # Let ModernCard manage its height with minimumHeight

    card_layout = QVBoxLayout()
    card_layout.setContentsMargins(15, 15, 15, 15)
    card_layout.setSpacing(8)

    top_layout = QHBoxLayout()
    icon_label = QLabel(icon)
    icon_label.setStyleSheet(f"font-size: 24px; color: {color};")
    title_label = QLabel(title)
    title_label.setStyleSheet(f"font-size: 12px; color: #7f8c8d; font-weight: bold;")
    title_label.setWordWrap(True)

    top_layout.addWidget(icon_label)
    top_layout.addWidget(title_label)
    top_layout.addStretch()

    value_label = QLabel(str(value))
    value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
    value_label.setObjectName(f"{title}_value")

    card_layout.addLayout(top_layout)
    card_layout.addWidget(value_label)
    card_layout.addStretch()

    card.setLayout(card_layout)
    return card

class ModernTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                selection-background-color: #E3F2FD; /* Light blue */
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


# Your existing imports for controllers and views
from controllers.expedition_controller import (
    handle_create_expedition, handle_pending_expeditions,
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
        self.detail_window = None # Keep a reference to the detail window

        self.setup_ui()
        self.apply_modern_theme() # Apply modern theme
        self.load_bons() # Load data after UI setup

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Header Section (Main Title + Stats Cards) ---
        header_layout = QVBoxLayout()
        title_label = QLabel("📦 Gestion des Expéditions")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #263238;") # Dark text for title
        header_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        self.stats_widget = StatsWidget()
        # You'll need to implement logic to get actual counts for these stats
        self.stats_widget.add_card(create_stat_card("📊", "Bons en Attente", "0", "#FFC107"), "Bons en Attente") # Amber
        self.stats_widget.add_card(create_stat_card("🚚", "Bons en Préparation", "0", "#2196F3"), "Bons en Préparation") # Blue
        self.stats_widget.add_card(create_stat_card("✅", "Bons Expédiés (Aujourd'hui)", "0", "#4CAF50"), "Bons Expédiés (Aujourd'hui)") # Green
        self.stats_widget.add_card(create_stat_card("🕒", "Dernière MAJ", "N/A", "#757575"), "Dernière MAJ") # Grey

        header_layout.addWidget(self.stats_widget)
        main_layout.addLayout(header_layout)

        # --- Create Expedition Section (within a ModernCard) ---
        creation_card = ModernCard()
        creation_layout = QHBoxLayout(creation_card)
        creation_layout.setSpacing(10)
        creation_card.setMinimumHeight(80) # Adjust as needed for input fields

        # Styles for labels and inputs
        label_style = "QLabel { color: #424242; font-weight: 600; }"
        input_style = """
            QLineEdit, QComboBox, QDateEdit {
                border: 1px solid #CFD8DC;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #F5F5F5;
                color: #212121;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #00BCD4; /* Teal focus */
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
                image: url(icons/calendar_icon.png); /* Ensure this icon exists or remove */
                subcontrol-origin: padding;
                subcontrol-position: right center;
            }
        """
        
        creation_layout.addWidget(QLabel("🆔 Référence:"))
        self.ref_input = QLineEdit()
        self.ref_input.setPlaceholderText("Ex: EXP-2023-001")
        self.ref_input.setStyleSheet(input_style)
        creation_layout.addWidget(self.ref_input)

        creation_layout.addWidget(QLabel("📅 Date prévue:"))
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet(input_style)
        creation_layout.addWidget(self.date_input)

        creation_layout.addWidget(QLabel("⚡ Priorité:"))
        self.priority_input = QComboBox()
        self.priority_input.addItems(["normal", "élevée", "urgente"]) # Remove emojis from list
        self.priority_input.setStyleSheet(input_style)
        creation_layout.addWidget(self.priority_input)

        create_btn = QPushButton("➕ Créer bon")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #00BCD4; /* Teal */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4DD0E1;
            }
            QPushButton:pressed {
                background-color: #0097A7;
            }
        """)
        create_btn.clicked.connect(self.create_expedition)
        creation_layout.addWidget(create_btn)
        
        main_layout.addWidget(creation_card)

        # --- Main Content Splitter (Bons Table on Left, Colis Summary/Preparation on Right) ---
        splitter = QSplitter(Qt.Horizontal)

        # Left Side: Bons Table
        bons_table_widget = QWidget()
        bons_table_layout = QVBoxLayout(bons_table_widget)
        bons_table_layout.setContentsMargins(0,0,0,0)

        table_title_label = QLabel("⌛ Bons d'expédition en attente :")
        table_title_label.setFont(QFont("Arial", 16, QFont.Bold))
        table_title_label.setStyleSheet("color: #424242;")
        bons_table_layout.addWidget(table_title_label)
        
        self.bons_table = ModernTableWidget() # Using ModernTableWidget
        self.bons_table.setColumnCount(6)
        self.bons_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Date création", "Date prévue", "Priorité", "Statut"
        ])
        self.bons_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.bons_table.setSelectionMode(QTableWidget.SingleSelection) # Ensure only one row can be selected
        self.bons_table.cellClicked.connect(self.on_bon_selected)
        bons_table_layout.addWidget(self.bons_table)

        # Buttons below Bons Table
        bons_buttons_layout = QHBoxLayout()
        refresh_bons_btn = QPushButton("🔄 Rafraîchir Bons")
        refresh_bons_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B; /* Blue Grey */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 12px;
                border: none;
            }
            QPushButton:hover { background-color: #78909C; }
            QPushButton:pressed { background-color: #455A64; }
        """)
        refresh_bons_btn.clicked.connect(self.load_bons)
        bons_buttons_layout.addWidget(refresh_bons_btn)

        validate_exp_btn = QPushButton("✅ Valider Expédition")
        validate_exp_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 12px;
                border: none;
            }
            QPushButton:hover { background-color: #66BB6A; }
            QPushButton:pressed { background-color: #388E3C; }
        """)
        validate_exp_btn.clicked.connect(self.valider_expedition)
        bons_buttons_layout.addWidget(validate_exp_btn)
        
        detail_bon_btn = QPushButton("🔍 Ouvrir Détails du Bon")
        detail_bon_btn.setStyleSheet("""
            QPushButton {
                background-color: #7B1FA2; /* Deep Purple */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 12px;
                border: none;
            }
            QPushButton:hover { background-color: #9C27B0; }
            QPushButton:pressed { background-color: #6A1B9A; }
        """)
        detail_bon_btn.clicked.connect(self.ouvrir_details)
        bons_buttons_layout.addWidget(detail_bon_btn)

        bons_table_layout.addLayout(bons_buttons_layout)
        splitter.addWidget(bons_table_widget)

        # Right Side: Colis Preparation and Summary (within a ModernCard)
        right_panel_card = ModernCard()
        right_panel_layout = QVBoxLayout(right_panel_card)
        right_panel_layout.setSpacing(15)

        colis_prep_title = QLabel("📦 Préparation des Colis")
        colis_prep_title.setFont(QFont("Arial", 16, QFont.Bold))
        colis_prep_title.setStyleSheet("color: #424242;")
        right_panel_layout.addWidget(colis_prep_title)

        prep_inputs_layout = QHBoxLayout()
        prep_inputs_layout.addWidget(QLabel("🔢 ID Produit:"))
        self.prod_id_input = QLineEdit()
        self.prod_id_input.setPlaceholderText("Ex: 123")
        self.prod_id_input.setStyleSheet(input_style)
        prep_inputs_layout.addWidget(self.prod_id_input)

        prep_inputs_layout.addWidget(QLabel("➕ Quantité:"))
        self.qte_input = QLineEdit()
        self.qte_input.setPlaceholderText("Ex: 10")
        self.qte_input.setStyleSheet(input_style)
        prep_inputs_layout.addWidget(self.qte_input)
        
        prepare_btn = QPushButton("📦 Préparer colis")
        prepare_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722; /* Deep Orange */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 12px;
                border: none;
            }
            QPushButton:hover { background-color: #FF8A65; }
            QPushButton:pressed { background-color: #E64A19; }
        """)
        prepare_btn.clicked.connect(self.prepare_colis)
        prep_inputs_layout.addWidget(prepare_btn)
        right_panel_layout.addLayout(prep_inputs_layout)

        colis_summary_title = QLabel("📋 Colis associés au Bon sélectionné:")
        colis_summary_title.setFont(QFont("Arial", 14, QFont.Bold))
        colis_summary_title.setStyleSheet("color: #424242;")
        right_panel_layout.addWidget(colis_summary_title)

        self.colis_table = ModernTableWidget() # Using ModernTableWidget
        self.colis_table.setColumnCount(4)
        self.colis_table.setHorizontalHeaderLabels([
            "ID Colis", "Référence", "Date", "Quantité totale"
        ])
        right_panel_layout.addWidget(self.colis_table)

        splitter.addWidget(right_panel_card)
        splitter.setSizes([700, 400]) # Adjust initial sizes as preferred
        main_layout.addWidget(splitter)


    def apply_modern_theme(self):
        """Applies the modern CSS styles to the widgets."""
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA; /* Light background for the module */
                color: #212121;
            }
            QLabel {
                font-family: "Arial", sans-serif;
            }
            /* The individual styles for QPushButton, QLineEdit, QComboBox, QDateEdit,
               QTableWidget, QHeaderView::section are now defined inline in setup_ui
               for better control over specific button/input colors per section.
               However, general styles can still be defined here.
            */
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

    def create_expedition(self):
        ref = self.ref_input.text().strip()
        if not ref:
            QMessageBox.warning(self, "⚠️ Champ requis", "Référence obligatoire.")
            return
        
        priorite_map = {
            "normal": "normal",
            "élevée": "élevée",
            "urgente": "urgente"
        }
        priorite = priorite_map.get(self.priority_input.currentText(), "normal") # Get actual value

        try:
            date_prevue = self.date_input.date().toPyDate()
            bon_id = handle_create_expedition(
                self.conn, ref, date_prevue, priorite, self.user["idIndividu"]
            )
            QMessageBox.information(self, "🎉 Succès", f"Bon d'expédition #{bon_id} créé avec succès.")
            self.ref_input.clear()
            self.load_bons()
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Échec de la création du bon d'expédition :\n{e}")

    def load_bons(self):
        try:
            bons = handle_pending_expeditions(self.conn)
            self.bons_table.setRowCount(len(bons))
            
            pending_count = 0
            preparing_count = 0
            expedited_today_count = 0
            current_date = datetime.date.today()

            for row, b in enumerate(bons):
                self.bons_table.setItem(row, 0, QTableWidgetItem(str(b["idBon"])))
                self.bons_table.setItem(row, 1, QTableWidgetItem(b["reference"]))
                self.bons_table.setItem(row, 2, QTableWidgetItem(b["dateCreation"].strftime("%d/%m/%Y %H:%M:%S"))) # Show time
                self.bons_table.setItem(row, 3, QTableWidgetItem(format_date(b["dateExpeditionPrevue"])))
                self.bons_table.setItem(row, 4, QTableWidgetItem(b["priorite"]))
                self.bons_table.setItem(row, 5, QTableWidgetItem(b["statut"]))

                # Apply row coloring based on status
                color = QColor(255, 255, 255) # Default white
                if b["statut"] == "en_attente":
                    color = QColor(255, 243, 224) # Light Orange
                    pending_count += 1
                elif b["statut"] == "en_preparation":
                    color = QColor(227, 242, 253) # Light Blue
                    preparing_count += 1
                elif b["statut"] == "expédié":
                    color = QColor(200, 255, 200) # Light Green
                    # Assuming 'dateValidation' or similar field exists for expedition date
                    # if 'dateExpedition' in b and b['dateExpedition'].date() == current_date:
                    #     expedited_today_count += 1
                    # For now, just count if status is 'expédié' (if it means it was expedited today or recently)
                    # You need to adjust your controller to return actual expedition date for accurate count
                    pass # Not counting for "expédié" unless specific date field is available.

                for col in range(self.bons_table.columnCount()):
                    item = self.bons_table.item(row, col)
                    if item:
                        item.setBackground(color)

            self.bons_table.resizeColumnsToContents()
            self.colis_table.setRowCount(0) # Clear colis table when bons are reloaded
            self.selected_bon_id = None # Deselect bon

            # Update stats cards
            self.stats_widget.update_card_value("Bons en Attente", pending_count)
            self.stats_widget.update_card_value("Bons en Préparation", preparing_count)
            # You'll need to fetch 'expedié' count specifically from your controller if it's not in pending_expeditions
            # For now, it will remain '0' unless you adjust handle_pending_expeditions or add a new handler.
            self.stats_widget.update_card_value("Bons Expédiés (Aujourd'hui)", expedited_today_count) 
            self.stats_widget.update_card_value("Dernière MAJ", datetime.datetime.now().strftime("%H:%M:%S"))

        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Échec du chargement des bons d'expédition :\n{e}")

    def on_bon_selected(self, row, _):
        self.selected_bon_id = int(self.bons_table.item(row, 0).text())
        self.load_colis()

    def load_colis(self):
        if not self.selected_bon_id:
            self.colis_table.setRowCount(0) # Clear if no bon selected
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
            QMessageBox.critical(self, "❌ Erreur", f"Chargement des colis échoué:\n{str(e)}")

    def prepare_colis(self):
        if not self.selected_bon_id:
            QMessageBox.warning(self, "⚠️ Sélection requise", "Veuillez sélectionner un bon d'expédition d'abord.")
            return
        try:
            produit_id = int(self.prod_id_input.text())
            quantite = int(self.qte_input.text())
            if quantite <= 0:
                raise ValueError("La quantité doit être un nombre positif.")
            
            # Ensure the bon is 'en_attente' or 'en_preparation' before preparing colis
            current_status = self.bons_table.item(self.bons_table.currentRow(), 5).text()
            if current_status not in ["en_attente", "en_preparation"]:
                QMessageBox.warning(self, "Action impossible", "Vous ne pouvez préparer des colis que pour les bons 'en_attente' ou 'en_preparation'.")
                return

            colis_id = handle_preparation_expedition(
                self.conn, self.selected_bon_id, produit_id, quantite
            )
            QMessageBox.information(self, "📦 Colis préparé", f"Colis #{colis_id} ajouté au bon d'expédition.")
            self.prod_id_input.clear()
            self.qte_input.clear()
            self.load_colis() # Refresh colis for the selected bon
            self.load_bons() # Refresh bons table as status might change to 'en_preparation'
        except ValueError:
            QMessageBox.warning(self, "⚠️ Erreur de saisie", "Veuillez entrer des nombres valides pour l'ID produit et la quantité.")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Échec de la préparation du colis :\n{str(e)}")

    def ouvrir_details(self):
        if not self.selected_bon_id:
            QMessageBox.warning(self, "⚠️ Sélection requise", "Veuillez sélectionner un bon d'expédition pour voir les détails.")
            return
        try:
            # Re-initialize detail_window to ensure it's fresh if opened multiple times
            if self.detail_window is None or not self.detail_window.isVisible():
                self.detail_window = ExpeditionDetailWindow(self.conn, self.user, self.selected_bon_id)
                # Connect a signal from the detail window to refresh bons when it closes or data changes
                self.detail_window.finished.connect(self.load_bons) # QDialog has a 'finished' signal
                self.detail_window.show()
            else:
                self.detail_window.raise_()
                self.detail_window.activateWindow()
                self.detail_window.load_expedition_data(self.selected_bon_id) # Reload data if already open
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Impossible d'ouvrir la fenêtre de détails :\n{str(e)}")

    def valider_expedition(self):
        try:
            row = self.bons_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "⚠️ Sélection", "Veuillez sélectionner un bon d’expédition à valider.")
                return

            bon_id = int(self.bons_table.item(row, 0).text())
            current_status = self.bons_table.item(row, 5).text()

            if current_status == "expédié":
                QMessageBox.information(self, "Info", "Ce bon d'expédition est déjà validé (expédié).")
                return
            
            # Check if there are any colis associated with the bon
            colis_for_bon = handle_colis_by_bon(self.conn, bon_id)
            if not colis_for_bon:
                reply = QMessageBox.question(self, "Confirmation", 
                                             "Ce bon n'a aucun colis associé. Voulez-vous vraiment le valider sans colis?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return

            handle_valider_expedition(self.conn, bon_id)

            QMessageBox.information(self, "✅ Succès", f"Bon d’expédition #{bon_id} validé avec succès (expédié).")
            self.load_bons() # Reload data to reflect status change
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Erreur lors de la validation de l'expédition :\n{e}")