from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QListWidget, QListWidgetItem, QStackedWidget,
    QLabel, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont
from datetime import datetime
import inspect
from typing import Type, Dict, Tuple
import logging

# ➤ Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ➤ Imports modèles et vues
# Assurez-vous que ces chemins sont corrects par rapport à l'emplacement de main_window.py
from models.user_model import get_user_roles
from views.reception import ReceptionModule
from views.expedition import ExpeditionModule
from views.inventaire import InventaireModule
from views.rapports import RapportsModule
from views.supervision import SupervisionModule
from views.admin import AdminModule
from views.mouvements import MouvementsModule
from views.produits import ProduitsModule
from views.cellules import CellulesModule
from views.deplacement import DeplacementModule
from views.livreur_confirmation import LivreurConfirmationWindow
from views.lot_detail import LotDetailWindow
from views.approvisionnement import ApprovisionnementWindow
from views.dashboard import DashboardModule


class MainWindow(QMainWindow):
    # Ce mappage est utile pour spécifier explicitement quels arguments
    # chaque module attend. 'conn' et 'user' sont gérés.
    MODULE_ARG_MAP: Dict[Type[QWidget], Tuple[str, ...]] = {
        MouvementsModule: ('conn','user'),
        SupervisionModule: ('conn', 'user'),
        ReceptionModule: ('conn', 'user'),
        ExpeditionModule: ('conn', 'user'),
        InventaireModule: ('conn', 'user'),
        RapportsModule: ('conn', 'user'),
        AdminModule: ('conn', 'user'),
        DeplacementModule: ('conn', 'user'),
        ProduitsModule: ('conn','user'),
        CellulesModule:('conn','user'),
        LivreurConfirmationWindow: ('conn', 'user'),
        LotDetailWindow: ('conn', 'user'),
        ApprovisionnementWindow: ('conn', 'user'),
        DashboardModule: ('conn', 'user'),
    }

    # ➤ Mappage des modules aux catégories et icônes
    # Ceci définit la structure de votre menu latéral et quels modules appartiennent à quelle catégorie.
    MODULE_CATEGORIES = {
        "Général": {
            "Dashboard": DashboardModule,
            "Inventaire": InventaireModule,
        },
        "Gestion du Stock": {
            "Réception": ReceptionModule,
            "Expédition": ExpeditionModule,
            "Mouvements": MouvementsModule,
            "Déplacement": DeplacementModule,
            "Produits": ProduitsModule,
            "Cellules": CellulesModule,
            "Approvisionnement": ApprovisionnementWindow,
            "Lot Détail": LotDetailWindow,
        },
        "Opérations Spéciales": {
            "Livreur": LivreurConfirmationWindow,
        },
        "Reporting & Admin": {
            "Rapports": RapportsModule,
            "Supervision": SupervisionModule,
            "Administration": AdminModule,
        },
    }

    # ➤ Définir les icônes pour chaque module et catégorie
    # J'utilise des emojis pour la simplicité, mais pour un rendu professionnel,
    # remplacez-les par des chemins vers des fichiers .png ou .svg (ex: "icons/dashboard.png").
    ICONS = {
        "Dashboard": "🏠",
        "Inventaire": "📦",
        "Réception": "📥",
        "Expédition": "📤",
        "Mouvements": "🔄",
        "Déplacement": "🚚",
        "Produits": "🏷️",
        "Cellules": "📍",
        "Approvisionnement": "➕",
        "Lot Détail": "🔎",
        "Livreur": "🧑‍🚚",
        "Rapports": "📈",
        "Supervision": "👀",
        "Administration": "⚙️",
        # Icônes pour les catégories (ces icônes peuvent être affichées à côté du titre de la catégorie)
        "Général": "🌐",
        "Gestion du Stock": "📦",
        "Opérations Spéciales": "✨",
        "Reporting & Admin": "📊",
    }


    def __init__(self, parent=None, db_conn=None, user=None):
        super().__init__(parent)
        self.db_conn = db_conn
        self.user = user
        # Dictionnaire pour stocker les instances uniques des modules chargés
        # Clé: Classe du module (hashable), Valeur: Instance du QWidget
        self.modules_instances: Dict[Type[QWidget], QWidget] = {}

        if not self.db_conn:
            logger.error("❌ Connexion DB manquante.")
            raise ValueError("Connexion à la base de données requise.")
        if not self.user or 'idIndividu' not in self.user:
            logger.error("❌ Utilisateur invalide ou ID manquant.")
            raise ValueError("Utilisateur avec ID requis.")

        logger.info(f"🧑‍💼 Connexion en cours pour {self.user.get('nom', 'Inconnu')}")
        self._init_ui()
        self._init_timer()
        logger.info("✅ Interface principale initialisée")

    def _init_ui(self):
        self.setWindowTitle(f"📦 SGE - {self.user.get('nom', 'Utilisateur')}")
        self.setMinimumSize(1024, 768)
        self._init_status_bar()
        self._init_layout()
        self._setup_sidebar_styles() # Application des styles CSS
        self._load_modules()

    def _init_status_bar(self):
        self.statusBar().showMessage(self._status_message)
        logger.debug("📡 Barre de statut prête")

    def _init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_status_bar)
        self.timer.start(1000)
        logger.debug("⏱️ Timer de mise à jour de la barre de statut activé")

    @property
    def _status_message(self) -> str:
        return f"🔐 Connecté : {self.user.get('nom', 'Utilisateur')} | 🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    def _update_status_bar(self):
        self.statusBar().showMessage(self._status_message)

    def _init_layout(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) # Pas de marges pour un look plein écran

        # --- Partie Gauche : Menu latéral (Sidebar) ---
        self.sidebar_widget = QWidget(self)
        self.sidebar_widget.setFixedWidth(250) # Largeur fixe pour la barre latérale
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(5) # Espacement entre les éléments

        # Titre du menu / Logo
        logo_label = QLabel("SGE - Système de Gestion d'Entrepôt")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Arial", 12, QFont.Bold))
        logo_label.setStyleSheet("color: white; padding-bottom: 15px;")
        sidebar_layout.addWidget(logo_label)

        # Liste des modules
        self.module_list_widget = QListWidget(self)
        self.module_list_widget.setFocusPolicy(Qt.NoFocus) # Empêche la sélection au clavier pour un clic uniquement
        self.module_list_widget.setAlternatingRowColors(False)
        self.module_list_widget.setIconSize(QSize(24, 24)) # Taille des icônes
        self.module_list_widget.itemClicked.connect(self._sidebar_item_clicked) # Connecte le clic

        sidebar_layout.addWidget(self.module_list_widget)

        # Espace flexible en bas de la sidebar
        sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        main_layout.addWidget(self.sidebar_widget)

        # --- Partie Droite : Contenu principal (Stacked Widget) ---
        self.stacked_widget = QStackedWidget(self)
        main_layout.addWidget(self.stacked_widget)

        logger.debug("📐 Layout principal avec sidebar et stacked widget configuré")

    def _setup_sidebar_styles(self):
        """
        Applique des styles CSS à la barre latérale et à ses éléments pour un look pro.
        """
        self.sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: #2c3e50; /* Bleu foncé pour la sidebar */
                color: #ecf0f1; /* Texte clair */
                border-right: 1px solid #34495e; /* Bordure discrète */
            }
            QListWidget {
                background-color: #2c3e50;
                border: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px 5px;
                margin-bottom: 3px;
                border-radius: 5px;
                color: #ecf0f1; /* Couleur par défaut des éléments */
            }
            QListWidget::item:selected {
                background-color: #3498db; /* Bleu vif à la sélection */
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #34495e; /* Gris foncé au survol */
            }
            /* Style pour les en-têtes de catégorie (non-cliquables) */
            QListWidget::item[data-role="category"] { /* Utilise le data-role pour cibler */
                font-weight: bold;
                color: #bdc3c7; /* Couleur légèrement plus claire pour les catégories */
                background-color: transparent;
                padding: 15px 5px 5px 5px; /* Plus d'espace au-dessus */
                border-bottom: 1px solid #34495e; /* Séparateur */
                margin-top: 10px;
            }
            QListWidget::item[data-role="category"]:selected,
            QListWidget::item[data-role="category"]:hover {
                background-color: transparent; /* Empêche la sélection/survol de changer l'apparence */
                color: #bdc3c7;
            }
        """)

    def _load_modules(self):
        """
        Charge les modules dynamiquement en fonction des rôles de l'utilisateur
        et les ajoute à la barre latérale et au stacked widget.
        """
        try:
            logger.info("🚀 Chargement des modules pour la sidebar...")

            raw_roles = get_user_roles(self.db_conn, self.user['idIndividu'])
            logger.debug(f"🔍 Rôles récupérés : {raw_roles}")

            roles = [
                r[0].strip().lower() if isinstance(r, tuple) else str(r).strip().lower()
                for r in raw_roles
            ]
            logger.info(f"🔑 Rôles normalisés : {roles}")

            # Nettoyer les widgets existants avant de recharger (utile si la fonction est appelée plusieurs fois)
            self.module_list_widget.clear()
            # Supprimer les widgets du QStackedWidget pour éviter les fuites mémoire
            for i in reversed(range(self.stacked_widget.count())):
                widget = self.stacked_widget.widget(i)
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater() # Supprime l'instance du widget de la mémoire
            self.modules_instances.clear() # Réinitialise le cache des instances de modules


            # Parcourir les catégories définies pour construire le menu
            for category_name, modules_in_category in self.MODULE_CATEGORIES.items():
                # Ajouter l'en-tête de catégorie à la QListWidget
                category_item = QListWidgetItem(f"{self.ICONS.get(category_name, '')} {category_name.upper()}")
                # Rendre l'élément de catégorie non sélectionnable
                category_item.setFlags(category_item.flags() & ~Qt.ItemIsSelectable)
                category_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                # Utiliser setData avec un rôle de données pour le ciblage CSS et l'identification
                category_item.setData(Qt.UserRole, "category")
                category_item.setData(Qt.AccessibleDescriptionRole, "category") # Pour le CSS [data-role="category"]
                self.module_list_widget.addItem(category_item)

                for module_name, module_class in modules_in_category.items():
                    # Vérifier les permissions basées sur les rôles de l'utilisateur
                    should_add = False
                    # Modules communs à tous les utilisateurs (ex: Dashboard, Inventaire)
                    if module_name in ["Dashboard", "Inventaire"]:
                        should_add = True
                    # Modules spécifiques aux magasiniers
                    elif any("magasinier" in r for r in roles) and module_class in [
                        ReceptionModule, ExpeditionModule, DeplacementModule,
                        ProduitsModule, MouvementsModule, CellulesModule,
                        LotDetailWindow, ApprovisionnementWindow
                    ]:
                        should_add = True
                    # Modules spécifiques aux livreurs
                    elif any("livreur" in r for r in roles) and module_class == LivreurConfirmationWindow:
                        should_add = True
                    # Modules spécifiques aux responsables
                    elif any("responsable" in r for r in roles) and module_class in [
                        RapportsModule, SupervisionModule, AdminModule, DeplacementModule
                    ]:
                        should_add = True

                    if should_add:
                        # Si l'utilisateur a la permission, ajouter le module au menu
                        self._add_module_to_sidebar(module_name, module_class)

            # Sélectionner le premier module cliquable par défaut après le chargement
            if self.module_list_widget.count() > 0:
                first_selectable_item = None
                for i in range(self.module_list_widget.count()):
                    item = self.module_list_widget.item(i)
                    if item.flags() & Qt.ItemIsSelectable: # Vérifie si l'élément est sélectionnable
                        first_selectable_item = item
                        break
                if first_selectable_item:
                    self.module_list_widget.setCurrentItem(first_selectable_item)
                    self._sidebar_item_clicked(first_selectable_item) # Déclenche l'affichage du premier module

            logger.info(f"✅ {self.stacked_widget.count()} modules chargés dans le stacked widget.")

        except Exception as e:
            logger.error(f"💥 Erreur lors du chargement des modules : {e}", exc_info=True)
            raise

    def _add_module_to_sidebar(self, name: str, module_class: Type[QWidget]):
        """
        Ajoute un module à la barre latérale (QListWidget) et gère son instance
        dans le QStackedWidget.
        """
        try:
            logger.debug(f"🧩 Tentative de chargement du module : {name}")

            # Créer l'instance du module si elle n'existe pas déjà
            if module_class not in self.modules_instances:
                args = self._resolve_args(module_class)
                instance = module_class(*args)
                self.modules_instances[module_class] = instance # Stocke l'instance avec la classe comme clé
                self.stacked_widget.addWidget(instance) # Ajoute l'instance au QStackedWidget
                logger.info(f"✅ Instance du module '{name}' créée et ajoutée au stacked widget.")
            else:
                instance = self.modules_instances[module_class]
                logger.info(f"🔄 Module '{name}' déjà instancié, réutilisation.")

            # Ajouter l'élément au QListWidget de la sidebar
            # Utilisez la méthode appropriée pour charger une icône réelle si nécessaire
            icon_text = self.ICONS.get(name, "")
            list_item = QListWidgetItem(f"{icon_text} {name}")

            # Stocke la classe du module (qui est hashable) dans le UserRole de l'item QListWidgetItem.
            # C'est la clé de la solution pour l'erreur 'unhashable type'.
            list_item.setData(Qt.UserRole, module_class)
            self.module_list_widget.addItem(list_item)

            logger.info(f"✅ Élément '{name}' ajouté à la barre latérale avec sa classe.")
        except Exception as e:
            logger.error(f"❌ Impossible de charger '{name}' : {e}", exc_info=True)

    def _resolve_args(self, module_class: Type[QWidget]) -> list:
        """
        Résout les arguments nécessaires pour l'initialisation d'un module
        en se basant sur self.MODULE_ARG_MAP ou en inspectant le constructeur.
        """
        try:
            arg_names = self.MODULE_ARG_MAP.get(module_class)

            if not arg_names:
                # Si non spécifié dans MODULE_ARG_MAP, inspecter le constructeur __init__
                # Cela permet une grande flexibilité si MODULE_ARG_MAP n'est pas exhaustif.
                sig = inspect.signature(module_class.__init__)
                # Filtrer 'self' et les arguments avec des valeurs par défaut si vous ne voulez pas les fournir
                arg_names = [p.name for p in sig.parameters.values() if p.name != 'self']
                logger.debug(f"ℹ️ Arguments du constructeur pour {module_class.__name__} (auto-détectés): {arg_names}")

            resolved = []
            for arg in arg_names:
                if arg == 'conn':
                    resolved.append(self.db_conn)
                elif arg == 'user':
                    resolved.append(self.user)
                else:
                    # Si un module a des arguments supplémentaires, il faudrait les gérer ici
                    # ou les spécifier dans MODULE_ARG_MAP.
                    logger.warning(f"❓ Argument inconnu '{arg}' pour le module {module_class.__name__}. Non fourni.")
                    # Vous pourriez vouloir lever une erreur ici ou fournir None/une valeur par défaut
                    # en fonction de la nécessité de l'argument.
                    resolved.append(None) # Ou gérer une valeur par défaut/erreur

            return resolved

        except Exception as e:
            logger.error(f"⚠️ Erreur de résolution des arguments pour {module_class.__name__}: {e}", exc_info=True)
            raise

    def _sidebar_item_clicked(self, item: QListWidgetItem):
        """
        Gère le clic sur un élément de la barre latérale.
        Change le widget affiché dans le QStackedWidget.
        """
        # Récupérer les données stockées dans l'item via UserRole
        item_data = item.data(Qt.UserRole)

        # Vérifier si c'est un élément de catégorie (que nous avons rendu non sélectionnable mais qui pourrait être cliqué)
        if item_data == "category":
            logger.debug(f"Catégorie cliquée : '{item.text()}', ignoré la sélection de module.")
            # Vous pouvez désélectionner l'élément pour éviter qu'il ne reste "activé" visuellement.
            self.module_list_widget.setCurrentItem(None) # Désélectionne l'élément
            return

        # Si ce n'est pas une catégorie, item_data doit être la classe du module
        if isinstance(item_data, type) and issubclass(item_data, QWidget):
            module_class = item_data
            module_widget = self.modules_instances.get(module_class) # Récupère l'instance du module

            if module_widget:
                self.stacked_widget.setCurrentWidget(module_widget) # Affiche le module
                # Met à jour le titre de la fenêtre avec le nom du module actuel
                clean_module_name = item.text().strip()
                # Enlève l'emoji du nom si présent pour le titre
                if len(clean_module_name) > 0 and clean_module_name[0] in self.ICONS.values():
                    clean_module_name = clean_module_name[1:].strip()
                self.setWindowTitle(f"📦 SGE - {clean_module_name} - {self.user.get('nom', 'Utilisateur')}")
                logger.info(f"➡️ Affichage du module : '{clean_module_name}'")
            else:
                logger.warning(f"⚠️ Aucun widget instancié trouvé pour la classe de module : {module_class.__name__}. Clic ignoré.")
        else:
            logger.warning(f"⚠️ Donnée UserRole invalide ou non-classe de module pour l'élément '{item.text()}'. Clic ignoré.")