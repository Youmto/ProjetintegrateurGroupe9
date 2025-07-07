from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout,
    QHeaderView, QFrame, QGraphicsDropShadowEffect, # Added for modern UI
    QSpacerItem, QSizePolicy # Added for flexible layouts
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont # Added for custom styling

from datetime import datetime
from controllers.expedition_controller import handle_colis_en_cours, handle_confirmer_livraison
from models.expedition_model import get_pending_expeditions

import logging
logger = logging.getLogger(__name__)

# --- Reusable Modern UI Components ---

class ModernCard(QFrame):
    """Modern card with shadow effect, reusable for sections."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
            }
            QFrame:hover {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class ModernTableWidget(QTableWidget):
    """Modern table with custom styles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                gridline-color: #f1f3f4;
                font-size: 13px;
                color: #2c3e50;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
                color: #495057;
                padding: 10px 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                font-size: 12px;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e9ecef, stop: 1 #dee2e6);
            }
        """)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)


class LivreurConfirmationWindow(QWidget):
    def __init__(self, db_conn, user):
        super().__init__()
        self.db_conn = db_conn
        self.user = user
        self.setWindowTitle("✅ Confirmation de Livraison des Colis") # Enhanced title
        self.setMinimumSize(950, 600) # Larger minimum size for modern layout
        self.init_ui()
        self.apply_modern_theme() # Apply general theme
        self.charger_colis() # Load data on startup

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # --- Header Section ---
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("🚚 Colis en attente de Confirmation") # Modern title label
        self.title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 5px;
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # --- Separator Line ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e1e5e9; height: 2px; border-radius: 1px;")
        main_layout.addWidget(separator)

        # --- Colis Table (inside a ModernCard) ---
        table_card = ModernCard()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)

        table_title = QLabel("📦 Liste des Colis à Confirmer")
        table_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        table_layout.addWidget(table_title)

        # Use ModernTableWidget, but keep original column count and labels
        self.colis_table = ModernTableWidget()
        self.colis_table.setColumnCount(5) # Sticking to original 5 columns
        self.colis_table.setHorizontalHeaderLabels([
            "ID Colis", "Référence", "Date création", "Bon d'expédition", "Statut"
        ])
        
        header = self.colis_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Stretch 'Référence'
        header.setSectionResizeMode(3, QHeaderView.Stretch) # Stretch 'Bon d\'expédition'
        header.setStretchLastSection(True)

        table_layout.addWidget(self.colis_table)
        table_card.setLayout(table_layout)
        main_layout.addWidget(table_card)

        # --- Buttons Area ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Rafraîchir la Liste")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ec971f; }
            QPushButton:pressed { background-color: #d58d1b; }
        """)
        self.refresh_btn.clicked.connect(self.charger_colis)
        button_layout.addWidget(self.refresh_btn)

        self.confirm_btn = QPushButton("✅ Confirmer la Livraison")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1e7e34; }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirmer_livraison)
        button_layout.addWidget(self.confirm_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def apply_modern_theme(self):
        """Applies the general modern theme to the window."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
        """)

    def charger_colis(self):
        """
        Loads parcels in progress and updates the table.
        Logic is preserved here, specifically no 'idBon' key expected from 'c'.
        """
        self.colis_table.setRowCount(0)
        # Re-set column count to original 5, if it was changed by a previous call
        # This is a safe guard, but generally setColumnCount should only be needed once.
        if self.colis_table.columnCount() != 5:
            self.colis_table.setColumnCount(5)
            self.colis_table.setHorizontalHeaderLabels([
                "ID Colis", "Référence", "Date création", "Bon d'expédition", "Statut"
            ])

        try:
            colis = handle_colis_en_cours(self.db_conn)

            if not colis:
                QMessageBox.information(self, "Aucun colis", "Aucun colis en cours à livrer.")
                self.title_label.setText("🚚 Colis en attente de Confirmation (0)")
                self.colis_table.setRowCount(0)
                self.confirm_btn.setEnabled(False) # Disable if no parcels
                return
                
            self.colis_table.setRowCount(len(colis))
            for row, c in enumerate(colis):
                self.colis_table.setItem(row, 0, QTableWidgetItem(str(c['idColis'])))
                self.colis_table.setItem(row, 1, QTableWidgetItem(c['reference']))
                
                # Robust date handling (unchanged)
                date = c['date_creation']
                display_date = ""
                if date:
                    if isinstance(date, str):
                        try:
                            dt_obj = datetime.fromisoformat(date)
                            display_date = dt_obj.strftime("%d/%m/%Y %H:%M:%S")
                        except ValueError:
                            try: # Try another common format if isoformat fails
                                dt_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                                display_date = dt_obj.strftime("%d/%m/%Y %H:%M:%S")
                            except ValueError:
                                display_date = "Date Invalide"
                                logger.warning(f"Unexpected date format for {date}")
                    elif isinstance(date, datetime):
                        display_date = date.strftime("%d/%m/%Y %H:%M:%S")
                self.colis_table.setItem(row, 2, QTableWidgetItem(display_date))
                
                self.colis_table.setItem(row, 3, QTableWidgetItem(c['bon_expedition']))
                
                # Conditional coloring for status (UI enhancement)
                status_item = QTableWidgetItem(c['statut'])
                status_text = c['statut'].lower()
                if status_text == 'livré':
                    status_item.setForeground(QColor(0, 128, 0)) # Green
                elif status_text == 'en cours':
                    status_item.setForeground(QColor(255, 140, 0)) # Orange
                elif status_text == 'en attente':
                    status_item.setForeground(QColor(0, 0, 128)) # Dark Blue
                else:
                    status_item.setForeground(QColor(50, 50, 50)) # Dark Grey default
                self.colis_table.setItem(row, 4, status_item)
            
            self.colis_table.resizeColumnsToContents()
            self.title_label.setText(f"🚚 Colis en attente de Confirmation ({len(colis)})")
            
            # Enable/disable confirm button based on 'En cours' parcels
            has_confirmable_colis = any(c.get('statut') == 'en_cours' for c in colis)
            self.confirm_btn.setEnabled(has_confirmable_colis)
                
        except Exception as e:
            logger.error(f"Error loading parcels: {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur de Chargement", f"Impossible de charger les colis : {str(e)}")
            self.title_label.setText("🚚 Colis en attente de Confirmation (Erreur)")
            self.confirm_btn.setEnabled(False)

    def confirmer_livraison(self):
        """
        Confirms the delivery of the selected parcel.
        The logic here is *strictly identical* to your original code.
        """
        selected_row = self.colis_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un colis.")
            return
            
        try:
            # ORIGINAL LOGIC PRESERVED: retrieves 'bon_ref' from visible column 3
            bon_ref = self.colis_table.item(selected_row, 3).text()
            colis_id = int(self.colis_table.item(selected_row, 0).text())
            
            # ORIGINAL LOGIC PRESERVED: searches for the corresponding 'bon'
            # by fetching ALL pending expeditions again and matching by 'reference'
            bons = get_pending_expeditions(self.db_conn)
            bon_trouve = None
            
            for bon in bons:
                if bon['reference'] == bon_ref:
                    bon_trouve = bon
                    break
                    
            if not bon_trouve:
                raise ValueError("Bon d'expédition non trouvé")
                
            # ORIGINAL LOGIC PRESERVED: calls the controller with 'idBon' from the found 'bon' object
            handle_confirmer_livraison(self.db_conn, bon_trouve['idBon'])
            
            QMessageBox.information(self, "Succès", "Colis marqué comme livré.")
            self.charger_colis()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de confirmation : {str(e)}")