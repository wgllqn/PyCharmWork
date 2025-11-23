#!/usr/bin/env python3
"""
测试 SQL 执行脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.config import get_database_url
from langchain_community.utilities import SQLDatabase

print("=" * 60)
print("测试 SQL 执行")
print("=" * 60)

# 1. 获取数据库 URL
db_url = get_database_url()
print(f"\n1. 数据库URL: {db_url.split('@')[-1] if '@' in db_url else db_url}")

# 2. 连接数据库
print("\n2. 连接数据库...")
try:
    db = SQLDatabase.from_uri(db_url)
    print("   ✅ 数据库连接成功")
except Exception as e:
    print(f"   ❌ 数据库连接失败: {e}")
    sys.exit(1)

# 3. 获取表列表
print("\n3. 获取表列表...")
try:
    tables = db.get_usable_table_names()
    print(f"   找到 {len(tables)} 个表:")
    for table in tables[:10]:
        print(f"      - {table}")
    if len(tables) > 10:
        print(f"      ... 还有 {len(tables) - 10} 个表")
except Exception as e:
    print(f"   ❌ 获取表失败: {e}")
    sys.exit(1)

# 4. 测试简单查询
print("\n4. 测试简单查询...")
test_table = tables[0] if tables else None
if test_table:
    test_sql = f"SELECT * FROM {test_table} LIMIT 5"
    print(f"   SQL: {test_sql}")

    try:
        # 方法 1: 使用 db.run()
        result = db.run(test_sql)
        print(f"   ✅ 查询成功 (db.run)")
        print(f"   结果类型: {type(result)}")
        print(f"   结果预览: {str(result)[:200]}...")
    except Exception as e:
        print(f"   ❌ 查询失败 (db.run): {e}")

    try:
        # 方法 2: 使用原生 SQL
        from sqlalchemy import text
        with db._engine.connect() as conn:
            result = conn.execute(text(test_sql))
            rows = result.fetchall()
            columns = list(result.keys())

            print(f"\n   ✅ 查询成功 (原生 SQL)")
            print(f"   返回行数: {len(rows)}")
            print(f"   列名: {columns}")
            if rows:
                print(f"   第一行数据: {dict(zip(columns, rows[0]))}")
    except Exception as e:
        print(f"   ❌ 查询失败 (原生 SQL): {e}")
        import traceback
        traceback.print_exc()

# 5. 测试您的具体 SQL
print("\n5. 测试您的查询...")
your_sql = "SELECT * FROM purchase_order_detail ORDER BY procurement_number_main DESC LIMIT 10"
print(f"   SQL: {your_sql}")

try:
    from sqlalchemy import text
    with db._engine.connect() as conn:
        result = conn.execute(text(your_sql))
        rows = result.fetchall()
        columns = list(result.keys())

        print(f"   ✅ 查询成功!")
        print(f"   返回行数: {len(rows)}")
        print(f"   列名 ({len(columns)} 列): {columns[:5]}{'...' if len(columns) > 5 else ''}")

        if rows:
            print(f"\n   前3行数据:")
            for i, row in enumerate(rows[:3]):
                row_dict = dict(zip(columns, row))
                # 只显示前几个字段
                preview = {k: v for k, v in list(row_dict.items())[:5]}
                print(f"      行 {i+1}: {preview}")
        else:
            print(f"   ⚠️  查询成功但没有返回数据")
            print(f"   可能原因:")
            print(f"      1. 表是空的")
            print(f"      2. procurement_number_main 列不存在或为NULL")
            print(f"      3. 字段名大小写不匹配")

            # 检查表结构
            print(f"\n   检查表结构...")
            try:
                table_info = db.get_table_info([your_sql.split("FROM")[1].split()[0]])
                print(f"   表结构:\n{table_info}")
            except Exception as e2:
                print(f"   无法获取表结构: {e2}")

except Exception as e:
    print(f"   ❌ 查询失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)