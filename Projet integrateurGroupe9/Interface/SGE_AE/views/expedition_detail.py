from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHBoxLayout, QHeaderView, QSizePolicy,
    QFrame, QGraphicsDropShadowEffect, QSplitter, QScrollArea,
    QSpacerItem, QApplication
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont, QCursor

# Assurez-vous que ce chemin est correct pour vos contrôleurs
from controllers.expedition_controller import (
    handle_get_colis_by_bon,
    handle_get_contenu_colis,
    handle_get_exceptions,
    handle_valider_expedition, # Cette fonction est celle que vous devez modifier dans le contrôleur
    handle_generer_bordereau_pdf,
)
import os
import datetime

# --- DÉFINITIONS DES CLASSES DE STYLE MODERNES ---
# Ces classes sont laissées ici pour que le fichier soit autonome.
# Pour une meilleure organisation, déplacez-les vers un fichier partagé (ex: utils/modern_widgets.py).

class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(15, 15, 15, 15)
        self.setMinimumHeight(100)

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

class ModernTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                selection-background-color: #E3F2FD;
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
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #B0BEC5;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)

# --- FIN DES DÉFINITIONS DES CLASSES DE STYLE MODERNES ---


def format_date(dt):
    """Formate un objet datetime ou date en chaîne de caractères JJ/MM/AAAA."""
    return dt.strftime("%d/%m/%Y") if isinstance(dt, (datetime.date, datetime.datetime)) else "—"

def format_datetime(dt):
    """Formate un objet datetime en chaîne de caractères JJ/MM/AAAA HH:MM:SS."""
    # CORRECTION ICI: %d/%m/%Y au lieu de %d/%d/%Y
    return dt.strftime("%d/%m/%Y %H:%M:%S") if isinstance(dt, datetime.datetime) else "—"


