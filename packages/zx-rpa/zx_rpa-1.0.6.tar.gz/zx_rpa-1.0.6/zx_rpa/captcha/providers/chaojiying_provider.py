"""
超级鹰验证码识别服务提供商（预留接口）
"""

from typing import Dict, Any, List
from loguru import logger


class ChaojieyingProvider:
    """超级鹰验证码识别服务提供商（预留实现）"""

    def __init__(self, username: str, password: str, soft_id: str = "1") -> None:
        """
        初始化超级鹰验证码识别服务

        Args:
            username: 超级鹰用户名
            password: 超级鹰密码
            soft_id: 软件ID
        """
        logger.debug("初始化超级鹰验证码客户端，用户: {}", username)

        if not username or not password:
            logger.error("超级鹰用户名和密码不能为空")
            raise ValueError("超级鹰用户名和密码不能为空")

        self._username = username
        self._password = password
        self._soft_id = soft_id

    def recognize(self, image_base64: str, type_id: int = 1) -> str:
        """
        识别验证码（预留接口）

        Args:
            image_base64: base64编码的图片数据
            type_id: 验证码类型ID

        Returns:
            str: 识别结果
        """
        logger.debug("超级鹰验证码识别，类型ID: {}", type_id)
        
        # TODO: 实现超级鹰API调用逻辑
        logger.error("超级鹰识别功能暂未实现")
        raise NotImplementedError("超级鹰识别功能暂未实现")

    def check_balance(self) -> Dict[str, Any]:
        """
        查询账户余额（预留接口）

        Returns:
            Dict: 账户信息
        """
        logger.debug("查询超级鹰账户余额")
        
        # TODO: 实现超级鹰余额查询逻辑
        logger.error("超级鹰余额查询功能暂未实现")
        raise NotImplementedError("超级鹰余额查询功能暂未实现")

    def get_supported_types(self) -> List[Dict[str, Any]]:
        """
        获取支持的验证码类型（预留接口）

        Returns:
            List: 支持的验证码类型列表
        """
        logger.debug("获取超级鹰支持的验证码类型")
        
        # TODO: 返回超级鹰支持的验证码类型
        return [
            {"id": 1001, "name": "数字英文", "description": "4位数字英文混合"},
            {"id": 1002, "name": "纯数字", "description": "4位纯数字"},
            {"id": 1003, "name": "纯英文", "description": "4位纯英文"},
            # 更多类型待补充
        ]
