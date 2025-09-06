"""
通知推送模块 - 提供微信、钉钉、飞书等多平台消息推送

## 引入方式
```python
from zx_rpa.notify import NotificationSender

sender = NotificationSender()
```

## 对外方法
- send_wecom(content, webhook_url) -> dict - 发送企业微信消息
- send_dingtalk(content, webhook_url, secret) -> dict - 发送钉钉消息
- send_feishu(content, webhook_url) -> dict - 发送飞书消息
- send_notification(content, platform, webhook_url, secret=None, **kwargs) -> dict - 统一发送接口
- get_supported_platforms() -> List[str] - 获取支持的平台列表

## 参数说明
- content: str - 消息内容
- webhook_url: str - Webhook地址
- secret: str - 钉钉机器人密钥（可选）
- platform: str - 平台名称，"wecom"/"dingtalk"/"feishu"
- kwargs: dict - 其他平台特定参数
"""

from .notifications import NotificationSender

__all__ = ['NotificationSender']