class ExpeditionDetailWindow(QWidget):
    data_changed = pyqtSignal()
    
    def __init__(self, db_conn, user, expedition_id):
        super().__init__()
        self.conn = db_conn
        self.user = user
        self.expedition_id = expedition_id
        self.setWindowTitle(f"📦 Détail de l'expédition #{expedition_id}")
        self.setMinimumSize(1000, 700)
        
        # Attributs pour l'affichage progressif
        self._all_colis_data = []
        self._current_colis_row_count = 0
        self.COLIS_LOAD_CHUNK_SIZE = 20 # Nombre de colis à charger à chaque fois
        self.colis_load_timer = QTimer(self)
        self.colis_load_timer.timeout.connect(self._load_next_colis_chunk)

        self._all_exceptions_data = []
        self._current_exceptions_row_count = 0
        self.EXCEPTIONS_LOAD_CHUNK_SIZE = 10 # Nombre d'exceptions à charger à chaque fois
        self.exceptions_load_timer = QTimer(self)
        self.exceptions_load_timer.timeout.connect(self._load_next_exceptions_chunk)

        self.init_ui()
        self.load_data() # Charger les données après l'initialisation de l'UI

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Titre principal avec icône
        title = QLabel(f"📦 Détail du Bon d'Expédition <span style='color:#2196F3;'>#{self.expedition_id}</span>")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setStyleSheet("color: #263238;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Utilisation de QSplitter pour une disposition flexible et redimensionnable
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setHandleWidth(10)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #CFD8DC;
                border: 1px solid #B0BEC5;
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: #90A4AE;
            }
        """)

        # --- Section Colis (dans une ModernCard) ---
        colis_card = ModernCard()
        colis_layout = QVBoxLayout(colis_card)
        colis_layout.setSpacing(10)

        colis_label = QLabel("🚚 Liste des Colis :")
        colis_label.setFont(QFont("Arial", 18, QFont.Bold))
        colis_label.setStyleSheet("color: #37474F;")
        colis_layout.addWidget(colis_label)

        self.colis_table = ModernTableWidget()
        self.colis_table.setColumnCount(4)
        self.colis_table.setHorizontalHeaderLabels(["ID Colis", "Référence", "Date création", "Statut"])
        self.colis_table.itemSelectionChanged.connect(self.show_contenu_colis)
        self.colis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.colis_table.verticalScrollBar().valueChanged.connect(self._check_scroll_colis)
        colis_layout.addWidget(self.colis_table)
        main_splitter.addWidget(colis_card)

        # Conteneur pour le résumé des colis et les exceptions
        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.setHandleWidth(10)
        bottom_splitter.setStyleSheet(main_splitter.styleSheet())

        # --- Section Contenu du Colis (dans une ModernCard) ---
        resume_card = ModernCard()
        resume_layout = QVBoxLayout(resume_card)
        resume_layout.setSpacing(10)

        resume_label = QLabel("📋 Contenu du Colis Sélectionné :")
        resume_label.setFont(QFont("Arial", 18, QFont.Bold))
        resume_label.setStyleSheet("color: #37474F;")
        resume_layout.addWidget(resume_label)

        self.resume_table = ModernTableWidget()
        self.resume_table.setColumnCount(4)
        self.resume_table.setHorizontalHeaderLabels(["Lot", "Date prod.", "Qté", "Date exp."])
        self.resume_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        resume_layout.addWidget(self.resume_table)
        bottom_splitter.addWidget(resume_card)

        # --- Section Exceptions (dans une ModernCard) ---
        exceptions_card = ModernCard()
        exceptions_layout = QVBoxLayout(exceptions_card)
        exceptions_layout.setSpacing(10)

        exceptions_label = QLabel("⚠️ Rapports d'Exception :")
        exceptions_label.setFont(QFont("Arial", 18, QFont.Bold))
        exceptions_label.setStyleSheet("color: #37474F;")
        exceptions_layout.addWidget(exceptions_label)

        self.exceptions_table = ModernTableWidget()
        self.exceptions_table.setColumnCount(3)
        self.exceptions_table.setHorizontalHeaderLabels(["Date", "Type", "Description"])
        self.exceptions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.exceptions_table.verticalScrollBar().valueChanged.connect(self._check_scroll_exceptions)
        exceptions_layout.addWidget(self.exceptions_table)
        bottom_splitter.addWidget(exceptions_card)

        main_splitter.addWidget(bottom_splitter)
        main_splitter.setSizes([self.height() // 2, self.height() // 2])
        bottom_splitter.setSizes([self.width() // 2, self.width() // 2])

        main_layout.addWidget(main_splitter)

        # --- Section Boutons (avec QGraphicsDropShadowEffect) ---
        btns_layout = QHBoxLayout()
        btns_layout.addStretch()

        # Base style for buttons (no box-shadow)
        button_base_style = """
            QPushButton {
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 12px 20px;
                border: none;
                margin: 8px;
            }
        """
        
        # Helper to create button with shadow and hover effects
        def create_shadowed_button(text, bg_color, hover_color, pressed_color, parent_widget, connect_func):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: white;
                    font-weight: bold;
                    border-radius: 10px;
                    padding: 12px 20px;
                    border: none;
                    margin: 8px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """)
            
            # Apply QGraphicsDropShadowEffect
            shadow = QGraphicsDropShadowEffect(btn)
            shadow.setBlurRadius(15) # Default shadow blur
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0, 0, 0, 80)) # Darker shadow for buttons
            btn.setGraphicsEffect(shadow)

            # Animations for hover (similar to ModernCard)
            blur_animation = QPropertyAnimation(shadow, b"blurRadius")
            blur_animation.setDuration(150)
            blur_animation.setEasingCurve(QEasingCurve.OutQuad)

            offset_animation = QPropertyAnimation(shadow, b"yOffset")
            offset_animation.setDuration(150)
            offset_animation.setEasingCurve(QEasingCurve.OutQuad)

            # Store animations on the button to prevent garbage collection
            btn._blur_animation = blur_animation
            btn._offset_animation = offset_animation

            # Override enter/leave events for custom shadow animation
            original_enter_event = btn.enterEvent
            original_leave_event = btn.leaveEvent

            def new_enter_event(event):
                blur_animation.setStartValue(shadow.blurRadius())
                blur_animation.setEndValue(25) # More blur on hover
                blur_animation.start()

                offset_animation.setStartValue(shadow.yOffset())
                offset_animation.setEndValue(8) # Lift up slightly on hover
                offset_animation.start()
                original_enter_event(event)

            def new_leave_event(event):
                blur_animation.setStartValue(shadow.blurRadius())
                blur_animation.setEndValue(15)
                blur_animation.start()

                offset_animation.setStartValue(shadow.yOffset())
                offset_animation.setEndValue(5)
                offset_animation.start()
                original_leave_event(event)
            
            btn.enterEvent = new_enter_event
            btn.leaveEvent = new_leave_event

            btn.clicked.connect(connect_func)
            return btn

        valider_btn = create_shadowed_button(
            "✅ Valider l'expédition", "#4CAF50", "#66BB6A", "#388E3C", self, self.valider_expedition
        )
        btns_layout.addWidget(valider_btn)

        pdf_btn = create_shadowed_button(
            "📄 Générer Bordereau PDF", "#2196F3", "#64B5F6", "#1976D2", self, self.generer_pdf
        )
        btns_layout.addWidget(pdf_btn)

        refresh_btn = create_shadowed_button(
            "🔄 Rafraîchir", "#607D8B", "#90A4AE", "#455A64", self, self.load_data
        )
        btns_layout.addWidget(refresh_btn)
        
        btns_layout.addStretch()

        main_layout.addLayout(btns_layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                color: #212121;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            }
            QLabel {
                color: #37474F;
            }
            QMessageBox {
                background-color: #FFFFFF;
                color: #212121;
            }
            QMessageBox QPushButton { /* Styles for QMessageBox buttons, not main window buttons */
                background-color: #42A5F5;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                border: none; /* Ensure no default border */
            }
        """)

    def load_data(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            # Votre logique existante d'appel aux contrôleurs
            self._all_colis_data = handle_get_colis_by_bon(self.conn, self.expedition_id)
            self.colis_table.setRowCount(0)
            self._current_colis_row_count = 0
            self.colis_load_timer.stop()
            self._load_next_colis_chunk()

            self._all_exceptions_data = handle_get_exceptions(self.conn, self.expedition_id)
            self.exceptions_table.setRowCount(0)
            self._current_exceptions_row_count = 0
            self.exceptions_load_timer.stop()
            self._load_next_exceptions_chunk()

            self.resume_table.setRowCount(0)
            
            if self._all_colis_data:
                QTimer.singleShot(100, lambda: self.colis_table.selectRow(0))
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur de chargement", f"Impossible de charger les détails de l'expédition :\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def _load_next_colis_chunk(self):
        start_index = self._current_colis_row_count
        end_index = min(len(self._all_colis_data), start_index + self.COLIS_LOAD_CHUNK_SIZE)
        
        if start_index >= end_index:
            self.colis_load_timer.stop()
            return

        self.colis_table.setUpdatesEnabled(False)
        self.colis_table.setRowCount(end_index)
        
        for row in range(start_index, end_index):
            colis = self._all_colis_data[row]
            # Assurez-vous que les clés du dictionnaire 'colis' sont bien 'idColis', 'reference', 'dateCreation', 'statut'
            # Cette date sera celle qui a été mise à jour par le contrôleur si l'expédition a été validée
            self.colis_table.setItem(row, 0, QTableWidgetItem(str(colis['idColis'])))
            self.colis_table.setItem(row, 1, QTableWidgetItem(colis['reference']))
            self.colis_table.setItem(row, 2, QTableWidgetItem(format_datetime(colis['dateCreation'])))
            self.colis_table.setItem(row, 3, QTableWidgetItem(colis['statut']))
        
        self.colis_table.setUpdatesEnabled(True)
        self.colis_table.viewport().update()
        self.colis_table.resizeColumnsToContents()
        self._current_colis_row_count = end_index

    def _check_scroll_colis(self, value):
        scroll_bar = self.colis_table.verticalScrollBar()
        # Adjusted condition: Check if scroll value is near the maximum, or if the table is small and has more data to load.
        if value > 0 and (value >= scroll_bar.maximum() - 2 or (scroll_bar.maximum() == 0 and len(self._all_colis_data) > self._current_colis_row_count)):
            if not self.colis_load_timer.isActive():
                self.colis_load_timer.start(50)

    def _load_next_exceptions_chunk(self):
        start_index = self._current_exceptions_row_count
        end_index = min(len(self._all_exceptions_data), start_index + self.EXCEPTIONS_LOAD_CHUNK_SIZE)
        
        if start_index >= end_index:
            self.exceptions_load_timer.stop()
            return

        self.exceptions_table.setUpdatesEnabled(False)
        self.exceptions_table.setRowCount(end_index)
        
        for row in range(start_index, end_index):
            exception = self._all_exceptions_data[row]
            # Assurez-vous que les clés du dictionnaire 'exception' sont bien 'date', 'type', 'description'
            self.exceptions_table.setItem(row, 0, QTableWidgetItem(format_datetime(exception['date'])))
            self.exceptions_table.setItem(row, 1, QTableWidgetItem(exception.get('type', '—')))
            self.exceptions_table.setItem(row, 2, QTableWidgetItem(exception['description']))
        
        self.exceptions_table.setUpdatesEnabled(True)
        self.exceptions_table.viewport().update()
        self.exceptions_table.resizeColumnsToContents()
        self._current_exceptions_row_count = end_index

    def _check_scroll_exceptions(self, value):
        scroll_bar = self.exceptions_table.verticalScrollBar()
        if value > 0 and (value >= scroll_bar.maximum() - 2 or (scroll_bar.maximum() == 0 and len(self._all_exceptions_data) > self._current_exceptions_row_count)):
            if not self.exceptions_load_timer.isActive():
                self.exceptions_load_timer.start(50)

    def show_contenu_colis(self):
        try:
            selected_rows = self.colis_table.selectionModel().selectedRows()
            if not selected_rows:
                self.resume_table.setRowCount(0)
                return

            row = selected_rows[0].row()
            id_colis_item = self.colis_table.item(row, 0)
            if id_colis_item is None or not id_colis_item.text().isdigit():
                self.resume_table.setRowCount(0)
                return

            id_colis = int(id_colis_item.text())
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
        try:
            reply = QMessageBox.question(self, "Confirmer Validation", 
                                         f"Êtes-vous sûr de vouloir valider l'expédition #{self.expedition_id} ?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

            # C'est ici que handle_valider_expedition est appelée.
            # Elle doit contenir la logique pour mettre à jour 'dateCreation' dans votre DB.
            handle_valider_expedition(self.conn, self.expedition_id) 
            
            QMessageBox.information(self, "Succès", f"L'expédition #{self.expedition_id} a été validée avec succès.")
            
            # Après la validation, on recharge les données pour que l'interface affiche la nouvelle date de création
            self.load_data() 
            self.data_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Erreur de validation", f"Échec de la validation de l'expédition :\n{str(e)}")

    def generer_pdf(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            file_path = handle_generer_bordereau_pdf(self.conn, self.expedition_id)
            if os.path.exists(file_path):
                QMessageBox.information(self, "PDF généré", f"Bordereau enregistré sous :\n{file_path}")
            else:
                raise FileNotFoundError("Le fichier n'a pas été généré correctement.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur PDF", f"Erreur génération PDF : {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def closeEvent(self, event):
        self.data_changed.emit()
        super().closeEvent(event)