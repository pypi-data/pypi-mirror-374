"""
伊性坊平台工具函数模块

提供通用的工具函数，遵循ZX_RPA规范。
"""

from loguru import logger

# 限制对外暴露的函数
__all__ = [
    'is_authorization_error',
    'extract_bn_id',
    'filter_price',
    'filter_spec_string'
]

def is_authorization_error(response_json: dict) -> bool:
    """
    判断是否为Authorization错误
    基于实际测试结果的精确判断逻辑
    
    Args:
        response_json: API响应的JSON数据
        
    Returns:
        bool: 如果是认证错误返回True，否则返回False
    """
    if not response_json:
        return False

    code = response_json.get('code')
    message = response_json.get('msg', response_json.get('message', '')).lower()

    # 明确的Authorization错误标识
    if code == 401:
        return True

    # 检查错误消息关键词
    auth_error_keywords = [
        '身份验证失败',
        '用户不存在', 
        '请从伊性坊页面跳转进入',
        '请登录后操作',
        'unauthorized',
        'authentication failed'
    ]

    if any(keyword in message for keyword in auth_error_keywords):
        return True

    return False

def extract_bn_id(url: str) -> str:
    """
    从URL中提取bn_id参数
    
    Args:
        url: 包含bn参数的URL
        
    Returns:
        str: 提取的bn_id，如果未找到返回None
    """
    logger.debug("提取URL中的bn_id参数: {}", url[:100])
    
    try:
        if "bn=" in url:
            bn_part = url.split("bn=")[-1]
            if "&" in bn_part:
                bn_part = bn_part.split("&")[0]
            logger.debug("提取到bn_id: {}", bn_part)
            return bn_part
        elif "bn_id=" in url:
            bn_part = url.split("bn_id=")[-1]
            if "&" in bn_part:
                bn_part = bn_part.split("&")[0]
            logger.debug("提取到bn_id: {}", bn_part)
            return bn_part

        logger.debug("URL中未找到bn参数")
        return None
    except Exception as e:
        logger.error("提取bn_id异常: {}", str(e))
        return None

def filter_price(price_string: str) -> str:
    """
    处理价格字符串，提取数字并格式化
    
    Args:
        price_string: 原始价格字符串
        
    Returns:
        str: 格式化后的价格字符串
    """
    import re
    try:
        # 去除所有非数字和小数点的字符
        price_clean = re.sub(r'[^\d.]', '', price_string)
        
        # 转换为浮点数并格式化
        price_float = float(price_clean)
        return f"{price_float:.2f}"
    except ValueError:
        logger.debug("价格格式化失败，使用默认值: {}", price_string)
        return "0.00"

def filter_spec_string(input_string: str) -> str:
    """
    处理规格字符串，移除特殊字符和限价信息
    
    Args:
        input_string: 原始规格字符串
        
    Returns:
        str: 处理后的规格字符串
    """
    import re
    try:
        # 删除特殊字符
        special_chars = r'[\\/:*?"<>|]'
        filtered_string = re.sub(special_chars, '', input_string)

        # 删除"限价"及其后面的内容
        filtered_string = re.sub(r'\s*（?限价\s*\d*\.?\d*）?', '', filtered_string)

        # 删除结尾的"查看"
        filtered_string = re.sub(r'\s*查看\s*', '', filtered_string)

        return filtered_string.strip()
    except Exception:
        logger.debug("规格字符串处理失败，返回原字符串: {}", input_string)
        return input_string
