"""
AI对话管理器
统一管理不同平台的对话功能
"""

from loguru import logger


class ChatManager:
    """AI对话管理器"""

    def __init__(self):
        """初始化对话管理器"""
        logger.debug("初始化AI对话管理器")
        self._provider_cache = {}  # 缓存Provider实例

    def chat_deepseek(self, message: str, api_key: str, model: str = "deepseek-chat", **kwargs) -> str:
        """
        使用DeepSeek进行对话

        Args:
            message: 对话消息内容
            api_key: DeepSeek API密钥
            model: 模型名称
            **kwargs: 其他参数（temperature、system_content等）

        Returns:
            str: AI回复内容
        """
        logger.debug("使用DeepSeek对话，模型: {}，消息长度: {}", model, len(message))

        try:
            # 生成缓存键（基于api_key和base_url）
            base_url = kwargs.get("base_url", "https://api.deepseek.com")
            cache_key = f"deepseek_{api_key}_{base_url}"

            # 检查缓存中是否已有Provider实例
            if cache_key not in self._provider_cache:
                logger.debug("创建新的DeepSeek Provider实例")
                from .providers.deepseek_provider import DeepseekProvider
                self._provider_cache[cache_key] = DeepseekProvider(api_key, base_url)
            else:
                logger.debug("使用缓存的DeepSeek Provider实例")

            provider = self._provider_cache[cache_key]

            result = provider.chat(
                message=message,
                model=model,
                temperature=kwargs.get("temperature", 0.7),
                system_content=kwargs.get("system_content")
            )

            # DeepSeek返回可能是tuple，取第一个元素
            if isinstance(result, tuple):
                return result[0]
            return result

        except Exception as e:
            logger.error("DeepSeek对话失败: {}", str(e))
            raise

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
        logger.debug("使用OpenAI对话，模型: {}", model)

        # TODO: 实现OpenAI对话逻辑
        logger.error("OpenAI对话功能暂未实现")
        raise NotImplementedError("OpenAI对话功能暂未实现")

    def chat_claude(self, message: str, api_key: str, model: str = "claude-3", **kwargs) -> str:
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
        logger.debug("使用Claude对话，模型: {}", model)

        # TODO: 实现Claude对话逻辑
        logger.error("Claude对话功能暂未实现")
        raise NotImplementedError("Claude对话功能暂未实现")

    def get_supported_models(self, provider: str) -> list:
        """
        获取指定提供商支持的模型列表

        Args:
            provider: 提供商名称

        Returns:
            list: 支持的模型列表
        """
        logger.debug("获取{}支持的模型列表", provider)

        if provider == "deepseek":
            return ["deepseek-chat", "deepseek-reasoner", "deepseek-coder"]
        elif provider == "openai":
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        elif provider == "claude":
            return ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"]
        else:
            logger.error("不支持的提供商: {}", provider)
            return []

    def clear_cache(self, provider: str = None):
        """
        清理Provider缓存

        Args:
            provider: 指定清理的提供商，None表示清理所有
        """
        if provider is None:
            logger.debug("清理所有Provider缓存")
            self._provider_cache.clear()
        else:
            # 清理指定提供商的缓存
            keys_to_remove = [key for key in self._provider_cache.keys() if key.startswith(f"{provider}_")]
            for key in keys_to_remove:
                del self._provider_cache[key]
            logger.debug("清理{}Provider缓存，数量: {}", provider, len(keys_to_remove))

    def get_cache_info(self) -> dict:
        """
        获取缓存信息

        Returns:
            dict: 缓存统计信息
        """
        cache_info = {}
        for key in self._provider_cache.keys():
            provider_name = key.split('_')[0]
            cache_info[provider_name] = cache_info.get(provider_name, 0) + 1

        logger.debug("当前缓存Provider数量: {}", cache_info)
        return cache_info
