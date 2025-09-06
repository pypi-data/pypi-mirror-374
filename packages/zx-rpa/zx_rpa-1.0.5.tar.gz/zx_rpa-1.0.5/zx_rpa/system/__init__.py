"""
系统资源操作模块 - 提供文件、图片、进程等系统级操作

## 引入方式
```python
from zx_rpa.system import SystemManager

# 系统管理器（未来实现，统一接口）
manager = SystemManager()
manager.copy_file("source.txt", "dest.txt")
manager.resize_image("input.jpg", "output.jpg", (800, 600))
manager.run_command("dir", timeout=10)
```

## 对外方法
### SystemManager（统一系统管理器，未来实现）
#### 文件操作
- copy_file(src, dst) -> bool - 复制文件
- move_file(src, dst) -> bool - 移动文件
- delete_file(path) -> bool - 删除文件
- read_text(path, encoding) -> str - 读取文本文件
- write_text(path, content, encoding) -> bool - 写入文本文件

#### 图片处理
- resize_image(input_path, output_path, size) -> bool - 调整图片大小
- compress_image(input_path, output_path, quality) -> bool - 压缩图片
- convert_image_format(input_path, output_path, format) -> bool - 转换图片格式

#### 进程管理
- run_command(cmd, timeout) -> dict - 执行系统命令
- kill_process(pid) -> bool - 终止进程
- get_process_list() -> List[dict] - 获取进程列表

## 参数说明
- src/dst/path: str - 文件路径
- size: tuple - 图片尺寸 (width, height)
- quality: int - 图片质量 1-100
- format: str - 图片格式，如 "jpg", "png", "webp"
- encoding: str - 文件编码，默认 "utf-8"
- cmd: str - 系统命令
- timeout: int - 超时时间（秒）
- pid: int - 进程ID
"""

# TODO: 未来实现系统操作功能
# 只导出统一管理器
# from .system_manager import SystemManager
# __all__ = ['SystemManager']

__all__ = []
