"""
OpenAI对话服务提供商（预留接口）
"""

from typing import List
from loguru import logger


class OpenAIProvider:
    """OpenAI对话服务提供商（预留实现）"""

    def __init__(self, api_key: str, base_url: str = None):
        """
        初始化OpenAI服务

        Args:
            api_key: OpenAI API密钥
            base_url: API基础URL
        """
        logger.debug("初始化OpenAI对话服务提供商")

        if not api_key:
            logger.error("OpenAI API密钥不能为空")
            raise ValueError("OpenAI API密钥不能为空")

        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"

    def chat(self, message: str, model: str = "gpt-3.5-turbo", **kwargs) -> str:
        """
        OpenAI对话（预留接口）

        Args:
            message: 用户输入内容
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            str: AI回复内容
        """
        logger.debug("OpenAI对话，模型: {}", model)

        # TODO: 实现OpenAI API调用逻辑
        logger.error("OpenAI对话功能暂未实现")
        raise NotImplementedError("OpenAI对话功能暂未实现")

    def get_models(self) -> List[str]:
        """
        获取可用模型列表

        Returns:
            List: 支持的模型列表
        """
        logger.debug("获取OpenAI可用模型列表")
        return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
