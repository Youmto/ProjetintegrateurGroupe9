from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDateEdit,
    QFormLayout, QFileDialog, QFrame, QGraphicsDropShadowEffect
) # QSplitter n'est pas utilisé dans le code fourni, je l'ai retiré pour la clarté
from PyQt5.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont
from datetime import datetime, date
import logging
import csv

# --- MODIFICATION ICI : IMPORTER handle_get_product_movement_totals DU CONTRÔLEUR ---
from controllers.movement_controller import handle_mouvements_produit, handle_get_product_movement_totals
from models.product_model import get_all_products


logger = logging.getLogger(__name__)


class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(15, 15, 15, 15)
        self.setMinimumHeight(80)

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
    card.setMinimumHeight(100)

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
                selection-background-color: #E3F2FD;
                selection-color: #212121;
                font-size: 13px;
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
                border-bottom: 1px solid #D0D0D0;
                font-weight: bold;
                font-size: 14px;
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


class MouvementsModule(QWidget):
    def __init__(self, conn, user=None):
        super().__init__()
        self.conn = conn
        self.user = user
        self.products = []
        self.movement_type_mapping = {
            "Tous": None,
            "Réception": "Entrée",
            "Expédition": "Sortie",
            "Déplacement": "Déplacement"
        }
        self.init_ui()
        self.apply_modern_theme()
        self.load_products()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title = QLabel("📦 Suivi des Mouvements de Stock")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #263238;")
        main_layout.addWidget(title)

        self.stats_widget = StatsWidget()
        self.stats_widget.add_card(create_stat_card("⬆️", "Réceptions Totales", "0", "#28a745"), "Réceptions Totales")
        self.stats_widget.add_card(create_stat_card("⬇️", "Expéditions Totales", "0", "#dc3545"), "Expéditions Totales")
        self.stats_widget.add_card(create_stat_card("🔄", "Déplacements Totaux", "0", "#17a2b8"), "Déplacements Totaux")
        self.stats_widget.add_card(create_stat_card("🗓️", "Mouvements Aujourd'hui", "0", "#ffc107"), "Mouvements Aujourd'hui")
        main_layout.addWidget(self.stats_widget)

        filter_card = ModernCard()
        filter_layout = QVBoxLayout(filter_card)
        filter_form_layout = QFormLayout()
        filter_form_layout.setSpacing(10)
        filter_form_layout.setContentsMargins(10, 10, 10, 10)

        input_style = """
            QComboBox, QDateEdit {
                border: 1px solid #CFD8DC;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #F5F5F5;
                color: #212121;
                min-height: 30px;
            }
            QComboBox:focus, QDateEdit:focus {
                border: 2px solid #00BCD4;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
                subcontrol-origin: padding;
                subcontrol-position: right center;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #424242;
            }
        """

        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(300)
        self.product_combo.setPlaceholderText("Sélectionnez un produit")
        self.product_combo.setStyleSheet(input_style)
        filter_form_layout.addRow("Produit :", self.product_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Tous", "Réception", "Expédition", "Déplacement"])
        self.type_combo.setStyleSheet(input_style)
        filter_form_layout.addRow("Type de mouvement :", self.type_combo)

        date_group_layout = QHBoxLayout()
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_from.setStyleSheet(input_style)

        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setStyleSheet(input_style)

        date_group_layout.addWidget(self.date_from)
        date_group_layout.addWidget(QLabel("au"))
        date_group_layout.addWidget(self.date_to)
        date_group_layout.addStretch()

        filter_form_layout.addRow("Période :", date_group_layout)
        filter_layout.addLayout(filter_form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(10, 0, 10, 10)

        self.btn = QPushButton("🚀 Afficher les mouvements")
        self.btn.clicked.connect(self.load_movements)
        self.btn.setStyleSheet(self._button_style("#3498db", "#2980b9"))
        btn_layout.addWidget(self.btn)

        self.export_btn = QPushButton("📄 Exporter CSV")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_to_csv)
        self.export_btn.setStyleSheet(self._button_style("#2ecc71", "#27ae60"))
        btn_layout.addWidget(self.export_btn)

        filter_layout.addLayout(btn_layout)
        main_layout.addWidget(filter_card)

        table_card = ModernCard()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(15, 15, 15, 15)

        table_title_label = QLabel("Historique des Mouvements")
        table_title_label.setFont(QFont("Arial", 16, QFont.Bold))
        table_title_label.setStyleSheet("color: #424242;")
        table_layout.addWidget(table_title_label)

        self.table = ModernTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Type", "Référence Bon", "Date", "Quantité", "Lot", "Cellule", "Description"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card)

        self.setLayout(main_layout)

    def apply_modern_theme(self):
        """Applique les styles CSS globaux."""
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                color: #212121;
                font-family: "Arial", sans-serif;
            }
            QLabel {
                color: #34495e;
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

    def _button_style(self, color, hover_color) -> str:
        return f"""
            QPushButton {{
                padding: 10px 20px;
                background-color: {color};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {color};
                border: 1px solid #CCCCCC;
            }}
            QPushButton:disabled {{
                background-color: #bdbdbd;
                color: #757575;
            }}
        """

    def load_products(self):
        try:
            logger.info("📦 Chargement des produits disponibles...")
            self.products = get_all_products(self.conn)
            self.product_combo.clear()

            if not self.products:
                logger.warning("🚫 Aucun produit trouvé.")
                QMessageBox.information(self, "Information", "Aucun produit disponible.")
                return

            self.product_combo.addItem("--- Sélectionnez un produit ---", None)
            for product in self.products:
                label = f"{product.get('reference', '')} - {product.get('nom', '')}"
                self.product_combo.addItem(label, product.get('idProduit'))

            logger.info(f"✅ {len(self.products)} produits chargés.")

        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des produits : {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", "Échec du chargement des produits.")

    def load_movements(self):
        try:
            index = self.product_combo.currentIndex()
            if index == 0 or self.product_combo.itemData(index) is None:
                QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un produit valide.")
                return

            product_id = self.product_combo.itemData(index)
            if not product_id:
                raise ValueError("ID produit invalide.")

            self.btn.setEnabled(False)
            self.btn.setText("Chargement...")

            mvt_type_displayed = self.type_combo.currentText()
            mvt_type = self.movement_type_mapping.get(mvt_type_displayed)

            date_from = self.date_from.date().toPyDate()
            date_to = self.date_to.date().toPyDate()

            # 1. Récupérer les mouvements détaillés (pour le tableau, avec filtres)
            mouvements = handle_mouvements_produit(
                self.conn, product_id, date_from, date_to, mvt_type
            )

            # --- MODIFICATION ICI : APPELER handle_get_product_movement_totals DU CONTRÔLEUR ---
            totals = handle_get_product_movement_totals(self.conn, product_id)

            # Passer les deux jeux de données à la méthode d'affichage
            self.display_results(mouvements, totals)

        except Exception as e:
            logger.error(f"❌ Erreur chargement mouvements : {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n{str(e)}")

        finally:
            self.btn.setEnabled(True)
            self.btn.setText("🚀 Afficher les mouvements")

    def display_results(self, mouvements, totals): # Ajout de l'argument 'totals'
        self.table.setRowCount(0)
        self.export_btn.setEnabled(False)

        # Mettre à jour les cartes de statistiques directement avec les totaux reçus
        # Assurez-vous que les clés correspondent exactement à celles retournées par votre requête SQL
        self.stats_widget.update_card_value("Réceptions Totales", totals.get("TotalReceptions", 0))
        self.stats_widget.update_card_value("Expéditions Totales", totals.get("TotalExpeditions", 0))
        self.stats_widget.update_card_value("Déplacements Totaux", totals.get("TotalDeplacements", 0))
        self.stats_widget.update_card_value("Mouvements Aujourd'hui", totals.get("TotalMouvementsAujourdHui", 0))


        if not mouvements:
            self.table.setRowCount(1)
            no_data_item = QTableWidgetItem("Aucun mouvement trouvé pour la sélection actuelle.")
            no_data_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, no_data_item)
            self.table.setSpan(0, 0, 1, self.table.columnCount())
            return

        self.table.setRowCount(len(mouvements))
        self.export_btn.setEnabled(True)

        color_map = {
            "Réception": "#e6ffe6",
            "Expédition": "#ffe6e6",
            "Déplacement": "#e6f2ff"
        }

        for row, mouvement in enumerate(mouvements):
            raw_date = mouvement.get("date", "")

            date_str = ""
            if isinstance(raw_date, datetime):
                date_str = raw_date.strftime("%d/%m/%Y %H:%M:%S")
            elif isinstance(raw_date, date):
                date_str = raw_date.strftime("%d/%m/%Y")
            else:
                date_str = str(raw_date)

            mvt_type = str(mouvement.get("type", ""))

            items = [
                QTableWidgetItem(mvt_type),
                QTableWidgetItem(str(mouvement.get("reference_bon", ""))),
                QTableWidgetItem(date_str),
                QTableWidgetItem(str(mouvement.get("quantite", ""))),
                QTableWidgetItem(str(mouvement.get("lot", ""))),
                QTableWidgetItem(str(mouvement.get("cellule", ""))),
                QTableWidgetItem(str(mouvement.get("description", "")))
            ]

            for col, item in enumerate(items):
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                bg_color = color_map.get(mvt_type, "#ffffff")
                item.setBackground(QColor(bg_color))
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def export_to_csv(self):
        try:
            if self.table.rowCount() == 0 or (self.table.rowCount() == 1 and self.table.item(0,0) and "Aucun mouvement" in self.table.item(0,0).text()):
                QMessageBox.information(self, "Export Impossible", "Aucune donnée à exporter.")
                return

            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter en CSV", f"mouvements_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "Fichiers CSV (*.csv)"
            )
            if not filename:
                return

            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')

                headers = [
                    self.table.horizontalHeaderItem(i).text()
                    for i in range(self.table.columnCount())
                ]
                writer.writerow(headers)

                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(self, "Export réussi", "Le fichier CSV a été enregistré avec succès.")
            logger.info(f"✅ Données exportées vers : {filename}")

        except Exception as e:
            logger.error(f"❌ Échec export CSV : {e}", exc_info=True)
            QMessageBox.critical(self, "Erreur", f"Échec de l'export :\n{str(e)}")