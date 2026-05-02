import os

from shared.db.runtime import resolve_database_connection_string
from shared.env import load_agent_env


load_agent_env(__file__)

SAP_BASE_URL = os.getenv("SAP_BASE_URL", "https://localhost:50000/b1s/v2")
SAP_USERNAME = os.getenv("SAP_USERNAME", "manager")
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "password")
SAP_COMPANYDB = os.getenv("SAP_COMPANYDB", "SBODEMO")
DATABASE_CONNECTION_STRING = resolve_database_connection_string()
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "120"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
SQL_QUERY_TIMEOUT = int(os.getenv("SQL_QUERY_TIMEOUT", "10"))
