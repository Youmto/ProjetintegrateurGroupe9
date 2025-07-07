from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QMessageBox, QFrame, QGraphicsDropShadowEffect,
    QFormLayout, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QPixmap 

# Assurez-vous que ces modules (controllers.deplacement_controller, models.stock_model)
# existent et contiennent les fonctions mentionnées dans votre projet.
from controllers.deplacement_controller import handle_deplacement
from models.stock_model import get_cellule_details, get_product_details, get_lot_info

import traceback # Pour un meilleur débogage des erreurs en production

# --- Classes de conception d'interface utilisateur réutilisables ---

class ModernCard(QFrame):
    """
    Un widget QFrame personnalisé qui simule une carte moderne avec des ombres portées
    et des effets de survol pour une meilleure interactivité visuelle.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(15, 15, 15, 15)
        self.setMinimumHeight(120)
        self.setMaximumWidth(500) # Limiter la largeur des cartes pour une meilleure esthétique
        self.setSizePolicy(
            QSizePolicy.Expanding, # Garde l'élasticité en largeur
            QSizePolicy.Fixed      # Fixe la hauteur
        )

        # QGraphicsDropShadowEffect est la méthode correcte pour les ombres dans PyQt
        self.initial_shadow = QGraphicsDropShadowEffect(self)
        self.initial_shadow.setBlurRadius(20)
        self.initial_shadow.setXOffset(0)
        self.initial_shadow.setYOffset(5)
        self.initial_shadow.setColor(QColor(0, 0, 0, 30)) # Ombre légère
        self.setGraphicsEffect(self.initial_shadow)

        # Paramètres d'ombre au survol
        self.hover_blur_radius = 35
        self.hover_y_offset = 10
        self.hover_shadow_color = QColor(0, 0, 0, 60) # Ombre plus prononcée

        # Animations pour l'effet de survol
        self.blur_animation = QPropertyAnimation(self.initial_shadow, b"blurRadius")
        self.blur_animation.setDuration(200)
        self.blur_animation.setEasingCurve(QEasingCurve.OutQuad)

        self.offset_animation = QPropertyAnimation(self.initial_shadow, b"yOffset")
        self.offset_animation.setDuration(200)
        self.offset_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Style CSS par défaut pour la carte
        # Note: Pas de 'box-shadow' ici, car QGraphicsDropShadowEffect le gère
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)

    def enterEvent(self, event):
        """Gère l'événement d'entrée de la souris (survol)."""
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #B0D8FF; /* Bordure bleue au survol */
            }
        """)
        # Démarrer les animations de l'ombre au survol
        self.blur_animation.setStartValue(self.initial_shadow.blurRadius())
        self.blur_animation.setEndValue(self.hover_blur_radius)
        self.blur_animation.start()

        self.offset_animation.setStartValue(self.initial_shadow.yOffset())
        self.offset_animation.setEndValue(self.hover_y_offset)
        self.offset_animation.start()

        self.initial_shadow.setColor(self.hover_shadow_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Gère l'événement de sortie de la souris."""
        self.setStyleSheet("""
            ModernCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0; /* Revenir à la bordure par défaut */
            }
        """)
        # Revenir aux animations d'ombre initiales
        self.blur_animation.setStartValue(self.initial_shadow.blurRadius())
        self.blur_animation.setEndValue(20)
        self.blur_animation.start()

        self.offset_animation.setStartValue(self.initial_shadow.yOffset())
        self.offset_animation.setEndValue(5)
        self.offset_animation.start()

        self.initial_shadow.setColor(QColor(0, 0, 0, 30))
        super().leaveEvent(event)

# StatsWidget et create_stat_card ne sont pas utilisés dans ce module spécifique,
# mais sont conservés pour la cohérence si ce fichier est une partie d'une plus grande suite d'UI.
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
    """
    Un widget QTableWidget stylisé avec un look moderne.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True) # Couleurs alternées pour les lignes
        self.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                selection-background-color: #E3F2FD; /* Bleu clair pour la sélection */
                selection-color: #212121;
                gridline-color: #F0F0F0; /* Lignes de grille plus claires */
            }
            QTableWidget::item {
                padding: 8px; /* Plus d'espace autour du texte des cellules */
                border-bottom: 1px solid #F0F0F0; /* Lignes de séparation des cellules */
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #212121;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                color: #424242;
                padding: 10px; /* Plus de padding pour les en-têtes */
                border-bottom: 2px solid #BBDEFB; /* Bordure plus épaisse et colorée en bas de l'en-tête */
                font-weight: bold;
                text-align: left; /* Alignement du texte des en-têtes */
            }
            QHeaderView::section:hover {
                background-color: #E0E0E0; /* Changement de couleur au survol de l'en-tête */
            }
            QHeaderView::section::first {
                border-top-left-radius: 8px; /* Coins arrondis pour le premier en-tête */
            }
            QHeaderView::section::last {
                border-top-right-radius: 8px; /* Coins arrondis pour le dernier en-tête */
            }
        """)
        self.horizontalHeader().setStretchLastSection(True) # Étirer la dernière colonne
        self.verticalHeader().setVisible(False) # Masquer l'en-tête vertical
        self.setSelectionBehavior(QTableWidget.SelectRows) # Sélectionner des lignes entières
        self.setSelectionMode(QTableWidget.SingleSelection) # Une seule sélection à la fois

