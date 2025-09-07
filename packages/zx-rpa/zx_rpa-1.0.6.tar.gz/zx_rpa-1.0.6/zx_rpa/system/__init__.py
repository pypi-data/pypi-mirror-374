"""
系统资源操作模块 - 提供文件、文件夹、图片、进程等系统级操作

## 引入方式
```python
# 文件处理器
from zx_rpa.system import FileHandler
file_handler = FileHandler()
lines = file_handler.read_txt_to_list("data.txt", strip=True, skip_empty=True)
files = file_handler.get_files_natural_sorted("./folder")

# 文件夹处理器
from zx_rpa.system import FolderHandler
folder_handler = FolderHandler()
output_path = folder_handler.create_output_folder_with_suffix("./data", "_输出")
```

## 对外方法
### FileHandler（文件处理器）
- read_txt_to_list(file_path, strip=True, skip_empty=True, remove_duplicates=False) -> List[str] - 读取txt文件内容并转换为列表
- get_files_natural_sorted(folder_path) -> List[Path] - 获取文件夹中的文件列表，按自然排序

### FolderHandler（文件夹处理器）
- create_output_folder_with_suffix(folder_path, suffix="_输出") -> str - 创建同级同名加指定后缀的新文件夹


"""

from .file_handler import FileHandler
from .folder_handler import FolderHandler

__all__ = ['FileHandler', 'FolderHandler']
