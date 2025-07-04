from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QSpinBox,
    QMessageBox, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from models.stock_model import (
    get_cellules_info, add_cellule, update_cellule,
    get_entrepot_capacite_restante
)


class CellulesModule(QWidget):
    def __init__(self, conn, user):
        super().__init__()
        self.conn = conn
        self.user = user
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Layout principal avec espacement et marges
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Style général de la fenêtre
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        # Titre avec icône et effet de gradient
        title = QLabel("📦 GESTION DES CELLULES D'ENTREPÔT")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #2c3e50);
                color: white;
                border-radius: 8px;
            }
        """)
        title.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title)

        # Frame pour le tableau avec ombre portée
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.StyledPanel)
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Tableau avec style professionnel
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "Entrepôt", "Capacité Max", "Qté Totale", 
            "Taux Occupation", "Volume Restant"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #e9ecef;
                font-size: 13px;
                border: none;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table.setSortingEnabled(True)
        
        table_layout.addWidget(self.table)
        main_layout.addWidget(table_frame)

        # Frame pour le formulaire
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
                padding: 15px;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(20)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Style commun pour les inputs
        input_style = """
            QLineEdit, QSpinBox, QComboBox {
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 13px;
                min-width: 180px;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #3498db;
                background-color: #f8fafc;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
            }
            QComboBox::drop-down {
                width: 25px;
                border-left: 1px solid #ced4da;
            }
        """

        # Création des champs avec placeholder et tooltips
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("ID existant pour modification")
        self.input_id.setToolTip("Entrez l'ID d'une cellule existante pour la modifier")
        self.input_id.setStyleSheet(input_style)

        self.input_reference = QLineEdit()
        self.input_reference.setPlaceholderText("Ex: CELL-001")
        self.input_reference.setToolTip("Référence unique de la cellule")
        self.input_reference.setStyleSheet(input_style)

        self.input_capacite = QSpinBox()
        self.input_capacite.setRange(1, 1_000_000)
        self.input_capacite.setPrefix("⏺ ")
        self.input_capacite.setStyleSheet(input_style)

        self.input_volume = QSpinBox()
        self.input_volume.setRange(1, 10_000_000)
        self.input_volume.setPrefix("⏺ ")
        self.input_volume.setStyleSheet(input_style)

        self.input_entrepot = QSpinBox()
        self.input_entrepot.setRange(1, 100)
        self.input_entrepot.setPrefix("🏭 ")
        self.input_entrepot.setStyleSheet(input_style)

        self.input_longueur = QSpinBox()
        self.input_longueur.setRange(1, 10000)
        self.input_longueur.setSuffix(" cm")
        self.input_longueur.setStyleSheet(input_style)

        self.input_largeur = QSpinBox()
        self.input_largeur.setRange(1, 10000)
        self.input_largeur.setSuffix(" cm")
        self.input_largeur.setStyleSheet(input_style)

        self.input_hauteur = QSpinBox()
        self.input_hauteur.setRange(1, 10000)
        self.input_hauteur.setSuffix(" cm")
        self.input_hauteur.setStyleSheet(input_style)

        self.input_masse_max = QSpinBox()
        self.input_masse_max.setRange(1, 100_000)
        self.input_masse_max.setSuffix(" kg")
        self.input_masse_max.setStyleSheet(input_style)

        self.input_statut = QComboBox()
        self.input_statut.addItems(["actif", "inactif"])
        self.input_statut.setStyleSheet(input_style)

        # Ajout des lignes au formulaire avec des labels stylés
        label_style = "font-weight: bold; color: #2c3e50; font-size: 13px;"
        
        form_layout.addRow(self.create_label("ID Cellule (modif):", label_style), self.input_id)
        form_layout.addRow(self.create_label("Référence:", label_style), self.input_reference)
        form_layout.addRow(self.create_label("Capacité Max:", label_style), self.input_capacite)
        form_layout.addRow(self.create_label("Volume Max:", label_style), self.input_volume)
        form_layout.addRow(self.create_label("ID Entrepôt:", label_style), self.input_entrepot)
        form_layout.addRow(self.create_label("Dimensions:", label_style), self.create_dimensions_layout())
        form_layout.addRow(self.create_label("Masse Max:", label_style), self.input_masse_max)
        form_layout.addRow(self.create_label("Statut:", label_style), self.input_statut)
        
        main_layout.addWidget(form_frame)

        # Boutons d'action avec icônes et effets hover
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(0, 10, 0, 0)

        self.btn_add = self.create_button("➕ Ajouter", "#27ae60", "#2ecc71", "#219653")
        self.btn_add.clicked.connect(self.ajouter_cellule)
        buttons_layout.addWidget(self.btn_add)

        self.btn_update = self.create_button("✏️ Modifier", "#2980b9", "#3498db", "#1f618d")
        self.btn_update.clicked.connect(self.modifier_cellule)
        buttons_layout.addWidget(self.btn_update)

        self.btn_clear = self.create_button("🗑️ Effacer", "#e74c3c", "#e67e22", "#c0392b")
        self.btn_clear.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.btn_clear)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def create_label(self, text, style):
        """Crée un QLabel stylisé"""
        label = QLabel(text)
        label.setStyleSheet(style)
        return label

    def create_button(self, text, normal_color, hover_color, pressed_color):
        """Crée un QPushButton stylisé"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {normal_color};
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
                font-size: 13px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
            }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def create_dimensions_layout(self):
        """Crée un layout horizontal pour les dimensions"""
        dim_layout = QHBoxLayout()
        dim_layout.setSpacing(10)
        
        self.input_longueur.setPrefix("L: ")
        self.input_largeur.setPrefix("l: ")
        self.input_hauteur.setPrefix("H: ")
        
        dim_layout.addWidget(self.input_longueur)
        dim_layout.addWidget(self.input_largeur)
        dim_layout.addWidget(self.input_hauteur)
        
        container = QWidget()
        container.setLayout(dim_layout)
        return container

    def load_data(self):
        try:
            self.table.clearContents() 
            cellules = get_cellules_info(self.conn)
            self.table.setRowCount(len(cellules))

            for row, c in enumerate(cellules):
                for col, val in enumerate([
                    c['idCellule'], c['reference'], c['nom_entrepot'],
                    c['capacite_max'], c['quantite_totale'],
                    f"{c['taux_occupation']}%", c['volume_restant']
                ]):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    
                    # Mise en forme conditionnelle
                    if c['quantite_totale'] > c['capacite_max']:
                        item.setBackground(QColor('#ffdddd'))
                        item.setForeground(QColor('#d63031'))
                    elif c['taux_occupation'] > 90:
                        item.setBackground(QColor('#fff3cd'))
                    item.setData(Qt.UserRole, c['idCellule'])  # Stocke l'ID pour référence
                    
                    self.table.setItem(row, col, item)

            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des cellules :\n{str(e)}")

    def ajouter_cellule(self):
        try:
            ref = self.input_reference.text().strip()
            cap = self.input_capacite.value()
            vol = self.input_volume.value()
            entrepot_id = self.input_entrepot.value()
            l = self.input_longueur.value()
            L = self.input_largeur.value()
            h = self.input_hauteur.value()
            masse = self.input_masse_max.value()
            position = f"Auto-{ref}"

            if not ref:
                QMessageBox.warning(self, "Champ requis", "La référence est obligatoire.")
                self.input_reference.setFocus()
                return

            restant = get_entrepot_capacite_restante(self.conn, entrepot_id)
            if restant is not None and cap > restant:
                QMessageBox.warning(
                    self, 
                    "Capacité dépassée",
                    f"L'entrepôt #{entrepot_id} ne dispose que de {restant} unités restantes.\n"
                    f"Vous essayez d'ajouter une cellule de capacité {cap}."
                )
                return

            add_cellule(self.conn, ref, l, L, h, masse, vol, cap, position, entrepot_id)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Succès")
            msg.setText(f"Cellule <b>{ref}</b> ajoutée avec succès.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            self.load_data()
            self.clear_form()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erreur", 
                f"Une erreur est survenue lors de l'ajout :\n{str(e)}"
            )

    def modifier_cellule(self):
        try:
            cell_id = int(self.input_id.text())
            l = self.input_longueur.value()
            L = self.input_largeur.value()
            h = self.input_hauteur.value()
            masse = self.input_masse_max.value()
            volume = self.input_volume.value()
            cap = self.input_capacite.value()
            statut = self.input_statut.currentText()

            update_cellule(self.conn, cell_id, l, L, h, masse, volume, cap, statut)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Mise à jour")
            msg.setText(f"Cellule <b>#{cell_id}</b> modifiée avec succès.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            self.load_data()
            self.clear_form()

        except ValueError:
            QMessageBox.warning(self, "ID invalide", "Veuillez entrer un ID valide pour modifier.")
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erreur", 
                f"Une erreur est survenue lors de la modification :\n{str(e)}"
            )

    def clear_form(self):
        """Réinitialise tous les champs du formulaire"""
        for widget in [
            self.input_id, self.input_reference
        ]:
            widget.clear()
            
        for spinbox in [
            self.input_capacite, self.input_volume, self.input_entrepot,
            self.input_longueur, self.input_largeur, self.input_hauteur,
            self.input_masse_max
        ]:
            spinbox.setValue(1)
            
        self.input_statut.setCurrentIndex(0)
        self.input_reference.setFocus()