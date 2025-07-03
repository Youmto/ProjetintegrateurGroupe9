from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
import inspect
from typing import Type, Dict, Tuple
import logging

# ➤ Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ➤ Imports modèles et vues
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

    def __init__(self, parent=None, db_conn=None, user=None):
        super().__init__(parent)
        self.db_conn = db_conn
        self.user = user

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
        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabPosition(QTabWidget.North)

        layout.addWidget(self.tab_widget)
        logger.debug("📐 Layout principal configuré")

    def _load_modules(self):
        try:
            logger.info("🚀 Chargement des modules...")

            raw_roles = get_user_roles(self.db_conn, self.user['idIndividu'])
            logger.debug(f"🔍 Rôles récupérés : {raw_roles}")

            roles = [
                r[0].strip().lower() if isinstance(r, tuple) else str(r).strip().lower()
                for r in raw_roles
            ]
            logger.info(f"🔑 Rôles normalisés : {roles}")

            # ➤ Modules communs
            self._add_module("📦 Inventaire", InventaireModule)

            # ➤ Modules par rôle
            if any("magasinier" in r for r in roles):
                logger.info("📦 Accès Magasinier")
                self._add_module("📥 Réception", ReceptionModule)
                self._add_module("📤 Expédition", ExpeditionModule)
                self._add_module("🔁 Déplacement", DeplacementModule)
                self._add_module("📦 Produits", ProduitsModule)
                self._add_module("📦 Mouvements", MouvementsModule)
                self._add_module("📦 Cellules", CellulesModule)
                self._add_module("🔍 Lot Detail", LotDetailWindow)
                self._add_module("🚚 Approvisionnement", ApprovisionnementWindow)
                self._add_module("📊 Dashboard", DashboardModule)

            if any("livreur" in r for r in roles):
                logger.info("🚚 Accès Livreur")
                self._add_module("📬 Livreur", LivreurConfirmationWindow)

            if any("responsable" in r for r in roles):
                logger.info("🛠️ Accès Responsable")
                self._add_module("📈 Rapports", RapportsModule)
                self._add_module("👀 Supervision", SupervisionModule)
                self._add_module("⚙️ Administration", AdminModule)
                self._add_module("🔁 Déplacements", DeplacementModule)

            logger.info(f"✅ {self.tab_widget.count()} modules chargés")

        except Exception as e:
            logger.error(f"💥 Erreur lors du chargement des modules : {e}", exc_info=True)
            raise

    def _add_module(self, name: str, module_class: Type[QWidget]):
        try:
            logger.debug(f"🧩 Chargement du module : {name}")
            args = self._resolve_args(module_class)
            instance = module_class(*args)
            self.tab_widget.addTab(instance, name)
            logger.info(f"✅ Module {name} ajouté")
        except Exception as e:
            logger.error(f"❌ Impossible de charger {name} : {e}", exc_info=True)

    def _resolve_args(self, module_class: Type[QWidget]) -> list:
        try:
            arg_names = self.MODULE_ARG_MAP.get(module_class)

            if not arg_names:
                sig = inspect.signature(module_class.__init__)
                arg_names = list(sig.parameters.keys())[1:]  # ignorer self

            resolved = []
            for arg in arg_names:
                if arg == 'conn':
                    resolved.append(self.db_conn)
                elif arg == 'user':
                    resolved.append(self.user)
                else:
                    raise ValueError(f"❓ Argument inconnu : {arg}")

            return resolved

        except Exception as e:
            logger.error(f"⚠️ Erreur de résolution des arguments : {e}", exc_info=True)
            raise