# --- Fin des classes de conception d'interface utilisateur ---


class DeplacementModule(QWidget):
    """
    Module PyQt5 pour gérer le déplacement des lots de produits entre cellules de stockage,
    avec une interface utilisateur au style moderne et sans dépendance d'image externe.
    """
    def __init__(self, conn, user):
        """
        Constructeur du module de déplacement.

        Args:
            conn: L'objet de connexion à la base de données.
            user: Un dictionnaire contenant les informations de l'utilisateur connecté, 
                  incluant au moins 'idIndividu'.
        """
        super().__init__()
        self.conn = conn  # Connexion à la base de données
        self.user = user  # Informations de l'utilisateur (e.g., {'idIndividu': 1, 'nom': 'Dupont'})
        self.setup_ui()   # Initialisation de l'interface utilisateur
        self.apply_modern_theme() # Applique le thème moderne

    def setup_ui(self):
        """
        Configure l'interface utilisateur du module de déplacement avec le style moderne.
        """
        self.setWindowTitle("Gestion des Déplacements de Lots")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Section En-tête (Titre principal + Icône/Emoji) ---
        header_layout = QVBoxLayout()
        
        # Titre principal
        title_label = QLabel("📦 Gestion des Déplacements de Lots")
        title_label.setFont(QFont("Arial", 28, QFont.Bold)) # Taille de police augmentée
        title_label.setStyleSheet("color: #263238; margin-bottom: 10px;") # Marge basse
        header_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Icône/Emoji pour un look professionnel sans image externe
        self.icon_label = QLabel("🚚") # Un emoji de camion ou de boîte
        self.icon_label.setFont(QFont("Segoe UI Emoji", 60)) # Grande taille pour l'emoji
        self.icon_label.setStyleSheet("color: #4CAF50;") # Couleur vive pour l'icône
        self.icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.icon_label)

        main_layout.addLayout(header_layout)

        # --- Section Formulaire de Déplacement (dans une ModernCard) ---
        deplacement_card = ModernCard()
        deplacement_card_layout = QFormLayout(deplacement_card)
        deplacement_card_layout.setSpacing(12) # Espacement amélioré entre les lignes du formulaire
        deplacement_card_layout.setContentsMargins(20, 20, 20, 20) # Marges intérieures pour le formulaire

        # Styles pour les champs de saisie
        # Suppression de 'box-shadow' car il n'est pas directement supporté pour QLineEdit/QSpinBox
        # dans le moteur CSS de PyQt. La bordure de focus fournit un retour visuel suffisant.
        input_style = """
            QLineEdit, QSpinBox {
                border: 1px solid #CFD8DC;
                border-radius: 8px;
                padding: 10px 15px; /* Plus de padding pour une meilleure ergonomie */
                font-size: 15px; /* Taille de police légèrement augmentée */
                background-color: #FDFDFD; /* Fond légèrement plus clair */
                color: #333333;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #00BCD4; /* Couleur de focus plus distinctive */
                background-color: #FFFFFF;
            }
        """
        
        label_style = "font-weight: bold; color: #546E7A;" # Style pour les labels du formulaire

        # Champs de saisie
        self.lot_input = QLineEdit()
        self.lot_input.setPlaceholderText("Entrez l'ID du lot (ex: 123)")
        self.lot_input.setStyleSheet(input_style)
        deplacement_card_layout.addRow(QLabel("ID du Lot :", styleSheet=label_style), self.lot_input)
        
        self.src_cellule_input = QLineEdit()
        self.src_cellule_input.setPlaceholderText("Entrez l'ID de la cellule source")
        self.src_cellule_input.setStyleSheet(input_style)
        deplacement_card_layout.addRow(QLabel("Cellule Source :", styleSheet=label_style), self.src_cellule_input)
        
        self.dest_cellule_input = QLineEdit()
        self.dest_cellule_input.setPlaceholderText("Entrez l'ID de la cellule destination")
        self.dest_cellule_input.setStyleSheet(input_style)
        deplacement_card_layout.addRow(QLabel("Cellule Destination :", styleSheet=label_style), self.dest_cellule_input)
        
        self.quantite_input = QSpinBox()
        self.quantite_input.setRange(1, 999999) # Plage plus réaliste pour une quantité
        self.quantite_input.setSingleStep(1)
        self.quantite_input.setStyleSheet(input_style)
        deplacement_card_layout.addRow(QLabel("Quantité :", styleSheet=label_style), self.quantite_input)

        # Bouton pour exécuter le déplacement (style moderne)
        # Suppression de 'box-shadow' car il n'est pas directement supporté pour QPushButton
        # dans le moteur CSS de PyQt.
        self.btn_deplacer = QPushButton("🚀 Exécuter le Déplacement")
        self.btn_deplacer.setFont(QFont("Arial", 16, QFont.Bold)) # Police plus grande pour le bouton principal
        self.btn_deplacer.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; /* Vert pour l'action principale */
                color: white;
                font-weight: bold;
                border-radius: 10px; /* Rayon de bordure plus grand */
                padding: 12px 20px; /* Plus de padding */
                border: none;
                margin-top: 20px; /* Plus d'espace au-dessus du bouton */
            }
            QPushButton:hover {
                background-color: #66BB6A; /* Vert plus clair au survol */
            }
            QPushButton:pressed {
                background-color: #388E3C; /* Vert plus foncé au clic */
            }
        """)
        self.btn_deplacer.clicked.connect(self.effectuer_deplacement)
        deplacement_card_layout.addRow(self.btn_deplacer)

        main_layout.addWidget(deplacement_card, alignment=Qt.AlignCenter) # Centrer la carte

        main_layout.addStretch() # Pousser le contenu vers le haut

    def apply_modern_theme(self):
        """Applique les styles CSS modernes à l'ensemble du widget du module."""
        # Pas de 'box-shadow' dans la feuille de style globale non plus
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA; /* Arrière-plan global doux */
                color: #212121; /* Couleur de texte par défaut */
                font-family: "Arial", sans-serif;
            }
            QLabel {
                color: #424242; /* Couleur générale des labels */
            }
            QMessageBox {
                background-color: #FFFFFF;
                color: #212121;
                font-family: "Arial", sans-serif;
                border-radius: 8px;
            }
            QMessageBox QPushButton {
                background-color: #42A5F5; /* Bleu pour les boutons de message */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 80px; /* Largeur minimale pour les boutons */
            }
            QMessageBox QPushButton:hover {
                background-color: #2196F3;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1976D2;
            }
        """)

    def effectuer_deplacement(self):
        """
        Gère la logique de validation et l'exécution du déplacement du lot.
        Cette méthode est appelée lorsque le bouton "Exécuter le déplacement" est cliqué.
        Toute la logique de validation et les appels aux contrôleurs sont consolidés ici.
        """
        try:
            # 1. Validation de base des entrées numériques
            # Utilisation de strip() pour nettoyer les espaces
            lot_text = self.lot_input.text().strip()
            src_cell_text = self.src_cellule_input.text().strip()
            dest_cell_text = self.dest_cellule_input.text().strip()

            if not lot_text or not lot_text.isdigit():
                QMessageBox.warning(self, "Entrée Invalide", "L'ID du lot doit être un nombre entier valide.")
                return
            if not src_cell_text or not src_cell_text.isdigit():
                QMessageBox.warning(self, "Entrée Invalide", "L'ID de la cellule source doit être un nombre entier valide.")
                return
            if not dest_cell_text or not dest_cell_text.isdigit():
                QMessageBox.warning(self, "Entrée Invalide", "L'ID de la cellule destination doit être un nombre entier valide.")
                return

            # Conversion des entrées en entiers
            id_lot = int(lot_text)
            cellule_src = int(src_cell_text)
            cellule_dest = int(dest_cell_text)
            quantite = self.quantite_input.value()
            
            # Récupération de l'ID du responsable de l'opération
            # Assurez-vous que self.user est bien défini et contient 'idIndividu'
            responsable_id = self.user.get('idIndividu')
            if not responsable_id:
                QMessageBox.critical(self, "Erreur d'Utilisateur", "Impossible de déterminer l'ID du responsable. Veuillez vous reconnecter.")
                return

            # Vérification que les cellules source et destination sont différentes
            if cellule_src == cellule_dest:
                QMessageBox.warning(self, "Déplacement Impossible", "La cellule source et la cellule de destination doivent être différentes.")
                return
            
            # La spinbox gère normalement quantite > 0, mais une double-vérification ne nuit pas
            if quantite <= 0:
                QMessageBox.warning(self, "Quantité Invalide", "La quantité à déplacer doit être supérieure à zéro.")
                return

            # 2. Récupération des informations du lot
            # Utilisez la connexion réelle à la base de données
            lot_info = get_lot_info(self.conn, id_lot)
            if not lot_info:
                QMessageBox.warning(self, "Lot Introuvable", f"Aucun lot trouvé avec l'ID : {id_lot}. Veuillez vérifier l'ID.")
                return

            # 3. Validation de la cellule source du lot
            # Vérifie si le lot se trouve réellement dans la cellule source déclarée
            # IMPORTANT : get_lot_info (telle que modifiée) retourne idCellule et quantite_actuelle_en_cellule
            # du premier emplacement trouvé pour ce lot. Si le lot est réparti sur plusieurs cellules,
            # et que la cellule_src n'est pas la première retournée, cette validation échouera.
            # Ce comportement est une limitation due à la signature de get_lot_info et la contrainte de ne pas ajouter de fonctions.
            if lot_info.get('idCellule') != cellule_src:
                QMessageBox.warning(self, "Erreur de Cellule Source",
                                    f"Le lot {id_lot} n'est pas situé dans la cellule source {cellule_src} "
                                    f"ou sa localisation principale est la cellule {lot_info.get('idCellule')}.")
                return

            # 4. Validation de la quantité à déplacer par rapport à la quantité disponible dans le lot *dans la cellule source*
            # Correction : Utiliser 'quantite_actuelle_en_cellule' qui vient de get_lot_info
            quantite_actuelle_lot_in_source = lot_info.get('quantite_actuelle_en_cellule', 0)
            if quantite > quantite_actuelle_lot_in_source:
                QMessageBox.warning(self, "Quantité Insuffisante",
                                    f"La quantité à déplacer ({quantite}) est supérieure à la quantité actuelle disponible du lot {id_lot} dans la cellule source ({quantite_actuelle_lot_in_source}).")
                return


            # 5. Récupération des informations de la cellule de destination
            cellule_info_dest = get_cellule_details(self.conn, cellule_dest)
            # get_cellule_details lève déjà une ValueError si la cellule est introuvable,
            # donc ce 'if not' est redondant mais inoffensif ici.
            # Cependant, si vous préférez que get_cellule_details retourne None plutôt que lever, ajustez là-bas.
            if not cellule_info_dest: 
                QMessageBox.warning(self, "Cellule Destination Introuvable", f"Aucune cellule destination trouvée avec l'ID : {cellule_dest}.")
                return
            
            # Vérification du statut de la cellule de destination
            if cellule_info_dest.get('statut') != 'actif':
                QMessageBox.warning(self, "Cellule Destination Inactive", f"La cellule de destination {cellule_dest} est inactive et ne peut pas recevoir de lots.")
                return

            # 6. Récupération des informations du produit associé au lot
            # get_product_details DOIT exister dans models.stock_model et retourner un dict avec 'type' et 'volume'.
            id_produit = lot_info.get('idProduit') 
            if not id_produit:
                QMessageBox.warning(self, "Produit Inconnu", f"L'ID du produit associé au lot {id_lot} est introuvable. Impossible de valider le type ou le volume.")
                return

            produit = get_product_details(self.conn, id_produit)
            if not produit:
                QMessageBox.warning(self, "Produit Introuvable", f"Les détails du produit (ID: {id_produit}) associé au lot {id_lot} sont introuvables.")
                return

            # 7. Validation de la capacité en quantité de la cellule de destination
            capacite_max_dest = cellule_info_dest.get("capacite_max", 0)
            # Correction : Utiliser 'quantite_totale' de get_cellule_details
            quantite_occupee_dest = cellule_info_dest.get("quantite_totale", 0) 
            
            if capacite_max_dest is None or capacite_max_dest < 0:
                QMessageBox.warning(self, "Configuration Cellule Invalide", f"La capacité maximale de la cellule de destination (ID: {cellule_dest}) est invalide.")
                return

            reste_capacite_quantite = capacite_max_dest - quantite_occupee_dest

            if quantite > reste_capacite_quantite:
                QMessageBox.warning(self, "Capacité en Quantité Insuffisante",
                                    f"La cellule de destination (ID: {cellule_dest}) ne peut accueillir que {reste_capacite_quantite} unité(s) supplémentaire(s).")
                return

            # 8. Validation de la capacité en volume si le produit est de type 'materiel'
            if produit.get("type") == "materiel":
                volume_unit = produit.get("volume", 0.0) # Utilisez 0.0 pour les calculs flottants
                if volume_unit <= 0:
                    QMessageBox.warning(self, "Volume Produit Invalide", f"Le produit (ID: {id_produit}) est de type 'materiel' mais son volume est nul ou non défini. Le déplacement est impossible.")
                    return

                volume_total_deplacement = volume_unit * quantite
                
                # Assurez-vous que votre fonction get_cellule_details retourne 'volume_restant'
                volume_restant_dest = cellule_info_dest.get("volume_restant", 0.0) 
                
                if volume_restant_dest is None or volume_restant_dest < 0:
                    QMessageBox.warning(self, "Configuration Cellule Invalide", f"Le volume restant de la cellule de destination (ID: {cellule_dest}) est invalide.")
                    return

                if volume_total_deplacement > volume_restant_dest:
                    QMessageBox.warning(self, "Volume Insuffisant",
                                        f"La cellule de destination (ID: {cellule_dest}) ne peut contenir que {volume_restant_dest:.2f} cm³ restants (besoin de {volume_total_deplacement:.2f} cm³).")
                    return

            # 9. Si toutes les validations passent, appel de la fonction de déplacement dans le contrôleur
            success = handle_deplacement(self.conn, id_lot, cellule_src, cellule_dest, quantite, responsable_id)
            
            if success:
                QMessageBox.information(self, "Déplacement Réussi", f"Le lot {id_lot} a été déplacé avec succès de la cellule {cellule_src} à la cellule {cellule_dest}.")
                self.clear_fields() # Nettoie les champs après un succès
            else:
                QMessageBox.warning(self, "Échec du Déplacement", "Le déplacement n'a pas pu être effectué. Une erreur est survenue lors de l'opération en base de données. Vérifiez les journaux pour plus de détails.")

        except ValueError as ve:
            # Erreur spécifique si la conversion en int échoue ou pour d'autres erreurs de valeur
            QMessageBox.warning(self, "Erreur de Saisie", f"Veuillez entrer des valeurs numériques valides. Détails: {ve}")
        except Exception as e:
            # Gestion générique des erreurs inattendues
            QMessageBox.critical(self, "Erreur Critique Inattendue", f"Une erreur inattendue est survenue lors du déplacement :\n{str(e)}")
            # En production, il est crucial de logguer cette erreur plus en détail
            traceback.print_exc()

    def clear_fields(self):
        """
        Réinitialise tous les champs de saisie de l'interface à leurs valeurs par défaut.
        """
        self.lot_input.clear()
        self.src_cellule_input.clear()
        self.dest_cellule_input.clear()
        self.quantite_input.setValue(1) # Réinitialise la spinbox à sa valeur minimale (1)