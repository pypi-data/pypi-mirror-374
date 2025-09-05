# 基础功能导入
from .config import init_global_config
from .notifications import (
    wecom_notification,
    dingtalk_notification,
    feishu_notification,
    send_notification
)

# 导出基础功能
__all__ = [
    "init_global_config",
    "wecom_notification",
    "dingtalk_notification",
    "feishu_notification",
    "send_notification",
]
