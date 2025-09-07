"""
伊性坊平台验证码处理模块

使用新的统一验证码模块，提供验证码识别功能。
遵循ZX_RPA规范，避免重复实现。
"""

from typing import Dict
from loguru import logger
from zx_rpa.captcha import CaptchaSolver

# 限制对外暴露的类
__all__ = ['CaptchaHandler']


class CaptchaHandler:
    """
    验证码处理器

    使用新的统一验证码模块，提供伊性坊平台专用的验证码处理功能。
    """

    def __init__(self, tujian_username: str, tujian_password: str):
        """
        初始化验证码处理器

        Args:
            tujian_username: 图鉴平台用户名
            tujian_password: 图鉴平台密码
        """
        logger.debug("初始化验证码处理器，图鉴用户: {}", tujian_username)

        if not tujian_username or not tujian_password:
            logger.error("图鉴用户名和密码不能为空")
            raise ValueError("图鉴用户名和密码不能为空")

        try:
            self._captcha_solver = CaptchaSolver()
            self._tujian_username = tujian_username
            self._tujian_password = tujian_password
            logger.debug("验证码处理器初始化成功")
        except Exception as e:
            logger.error("初始化验证码处理器失败: {}", str(e))
            raise

    def recognize_captcha(self, image_source: str, type_id: int = 1) -> str:
        """
        识别验证码

        Args:
            image_source: 图片来源，支持base64编码、本地文件路径、网络URL
            type_id: 验证码类型ID，默认为1（普通英数字验证码）

        Returns:
            str: 识别结果

        Raises:
            Exception: 识别失败时抛出异常
        """
        logger.debug("开始识别验证码，类型ID: {}", type_id)

        try:
            # 使用新的统一验证码模块
            result = self._captcha_solver.recognize_tujian(
                image=image_source,
                username=self._tujian_username,
                password=self._tujian_password,
                type_id=type_id
            )
            logger.debug("验证码识别成功，结果长度: {}", len(result))
            return result
        except Exception as e:
            logger.error("验证码识别失败: {}", str(e))
            raise Exception(f"验证码识别失败: {str(e)}")

    def recognize_with_retry(self, image_source: str, type_id: int = 1, max_retries: int = 3) -> str:
        """
        带重试机制的验证码识别
        
        Args:
            image_source: 图片来源
            type_id: 验证码类型ID
            max_retries: 最大重试次数
            
        Returns:
            str: 识别结果
            
        Raises:
            Exception: 所有重试都失败时抛出异常
        """
        logger.debug("开始验证码识别，最大重试次数: {}", max_retries)
        
        last_error = None
        for attempt in range(max_retries):
            try:
                result = self.recognize_captcha(image_source, type_id)
                if result and result.strip():
                    logger.debug("第{}次尝试识别成功", attempt + 1)
                    return result.strip()
                else:
                    logger.debug("第{}次尝试识别结果为空", attempt + 1)
                    continue
            except Exception as e:
                last_error = e
                logger.debug("第{}次尝试识别失败: {}", attempt + 1, str(e))
                if attempt < max_retries - 1:
                    continue
                    
        logger.error("验证码识别重试全部失败，重试次数: {}", max_retries)
        raise Exception(f"验证码识别重试全部失败: {str(last_error)}")

    def check_balance(self) -> Dict[str, str]:
        """
        查询图鉴账户余额

        Returns:
            dict: 余额信息

        Raises:
            Exception: 查询失败时抛出异常
        """
        logger.debug("查询图鉴账户余额")

        try:
            # 使用新的统一验证码模块查询余额
            balance_info = self._captcha_solver.check_balance_tujian(
                username=self._tujian_username,
                password=self._tujian_password
            )
            logger.debug("余额查询成功")
            return balance_info
        except Exception as e:
            logger.error("查询余额失败: {}", str(e))
            raise Exception(f"查询余额失败: {str(e)}")

    def validate_image(self, image_source: str) -> bool:
        """
        验证图片格式是否有效

        Args:
            image_source: 图片来源

        Returns:
            bool: 图片格式是否有效
        """
        logger.debug("验证图片格式")

        try:
            return self._captcha_solver.validate_image(image_source)
        except Exception as e:
            logger.debug("图片格式验证失败: {}", str(e))
            return False
