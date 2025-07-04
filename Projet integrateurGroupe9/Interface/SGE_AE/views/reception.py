from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QDateEdit, QMessageBox,
    QSplitter, QGroupBox, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import QDate, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont
import datetime

# --- MODIFIED ModernCard CLASS ---
class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(15, 15, 15, 15)
        self.setMinimumHeight(120) # Give it a bit more minimum height

        # Initial Shadow Effect - make it a child of self for proper memory management
        self.initial_shadow = QGraphicsDropShadowEffect(self)
        self.initial_shadow.setBlurRadius(20)
        self.initial_shadow.setXOffset(0)
        self.initial_shadow.setYOffset(5)
        self.initial_shadow.setColor(QColor(0, 0, 0, 30))
        
        # Hover Shadow Properties (values for animation target)
        self.hover_blur_radius = 35
        self.hover_y_offset = 10
        self.hover_shadow_color = QColor(0, 0, 0, 60)

        # Start with the initial shadow
        self.setGraphicsEffect(self.initial_shadow)

        # QPropertyAnimation for smooth transition of blur radius and yOffset
        self.blur_animation = QPropertyAnimation(self.initial_shadow, b"blurRadius")
        self.blur_animation.setDuration(200) # milliseconds
        self.blur_animation.setEasingCurve(QEasingCurve.OutQuad)

        self.offset_animation = QPropertyAnimation(self.initial_shadow, b"yOffset")
        self.offset_animation.setDuration(200)
        self.offset_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Apply initial border style
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0; /* Subtle initial border */
            }
        """)

    def enterEvent(self, event):
        # Change border on hover
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #B0D8FF; /* Lighter blue border on hover */
            }
        """)
        # Animate to hover shadow properties
        self.blur_animation.setStartValue(self.initial_shadow.blurRadius())
        self.blur_animation.setEndValue(self.hover_blur_radius)
        self.blur_animation.start()

        self.offset_animation.setStartValue(self.initial_shadow.yOffset())
        self.offset_animation.setEndValue(self.hover_y_offset)
        self.offset_animation.start()

        # Set hover shadow color directly
        self.initial_shadow.setColor(self.hover_shadow_color)

        super().enterEvent(event)

    def leaveEvent(self, event):
        # Revert border
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0; /* Revert to initial border */
            }
        """)
        # Animate back to initial shadow properties
        self.blur_animation.setStartValue(self.initial_shadow.blurRadius())
        self.blur_animation.setEndValue(20) # Revert to initial blur radius
        self.blur_animation.start()

        self.offset_animation.setStartValue(self.initial_shadow.yOffset())
        self.offset_animation.setEndValue(5) # Revert to initial yOffset
        self.offset_animation.start()

        # Revert shadow color directly
        self.initial_shadow.setColor(QColor(0, 0, 0, 30))

        super().leaveEvent(event)

# --- Your existing StatsWidget ---
class StatsWidget(QWidget):
    """
    Widget conteneur pour les cartes de statistiques.
    Il ne crée plus les cartes, mais les dispose.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)
        self.card_value_labels = {} # Pour stocker les QLabel de valeur des cartes

    def add_card(self, card_widget, title_key):
        """Ajoute une carte au layout et stocke son QLabel de valeur."""
        self.layout.addWidget(card_widget)
        # Assurez-vous que le QLabel de la valeur a bien un objectName pour être retrouvé
        value_label = card_widget.findChild(QLabel, f"{title_key}_value")
        if value_label:
            self.card_value_labels[title_key] = value_label

    def update_card_value(self, title_key, value):
        """Met à jour la valeur d'une carte existante par son titre/clé."""
        if title_key in self.card_value_labels:
            self.card_value_labels[title_key].setText(str(value))
        else:
            print(f"Erreur: La carte '{title_key}' n'a pas été trouvée pour la mise à jour.")

