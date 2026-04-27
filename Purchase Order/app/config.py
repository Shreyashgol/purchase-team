import os


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url

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

# Database configuration (Neon/PostgreSQL)
DATABASE_CONNECTION_STRING = _normalize_database_url(
    os.getenv(
        "DATABASE_CONNECTION_STRING",
        os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:password@localhost:5432/purchase_orders_db",
        ),
    )
)
