"""
图鉴验证码识别服务提供商
专注于API调用，图片处理由ImageProcessor统一处理
"""

import requests
from typing import Dict, Any, List
from loguru import logger


class TujianProvider:
    """图鉴验证码识别服务提供商"""

    API_URL = "http://api.ttshitu.com/predict"
    BALANCE_URL = "http://api.ttshitu.com/queryAccountInfo.json"
    DEFAULT_USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")

    def __init__(self, username: str, password: str) -> None:
        """
        初始化图鉴验证码识别服务

        Args:
            username: 图鉴平台注册用户名
            password: 图鉴平台注册密码
        """
        logger.debug("初始化图鉴验证码客户端，用户: {}", username)

        if not username or not password:
            logger.error("图鉴用户名和密码不能为空")
            raise ValueError("图鉴用户名和密码不能为空")

        self._base_params = {'username': username, 'password': password}
        self._headers = {"User-Agent": self.DEFAULT_USER_AGENT}

    def recognize(self, image_base64: str, type_id: int = 1) -> str:
        """
        识别验证码（接收已处理的base64图片）

        Args:
            image_base64: base64编码的图片数据
            type_id: 验证码类型ID，详见：https://www.ttshitu.com/docs/index.html

        Returns:
            str: 识别结果

        Raises:
            Exception: 识别过程中的各种异常
        """
        logger.debug("开始识别验证码，类型ID: {}，图片数据长度: {}KB", type_id, len(image_base64) // 1024)

        try:
            result = self._call_api(image_base64, type_id)

            if result.get('success'):
                captcha_result = result["data"]["result"]
                logger.debug("验证码识别成功，结果: {}", captcha_result)
                return captcha_result
            else:
                error_msg = result.get('message', '未知错误')
                logger.error("图鉴API识别失败: {}", error_msg)
                raise Exception(f"API识别失败: {error_msg}")

        except requests.RequestException as e:
            logger.error("图鉴API网络请求失败: {}", str(e))
            raise Exception(f"网络请求失败: {e}")
        except KeyError as e:
            logger.error("图鉴API响应格式错误: {}", str(e))
            raise Exception(f"响应格式错误: {e}")
        except Exception as e:
            logger.error("验证码识别失败: {}", str(e))
            raise

    def check_balance(self) -> Dict[str, Any]:
        """
        查询账户信息余额

        Returns:
            Dict: 账户信息字典

        Raises:
            Exception: 查询失败
        """
        logger.debug("查询图鉴账户余额")

        try:
            response = requests.post(
                self.BALANCE_URL,
                json=self._base_params,
                headers=self._headers,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            logger.debug("余额查询成功")
            return result

        except requests.RequestException as e:
            logger.error("余额查询网络请求失败: {}", str(e))
            raise Exception(f"查询余额失败: {e}")
        except Exception as e:
            logger.error("余额查询失败: {}", str(e))
            raise

    def _call_api(self, image_base64: str, type_id: int) -> Dict[str, Any]:
        """
        调用图鉴API进行验证码识别

        Args:
            image_base64: base64编码的图片数据
            type_id: 验证码类型ID

        Returns:
            Dict: API响应结果字典

        Raises:
            requests.RequestException: 网络请求异常
        """
        logger.debug("调用图鉴API，类型ID: {}，图片数据长度: {}KB", type_id, len(image_base64) // 1024)

        params = {'typeid': type_id, 'image': image_base64}
        params.update(self._base_params)

        try:
            response = requests.post(
                self.API_URL,
                json=params,
                headers=self._headers,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            logger.debug("图鉴API调用成功，状态码: {}", response.status_code)
            return result

        except requests.RequestException as e:
            logger.error("图鉴API网络请求失败: {}", str(e))
            raise
        except Exception as e:
            logger.error("图鉴API调用异常: {}", str(e))
            raise


# 为了保持向后兼容，保留原有的类名
TjCaptcha = TujianProvider