# --- The create_stat_card function, matching your Inventaire structure ---
def create_stat_card(icon, title, value, color):
    """
    Crée une carte de statistique individuelle avec icône, titre et valeur.
    Adapté pour utiliser ModernCard et les styles visuels souhaités.
    """
    card = ModernCard()
    # card.setFixedHeight(100) # REMOVED: Let ModernCard manage its height with minimumHeight

    card_layout = QVBoxLayout()
    card_layout.setContentsMargins(15, 15, 15, 15) # Marges internes
    card_layout.setSpacing(8)

    # Icône et titre
    top_layout = QHBoxLayout()
    icon_label = QLabel(icon)
    icon_label.setStyleSheet(f"font-size: 24px; color: {color};")
    title_label = QLabel(title)
    title_label.setStyleSheet(f"font-size: 12px; color: #7f8c8d; font-weight: bold;")
    title_label.setWordWrap(True) # Allow title to wrap if too long

    top_layout.addWidget(icon_label)
    top_layout.addWidget(title_label)
    top_layout.addStretch() # Pousse l'icône et le titre vers la gauche

    # Valeur
    value_label = QLabel(str(value)) # Ensure value is converted to string for QLabel
    value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
    value_label.setObjectName(f"{title}_value") # Nom d'objet pour retrouver le QLabel de valeur

    card_layout.addLayout(top_layout)
    card_layout.addWidget(value_label)
    card_layout.addStretch() # Pousse la valeur vers le haut

    card.setLayout(card_layout)
    return card

# --- Rest of your ReceptionModule code ---

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


# Importations de vos contrôleurs et vues existants
from controllers.reception_controller import (
    handle_receptions_en_attente,
    handle_validation_reception,
    valider_reception
)
from views.reception_detail import ReceptionDetailWindow


