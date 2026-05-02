import os

from shared.db.runtime import resolve_database_connection_string


SAP_BASE_URL = os.getenv("SAP_BASE_URL", "https://localhost:50000/b1s/v2")
SAP_USERNAME = os.getenv("SAP_USERNAME", "manager")
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "password")
SAP_COMPANYDB = os.getenv("SAP_COMPANYDB", "SBODEMOUS")

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 30))

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
SQL_QUERY_TIMEOUT = int(os.getenv("SQL_QUERY_TIMEOUT", 30))

DATABASE_CONNECTION_STRING = resolve_database_connection_string()
