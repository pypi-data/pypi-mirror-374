"""
Claude对话服务提供商（预留接口）
"""

from typing import List
from loguru import logger


class ClaudeProvider:
    """Claude对话服务提供商（预留实现）"""

    def __init__(self, api_key: str, base_url: str = None):
        """
        初始化Claude服务

        Args:
            api_key: Claude API密钥
            base_url: API基础URL
        """
        logger.debug("初始化Claude对话服务提供商")

        if not api_key:
            logger.error("Claude API密钥不能为空")
            raise ValueError("Claude API密钥不能为空")

        self.api_key = api_key
        self.base_url = base_url or "https://api.anthropic.com"

    def chat(self, message: str, model: str = "claude-3-haiku", **kwargs) -> str:
        """
        Claude对话（预留接口）

        Args:
            message: 用户输入内容
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            str: AI回复内容
        """
        logger.debug("Claude对话，模型: {}", model)

        # TODO: 实现Claude API调用逻辑
        logger.error("Claude对话功能暂未实现")
        raise NotImplementedError("Claude对话功能暂未实现")

    def get_models(self) -> List[str]:
        """
        获取可用模型列表

        Returns:
            List: 支持的模型列表
        """
        logger.debug("获取Claude可用模型列表")
        return ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"]
