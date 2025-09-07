#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多行列表数据提取器

提供多行列表数据与嵌套结构数据的双向转换功能。
支持自定义字段名称和灵活的数据结构转换。

主要功能：
1. 多行列表 → 嵌套结构：将多行数据提取到指定字段的列表中
2. 嵌套结构 → 多行列表：将嵌套结构数据展开为多行列表
3. 支持自定义字段名称（默认为'items'）
4. 支持字段映射和数据验证

使用场景：
- Excel数据导入处理
- API数据格式转换
- 数据库查询结果处理
- 批量数据操作
"""

from typing import List, Dict, Any, Optional, Union
from loguru import logger


class MultiRowExtractor:
    """多行列表数据提取器"""
    
    def __init__(self):
        """初始化多行列表数据提取器"""
        logger.debug("初始化多行列表数据提取器")
    
    def extract_to_nested(self,
                         multi_row_data: List[Dict[str, Any]],
                         target_field: str = 'items',
                         row_fields: Optional[List[str]] = None,
                         base_fields: Optional[List[str]] = None,
                         field_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        将多行列表数据提取为嵌套结构格式
        
        Args:
            multi_row_data: 多行数据列表
            target_field: 目标字段名称，默认'items'
            row_fields: 行字段列表（每行都要提取的字段），必传
            base_fields: 基础字段列表（公共字段），可选，不传则自动计算为除row_fields外的所有字段
            field_mapping: 字段映射字典，用于重命名字段

        Returns:
            嵌套结构数据字典
            
        Example:
            multi_row_data = [
                {"商品名称": "测试商品", "颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
                {"商品名称": "测试商品", "颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
            ]
            
            result = extractor.extract_to_nested(
                multi_row_data,
                target_field='items',
                row_fields=['颜色', '尺寸', '价格', '库存'],
                base_fields=['商品名称']  # 可选，不传则自动计算
            )

            # 结果：
            # {
            #     "商品名称": "测试商品",
            #     "items": [
            #         {"颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
            #         {"颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
            #     ]
            # }
        """
        logger.debug(f"开始提取多行数据为嵌套结构，数据行数: {len(multi_row_data)}, 目标字段: {target_field}")
        
        if not multi_row_data:
            logger.warning("输入数据为空")
            return {}

        # 如果没有指定row_fields，自动分析所有字段
        if row_fields is None:
            base_fields, row_fields = self._auto_analyze_fields(multi_row_data)
            logger.debug(f"自动分析字段 - 基础字段: {base_fields}, 行字段: {row_fields}")
        else:
            # 如果指定了row_fields但没有指定base_fields，自动计算base_fields
            if base_fields is None:
                # 获取所有字段
                all_fields = set()
                for row in multi_row_data:
                    all_fields.update(row.keys())

                # base_fields = 所有字段 - row_fields
                base_fields = list(all_fields - set(row_fields))
                logger.debug(f"自动计算基础字段: {base_fields}")

            logger.debug(f"使用指定字段 - 基础字段: {base_fields}, 行字段: {row_fields}")
        
        # 构建嵌套结构数据
        nested_data = {}

        # 提取基础字段（从第一行）
        first_row = multi_row_data[0]
        for field in base_fields:
            if field in first_row:
                # 应用字段映射
                mapped_field = field_mapping.get(field, field) if field_mapping else field
                nested_data[mapped_field] = first_row[field]

        # 提取行数据到目标字段
        target_list = []
        for row in multi_row_data:
            row_data = {}
            for field in row_fields:
                if field in row:
                    # 应用字段映射
                    mapped_field = field_mapping.get(field, field) if field_mapping else field
                    row_data[mapped_field] = row[field]
            if row_data:  # 只添加非空的行数据
                target_list.append(row_data)

        nested_data[target_field] = target_list

        logger.debug(f"提取完成，基础字段数: {len(base_fields)}, {target_field}数量: {len(target_list)}")
        return nested_data
    
    def expand_from_nested(self,
                          nested_data: Dict[str, Any],
                          source_field: str = 'skus',
                          field_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        将嵌套结构数据展开为多行列表
        
        Args:
            nested_data: 嵌套结构数据
            source_field: 源字段名称，默认'skus'
            field_mapping: 字段映射字典，用于重命名字段

        Returns:
            多行数据列表

        Example:
            nested_data = {
                "商品名称": "测试商品",
                "skus": [
                    {"颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
                    {"颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
                ]
            }

            result = extractor.expand_from_nested(nested_data, source_field='skus')

            # 结果：
            # [
            #     {"商品名称": "测试商品", "颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
            #     {"商品名称": "测试商品", "颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
            # ]
        """
        logger.debug(f"开始展开嵌套结构数据为多行列表，源字段: {source_field}")

        if not nested_data or source_field not in nested_data:
            logger.warning(f"嵌套结构数据为空或不包含字段: {source_field}")
            return []

        source_list = nested_data[source_field]
        if not isinstance(source_list, list):
            logger.warning(f"字段 {source_field} 不是列表类型")
            return []

        # 获取基础字段（除了源字段之外的所有字段）
        base_data = {k: v for k, v in nested_data.items() if k != source_field}
        
        # 展开为多行数据
        multi_row_data = []
        for item in source_list:
            if isinstance(item, dict):
                # 合并基础数据和行数据
                row_data = base_data.copy()
                row_data.update(item)
                
                # 应用字段映射
                if field_mapping:
                    mapped_row = {}
                    for key, value in row_data.items():
                        mapped_key = field_mapping.get(key, key)
                        mapped_row[mapped_key] = value
                    row_data = mapped_row
                
                multi_row_data.append(row_data)
        
        logger.debug(f"展开完成，生成行数: {len(multi_row_data)}")
        return multi_row_data
    
    def _auto_analyze_fields(self, multi_row_data: List[Dict[str, Any]]) -> tuple:
        """
        自动分析字段分类
        
        Args:
            multi_row_data: 多行数据列表
            
        Returns:
            (base_fields, row_fields) 元组
        """
        if not multi_row_data:
            return [], []
        
        # 获取所有字段
        all_fields = set()
        for row in multi_row_data:
            all_fields.update(row.keys())
        
        # 分析字段变化情况
        base_fields = []
        row_fields = []
        
        for field in all_fields:
            # 获取该字段在所有行中的值
            values = [row.get(field) for row in multi_row_data if field in row]
            unique_values = set(values)
            
            # 如果所有行的值都相同，认为是基础字段
            if len(unique_values) <= 1:
                base_fields.append(field)
            else:
                row_fields.append(field)
        
        logger.debug(f"自动分析完成 - 基础字段: {base_fields}, 变化字段: {row_fields}")
        return base_fields, row_fields
    
    def validate_data(self, data: Union[List[Dict], Dict], data_type: str = 'auto') -> bool:
        """
        验证数据格式
        
        Args:
            data: 要验证的数据
            data_type: 数据类型，'multi_row', 'nested', 'auto'

        Returns:
            是否有效
        """
        if data_type == 'auto':
            # 自动判断数据类型
            if isinstance(data, list):
                data_type = 'multi_row'
            elif isinstance(data, dict):
                data_type = 'nested'
            else:
                return False

        if data_type == 'multi_row':
            return self._validate_multi_row(data)
        elif data_type == 'nested':
            return self._validate_nested(data)
        
        return False
    
    def _validate_multi_row(self, data: List[Dict]) -> bool:
        """验证多行数据格式"""
        if not isinstance(data, list) or not data:
            return False
        
        for row in data:
            if not isinstance(row, dict):
                return False
        
        return True
    
    def _validate_nested(self, data: Dict) -> bool:
        """验证嵌套结构数据"""
        if not isinstance(data, dict):
            return False

        # 至少包含一个列表字段
        has_list_field = any(isinstance(v, list) for v in data.values())
        return has_list_field





if __name__ == "__main__":
    # 示例用法
    extractor = MultiRowExtractor()
    
    # 示例数据
    multi_row_data = [
        {"商品名称": "测试商品", "商品描述": "测试描述", "颜色": "红色", "尺寸": "L", "价格": 199.0, "库存": 100},
        {"商品名称": "测试商品", "商品描述": "测试描述", "颜色": "蓝色", "尺寸": "M", "价格": 189.0, "库存": 80}
    ]
    
    print("原始多行数据:")
    for i, row in enumerate(multi_row_data, 1):
        print(f"  行{i}: {row}")
    
    # 提取为嵌套结构
    nested = extractor.extract_to_nested(
        multi_row_data,
        target_field='items',
        row_fields=['颜色', '尺寸', '价格', '库存'],  # 必传：变化的字段
        base_fields=['商品名称', '商品描述']  # 可选：不传则自动计算
    )

    print(f"\n提取为嵌套结构:")
    print(f"  基础字段: {nested.get('商品名称')}, {nested.get('商品描述')}")
    print(f"  条目数量: {len(nested.get('items', []))}")
    for i, item in enumerate(nested.get('items', []), 1):
        print(f"    条目{i}: {item}")

    # 展开回多行格式
    expanded = extractor.expand_from_nested(nested, source_field='items')

    print(f"\n展开回多行格式:")
    for i, row in enumerate(expanded, 1):
        print(f"  行{i}: {row}")
