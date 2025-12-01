#!/usr/bin/env python3
"""
测试数据库连接脚本
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("测试外部数据库连接")
print("=" * 60)

# 1. 测试环境变量
print("\n1. 检查环境变量...")
from dotenv import load_dotenv
load_dotenv()

external_db_type = os.getenv('EXTERNAL_DB_TYPE')
external_db_host = os.getenv('EXTERNAL_DB_HOST')
external_db_port = os.getenv('EXTERNAL_DB_PORT')
external_db_user = os.getenv('EXTERNAL_DB_USER')
external_db_password = os.getenv('EXTERNAL_DB_PASSWORD')
external_db_name = os.getenv('EXTERNAL_DB_NAME')

print(f"   EXTERNAL_DB_TYPE: {external_db_type}")
print(f"   EXTERNAL_DB_HOST: {external_db_host}")
print(f"   EXTERNAL_DB_PORT: {external_db_port}")
print(f"   EXTERNAL_DB_USER: {external_db_user}")
print(f"   EXTERNAL_DB_PASSWORD: {'*' * len(external_db_password) if external_db_password else None}")
print(f"   EXTERNAL_DB_NAME: {external_db_name}")

# 2. 测试配置加载
print("\n2. 检查配置加载...")
from app.config import settings, get_database_url

print(f"   settings.external_db_type: {settings.external_db_type}")
print(f"   settings.external_db_host: {settings.external_db_host}")
print(f"   settings.external_db_name: {settings.external_db_name}")

db_url = get_database_url()
print(f"   生成的数据库URL: {db_url.split('@')[-1] if '@' in db_url else db_url}")

# 3. 测试数据库管理器
print("\n3. 测试数据库连接...")
from app.database import DatabaseManager

try:
    db_manager = DatabaseManager()
    print(f"   数据库类型: {db_manager.db_type}")
    print(f"   连接URL: {db_manager._mask_password(db_manager.db_url)}")

    print("\n   正在连接数据库...")
    if db_manager.connect():
        print("   ✅ 数据库连接成功！")

        # 获取表列表
        tables = db_manager.get_tables()
        print(f"\n   找到 {len(tables)} 个表:")
        for table in tables[:10]:  # 只显示前10个
            print(f"      - {table}")

        if len(tables) > 10:
            print(f"      ... 还有 {len(tables) - 10} 个表")

        # 获取第一个表的详细信息
        if tables:
            print(f"\n   获取表 '{tables[0]}' 的详细信息:")
            info = db_manager.get_table_info(tables[0])
            print(f"      行数: {info.get('row_count', 0)}")
            print(f"      列数: {info.get('column_count', 0)}")
            if info.get('columns'):
                print(f"      列: {[col['name'] for col in info['columns'][:5]]}")

        db_manager.close()
    else:
        print("   ❌ 数据库连接失败！")

except Exception as e:
    print(f"   ❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()

# 4. 测试 API 端点
print("\n4. 测试 /datasources API...")
try:
    import requests
    response = requests.get('http://localhost:8000/datasources')
    result = response.json()

    if result.get('success'):
        sources = result.get('sources', [])
        print(f"   ✅ API 返回 {len(sources)} 个数据源")

        # 按类型分组
        db_sources = [s for s in sources if s.get('source') == 'database']
        mock_sources = [s for s in sources if s.get('source') in ['mock', 'derived']]
        upload_sources = [s for s in sources if s.get('source') == 'upload']

        print(f"      - 外部数据库: {len(db_sources)} 个")
        print(f"      - 模拟数据: {len(mock_sources)} 个")
        print(f"      - 上传文件: {len(upload_sources)} 个")

        if db_sources:
            print(f"\n   外部数据库表:")
            for source in db_sources[:5]:
                print(f"      - {source.get('name')} ({source.get('rows', 0)} 行)")
    else:
        print(f"   ❌ API 调用失败")

except requests.exceptions.ConnectionError:
    print("   ⚠️  后端服务器未运行，请先启动: python run.py")
except Exception as e:
    print(f"   ❌ 错误: {str(e)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)