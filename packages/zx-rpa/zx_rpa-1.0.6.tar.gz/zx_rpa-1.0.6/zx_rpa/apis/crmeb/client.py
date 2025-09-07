#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB统一客户端模块

提供CRMEB平台的统一对外接口，封装所有API调用和前端请求功能。
"""

from typing import Dict, Optional, Any, List
from loguru import logger

from .product_manager import ProductManager


class CrmebClient:
    """CRMEB统一客户端 - 对外统一接口"""

    def __init__(self, main_url: str, appid: str, appsecret: str, timeout: int = 30):
        """初始化CRMEB客户端

        Args:
            main_url: CRMEB主域名
            appid: 应用ID
            appsecret: 应用密钥
            timeout: 请求超时时间（秒）
        """
        logger.debug("初始化CRMEB统一客户端")

        # 初始化各功能模块
        self._product_manager = ProductManager(main_url, appid, appsecret, timeout)

        logger.debug("CRMEB统一客户端初始化完成")

    # ==================== 商品管理方法 ====================

    def update_product_status(self, product_id: int, is_show: int) -> Dict:
        """更新商品状态

        Args:
            product_id: 商品ID
            is_show: 上架状态，1表示上架展示，0表示下架隐藏

        Returns:
            API响应数据，包含status和msg字段
        """
        return self._product_manager.update_product_status(product_id, is_show)









    def get_product_data(self, product_id: int) -> Dict[str, Any]:
        """获取商品详情数据

        Args:
            product_id: 商品ID

        Returns:
            商品详情数据
        """
        return self._product_manager.get_product_data(product_id)

    def create_product_unified(self, unified_data: Dict[str, Any],
                              spec_columns: Optional[List[str]] = None,
                              base_field_mapping: Optional[Dict[str, str]] = None,
                              attr_mapping: Optional[Dict[str, str]] = None) -> Dict:
        """使用统一格式创建商品

        Args:
            unified_data: 统一格式的商品数据
                {
                    "store_name": "商品名称",
                    "store_info": "商品描述",
                    "skus": [
                        {
                            "code": "sku_001",
                            "price": 299.0,
                            "stock": 100,
                            "颜色": "红色",
                            "尺寸": "L"
                        }
                    ]
                }
            spec_columns: 规格列名列表，如 ['颜色', '尺寸']。如果不提供，会自动识别
            base_field_mapping: 基础字段映射，如 {'store_name': '商品名称'}
            attr_mapping: 属性字段映射，如 {'price': '价格', 'stock': '库存'}

        Returns:
            API响应数据，包含status和msg字段
        """
        return self._product_manager.create_product_unified(
            unified_data, spec_columns, base_field_mapping, attr_mapping
        )

    def update_product_unified(self, product_id: int, unified_data: Dict[str, Any],
                              spec_columns: Optional[List[str]] = None,
                              base_field_mapping: Optional[Dict[str, str]] = None,
                              attr_mapping: Optional[Dict[str, str]] = None) -> Dict:
        """使用统一格式更新商品

        Args:
            product_id: 商品ID
            unified_data: 统一格式的商品数据
            spec_columns: 规格列名列表，如 ['颜色', '尺寸']。如果不提供，会自动识别
            base_field_mapping: 基础字段映射，如 {'store_name': '商品名称'}
            attr_mapping: 属性字段映射，如 {'price': '价格', 'stock': '库存'}

        Returns:
            API响应数据，包含status和msg字段
        """
        return self._product_manager.update_product_unified(
            product_id, unified_data, spec_columns, base_field_mapping, attr_mapping
        )

    def partial_update_product(self, product_id: int, update_data: Dict[str, Any]) -> Dict:
        """部分更新商品

        先获取商品完整数据，然后与更新数据合并，最后提交更新。
        支持基础字段更新和SKU精确更新。

        Args:
            product_id: 商品ID
            update_data: 统一格式的更新数据
                {
                    "store_name": "新商品名称",  # 基础字段更新
                    "skus": [                    # SKU更新（通过code匹配）
                        {
                            "code": "sku_001",
                            "price": 299.0,
                            "stock": 100,
                            "pic": "new_image.jpg"
                        }
                    ]
                }

        Returns:
            API响应数据，包含status和msg字段
        """
        return self._product_manager.partial_update_product(product_id, update_data)


    def close(self):
        """关闭客户端连接"""
        logger.debug("关闭CRMEB客户端")
        if hasattr(self, '_product_manager'):
            self._product_manager.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        self.close()
