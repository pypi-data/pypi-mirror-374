"""
ZX_RPA统一消息通知模块
整合企业微信、钉钉、飞书等平台的消息通知功能

从 zx_rpa/notifications.py 迁移而来，保持完整功能并添加统一接口类
"""

import requests
import time
import hmac
import hashlib
import base64
from urllib.parse import quote_plus
from typing import Dict, Optional, List
from loguru import logger


class NotificationSender:
    """统一通知发送器"""

    def __init__(self):
        """初始化通知发送器"""
        logger.debug("初始化通知发送器")

    def send_wecom(self, content: str, webhook_url: str) -> Dict:
        """发送企业微信消息"""
        logger.debug("NotificationSender发送企业微信通知")
        return wecom_notification(content, webhook_url)

    def send_dingtalk(self, content: str, webhook_url: str, secret: Optional[str] = None) -> Dict:
        """发送钉钉消息"""
        logger.debug("NotificationSender发送钉钉通知")
        return dingtalk_notification(content, webhook_url, secret)

    def send_feishu(self, content: str, webhook_url: str) -> Dict:
        """发送飞书消息"""
        logger.debug("NotificationSender发送飞书通知")
        return feishu_notification(content, webhook_url)

    def send_notification(self, content: str, platform: str, webhook_url: str, **kwargs) -> Dict:
        """统一发送接口"""
        logger.debug("NotificationSender统一发送通知，平台: {}", platform)
        return send_notification(content, platform, webhook_url, **kwargs)

    def get_supported_platforms(self) -> List[str]:
        """获取支持的平台列表"""
        return ["wecom", "dingtalk", "feishu"]


def wecom_notification(content: str, webhook_url: str) -> Dict:
    """
    发送企业微信群机器人文本通知

    Args:
        content: 消息内容
        webhook_url: 企业微信群机器人的完整webhook地址(包含key)

    Returns:
        Dict: 接口返回结果

    Raises:
        requests.RequestException: 网络请求异常
        requests.HTTPError: HTTP状态码异常
        ValueError: API返回错误码非0
    """
    logger.debug("发送企业微信通知，内容: {}", content)

    try:
        response = requests.post(
            webhook_url,
            json={
                "msgtype": "text",
                "text": {
                    "content": content
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        response.raise_for_status()
        result = response.json()

        if result.get("errcode") != 0:
            logger.error("企业微信API错误: {}", result.get('errmsg', '未知错误'))
            raise ValueError(f"企业微信API错误: {result.get('errmsg', '未知错误')}")

        logger.debug("企业微信通知发送成功")
        return result

    except requests.RequestException as e:
        logger.error("企业微信通知网络请求失败: {}", str(e))
        raise
    except Exception as e:
        logger.error("企业微信通知发送失败: {}", str(e))
        raise


def dingtalk_notification(content: str, webhook_url: str, secret: Optional[str] = None) -> Dict:
    """
    发送钉钉群机器人文本通知

    Args:
        content: 消息内容
        webhook_url: 钉钉群机器人webhook地址
        secret: 机器人密钥（用于签名验证）

    Returns:
        Dict: 接口返回结果

    Raises:
        requests.RequestException: 网络请求异常
        ValueError: API返回错误
    """
    logger.debug("发送钉钉通知，内容: {}，是否有签名: {}", content, bool(secret))

    try:
        # 如果有密钥，生成签名
        if secret:
            timestamp = str(round(time.time() * 1000))
            string_to_sign = f"{timestamp}\n{secret}"
            hmac_code = hmac.new(
                secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            sign = quote_plus(base64.b64encode(hmac_code))
            webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

        response = requests.post(
            webhook_url,
            json={
                "msgtype": "text",
                "text": {
                    "content": content
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        response.raise_for_status()
        result = response.json()

        if result.get("errcode") != 0:
            logger.error("钉钉API错误: {}", result.get('errmsg', '未知错误'))
            raise ValueError(f"钉钉API错误: {result.get('errmsg', '未知错误')}")

        logger.debug("钉钉通知发送成功")
        return result

    except requests.RequestException as e:
        logger.error("钉钉通知网络请求失败: {}", str(e))
        raise
    except Exception as e:
        logger.error("钉钉通知发送失败: {}", str(e))
        raise


def feishu_notification(content: str, webhook_url: str) -> Dict:
    """
    发送飞书群机器人文本通知

    Args:
        content: 消息内容
        webhook_url: 飞书群机器人webhook地址

    Returns:
        Dict: 接口返回结果

    Raises:
        requests.RequestException: 网络请求异常
        ValueError: API返回错误
    """
    logger.debug("发送飞书通知，内容: {}", content)

    try:
        response = requests.post(
            webhook_url,
            json={
                "msg_type": "text",
                "content": {
                    "text": content
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        response.raise_for_status()
        result = response.json()

        if result.get("code") != 0:
            logger.error("飞书API错误: {}", result.get('msg', '未知错误'))
            raise ValueError(f"飞书API错误: {result.get('msg', '未知错误')}")

        logger.debug("飞书通知发送成功")
        return result

    except requests.RequestException as e:
        logger.error("飞书通知网络请求失败: {}", str(e))
        raise
    except Exception as e:
        logger.error("飞书通知发送失败: {}", str(e))
        raise


def send_notification(
    content: str,
    platform: str,
    webhook_url: str,
    secret: Optional[str] = None
) -> Dict:
    """
    统一的消息通知发送接口

    Args:
        content: 消息内容
        platform: 平台类型 ('wecom', 'dingtalk', 'feishu')
        webhook_url: webhook地址
        secret: 密钥（钉钉需要）

    Returns:
        Dict: 接口返回结果

    Raises:
        ValueError: 不支持的平台类型
    """
    logger.debug("发送{}平台通知，内容: {}", platform, content)

    platform = platform.lower()

    if platform == 'wecom':
        return wecom_notification(content, webhook_url)
    elif platform == 'dingtalk':
        return dingtalk_notification(content, webhook_url, secret)
    elif platform == 'feishu':
        return feishu_notification(content, webhook_url)
    else:
        logger.error("不支持的通知平台: {}", platform)
        raise ValueError(f"不支持的通知平台: {platform}")


__all__ = [
    "NotificationSender",
    "wecom_notification",
    "dingtalk_notification",
    "feishu_notification",
    "send_notification"
]
