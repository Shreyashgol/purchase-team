import os

from shared.db.runtime import resolve_database_connection_string


# SAP Service Layer configuration
SAP_BASE_URL = os.getenv("SAP_BASE_URL", "http://localhost:50000/b1s/v1")
SAP_USERNAME = os.getenv("SAP_USERNAME", "************")
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "************")
SAP_COMPANYDB = os.getenv("SAP_COMPANYDB", "************")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 30))

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# SQL Query configuration
SQL_QUERY_TIMEOUT = int(os.getenv("SQL_QUERY_TIMEOUT", 30))

# Shared PostgreSQL configuration for all SAP agents
DATABASE_CONNECTION_STRING = resolve_database_connection_string()
