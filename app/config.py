import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.db.runtime import resolve_database_connection_string
from shared.env import load_agent_env


load_agent_env(__file__)

APP_NAME = "SAP B1 ERP Big Supervisor Agent"
API_PREFIX = ""

SAP_BASE_URL = os.getenv("SAP_BASE_URL", "http://localhost:50000/b1s/v1")
SAP_USERNAME = os.getenv("SAP_USERNAME", "manager")
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "password")
SAP_COMPANYDB = os.getenv("SAP_COMPANYDB", "SBODEMOUS")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "120"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
BIG_SUPERVISOR_GROQ_API_KEY = os.getenv("BIG_SUPERVISOR_GROQ_API_KEY", GROQ_API_KEY)
BIG_SUPERVISOR_GROQ_MODEL = os.getenv("BIG_SUPERVISOR_GROQ_MODEL", GROQ_MODEL)
PURCHASE_TEAM_GROQ_API_KEY = os.getenv("PURCHASE_TEAM_GROQ_API_KEY", GROQ_API_KEY)
PURCHASE_TEAM_GROQ_MODEL = os.getenv("PURCHASE_TEAM_GROQ_MODEL", GROQ_MODEL)
SALES_TEAM_GROQ_API_KEY = os.getenv("SALES_TEAM_GROQ_API_KEY", GROQ_API_KEY)
SALES_TEAM_GROQ_MODEL = os.getenv("SALES_TEAM_GROQ_MODEL", GROQ_MODEL)
SALES_SQL_GROQ_API_KEY = os.getenv("SALES_SQL_GROQ_API_KEY", SALES_TEAM_GROQ_API_KEY)
SALES_SQL_GROQ_MODEL = os.getenv("SALES_SQL_GROQ_MODEL", SALES_TEAM_GROQ_MODEL)

SQL_QUERY_TIMEOUT = int(os.getenv("SQL_QUERY_TIMEOUT", "30"))
HANA_SQL_API_URL = os.getenv(
    "HANA_SQL_API_URL",
    "http://vzone.in:1662/api/GetMethod/GetData",
)
DATABASE_CONNECTION_STRING = resolve_database_connection_string()

PURCHASE_RAG_EMBEDDING_MODEL = os.getenv("PURCHASE_RAG_EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
_purchase_rag_persist_dir = Path(os.getenv("PURCHASE_RAG_PERSIST_DIR", ".rag_chroma/purchase"))
PURCHASE_RAG_PERSIST_DIR = (
    _purchase_rag_persist_dir
    if _purchase_rag_persist_dir.is_absolute()
    else REPO_ROOT / _purchase_rag_persist_dir
)
SALES_RAG_EMBEDDING_MODEL = os.getenv("SALES_RAG_EMBEDDING_MODEL", PURCHASE_RAG_EMBEDDING_MODEL)
_sales_rag_persist_dir = Path(os.getenv("SALES_RAG_PERSIST_DIR", ".rag_chroma/sales"))
SALES_RAG_PERSIST_DIR = (
    _sales_rag_persist_dir
    if _sales_rag_persist_dir.is_absolute()
    else REPO_ROOT / _sales_rag_persist_dir
)
SALES_RAG_USE_VECTOR = os.getenv("SALES_RAG_USE_VECTOR", "false").strip().lower() in {"1", "true", "yes", "on"}

PURCHASE_ORDER_API_URL = os.getenv(
    "PURCHASE_ORDER_API_URL",
    "http://127.0.0.1:8000/purchase-orders/parse-and-execute",
)
AP_INVOICE_API_URL = os.getenv(
    "AP_INVOICE_API_URL",
    "http://127.0.0.1:8000/ap-invoices/parse-and-execute",
)
PURCHASE_RETURN_API_URL = os.getenv(
    "PURCHASE_RETURN_API_URL",
    "http://127.0.0.1:8000/purchase-returns/parse-and-execute",
)
