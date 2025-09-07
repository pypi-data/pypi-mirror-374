#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB商城平台API封装模块 - 统一格式商品管理

## 引入方式
```python
from zx_rpa.apis.crmeb import CrmebClient

# 统一客户端（推荐）
client = CrmebClient(
    main_url="https://your-domain.com",
    appid="your_appid",
    appsecret="your_appsecret"
)
```

## 对外方法

### 商品管理
- create_product_unified(unified_data, spec_columns=None, base_field_mapping=None, attr_mapping=None) -> dict - 统一格式创建商品
- update_product_unified(product_id, unified_data, spec_columns=None, base_field_mapping=None, attr_mapping=None) -> dict - 统一格式完整更新商品
- partial_update_product(product_id, update_data) -> dict - 智能部分更新商品
- get_product_data(product_id) -> dict - 获取完整商品数据
- update_product_status(product_id, is_show) -> dict - 更新商品状态（上架/下架）

### 资源管理
- close() - 关闭客户端并清理资源



"""

from .client import CrmebClient

__all__ = ["CrmebClient"]
