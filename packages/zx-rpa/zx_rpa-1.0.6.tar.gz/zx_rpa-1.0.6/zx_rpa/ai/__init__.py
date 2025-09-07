"""
AI功能模块 - 提供统一的AI服务接口

## 引入方式
```python
from zx_rpa.ai import AIAssistant

# AI助手
assistant = AIAssistant()
```

## 对外方法
### AIAssistant（AI助手统一接口）
#### 对话功能
- chat_deepseek(message, api_key, model="deepseek-chat", **kwargs) -> str - DeepSeek对话
- chat_openai(message, api_key, model="gpt-3.5-turbo", **kwargs) -> str - OpenAI对话
- chat_claude(message, api_key, model="claude-3", **kwargs) -> str - Claude对话
- chat_doubao(message, api_key, model, **kwargs) -> str - 豆包智能体对话

#### 向量化功能（预留）
- embedding_openai(text, api_key, model="text-embedding-ada-002") -> List[float] - OpenAI向量化
- embedding_local(text, model_path) -> List[float] - 本地向量化

#### 缓存管理
- clear_cache(provider=None) - 清理Provider缓存
- get_cache_info() -> dict - 获取缓存统计信息

### AI Providers（AI服务提供商，高级用户使用）
- DeepseekProvider - DeepSeek对话服务提供商
- OpenAIProvider - OpenAI对话服务提供商
- ClaudeProvider - Claude对话服务提供商
- DoubaoProvider - 豆包智能体对话服务提供商


"""

from .ai_assistant import AIAssistant

__all__ = ['AIAssistant']
