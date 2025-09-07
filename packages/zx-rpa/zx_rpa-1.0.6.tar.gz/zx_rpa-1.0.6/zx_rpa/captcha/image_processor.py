"""
验证码图片处理模块
提取通用的图片处理功能，支持多种格式转换和验证
"""

import os
import time
import base64
import requests
import re
from typing import Optional
from urllib.parse import urlparse
from loguru import logger


class ImageProcessor:
    """验证码图片处理器"""

    DEFAULT_USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
    NETWORK_SCHEMES = {'http', 'https'}

    def __init__(self):
        """初始化图片处理器"""
        logger.debug("初始化验证码图片处理器")
        self._headers = {"User-Agent": self.DEFAULT_USER_AGENT}

    def process_image(self, image: str) -> str:
        """
        处理图片，统一转换为base64格式

        Args:
            image: 图片来源（base64编码/文件路径/URL）

        Returns:
            str: base64编码的图片数据

        Raises:
            Exception: 图片处理失败
        """
        logger.debug("开始处理图片，源长度: {}", len(image))

        try:
            # 判断是否已经是base64格式
            if self._is_base64_string(image):
                logger.debug("检测到base64格式图片")
                return image

            # 判断是否是网络URL
            if self._is_network_url(image):
                logger.debug("检测到网络URL图片: {}", image[:100])
                return self._convert_url_to_base64(image)

            # 默认作为本地文件路径处理
            logger.debug("检测到本地文件路径: {}", image)
            return self._convert_local_to_base64(image)

        except Exception as e:
            logger.error("图片处理失败: {}", str(e))
            raise Exception(f"图片处理失败: {e}")

    def validate_image(self, image: str) -> bool:
        """
        验证图片格式是否有效

        Args:
            image: 图片来源

        Returns:
            bool: 是否为有效图片
        """
        logger.debug("验证图片格式")

        try:
            # 尝试处理图片
            self.process_image(image)
            return True
        except Exception as e:
            logger.debug("图片格式验证失败: {}", str(e))
            return False

    def base64_to_image(self, base64_data: str, output_path: str) -> bool:
        """
        将base64数据转换为本地图片文件

        Args:
            base64_data: base64编码的图片数据
            output_path: 输出文件路径

        Returns:
            bool: 转换是否成功

        Raises:
            Exception: 转换失败
        """
        logger.debug("将base64转换为本地图片: {}", output_path)

        try:
            # 解码base64数据
            image_data = base64.b64decode(base64_data)

            # 写入文件
            with open(output_path, 'wb') as f:
                f.write(image_data)

            logger.debug("base64转图片成功，大小: {}KB", len(image_data) // 1024)
            return True

        except Exception as e:
            logger.error("base64转图片失败: {}", str(e))
            raise Exception(f"base64转图片失败: {e}")

    def _is_base64_string(self, s: str) -> bool:
        """
        判断字符串是否为有效的base64编码

        Args:
            s: 待检测的字符串

        Returns:
            bool: 是否为base64编码
        """
        # 基本格式检查：长度应该是4的倍数，只包含base64字符
        if len(s) % 4 != 0:
            return False

        # 检查字符是否都是base64有效字符
        base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
        if not base64_pattern.match(s):
            return False

        # 尝试解码验证
        try:
            decoded = base64.b64decode(s, validate=True)
            # 检查解码后的数据是否像图片数据（至少有一定长度）
            return len(decoded) > 100  # 图片数据通常比较大
        except Exception:
            return False

    def _is_network_url(self, url: str) -> bool:
        """
        判断URL是否为网络资源

        Args:
            url: 待检测的URL

        Returns:
            bool: 是否为网络URL
        """
        try:
            parsed_url = urlparse(url)
            return parsed_url.scheme in self.NETWORK_SCHEMES
        except Exception:
            return False

    def _convert_local_to_base64(self, image_path: str) -> str:
        """
        将本地图片转换为base64编码

        Args:
            image_path: 本地图片路径

        Returns:
            str: base64编码的图片数据

        Raises:
            Exception: 文件读取失败
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                logger.debug("本地图片转换成功，大小: {}KB", len(image_data) // 1024)
                return base64_data
        except Exception as e:
            logger.error("本地图片读取失败: {}", str(e))
            raise

    def _convert_url_to_base64(self, image_url: str) -> str:
        """
        将网络图片转换为base64编码

        Args:
            image_url: 图片URL

        Returns:
            str: base64编码的图片数据

        Raises:
            Exception: 网络请求失败
        """
        temp_filename = None
        try:
            # 下载图片
            response = requests.get(image_url, headers=self._headers, timeout=30)
            response.raise_for_status()

            # 创建临时文件
            temp_filename = f"captcha_{int(time.time() * 1000)}.tmp"
            with open(temp_filename, 'wb') as f:
                f.write(response.content)

            # 转换为base64
            return self._convert_local_to_base64(temp_filename)

        except requests.RequestException as e:
            logger.error("网络图片下载失败: {}", str(e))
            raise
        finally:
            # 清理临时文件
            if temp_filename and os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                    logger.debug("临时文件已清理: {}", temp_filename)
                except Exception as e:
                    logger.debug("临时文件清理失败: {}", str(e))
