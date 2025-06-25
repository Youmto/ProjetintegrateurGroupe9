from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QStatusBar
)
from views.deplacement import DeplacementModule
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
import inspect
from typing import Type, Dict, Tuple
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from models.user_model import get_user_roles
from views.reception import ReceptionModule
from views.expedition import ExpeditionModule
from views.inventaire import InventaireModule
from views.rapports import RapportsModule
from views.supervision import SupervisionModule
from views.admin import AdminModule
from views.mouvements import MouvementsModule
from views.produits import ProduitsModule

# ➤ Suppression de: from views.alertes import AlertesModule

class MainWindow(QMainWindow):
    MODULE_ARG_MAP: Dict[Type[QWidget], Tuple[str, ...]] = {
        MouvementsModule: ('conn','user'),
        SupervisionModule: ('conn', 'user'),
        ReceptionModule: ('conn', 'user'),
        ExpeditionModule: ('conn', 'user'),
        InventaireModule: ('conn', 'user'),
        RapportsModule: ('conn', 'user'),
        AdminModule: ('conn', 'user'),
        DeplacementModule: ('conn', 'user'),
        ProduitsModule: ('conn','user')

        
    }

    def __init__(self, parent=None, db_conn=None, user=None):
        super().__init__(parent)
        self.db_conn = db_conn
        self.user = user

        if not db_conn:
            logger.error("La connexion à la base de données est manquante")
            raise ValueError("db_conn est requis")
        if not user or 'idIndividu' not in user:
            logger.error("L'utilisateur ou son ID est manquant")
            raise ValueError("user avec idIndividu est requis")

        self._init_ui_components()
        self._setup_timer()
        logger.info(f"Fenêtre principale initialisée pour l'utilisateur {user.get('nom', 'inconnu')}")

    def _init_ui_components(self):
        self.setWindowTitle(f"SGE - {self.user.get('nom', 'Utilisateur')}")
        self.setMinimumSize(1024, 768)
        self._setup_status_bar()
        self._setup_main_layout()
        self._load_modules()

    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_status_bar)
        self.timer.start(1000)
        logger.debug("Timer de la barre de statut initialisé")

    def _setup_status_bar(self):
        self.statusBar().showMessage(self._status_message)
        logger.debug("Barre de statut configurée")

    @property
    def _status_message(self) -> str:
        return f"Connecté : {self.user.get('nom', 'Utilisateur')} | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    def _update_status_bar(self):
        self.statusBar().showMessage(self._status_message)

    def _setup_main_layout(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabPosition(QTabWidget.North)
        layout.addWidget(self.tab_widget)
        logger.debug("Layout principal configuré")

    def _load_modules(self):
        try:
            logger.debug("Début du chargement des modules")

            raw_roles = get_user_roles(self.db_conn, self.user['idIndividu'])
            logger.debug(f"Rôles bruts récupérés: {raw_roles}")

            if not raw_roles:
                logger.warning("Aucun rôle trouvé pour cet utilisateur")

            roles = [r[0].lower().strip() if isinstance(r, tuple) else str(r).lower().strip() for r in raw_roles]
            logger.info(f"Rôles normalisés: {roles}")

            # Modules toujours disponibles
            self._add_module("Inventaire", InventaireModule)
            

            # Modules conditionnels
            if any('magasinier' in r for r in roles):
                logger.info("Chargement des modules magasinier")
                self._add_module("Réception", ReceptionModule)
                self._add_module("Expédition", ExpeditionModule)
                self._add_module("Déplacement", DeplacementModule)
                self._add_module("Produits", ProduitsModule)
                self._add_module("Mouvements", MouvementsModule)
            if any('responsable' in r for r in roles):
                logger.info("Chargement des modules responsable")
                self._add_module("Rapports", RapportsModule)
                self._add_module("Supervision", SupervisionModule)
                self._add_module("Administration", AdminModule)
                self._add_module("Déplacements", DeplacementModule)
                
            logger.info(f"Nombre d'onglets chargés: {self.tab_widget.count()}")

        except Exception as e:
            logger.error(f"Erreur lors du chargement des modules: {str(e)}", exc_info=True)
            raise

    def _add_module(self, name: str, module_class: Type[QWidget]):
        try:
            logger.debug(f"Tentative de chargement du module: {name}")
            args = self._resolve_module_args(module_class)
            logger.debug(f"Arguments résolus pour {name}: {args}")
            instance = module_class(*args)
            self.tab_widget.addTab(instance, name)
            logger.info(f"Module {name} chargé avec succès")
        except Exception as e:
            logger.error(f"Échec du chargement du module {name}: {str(e)}", exc_info=True)

    def _resolve_module_args(self, module_class: Type[QWidget]) -> list:
        try:
            if module_class in self.MODULE_ARG_MAP:
                arg_names = self.MODULE_ARG_MAP[module_class]
            else:
                sig = inspect.signature(module_class.__init__)
                arg_names = list(sig.parameters.keys())[1:]  # Exclure 'self'

            args = []
            for arg in arg_names:
                if arg == 'conn':
                    args.append(self.db_conn)
                elif arg == 'user':
                    args.append(self.user)

            return args

        except Exception as e:
            logger.error(f"Erreur de résolution des arguments: {str(e)}", exc_info=True)
            raise
