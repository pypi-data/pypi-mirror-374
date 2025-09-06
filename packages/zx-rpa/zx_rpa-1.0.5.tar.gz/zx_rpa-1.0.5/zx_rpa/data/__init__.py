"""
数据处理模块 - 提供数据转换、验证、清洗等处理功能

## 引入方式
```python
from zx_rpa.data import DataProcessor

# 数据处理器（未来实现，统一接口）
processor = DataProcessor()
json_data = processor.dict_to_json({"name": "张三", "age": 25})
is_valid = processor.validate_email("test@example.com")
cleaned_data = processor.remove_duplicates(data_list, "id")
```

## 对外方法
### DataProcessor（统一数据处理器，未来实现）
#### 数据转换
- dict_to_json(data, ensure_ascii) -> str - 字典转JSON
- json_to_dict(json_str) -> dict - JSON转字典
- csv_to_dict(csv_path, encoding) -> List[dict] - CSV转字典列表
- dict_to_csv(data, csv_path, encoding) -> bool - 字典列表转CSV
- xml_to_dict(xml_str) -> dict - XML转字典
- dict_to_xml(data, root_name) -> str - 字典转XML

#### 数据验证
- validate_email(email) -> bool - 验证邮箱格式
- validate_phone(phone, country) -> bool - 验证手机号
- validate_url(url) -> bool - 验证URL格式
- validate_id_card(id_card) -> bool - 验证身份证号
- validate_data_schema(data, schema) -> bool - 验证数据结构

#### 数据清洗
- clean_text(text, remove_chars) -> str - 清理文本
- remove_duplicates(data, key) -> List[dict] - 去重
- normalize_text(text, method) -> str - 文本标准化
- fill_missing_values(data, strategy) -> List[dict] - 填充缺失值

## 参数说明
- data: dict|List[dict] - 数据
- ensure_ascii: bool - JSON是否转义非ASCII字符
- encoding: str - 文件编码，默认 "utf-8"
- country: str - 国家代码，如 "CN"
- key: str - 去重依据的字段名
- remove_chars: str - 要移除的字符
- schema: dict - 数据结构定义
- method: str - 标准化方法，如 "lower", "upper"
- strategy: str - 填充策略，如 "mean", "median", "mode"
"""

# TODO: 未来实现数据处理功能
# 只导出统一处理器
# from .data_processor import DataProcessor
# __all__ = ['DataProcessor']

__all__ = []
