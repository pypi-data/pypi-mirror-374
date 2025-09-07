"""
豆包AI对话服务提供商
专注于豆包平台的智能体对话API调用
"""

import requests
from loguru import logger
from typing import List, Optional


class DoubaoProvider:
    """豆包AI对话服务提供商"""

    def __init__(self, api_key: str, base_url: str = "https://ark.cn-beijing.volces.com"):
        """
        初始化豆包AI服务
        
        Args:
            api_key (str): 豆包API密钥
            base_url (str): API基础URL，默认为官方地址
        """
        logger.debug("初始化豆包对话服务提供商")
        
        if not api_key:
            logger.error("豆包API密钥不能为空")
            raise ValueError("豆包API密钥不能为空")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'zx-rpa/DoubaoProvider'
        })
        
        logger.debug("豆包服务提供商初始化完成，API密钥长度: {}", len(api_key))
    
    def chat(self, message: str, model: str, temperature: float = 0.7, 
             system_content: str = None) -> str:
        """
        豆包智能体对话
        
        Args:
            message (str): 用户输入内容
            model (str): 智能体模型ID
            temperature (float): 温度参数（豆包暂不支持，保持接口一致性）
            system_content (str): 系统提示词（豆包暂不支持，保持接口一致性）
            
        Returns:
            str: AI回复内容
            
        Raises:
            ValueError: 当参数为空时抛出异常
            Exception: 当API调用失败时抛出异常
        """
        logger.debug("开始调用豆包API，模型ID: {}，用户输入长度: {}", model, len(message))
        
        # 参数验证
        if not message.strip():
            logger.error("用户输入内容不能为空")
            raise ValueError("用户输入内容不能为空")
            
        if not model:
            logger.error("模型ID不能为空")
            raise ValueError("模型ID不能为空")
        
        url = f"{self.base_url}/api/v3/bots/chat/completions"
        
        data = {
            "model": model,
            "stream": False,
            "stream_options": {"include_usage": True},
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
        
        try:
            logger.debug("发送请求到豆包API: {}", url)
            response = self._session.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            
            logger.debug("豆包API响应成功，内容长度: {}", len(content))
            return content
            
        except requests.exceptions.Timeout as e:
            logger.error("豆包API请求超时: {}", str(e))
            raise Exception(f"豆包API请求超时: {e}")
        except requests.exceptions.RequestException as e:
            logger.error("豆包API网络请求失败: {}", str(e))
            raise Exception(f"豆包API网络请求失败: {e}")
        except (KeyError, IndexError) as e:
            logger.error("豆包API响应解析失败: {}", str(e))
            raise Exception(f"豆包API响应格式错误: {e}")
        except Exception as e:
            logger.error("豆包API调用异常: {}", str(e))
            raise
    
    def get_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            List[str]: 支持的模型列表（豆包需要用户提供具体的智能体ID）
        """
        logger.debug("获取豆包可用模型列表")
        return ["用户自定义智能体ID"]  # 豆包使用用户创建的智能体ID
    
    def __enter__(self):
        """支持上下文管理器"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        if hasattr(self, '_session'):
            self._session.close()
            logger.debug("豆包服务提供商资源已清理")
