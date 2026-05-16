from app.config import DATABASE_CONNECTION_STRING
from app.db.sales_models import Base
from shared.db.runtime import DatabaseRuntime


db_runtime = DatabaseRuntime(
    database_url=DATABASE_CONNECTION_STRING,
    metadata=Base.metadata,
    logger_name=__name__,
)


def get_database_connection_string() -> str:
    return DATABASE_CONNECTION_STRING


def init_db_pool():
    return db_runtime.init()


def get_db_session():
    return db_runtime.session_scope()
