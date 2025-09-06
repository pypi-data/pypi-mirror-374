"""
ZX_RPA APIs模块
统一的第三方平台API封装
"""

# 导入单个平台API
from .qiniuyun import QiniuManager

__all__ = [
    "QiniuManager"
]
