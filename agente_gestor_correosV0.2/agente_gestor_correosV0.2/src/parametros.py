from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if load_dotenv and ENV_PATH.exists():
    load_dotenv(ENV_PATH)

AGENTE_VERSION = "0.1.4-mitumi-hilos-markread-fallback"

def _bool(nombre: str, default: bool = False) -> bool:
    valor = os.getenv(nombre)
    if valor is None:
        return default
    return str(valor).strip().lower() in {"1", "true", "yes", "si", "sí", "on"}

def _int(nombre: str, default: int) -> int:
    try:
        return int(os.getenv(nombre, str(default)))
    except Exception:
        return default

def _float(nombre: str, default: float) -> float:
    try:
        return float(os.getenv(nombre, str(default)))
    except Exception:
        return default

MODO_DEMO = _bool("MODO_DEMO", False)
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

LLM_ENABLED = _bool("LLM_ENABLED", True)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai_compatible")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = _float("LLM_TEMPERATURE", 0.2)
LLM_MAX_TOKENS = min(_int("LLM_MAX_TOKENS", 300), 350)
LLM_CALL_DELAY_SECONDS = _float("LLM_CALL_DELAY_SECONDS", 3.0)
LLM_RETRY_MAX_ATTEMPTS = _int("LLM_RETRY_MAX_ATTEMPTS", 2)
LLM_RETRY_BASE_SECONDS = _float("LLM_RETRY_BASE_SECONDS", 4.0)
LLM_JSON_MODE = _bool("LLM_JSON_MODE", False)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")

COMPOSIO_ENABLED = _bool("COMPOSIO_ENABLED", True)
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY", "")
GMAIL_ENABLED = _bool("GMAIL_ENABLED", True)
GMAIL_ACCOUNT_LABEL = os.getenv("GMAIL_ACCOUNT_LABEL", "secretario_ampa_pruebas")
GMAIL_QUERY = os.getenv("GMAIL_QUERY", "in:inbox is:unread newer_than:7d")
GMAIL_MAX_RESULTS = _int("GMAIL_MAX_RESULTS", _int("MAX_EMAILS_PER_RUN", 5))

ALLOW_CREATE_DRAFTS = _bool("ALLOW_CREATE_DRAFTS", True)
ALLOW_MARK_AS_READ = _bool("ALLOW_MARK_AS_READ", False)
ALLOW_EMAIL_SEND = _bool("ALLOW_EMAIL_SEND", False)
ALLOW_DELETE_EMAIL = _bool("ALLOW_DELETE_EMAIL", False)
ALLOW_FORWARD_EMAIL = _bool("ALLOW_FORWARD_EMAIL", False)
ALLOW_ARCHIVE_EMAIL = _bool("ALLOW_ARCHIVE_EMAIL", False)

EMAIL_FACTURACION_DESTINO = os.getenv("EMAIL_FACTURACION_DESTINO", "")
OUTPUTS_DIR = BASE_DIR / os.getenv("OUTPUTS_DIR", "outputs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

SHOW_STEPS = _bool("SHOW_STEPS", True)
MARK_READ_AFTER_DRAFT = _bool("MARK_READ_AFTER_DRAFT", True)
