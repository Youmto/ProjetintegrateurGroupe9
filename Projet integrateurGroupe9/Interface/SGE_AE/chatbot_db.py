from pathlib import Path

# Chemin relatif recommandé (le dossier sera créé automatiquement)
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "dataChat" / "chatbot.db"

def get_chatbot_db_uri():
    """Retourne l'URI SQLite formatée correctement"""
    return f"sqlite:///{DB_PATH}"