#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB商品管理模块

提供CRMEB平台的商品管理功能实现。
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from .api_client import CrmebApiClient
from .product_template import ProductTemplate
from .unified_converter import UnifiedProductConverter


class ProductManager:
    """CRMEB商品管理器"""

    def __init__(self, main_url: str, appid: str, appsecret: str, timeout: int = 30):
        """初始化商品管理器
        
        Args:
            main_url: CRMEB主域名
            appid: 应用ID
            appsecret: 应用密钥
            timeout: 请求超时时间（秒）
        """
        logger.debug("初始化CRMEB商品管理器")
        self._api_client = CrmebApiClient(main_url, appid, appsecret, timeout)
        logger.debug("CRMEB商品管理器初始化完成")

    def update_product_status(self, product_id: int, is_show: int) -> Dict:
        """更新商品状态
        
        Args:
            product_id: 商品ID
            is_show: 上架状态，1表示上架展示，0表示下架隐藏
            
        Returns:
            API响应数据，包含status和msg字段
        """
        logger.debug("更新商品状态，商品ID: {}，状态: {}", product_id, is_show)
        
        # 参数验证
        if not isinstance(product_id, int) or product_id <= 0:
            logger.error("商品ID无效: {}", product_id)
            raise ValueError("商品ID必须是正整数")
        
        if is_show not in [0, 1]:
            logger.error("商品状态参数无效: {}", is_show)
            raise ValueError("商品状态参数必须是0（下架）或1（上架）")
        
        # 构建API端点
        endpoint = f"/outapi/product/set_show/{product_id}/{is_show}"
        
        try:
            result = self._api_client.make_request("PUT", endpoint)
            
            status_text = "上架" if is_show == 1 else "下架"
            logger.debug("商品状态更新成功，商品ID: {}，状态: {}", product_id, status_text)
            
            return result
            
        except Exception as e:
            logger.error("更新商品状态失败，商品ID: {}，错误: {}", product_id, str(e))
            raise

    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict:
        """更新商品

        Args:
            product_id: 商品ID
            product_data: 商品数据

        Returns:
            API响应数据
        """
        logger.debug("开始更新商品，商品ID: {}, 传入字段数量: {}", product_id, len(product_data))
        logger.debug("更新商品原始数据: {}", product_data)

        # 设置商品ID
        product_data['id'] = product_id

        # 使用模板确保数据完整性
        complete_data = ProductTemplate.create_product_data(product_data)
        logger.debug("模板处理后的完整更新数据: {}", complete_data)

        try:
            response = self._api_client.make_request('POST', '/outapi/product', complete_data)
            logger.debug("更新商品API响应: {}", response)

            if response.get('status') == 200:
                product_name = complete_data.get('store_name', '未知商品')
                logger.debug("商品更新成功，商品名称: {}", product_name)
            else:
                logger.warning("商品更新失败，响应: {}", response)

            return response

        except Exception as e:
            logger.error("更新商品时发生错误: {}", str(e))
            raise

    def get_product_data(self, product_id: int) -> Dict[str, Any]:
        """获取商品详情

        Args:
            product_id: 商品ID

        Returns:
            商品详情数据
        """
        logger.debug("开始获取商品详情，商品ID: {}", product_id)

        try:
            response = self._api_client.make_request('GET', f'/outapi/product/{product_id}')
            logger.debug("获取商品API响应: {}", response)

            if response.get('status') == 200:
                # API返回的数据结构是 {'status': 200, 'data': {'productInfo': {...}}}
                data = response.get('data', {})
                product_info = data.get('productInfo', {})
                if product_info:
                    product_name = product_info.get('store_name', '未知商品')
                    logger.debug("商品详情获取成功，商品名称: {}", product_name)
                    logger.debug("获取到的完整商品数据: {}", product_info)
                    return product_info
                else:
                    logger.warning("商品详情数据为空，响应: {}", response)
                    return response
            else:
                logger.warning("商品详情获取失败，响应: {}", response)
                return response

        except Exception as e:
            logger.error("获取商品详情时发生错误: {}", str(e))
            raise

    def create_product(self, product_data: Dict[str, Any]) -> Dict:
        """创建商品

        Args:
            product_data: 商品数据字典，会与默认模板合并

        Returns:
            API响应数据，包含status和msg字段
        """
        logger.debug("开始创建商品，传入字段数量: {}", len(product_data))
        logger.debug("创建商品原始数据: {}", product_data)

        # 使用模板创建完整的商品数据
        full_product_data = ProductTemplate.create_product_data(product_data)
        logger.debug("模板处理后的完整商品数据: {}", full_product_data)

        # 验证必填字段
        missing_fields = ProductTemplate.validate_required_fields(full_product_data)
        if missing_fields:
            error_msg = f"商品数据缺失必填字段: {missing_fields}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 调用API创建商品
        try:
            result = self._api_client.make_request("POST", "/outapi/product", full_product_data)
            logger.debug("创建商品API响应: {}", result)

            logger.debug("商品创建成功，商品名称: {}", full_product_data.get('store_name', '未知'))
            return result

        except Exception as e:
            logger.error("创建商品失败，错误: {}", str(e))
            raise

    def create_product_unified(self, unified_data: Dict[str, Any],
                              spec_columns: Optional[List[str]] = None,
                              base_field_mapping: Optional[Dict[str, str]] = None,
                              attr_mapping: Optional[Dict[str, str]] = None) -> Dict:
        """使用统一格式创建商品

        Args:
            unified_data: 统一格式的商品数据
            spec_columns: 规格列名列表
            base_field_mapping: 基础字段映射
            attr_mapping: 属性字段映射

        Returns:
            API响应数据
        """
        logger.debug("使用统一格式创建商品，SKU数量: {}", len(unified_data.get('skus', [])))
        logger.debug("统一格式商品数据: {}", unified_data)

        # 使用统一格式转换器转换数据
        converter = UnifiedProductConverter()
        product_data = converter.convert(unified_data, spec_columns, base_field_mapping, attr_mapping)

        logger.debug("转换后的CRMEB格式数据: {}", product_data)

        # 创建商品
        return self.create_product(product_data)

    def update_product_unified(self, product_id: int, unified_data: Dict[str, Any],
                              spec_columns: Optional[List[str]] = None,
                              base_field_mapping: Optional[Dict[str, str]] = None,
                              attr_mapping: Optional[Dict[str, str]] = None) -> Dict:
        """使用统一格式更新商品

        Args:
            product_id: 商品ID
            unified_data: 统一格式的商品数据
            spec_columns: 规格列名列表
            base_field_mapping: 基础字段映射
            attr_mapping: 属性字段映射

        Returns:
            API响应数据
        """
        logger.debug("使用统一格式更新商品，商品ID: {}, SKU数量: {}", product_id, len(unified_data.get('skus', [])))
        logger.debug("统一格式商品数据: {}", unified_data)

        # 使用统一格式转换器转换数据
        converter = UnifiedProductConverter()
        product_data = converter.convert(unified_data, spec_columns, base_field_mapping, attr_mapping)

        logger.debug("转换后的CRMEB格式数据: {}", product_data)

        # 更新商品
        return self.update_product(product_id, product_data)

    def partial_update_product(self, product_id: int, update_data: Dict[str, Any]) -> Dict:
        """部分更新商品

        Args:
            product_id: 商品ID
            update_data: 统一格式的更新数据

        Returns:
            API响应数据
        """
        logger.debug("部分更新商品，商品ID: {}, 更新字段数: {}", product_id, len(update_data))
        logger.debug("部分更新数据: {}", update_data)

        # 1. 获取原始商品数据
        original_data = self.get_product_data(product_id)
        if not original_data or 'id' not in original_data:
            raise ValueError(f"商品ID {product_id} 不存在或获取失败")

        logger.debug("获取到的原始商品数据: {}", original_data)

        # 2. 转换原始数据为统一格式
        unified_original = self._convert_to_unified_format(original_data)
        logger.debug("转换为统一格式的原始数据: {}", unified_original)

        # 3. 合并更新数据
        merged_data = self._merge_update_data(unified_original, update_data)
        logger.debug("合并后的统一格式数据: {}", merged_data)

        # 4. 使用统一格式更新商品
        return self.update_product_unified(product_id, merged_data)

    def _convert_to_unified_format(self, crmeb_data: Dict[str, Any]) -> Dict[str, Any]:
        """将CRMEB格式数据转换为统一格式"""
        logger.debug("转换CRMEB数据为统一格式")

        # 提取基础字段
        unified_data = {}
        base_fields = [
            'store_name', 'store_info', 'keyword', 'cate_id', 'slider_image',
            'description', 'postage', 'unit_name', 'is_show', 'code'
        ]

        for field in base_fields:
            if field in crmeb_data:
                unified_data[field] = crmeb_data[field]

        # 转换SKU数据
        attrs = crmeb_data.get('attrs', [])
        if attrs:
            skus = []
            for attr in attrs:
                sku = {
                    'code': attr.get('code', ''),
                    'price': attr.get('price', 0),
                    'stock': attr.get('stock', 0),
                    'cost': attr.get('cost', 0),
                    'ot_price': attr.get('ot_price', 0),
                    'pic': attr.get('pic', ''),
                    'weight': attr.get('weight', 0),
                    'volume': attr.get('volume', 0),
                    'brokerage': attr.get('brokerage', 0),
                    'brokerage_two': attr.get('brokerage_two', 0),
                    'vip_price': attr.get('vip_price', 0)
                }

                # 添加规格字段
                detail = attr.get('detail', {})
                for spec_name, spec_value in detail.items():
                    sku[spec_name] = spec_value

                skus.append(sku)

            unified_data['skus'] = skus

        return unified_data

    def _merge_update_data(self, original: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """合并原始数据和更新数据"""
        logger.debug("合并原始数据和更新数据")

        merged = original.copy()

        # 更新基础字段
        for key, value in update.items():
            if key != 'skus':
                merged[key] = value
                logger.debug("更新基础字段: {} = {}", key, value)

        # 更新SKU数据
        if 'skus' in update:
            update_skus = update['skus']
            original_skus = merged.get('skus', [])

            # 创建code到SKU的映射
            sku_map = {sku.get('code'): sku for sku in original_skus}

            # 更新匹配的SKU
            for update_sku in update_skus:
                sku_code = update_sku.get('code')
                if not sku_code:
                    logger.warning("更新SKU缺少code字段，跳过: {}", update_sku)
                    continue

                if sku_code in sku_map:
                    # 更新现有SKU
                    original_sku = sku_map[sku_code]
                    for field, value in update_sku.items():
                        if field != 'code':  # code字段不更新
                            original_sku[field] = value
                            logger.debug("更新SKU {} 字段: {} = {}", sku_code, field, value)
                else:
                    logger.warning("SKU code {} 不存在，跳过更新", sku_code)

        return merged

    def close(self):
        """关闭管理器连接"""
        logger.debug("关闭CRMEB商品管理器")
        if hasattr(self, '_api_client'):
            self._api_client.close()
