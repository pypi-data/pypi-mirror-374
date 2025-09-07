"""
列表处理工具模块

提供各种列表数据处理和转换功能
"""

from typing import List, Any
from loguru import logger


class ListUtils:
    """列表处理工具类"""

    def __init__(self):
        """初始化列表处理工具"""
        logger.debug("初始化列表处理工具")

    def split_list_to_2d(
        self,
        input_list: List[Any],
        sub_length: int,
        keep_remainder: bool = True
    ) -> List[List[Any]]:
        """
        将一维列表转换为二维列表

        Args:
            input_list (List[Any]): 需要转换的输入一维列表
            sub_length (int): 每个子列表的长度
            keep_remainder (bool, optional): 是否保留不足sub_length长度的剩余元素. 默认为True

        Returns:
            List[List[Any]]: 转换后的二维列表
                例如:
                input_list=[1,2,3,4,5], sub_length=2, keep_remainder=True
                返回 [[1,2], [3,4], [5]]

        Raises:
            ValueError: 当input_list为空列表，或sub_length小于等于0时抛出异常
        """
        logger.debug("开始列表分割，输入长度: {}，子列表长度: {}，保留余数: {}",
                    len(input_list), sub_length, keep_remainder)

        # 参数验证
        if not input_list:
            logger.error("输入列表不能为空")
            raise ValueError("输入列表不能为空")

        if sub_length <= 0:
            logger.error("子列表长度必须大于0，当前值: {}", sub_length)
            raise ValueError("子列表长度必须大于0")

        result = []

        # 计算可以完整分割的子列表
        for i in range(0, len(input_list), sub_length):
            if i + sub_length <= len(input_list):
                result.append(input_list[i:i + sub_length])
            # 处理剩余元素
            elif keep_remainder:
                result.append(input_list[i:])

        logger.debug("列表分割完成，生成{}个子列表", len(result))
        return result
