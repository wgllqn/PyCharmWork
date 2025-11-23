from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # LangSmith Configuration
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "sql-agent-project"

    # Database Configuration
    database_url: str = "sqlite:///./data/sql_agent.db"

    # External Database Configuration (Optional)
    external_db_type: Optional[str] = None  # mysql, postgresql, mssql
    external_db_host: Optional[str] = None
    external_db_port: Optional[int] = None
    external_db_user: Optional[str] = None
    external_db_password: Optional[str] = None
    external_db_name: Optional[str] = None

    # FastAPI Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # File Upload Configuration
    max_file_size: str = "100MB"
    upload_dir: str = "./data/uploads"

    # Visualization Configuration
    vis_output_dir: str = "./data/visualizations"

    # Model Configuration
    default_model: str = "qwen-plus"
    temperature: float = 0.0

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Initialize settings
settings = Settings()

# Configure LangSmith if enabled
if settings.langchain_tracing_v2 and settings.langchain_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project


def get_database_url() -> str:
    """
    获取数据库连接URL
    优先使用外部数据库配置，否则使用默认的 DATABASE_URL
    """
    if settings.external_db_type and settings.external_db_host:
        # 构建外部数据库连接字符串
        from urllib.parse import quote_plus

        db_type = settings.external_db_type.lower()
        user = settings.external_db_user or ""
        password = settings.external_db_password or ""
        host = settings.external_db_host
        port = settings.external_db_port
        db_name = settings.external_db_name or ""

        # URL编码用户名和密码，避免特殊字符问题
        user_encoded = quote_plus(user) if user else ""
        password_encoded = quote_plus(password) if password else ""

        if db_type == "mysql":
            # MySQL: mysql+pymysql://user:password@host:port/database
            port = port or 3306
            return f"mysql+pymysql://{user_encoded}:{password_encoded}@{host}:{port}/{db_name}"

        elif db_type == "postgresql":
            # PostgreSQL: postgresql://user:password@host:port/database
            port = port or 5432
            return f"postgresql://{user_encoded}:{password_encoded}@{host}:{port}/{db_name}"

        elif db_type == "mssql":
            # SQL Server: mssql+pyodbc://user:password@host:port/database?driver=...
            port = port or 1433
            return f"mssql+pyodbc://{user_encoded}:{password_encoded}@{host}:{port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"

        elif db_type == "sqlite":
            # SQLite: sqlite:///path/to/database.db
            return f"sqlite:///{db_name}"

    # 使用默认配置
    return settings.database_url