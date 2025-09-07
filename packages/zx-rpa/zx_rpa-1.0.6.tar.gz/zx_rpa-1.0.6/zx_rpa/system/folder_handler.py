"""
文件夹处理器模块

提供文件夹创建和管理功能
"""

from pathlib import Path
from typing import Union
from loguru import logger


class FolderHandler:
    """文件夹处理器"""
    
    def __init__(self):
        """初始化文件夹处理器"""
        logger.debug("初始化文件夹处理器")
    
    def create_output_folder_with_suffix(
        self, 
        folder_path: Union[str, Path], 
        suffix: str = "_输出"
    ) -> str:
        """
        创建同级同名加指定后缀的新文件夹（已存在则忽略），返回新文件夹路径
        
        Args:
            folder_path (str | Path): 原始文件夹完整路径
            suffix (str): 新文件夹的后缀，默认为"_输出"
            
        Returns:
            str: 新文件夹的完整路径
            
        Raises:
            ValueError: 当原始路径不是有效文件夹时抛出异常
            Exception: 当创建文件夹失败时抛出异常
        """
        logger.debug("创建输出文件夹，原路径: {}，后缀: {}", folder_path, suffix)
        
        try:
            folder = Path(folder_path)
            
            if not folder.exists():
                logger.error("原始文件夹不存在: {}", folder_path)
                raise ValueError(f"'{folder_path}' 不存在")
                
            if not folder.is_dir():
                logger.error("路径不是文件夹: {}", folder_path)
                raise ValueError(f"'{folder_path}' 不是一个有效的文件夹路径")
            
            output_folder = folder.parent / f"{folder.name}{suffix}"
            
            if output_folder.exists():
                logger.debug("输出文件夹已存在，跳过创建: {}", output_folder)
            else:
                output_folder.mkdir(exist_ok=True)
                logger.debug("输出文件夹创建成功: {}", output_folder)
            
            return str(output_folder)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error("创建输出文件夹失败: {}", str(e))
            raise Exception(f"创建输出文件夹失败: {e}")
