#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRMEB统一格式转换器

将统一的商品数据格式转换为CRMEB API需要的格式。
统一格式：基础字段 + skus列表
"""

from typing import Dict, List, Any, Optional
from loguru import logger

from .product_template import ProductTemplate


class UnifiedProductConverter:
    """统一商品数据格式转换器
    
    将统一格式的商品数据转换为CRMEB API格式
    """
    
    def __init__(self):
        """初始化转换器"""
        logger.debug("初始化统一商品数据格式转换器")
    
    def convert(self, unified_data: Dict[str, Any],
                spec_columns: Optional[List[str]] = None,
                base_field_mapping: Optional[Dict[str, str]] = None,
                attr_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """转换统一格式数据为CRMEB API格式

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
            CRMEB API格式的商品数据
        """
        logger.debug("开始转换统一格式数据，SKU数量: {}", len(unified_data.get('skus', [])))

        # 应用字段映射
        mapped_data = self._apply_field_mappings(unified_data, base_field_mapping, attr_mapping)

        # 验证映射后的数据
        self._validate_unified_data(mapped_data)

        # 提取基础字段和SKU数据
        base_fields = self._extract_base_fields(mapped_data)
        skus = mapped_data.get('skus', [])
        
        if not skus:
            # 单规格商品
            return self._convert_single_spec(base_fields)
        else:
            # 多规格商品
            return self._convert_multi_spec(base_fields, skus, spec_columns)
    
    def _validate_unified_data(self, data: Dict[str, Any]) -> None:
        """验证统一格式数据"""
        if not isinstance(data, dict):
            raise ValueError("统一格式数据必须是字典类型")
        
        if 'store_name' not in data:
            raise ValueError("缺少必需字段: store_name")
        
        skus = data.get('skus', [])
        if skus and not isinstance(skus, list):
            raise ValueError("skus字段必须是列表类型")
        
        # 验证SKU数据
        for i, sku in enumerate(skus):
            if not isinstance(sku, dict):
                raise ValueError(f"SKU[{i}]必须是字典类型")
            if 'code' not in sku:
                raise ValueError(f"SKU[{i}]缺少必需字段: code")

    def _apply_field_mappings(self, data: Dict[str, Any],
                             base_field_mapping: Optional[Dict[str, str]] = None,
                             attr_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """应用字段映射"""
        if not attr_mapping and not base_field_mapping:
            return data

        mapped_data = {}

        # 处理基础字段映射
        if base_field_mapping:
            for api_field, user_field in base_field_mapping.items():
                if user_field in data:
                    mapped_data[api_field] = data[user_field]
                    logger.debug("基础字段映射: {} -> {}", user_field, api_field)

        # 复制未映射的基础字段
        for key, value in data.items():
            if key != 'skus' and key not in mapped_data:
                mapped_data[key] = value

        # 处理SKU字段映射
        skus = data.get('skus', [])
        if skus and attr_mapping:
            mapped_skus = []
            for sku in skus:
                mapped_sku = {}

                # 应用属性字段映射
                for api_field, user_field in attr_mapping.items():
                    if user_field in sku:
                        mapped_sku[api_field] = sku[user_field]
                        logger.debug("SKU字段映射: {} -> {}", user_field, api_field)

                # 复制未映射的SKU字段
                for key, value in sku.items():
                    if key not in mapped_sku:
                        mapped_sku[key] = value

                mapped_skus.append(mapped_sku)

            mapped_data['skus'] = mapped_skus
        else:
            mapped_data['skus'] = skus

        return mapped_data
    
    def _extract_base_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """提取基础字段"""
        base_fields = {}
        
        # 排除skus字段，其他都是基础字段
        for key, value in data.items():
            if key != 'skus':
                base_fields[key] = value
        
        return base_fields
    
    def _convert_single_spec(self, base_fields: Dict[str, Any]) -> Dict[str, Any]:
        """转换单规格商品"""
        logger.debug("转换单规格商品")
        
        # 单规格商品数据
        product_data = base_fields.copy()
        product_data.update({
            'spec_type': 0,  # 单规格
            'items': [],
            'attrs': [{
                'attr_arr': ['规格值1', '这是描述值'],
                'detail': {'规格': '规格值1', '描述': '这是描述值'},
                'title': '描述',
                'key': '描述',
                'price': float(base_fields.get('price', 0)),
                'pic': base_fields.get('pic', ''),
                'ot_price': float(base_fields.get('ot_price', base_fields.get('price', 0))),
                'cost': float(base_fields.get('cost', 0)),
                'stock': int(base_fields.get('stock', 0)),
                'is_show': 1,
                'is_default_select': 1,
                'unique': '',
                'weight': float(base_fields.get('weight', 0)),
                'volume': float(base_fields.get('volume', 0)),
                'brokerage': float(base_fields.get('brokerage', 0)),
                'brokerage_two': float(base_fields.get('brokerage_two', 0)),
                'vip_price': float(base_fields.get('vip_price', 0)),
                'vip_proportion': float(base_fields.get('vip_proportion', 0)),
                'index': 1,
                'code': base_fields.get('code', 'sku_001')
            }]
        })
        
        # 使用模板确保数据完整性
        return ProductTemplate.create_product_data(product_data)
    
    def _convert_multi_spec(self, base_fields: Dict[str, Any], skus: List[Dict[str, Any]],
                           spec_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """转换多规格商品"""
        logger.debug("转换多规格商品，SKU数量: {}", len(skus))
        
        # 分析规格维度
        if spec_columns is None:
            spec_columns = self._analyze_spec_columns(skus)
            logger.debug("自动识别规格维度: {}", spec_columns)
        else:
            logger.debug("使用指定规格维度: {}", spec_columns)
        
        # 构建items（规格定义）
        items = self._build_items(skus, spec_columns)
        
        # 构建attrs（SKU详情）
        attrs = self._build_attrs(skus, spec_columns)
        
        # 组装商品数据
        product_data = base_fields.copy()
        product_data.update({
            'spec_type': 1,  # 多规格
            'items': items,
            'attrs': attrs
        })
        
        # 使用模板确保数据完整性
        return ProductTemplate.create_product_data(product_data)
    
    def _analyze_spec_columns(self, skus: List[Dict[str, Any]]) -> List[str]:
        """分析规格维度"""
        # 排除非规格字段
        non_spec_fields = {
            'code', 'price', 'stock', 'cost', 'ot_price', 'pic', 
            'weight', 'volume', 'brokerage', 'brokerage_two', 'vip_price'
        }
        
        spec_columns = set()
        for sku in skus:
            for key in sku.keys():
                if key not in non_spec_fields:
                    spec_columns.add(key)
        
        return sorted(list(spec_columns))  # 排序保证一致性
    
    def _build_items(self, skus: List[Dict[str, Any]], spec_columns: List[str]) -> List[Dict[str, Any]]:
        """构建items（规格定义）"""
        items = []
        
        for i, spec_name in enumerate(spec_columns):
            # 收集该规格的所有值
            spec_values = set()
            for sku in skus:
                if spec_name in sku:
                    spec_values.add(str(sku[spec_name]))
            
            # 构建规格项
            item = {
                "value": spec_name,
                "add_pic": 1 if i == 0 else 0,  # 第一个规格项add_pic为1
                "detail": []
            }
            
            # 构建规格值详情
            for spec_value in sorted(spec_values):
                # 从SKU中查找该规格值对应的图片
                pic_url = ""
                for sku in skus:
                    if str(sku.get(spec_name, '')) == spec_value:
                        pic_url = sku.get('pic', '')
                        break  # 找到第一个匹配的图片就使用

                detail = {
                    "value": spec_value,
                    "pic": pic_url
                }
                item["detail"].append(detail)
            
            items.append(item)
        
        return items
    
    def _build_attrs(self, skus: List[Dict[str, Any]], spec_columns: List[str]) -> List[Dict[str, Any]]:
        """构建attrs（SKU详情）"""
        attrs = []
        
        for i, sku in enumerate(skus):
            # 构建attr_arr（规格组合）
            attr_arr = []
            detail = {}
            for spec_name in spec_columns:
                spec_value = str(sku.get(spec_name, ''))
                attr_arr.append(spec_value)
                detail[spec_name] = spec_value
            
            # 构建SKU详情
            attr = {
                'attr_arr': attr_arr,
                'detail': detail,
                'title': spec_columns[-1] if spec_columns else '规格',  # 使用最后一个规格作为title
                'key': spec_columns[-1] if spec_columns else '规格',
                'price': float(sku.get('price', 0)),
                'pic': sku.get('pic', ''),
                'ot_price': float(sku.get('ot_price', sku.get('price', 0))),
                'cost': float(sku.get('cost', 0)),
                'stock': int(sku.get('stock', 0)),
                'is_show': 1,
                'is_default_select': 1 if i == 0 else 0,  # 第一个SKU为默认选中
                'unique': '',
                'weight': float(sku.get('weight', 0)),
                'volume': float(sku.get('volume', 0)),
                'brokerage': float(sku.get('brokerage', 0)),
                'brokerage_two': float(sku.get('brokerage_two', 0)),
                'vip_price': float(sku.get('vip_price', 0)),
                'vip_proportion': float(sku.get('vip_proportion', 0)),
                'index': i + 1,
                'code': sku.get('code', f'sku_{i+1:03d}')
            }
            
            # 添加规格字段到attr中
            for spec_name in spec_columns:
                attr[spec_name] = str(sku.get(spec_name, ''))
            
            attrs.append(attr)
        
        return attrs