class ReceptionModule(QWidget):
    """Module de gestion des bons de réception avec une interface modernisée"""

    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.last_created_id = None
        self.detail_window = None
        self.setup_ui()
        self.apply_modern_theme() # Appliquer le thème moderne
        self.load_receptions()
        # update_stats est maintenant appelé à la fin de load_receptions

    def setup_ui(self):
        """Construction de l'interface utilisateur modernisée"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Section En-tête (Titre principal + Statistiques) ---
        header_layout = QVBoxLayout()
        title_label = QLabel("🚚 Gestion des Réceptions")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #263238;")
        header_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Initialisation du StatsWidget et ajout des cartes
        self.stats_widget = StatsWidget()
        # Adjusted colors for better contrast/visual appeal, feel free to fine-tune
        self.stats_widget.add_card(create_stat_card("📊", "Bons en Attente", "0", "#FF8A65"), "Bons en Attente") # Deeper Orange
        self.stats_widget.add_card(create_stat_card("⏳", "Bons en Cours", "0", "#64B5F6"), "Bons en Cours") # Brighter Blue
        # IMPORTANT: "Bons Validés (Aujourd'hui)" might be long, word-wrap helps.
        self.stats_widget.add_card(create_stat_card("✅", "Bons Validés (Aujourd'hui)", "0", "#81C784"), "Bons Validés (Aujourd'hui)") # More vibrant Green
        self.stats_widget.add_card(create_stat_card("🕒", "Dernière MAJ", "N/A", "#9E9E9E"), "Dernière MAJ") # Standard Grey
        
        header_layout.addWidget(self.stats_widget)
        main_layout.addLayout(header_layout)

        # --- Section Création de Bon de Réception (dans une ModernCard) ---
        creation_card = ModernCard()
        creation_layout = QHBoxLayout(creation_card)
        creation_layout.setSpacing(10)
        
        # Style des labels et inputs
        label_style = "QLabel { color: #424242; font-weight: 600; }"
        input_style = """
            QLineEdit, QDateEdit {
                border: 1px solid #CFD8DC;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #F5F5F5;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #2196F3;
                background-color: #FFFFFF;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
                image: url(icons/calendar_icon.png); /* Assurez-vous d'avoir cette icône ou retirez-la */
                subcontrol-origin: padding;
                subcontrol-position: right center;
            }
        """
        
        ref_label = QLabel("Référence*:")
        ref_label.setStyleSheet(label_style)
        creation_layout.addWidget(ref_label)
        self.ref_input = QLineEdit()
        self.ref_input.setPlaceholderText("Ex: REC-2023-001")
        self.ref_input.setStyleSheet(input_style)
        creation_layout.addWidget(self.ref_input)

        date_label = QLabel("Date prévue*:")
        date_label.setStyleSheet(label_style)
        creation_layout.addWidget(date_label)
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet(input_style)
        creation_layout.addWidget(self.date_input)

        self.create_btn = QPushButton("➕ Créer bon")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; /* Vert */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.create_btn.clicked.connect(self.create_reception)
        creation_layout.addWidget(self.create_btn)
        
        main_layout.addWidget(creation_card)

        # --- Section Liste des bons en attente (dans un QSplitter pour les détails) ---
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Table of Receptions
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0,0,0,0) # Pas de marges supplémentaires
        
        table_title_label = QLabel("📋 Bons de Réception")
        table_title_label.setFont(QFont("Arial", 16, QFont.Bold))
        table_title_label.setStyleSheet("color: #424242;")
        table_layout.addWidget(table_title_label)
        
        self.receptions_table = ModernTableWidget() # Utilisation de ModernTableWidget
        self.receptions_table.setColumnCount(5)
        self.receptions_table.setHorizontalHeaderLabels([
            "ID", "Référence", "Date création", "Date prévue", "Statut"
        ])
        self.receptions_table.doubleClicked.connect(self.show_reception_details)
        table_layout.addWidget(self.receptions_table)

        # Action Buttons below the table
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.refresh_btn = QPushButton("🔄 Rafraîchir")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B; /* Gris bleu */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #78909C;
            }
            QPushButton:pressed {
                background-color: #455A64;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_receptions)
        btn_layout.addWidget(self.refresh_btn)

        self.validate_btn = QPushButton("✅ Valider la réception finale")
        self.validate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; /* Bleu */
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #64B5F6;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        self.validate_btn.clicked.connect(self.validate_selected_reception)
        btn_layout.addWidget(self.validate_btn)

        table_layout.addLayout(btn_layout)
        
        splitter.addWidget(table_widget)

        # Right side: Placeholder for details (ReceptionDetailWindow will handle this separately)
        right_panel = ModernCard()
        right_panel_layout = QVBoxLayout(right_panel)
        message_label = QLabel("Cliquez deux fois sur un bon de réception\npour afficher ses détails ou enregistrer des lots.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #757575; font-style: italic; font-size: 14px;")
        right_panel_layout.addWidget(message_label)
        right_panel_layout.addStretch() # Pousse le message au centre
        splitter.addWidget(right_panel)

        splitter.setSizes([700, 300]) # Ajustez les tailles initiales selon vos préférences
        main_layout.addWidget(splitter)

    def apply_modern_theme(self):
        """Applique les styles CSS modernes aux widgets"""
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA; /* Couleur de fond légère pour tout le module */
                color: #212121;
            }
            QLabel {
                font-family: "Arial", sans-serif;
            }
        """)

    def load_receptions(self):
        """Charge et affiche la liste des bons de réception en attente et met à jour les stats"""
        try:
            receptions = handle_receptions_en_attente(self.db_conn)
            self.receptions_table.setRowCount(len(receptions))

            pending_count = 0
            in_progress_count = 0
            validated_today_count = 0
            current_date = datetime.date.today() # Utilise datetime.date pour comparaison

            for row_idx, reception in enumerate(receptions):
                self.receptions_table.setItem(row_idx, 0, QTableWidgetItem(str(reception['idBon'])))
                self.receptions_table.setItem(row_idx, 1, QTableWidgetItem(reception['reference']))
                
                date_creation_str = reception['dateCreation'].strftime("%d/%m/%Y %H:%M:%S") # Inclure l'heure
                self.receptions_table.setItem(row_idx, 2, QTableWidgetItem(date_creation_str))
                
                date_prevue_str = reception['dateReceptionPrevue'].strftime("%d/%m/%Y")
                self.receptions_table.setItem(row_idx, 3, QTableWidgetItem(date_prevue_str))
                
                statut = reception['statut']
                self.receptions_table.setItem(row_idx, 4, QTableWidgetItem(statut))

                # Colorisation des lignes et comptage des statistiques
                color = QColor(240, 240, 240)  # Par défaut gris clair (en attente si pas d'autre match)
                if statut == "en_cours":
                    color = QColor(255, 255, 200)  # Jaune clair
                    in_progress_count += 1
                elif statut == "validé":
                    color = QColor(200, 255, 200)  # Vert clair
                    # IMPORTANT: Assurez-vous que 'dateValidation' est retourné par handle_receptions_en_attente
                    # et qu'il s'agit d'un objet datetime.date ou datetime.datetime
                    if 'dateValidation' in reception and reception['dateValidation'].date() == current_date:
                        validated_today_count += 1
                elif statut == "en_attente":
                    color = QColor(255, 243, 224) # Orange très clair
                    pending_count += 1 
                
                for col in range(self.receptions_table.columnCount()):
                    item = self.receptions_table.item(row_idx, col)
                    if item: 
                        item.setBackground(color)

            self.receptions_table.resizeColumnsToContents()

            # Sélectionne automatiquement le dernier bon créé
            if self.last_created_id is not None:
                for r in range(self.receptions_table.rowCount()):
                    if int(self.receptions_table.item(r, 0).text()) == self.last_created_id:
                        self.receptions_table.selectRow(r)
                        self.last_created_id = None
                        break
            
            # Mettre à jour les statistiques après le chargement
            self.stats_widget.update_card_value("Bons en Attente", pending_count)
            self.stats_widget.update_card_value("Bons en Cours", in_progress_count)
            self.stats_widget.update_card_value("Bons Validés (Aujourd'hui)", validated_today_count)
            self.stats_widget.update_card_value("Dernière MAJ", datetime.datetime.now().strftime("%H:%M:%S"))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec du chargement des réceptions :\n{e}")

    def create_reception(self):
        """Crée un nouveau bon de réception"""
        reference = self.ref_input.text().strip()
        date_prevue = self.date_input.date().toString("yyyy-MM-dd")

        if not reference:
            QMessageBox.warning(self, "Champ requis", "La référence est obligatoire.")
            return

        try:
            reception_id = handle_validation_reception(
                self.db_conn,
                reference,
                date_prevue,
                self.user['idIndividu']
            )
            self.last_created_id = reception_id
            QMessageBox.information(self, "Succès", f"Bon de réception #{reception_id} créé avec succès.")
            self.ref_input.clear()
            self.load_receptions() # Recharge la table et met à jour les stats
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la création :\n{e}")

    def show_reception_details(self, index):
        """Affiche les détails du bon de réception sélectionné"""
        reception_id = int(self.receptions_table.item(index.row(), 0).text())
        if self.detail_window is None or not self.detail_window.isVisible():
            self.detail_window = ReceptionDetailWindow(self.db_conn, self.user, reception_id)
            self.detail_window.reception_completed.connect(self.load_receptions)
            self.detail_window.closed.connect(self.load_receptions)
            self.detail_window.show()
        else:
            self.detail_window.raise_()
            self.detail_window.activateWindow()
            self.detail_window.load_reception_data(reception_id)


    def validate_selected_reception(self):
        """Valide le bon de réception sélectionné"""
        selected_row = self.receptions_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un bon de réception à valider.")
            return
        
        reception_id = int(self.receptions_table.item(selected_row, 0).text())
        statut = self.receptions_table.item(selected_row, 4).text()

        if statut != "en_cours":
            QMessageBox.warning(self, "Validation impossible", "Seuls les bons 'en_cours' peuvent être validés.")
            return

        try:
            valider_reception(self.db_conn, reception_id)
            QMessageBox.information(self, "Succès", f"Bon #{reception_id} validé avec succès.")
            self.load_receptions() # Recharge la table et met à jour les stats
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la validation :\n{e}")