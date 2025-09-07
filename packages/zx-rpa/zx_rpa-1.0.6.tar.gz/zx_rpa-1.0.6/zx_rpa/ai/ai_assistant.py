"""
AI助手
提供各种AI功能的统一接口
"""

from loguru import logger
from typing import List, Dict, Any, Optional
from .chat.chat_manager import ChatManager


class AIAssistant:
    """AI助手"""

    def __init__(self):
        """初始化AI助手"""
        logger.debug("初始化AI助手")
        self._chat_manager = ChatManager()

    # ==================== 对话功能 ====================

    def chat_deepseek(self, message: str, api_key: str, model: str = "deepseek-chat", **kwargs) -> str:
        """
        使用DeepSeek进行对话

        Args:
            message: 对话消息内容
            api_key: DeepSeek API密钥
            model: 模型名称
            **kwargs: 其他参数（temperature、system_content、base_url等）

        Returns:
            str: AI回复内容
        """
        logger.debug("DeepSeek对话，消息长度: {}", len(message))
        return self._chat_manager.chat_deepseek(message, api_key, model, **kwargs)

    def chat_openai(self, message: str, api_key: str, model: str = "gpt-3.5-turbo", **kwargs) -> str:
        """
        使用OpenAI进行对话（预留接口）

        Args:
            message: 对话消息内容
            api_key: OpenAI API密钥
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            str: AI回复内容
        """
        logger.debug("OpenAI对话，消息长度: {}", len(message))
        return self._chat_manager.chat_openai(message, api_key, model, **kwargs)

    def chat_claude(self, message: str, api_key: str, model: str = "claude-3-haiku", **kwargs) -> str:
        """
        使用Claude进行对话（预留接口）

        Args:
            message: 对话消息内容
            api_key: Claude API密钥
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            str: AI回复内容
        """
        logger.debug("Claude对话，消息长度: {}", len(message))
        return self._chat_manager.chat_claude(message, api_key, model, **kwargs)

    def chat_doubao(self, message: str, api_key: str, model: str, **kwargs) -> str:
        """
        使用豆包智能体进行对话

        Args:
            message: 对话消息内容
            api_key: 豆包API密钥
            model: 智能体模型ID
            **kwargs: 其他参数（base_url等）

        Returns:
            str: AI回复内容
        """
        logger.debug("豆包对话，消息长度: {}", len(message))
        return self._chat_manager.chat_doubao(message, api_key, model, **kwargs)

    # ==================== 向量化功能（预留） ====================

    def embedding_openai(self, text: str, api_key: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        使用OpenAI进行文本向量化（预留接口）

        Args:
            text: 待向量化的文本
            api_key: OpenAI API密钥
            model: 向量化模型名称

        Returns:
            List[float]: 文本向量
        """
        logger.debug("OpenAI文本向量化，文本长度: {}", len(text))

        # TODO: 实现OpenAI向量化功能
        logger.error("OpenAI向量化功能暂未实现")
        raise NotImplementedError("OpenAI向量化功能暂未实现")

    def embedding_local(self, text: str, model_path: str) -> List[float]:
        """
        使用本地模型进行文本向量化（预留接口）

        Args:
            text: 待向量化的文本
            model_path: 本地模型路径

        Returns:
            List[float]: 文本向量
        """
        logger.debug("本地文本向量化，文本长度: {}", len(text))

        # TODO: 实现本地向量化功能
        logger.error("本地向量化功能暂未实现")
        raise NotImplementedError("本地向量化功能暂未实现")

    # ==================== 工具方法 ====================

    def get_supported_models(self, provider: str) -> List[str]:
        """
        获取指定提供商支持的模型列表

        Args:
            provider: 提供商名称（deepseek、openai、claude）

        Returns:
            List[str]: 支持的模型列表
        """
        logger.debug("获取{}支持的模型列表", provider)
        return self._chat_manager.get_supported_models(provider)

    def clear_cache(self, provider: str = None):
        """
        清理Provider缓存

        Args:
            provider: 指定清理的提供商，None表示清理所有
        """
        logger.debug("清理Provider缓存")
        self._chat_manager.clear_cache(provider)

    def get_cache_info(self) -> dict:
        """
        获取缓存信息

        Returns:
            dict: 缓存统计信息
        """
        return self._chat_manager.get_cache_info()
