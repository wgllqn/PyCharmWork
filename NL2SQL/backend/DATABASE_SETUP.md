# 外部数据库配置指南

本文档将指导您如何将 SQL Agent 系统配置为使用外部数据库（MySQL、PostgreSQL、SQL Server）而不是默认的 SQLite 模拟数据。

## 目录

1. [支持的数据库](#支持的数据库)
2. [MySQL 配置](#mysql-配置)
3. [PostgreSQL 配置](#postgresql-配置)
4. [SQL Server 配置](#sql-server-配置)
5. [测试连接](#测试连接)
6. [常见问题](#常见问题)

---

## 支持的数据库

- ✅ MySQL 5.7+ / MariaDB 10.2+
- ✅ PostgreSQL 10+
- ✅ Microsoft SQL Server 2017+
- ✅ SQLite 3 (默认)

---

## MySQL 配置

### 1. 安装 MySQL 驱动

```bash
pip install pymysql
```

### 2. 配置 .env 文件

编辑 `backend/.env` 文件，取消注释并填写以下配置：

```env
# 外部数据库配置
EXTERNAL_DB_TYPE=mysql
EXTERNAL_DB_HOST=localhost
EXTERNAL_DB_PORT=3306
EXTERNAL_DB_USER=your_username
EXTERNAL_DB_PASSWORD=your_password
EXTERNAL_DB_NAME=your_database_name
```

### 3. 示例配置

```env
EXTERNAL_DB_TYPE=mysql
EXTERNAL_DB_HOST=192.168.1.100
EXTERNAL_DB_PORT=3306
EXTERNAL_DB_USER=root
EXTERNAL_DB_PASSWORD=mypassword123
EXTERNAL_DB_NAME=sales_db
```

### 4. 连接字符串格式

系统会自动生成：
```
mysql+pymysql://root:mypassword123@192.168.1.100:3306/sales_db
```

---

## PostgreSQL 配置

### 1. 安装 PostgreSQL 驱动

```bash
pip install psycopg2-binary
```

### 2. 配置 .env 文件

```env
EXTERNAL_DB_TYPE=postgresql
EXTERNAL_DB_HOST=localhost
EXTERNAL_DB_PORT=5432
EXTERNAL_DB_USER=postgres
EXTERNAL_DB_PASSWORD=your_password
EXTERNAL_DB_NAME=your_database_name
```

### 3. 示例配置

```env
EXTERNAL_DB_TYPE=postgresql
EXTERNAL_DB_HOST=db.example.com
EXTERNAL_DB_PORT=5432
EXTERNAL_DB_USER=admin
EXTERNAL_DB_PASSWORD=securepass456
EXTERNAL_DB_NAME=analytics_db
```

### 4. 连接字符串格式

系统会自动生成：
```
postgresql://admin:securepass456@db.example.com:5432/analytics_db
```

---

## SQL Server 配置

### 1. 安装 SQL Server 驱动

```bash
pip install pyodbc
```

并确保已安装 ODBC Driver 17 for SQL Server：
- Windows: [下载地址](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Linux: `sudo apt-get install msodbcsql17`

### 2. 配置 .env 文件

```env
EXTERNAL_DB_TYPE=mssql
EXTERNAL_DB_HOST=localhost
EXTERNAL_DB_PORT=1433
EXTERNAL_DB_USER=sa
EXTERNAL_DB_PASSWORD=your_password
EXTERNAL_DB_NAME=your_database_name
```

### 3. 示例配置

```env
EXTERNAL_DB_TYPE=mssql
EXTERNAL_DB_HOST=sqlserver.company.com
EXTERNAL_DB_PORT=1433
EXTERNAL_DB_USER=dbadmin
EXTERNAL_DB_PASSWORD=ComplexPass789!
EXTERNAL_DB_NAME=erp_system
```

### 4. 连接字符串格式

系统会自动生成：
```
mssql+pyodbc://dbadmin:ComplexPass789!@sqlserver.company.com:1433/erp_system?driver=ODBC+Driver+17+for+SQL+Server
```

---

## 测试连接

### 方法 1: 使用 Python 脚本测试

```bash
cd backend
python -c "from app.database import test_database_connection; test_database_connection()"
```

输出示例：
```
==================================================
测试数据库连接
==================================================
✅ 连接成功!
   数据库类型: mysql
   连接URL: mysql+pymysql://root:****@localhost:3306/sales_db
   表数量: 5
   表列表: ['products', 'orders', 'customers', 'sales', 'inventory']

表: products
  行数: 1250
  列数: 8
  列: ['id', 'name', 'category', 'price', 'stock']
```

### 方法 2: 使用 API 测试

启动服务器：
```bash
cd backend
python app/main.py
```

访问测试端点：
```bash
curl -X POST http://localhost:8000/database/test
```

或在浏览器中访问：
```
http://localhost:8000/docs
```
然后使用 `/database/test` 端点。

### 方法 3: 查看数据库信息

```bash
curl http://localhost:8000/database/info
```

返回示例：
```json
{
  "success": true,
  "db_type": "mysql",
  "db_url": "mysql+pymysql://root:****@localhost:3306/sales_db",
  "tables": [
    {
      "name": "products",
      "rows": 1250,
      "columns": ["id", "name", "category", "price", "stock"],
      "column_count": 5
    },
    {
      "name": "orders",
      "rows": 5430,
      "columns": ["order_id", "customer_id", "total", "order_date"],
      "column_count": 4
    }
  ],
  "table_count": 2
}
```

---

## 使用外部数据库查询

配置好外部数据库后，您可以直接使用自然语言查询：

### API 调用示例

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "显示销售额最高的前10个产品",
    "table_name": "products"
  }'
```

### Python 代码示例

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "统计每个类别的产品数量",
        "table_name": "products"
    }
)

result = response.json()
print(result["answer"])
print(result["data"])
```

---

## 常见问题

### Q1: 连接失败怎么办？

**检查清单：**
1. 确认数据库服务正在运行
2. 验证主机地址、端口、用户名、密码是否正确
3. 确认数据库存在且有访问权限
4. 检查防火墙设置
5. 测试网络连接：`ping 数据库主机`

**MySQL 特定问题：**
```bash
# 检查 MySQL 是否允许远程连接
mysql -u root -p
mysql> SELECT host, user FROM mysql.user;
# 如果看不到 '%' 或特定 IP，需要授权：
mysql> GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'password';
mysql> FLUSH PRIVILEGES;
```

### Q2: 驱动安装失败怎么办？

**MySQL (pymysql):**
```bash
pip install --upgrade pymysql
```

**PostgreSQL (psycopg2):**
```bash
# 方法 1: 使用二进制版本
pip install psycopg2-binary

# 方法 2: 从源码编译（需要 PostgreSQL 开发包）
# Ubuntu/Debian:
sudo apt-get install libpq-dev python3-dev
pip install psycopg2
```

**SQL Server (pyodbc):**
```bash
# Windows
pip install pyodbc

# Linux (Ubuntu/Debian)
sudo apt-get install unixodbc unixodbc-dev
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
# 安装 ODBC Driver 17
pip install pyodbc
```

### Q3: 如何切换回 SQLite？

在 `.env` 文件中注释掉外部数据库配置：

```env
# EXTERNAL_DB_TYPE=mysql
# EXTERNAL_DB_HOST=localhost
# EXTERNAL_DB_PORT=3306
# EXTERNAL_DB_USER=root
# EXTERNAL_DB_PASSWORD=password
# EXTERNAL_DB_NAME=database
```

系统会自动使用默认的 SQLite 配置。

### Q4: 支持多个数据库同时使用吗？

目前一次只能配置一个主数据库。但您可以：
1. 上传 CSV/Excel 文件（临时 SQLite）
2. 同时查询配置的外部数据库

### Q5: 数据库密码包含特殊字符怎么办？

如果密码包含特殊字符（如 `@`, `#`, `:` 等），需要进行 URL 编码：

```python
from urllib.parse import quote_plus

password = "p@ssw0rd!#"
encoded = quote_plus(password)
print(encoded)  # p%40ssw0rd%21%23
```

然后在 `.env` 中使用编码后的密码：
```env
EXTERNAL_DB_PASSWORD=p%40ssw0rd%21%23
```

或者，直接使用完整的 `DATABASE_URL`：
```env
DATABASE_URL=mysql+pymysql://user:p%40ssw0rd%21%23@localhost:3306/dbname
```

### Q6: 如何查看系统正在使用哪个数据库？

查看日志输出，启动时会显示：
```
INFO - Connecting to database: localhost:3306/sales_db
INFO - ✅ Successfully connected to database
```

或调用 API：
```bash
curl http://localhost:8000/database/info
```

---

## 数据库权限要求

确保数据库用户具有以下权限：

### MySQL
```sql
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX
ON database_name.* TO 'username'@'host';
FLUSH PRIVILEGES;
```

### PostgreSQL
```sql
GRANT ALL PRIVILEGES ON DATABASE database_name TO username;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO username;
```

### SQL Server
```sql
USE database_name;
CREATE USER username FOR LOGIN username;
EXEC sp_addrolemember 'db_datareader', 'username';
EXEC sp_addrolemember 'db_datawriter', 'username';
```

---

## 安全建议

1. **不要在代码中硬编码密码**
   - 始终使用 `.env` 文件
   - 将 `.env` 添加到 `.gitignore`

2. **使用强密码**
   - 至少 12 个字符
   - 包含大小写字母、数字和特殊字符

3. **限制数据库访问**
   - 只授予必要的权限
   - 使用防火墙限制访问 IP

4. **使用 SSL/TLS 连接**（生产环境）
   ```env
   DATABASE_URL=mysql+pymysql://user:pass@host:3306/db?ssl_ca=/path/to/ca.pem
   ```

5. **定期更新驱动程序**
   ```bash
   pip install --upgrade pymysql psycopg2-binary pyodbc
   ```

---

## 需要帮助？

如果遇到问题：
1. 检查应用日志：`logs/app.log`
2. 查看 FastAPI 文档：`http://localhost:8000/docs`
3. 运行数据库测试脚本：`python app/database.py`

---

**配置完成后，重启应用即可生效！** 🎉