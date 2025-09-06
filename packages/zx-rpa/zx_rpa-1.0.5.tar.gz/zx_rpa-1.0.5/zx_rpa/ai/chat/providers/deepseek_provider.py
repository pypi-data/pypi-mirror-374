"""
DeepSeek AI对话服务提供商
专注于DeepSeek平台的对话API调用
"""

import requests
from loguru import logger
from typing import List, Union, Tuple, Optional


class DeepseekProvider:
    """DeepSeek AI对话服务提供商"""

    def __init__(self, api_key: str, base_url: str = None):
        """
        初始化DeepSeek AI服务

        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL（可选，默认使用官方API）
        """
        logger.debug("初始化DeepSeek对话服务提供商")

        if not api_key:
            logger.error("DeepSeek API密钥不能为空")
            raise ValueError("DeepSeek API密钥不能为空")

        self.api_key = api_key
        self.base_url = base_url or "https://api.deepseek.com"

    def chat(self, message: str, model: str = "deepseek-chat",
             temperature: float = 0.7, system_content: str = None) -> Union[str, Tuple[str, str]]:
        """
        DeepSeek对话

        Args:
            message: 用户输入内容
            model: 模型名称，可选 "deepseek-chat" 或 "deepseek-reasoner"
            temperature: 温度参数（暂未使用，保持接口一致性）
            system_content: 系统提示词

        Returns:
            对于 deepseek-chat: 返回 str (AI回复内容)
            对于 deepseek-reasoner: 返回 tuple (content, reasoning_content)

        Raises:
            Exception: API调用失败
        """
        logger.debug("开始调用DeepSeek API，模型: {}，用户输入长度: {}", model, len(message))

        # 参数验证
        if not message.strip():
            logger.error("用户输入内容不能为空")
            raise ValueError("用户输入内容不能为空")

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构建消息列表
        messages = [
            {"role": "system", "content": system_content or "You are a helpful assistant"},
            {"role": "user", "content": message}
        ]

        data = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        try:
            logger.debug("发送请求到DeepSeek API: {}", url)
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            response_data = response.json()
            logger.debug("DeepSeek API响应成功，状态码: {}", response.status_code)

            # 提取AI回复内容
            if "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]
                message_data = choice["message"]

                if model == "deepseek-reasoner":
                    # 推理模型返回推理过程和最终答案
                    reasoning_content = message_data.get("reasoning_content", "")
                    content = message_data.get("content", "")
                    logger.debug("DeepSeek推理模型响应完成，内容长度: {}，推理长度: {}",
                               len(content), len(reasoning_content))
                    return content, reasoning_content
                else:
                    # 普通对话模型只返回内容
                    content = message_data.get("content", "")
                    logger.debug("DeepSeek对话模型响应完成，内容长度: {}", len(content))
                    return content
            else:
                logger.error("DeepSeek API响应格式异常，未找到choices字段")
                raise Exception("DeepSeek API响应格式异常，未找到choices字段")

        except requests.RequestException as e:
            logger.error("DeepSeek API网络请求失败: {}", str(e))
            raise Exception(f"DeepSeek API网络请求失败: {e}")
        except Exception as e:
            logger.error("DeepSeek API调用异常: {}", str(e))
            raise

    def get_models(self) -> List[str]:
        """
        获取可用模型列表

        Returns:
            List: 支持的模型列表
        """
        logger.debug("获取DeepSeek可用模型列表")
        return ["deepseek-chat", "deepseek-reasoner", "deepseek-coder"]
