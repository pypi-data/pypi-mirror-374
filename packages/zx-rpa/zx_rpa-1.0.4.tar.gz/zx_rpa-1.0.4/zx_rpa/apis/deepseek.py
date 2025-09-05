import requests
from loguru import logger

def deepseek_chat(user_content: str, model: str = "deepseek-chat", api_key: str = None,
                  system_content: str = "You are a helpful assistant"):
    """
    调用DeepSeek AI API进行对话
    https://api-docs.deepseek.com/zh-cn/

    Args:
        user_content (str): 用户输入内容
        model (str): 模型名称，可选 "deepseek-chat" 或 "deepseek-reasoner"，默认为 "deepseek-chat"
        api_key (str): DeepSeek API密钥
        system_content (str): 系统提示词，默认为 "You are a helpful assistant"

    Returns:
        对于 deepseek-chat: 返回 str (AI回复内容) 或 None (失败时)
        对于 deepseek-reasoner: 返回 tuple (content, reasoning_content) 或 None (失败时)
    """
    logger.debug("开始调用DeepSeek API，模型: {}，用户输入长度: {}", model, len(user_content))

    # 参数验证
    if not api_key:
        logger.error("DeepSeek API密钥不能为空")
        raise ValueError("DeepSeek API密钥不能为空")

    if not user_content.strip():
        logger.error("用户输入内容不能为空")
        raise ValueError("用户输入内容不能为空")

    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 构建消息列表
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]

    data = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        logger.debug("发送请求到DeepSeek API: {}", url)
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # 检查HTTP状态码

        response_data = response.json()
        logger.debug("DeepSeek API响应成功，状态码: {}", response.status_code)

        # 提取AI回复内容
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            message = choice["message"]

            if model == "deepseek-reasoner":
                # 推理模型返回推理过程和最终答案
                reasoning_content = message.get("reasoning_content", "")
                content = message.get("content", "")
                logger.debug("DeepSeek推理模型响应完成，内容长度: {}，推理长度: {}",
                           len(content), len(reasoning_content))
                return content, reasoning_content
            else:
                # 普通对话模型只返回内容
                content = message.get("content", "")
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
        raise Exception(f"DeepSeek API调用异常: {e}")