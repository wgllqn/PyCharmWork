"""
数据库连接管理工具
支持 MySQL, PostgreSQL, SQL Server, SQLite
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from typing import Dict, List, Any, Optional
import logging
from app.config import get_database_url, settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器，支持多种数据库类型"""

    def __init__(self, db_url: Optional[str] = None):
        """
        初始化数据库管理器

        Args:
            db_url: 数据库连接URL，如果不提供则使用配置中的URL
        """
        self.db_url = db_url or get_database_url()
        self.engine: Optional[Engine] = None
        self.db_type = self._detect_db_type()
        logger.info(f"Initializing database manager with type: {self.db_type}")

    def _detect_db_type(self) -> str:
        """检测数据库类型"""
        if self.db_url.startswith("mysql"):
            return "mysql"
        elif self.db_url.startswith("postgresql"):
            return "postgresql"
        elif self.db_url.startswith("mssql"):
            return "mssql"
        elif self.db_url.startswith("sqlite"):
            return "sqlite"
        else:
            return "unknown"

    def connect(self) -> bool:
        """
        连接到数据库

        Returns:
            是否连接成功
        """
        try:
            logger.info(f"Connecting to database: {self._mask_password(self.db_url)}")

            # 根据数据库类型设置连接参数
            connect_args = {}
            if self.db_type == "sqlite":
                connect_args = {"check_same_thread": False}

            self.engine = create_engine(
                self.db_url,
                connect_args=connect_args,
                pool_pre_ping=True,  # 自动检查连接是否有效
                echo=settings.debug  # debug模式下显示SQL语句
            )

            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("✅ Database connected successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {str(e)}")
            self.engine = None
            return False

    def _mask_password(self, url: str) -> str:
        """隐藏URL中的密码"""
        if "://" in url and "@" in url:
            parts = url.split("://")
            if len(parts) == 2:
                protocol = parts[0]
                rest = parts[1]
                if "@" in rest:
                    credentials, host = rest.split("@", 1)
                    if ":" in credentials:
                        user, _ = credentials.split(":", 1)
                        return f"{protocol}://{user}:****@{host}"
        return url

    def get_tables(self) -> List[str]:
        """
        获取数据库中的所有表名

        Returns:
            表名列表
        """
        if not self.engine:
            logger.error("Database not connected")
            return []

        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"Found {len(tables)} tables: {tables}")
            return tables
        except Exception as e:
            logger.error(f"Error getting tables: {str(e)}")
            return []

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表的详细信息

        Args:
            table_name: 表名

        Returns:
            表信息字典
        """
        if not self.engine:
            logger.error("Database not connected")
            return {}

        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)

            # 获取行数
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()

            return {
                "name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True),
                        "default": col.get("default"),
                    }
                    for col in columns
                ],
                "row_count": row_count,
                "column_count": len(columns),
            }
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {str(e)}")
            return {}

    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        执行SQL查询

        Args:
            query: SQL查询语句

        Returns:
            查询结果
        """
        if not self.engine:
            return {"success": False, "error": "Database not connected"}

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))

                # 检查是否是查询语句
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = list(result.keys())
                    data = [dict(zip(columns, row)) for row in rows]

                    return {
                        "success": True,
                        "data": data,
                        "columns": columns,
                        "row_count": len(data),
                    }
                else:
                    # 非查询语句（INSERT, UPDATE, DELETE等）
                    conn.commit()
                    return {
                        "success": True,
                        "message": "Query executed successfully",
                        "rows_affected": result.rowcount,
                    }

        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {"success": False, "error": str(e)}

    def test_connection(self) -> Dict[str, Any]:
        """
        测试数据库连接并返回基本信息

        Returns:
            连接测试结果
        """
        if not self.connect():
            return {
                "success": False,
                "error": "Failed to connect to database"
            }

        tables = self.get_tables()

        return {
            "success": True,
            "db_type": self.db_type,
            "db_url": self._mask_password(self.db_url),
            "tables": tables,
            "table_count": len(tables),
        }

    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# 创建全局数据库管理器实例
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    return db_manager


# 测试函数
def test_database_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("测试数据库连接")
    print("=" * 50)

    manager = DatabaseManager()
    result = manager.test_connection()

    if result["success"]:
        print(f"✅ 连接成功!")
        print(f"   数据库类型: {result['db_type']}")
        print(f"   连接URL: {result['db_url']}")
        print(f"   表数量: {result['table_count']}")
        print(f"   表列表: {result['tables']}")

        # 获取每个表的详细信息
        for table in result['tables'][:3]:  # 只显示前3个表
            info = manager.get_table_info(table)
            print(f"\n表: {table}")
            print(f"  行数: {info.get('row_count', 0)}")
            print(f"  列数: {info.get('column_count', 0)}")
            if info.get('columns'):
                print(f"  列: {[col['name'] for col in info['columns'][:5]]}")
    else:
        print(f"❌ 连接失败: {result.get('error')}")

    manager.close()


if __name__ == "__main__":
    test_database_connection()