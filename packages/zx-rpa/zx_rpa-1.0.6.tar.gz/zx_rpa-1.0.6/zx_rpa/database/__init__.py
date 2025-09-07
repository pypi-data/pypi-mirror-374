"""
数据库操作模块 - 提供各种数据库的操作接口

# Mysql

## 引入方式
```python
from zx_rpa.database import MySQLTable

## MySQL表操作
table = MySQLTable({'host': 'localhost', 'user': 'root', 'password': '123456', 'database': 'test_db'}, 'users')

## 或使用现有连接
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='123456', database='test_db')
table = MySQLTable(conn, 'users')

```

## 对外方法
### MySQLTable
- insert(data) -> int|List[int] - 插入数据，支持单条或批量
- select(where, fields, order_by, limit, offset) -> List[Dict] - 查询数据
- update(data, where) -> int - 更新数据
- delete(where) -> int - 删除数据
- count(where) -> int - 统计记录数
- exists(where) -> bool - 检查记录是否存在
- get_one(where, fields) -> Dict|None - 获取单条记录
- insert_or_update(data, where) -> tuple - 插入或更新
- close() -> bool - 关闭数据库连接
- execute(sql, params) -> List[Dict] - 执行原生SQL语句

### SQLiteTable（未来实现）
- 与MySQLTable相同的接口，适用于SQLite数据库

### MongoTable（未来实现）
- 类似接口，适用于MongoDB数据库

## Where条件操作符使用说明
- 相等: {"name": "张三"}
- 大于等于: {"age__>=": 18} 或 {"age__gte": 18}
- 小于等于: {"age__<=": 60} 或 {"age__lte": 60}
- 大于: {"age__>": 18} 或 {"age__gt": 18}
- 小于: {"age__<": 60} 或 {"age__lt": 60}
- 不等于: {"age__!=": 25} 或 {"age__ne": 25}
- 通配符匹配: {"name__*": "张"} 或 {"name__like": "张"}  # 包含"张"，支持*和?通配符
- 在列表中: {"status__in": ["完成", "进行中"]}
- 不在列表中: {"status__not_in": ["取消"]}
- 是否为空: {"remark__isnull": True}

```

```
"""

# 未来支持更多数据库类型
# from zx_rpa.database import SQLiteTable, MongoTable
# sqlite_table = SQLiteTable("database.db", "users")
# mongo_table = MongoTable("mongodb://localhost:27017", "test_db", "users")

# 按数据库类型导出不同的表操作类
from .mysql_table import MySQLTable

# 未来扩展
# from .sqlite_table import SQLiteTable
# from .mongo_table import MongoTable

__all__ = [
    'MySQLTable',
    # 'SQLiteTable',    # 未来实现
    # 'MongoTable',     # 未来实现
]
