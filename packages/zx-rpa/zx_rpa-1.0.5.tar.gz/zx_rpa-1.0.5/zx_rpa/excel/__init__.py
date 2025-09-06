"""
Excel表格处理模块 - 提供Excel读写、格式化、数据分析功能

## 引入方式
```python
from zx_rpa.excel import ExcelHandler

# Excel处理器（未来实现，统一接口）
handler = ExcelHandler("data.xlsx")
data = handler.read_sheet("Sheet1")
handler.write_data(data, "output.xlsx", "Sheet1")
handler.set_style("A1:C10", bold=True, color="red")
handler.add_chart("bar", "A1:C10", "E1")
```

## 对外方法
### ExcelHandler（统一Excel处理器，未来实现）
#### 文件操作
- open_file(file_path) -> bool - 打开Excel文件
- save_file(file_path) -> bool - 保存Excel文件
- close_file() -> bool - 关闭Excel文件

#### 工作表操作
- read_sheet(sheet_name, header_row) -> List[Dict] - 读取工作表数据
- write_data(data, sheet_name, start_row, start_col) -> bool - 写入数据
- get_sheet_names() -> List[str] - 获取所有工作表名称
- create_sheet(sheet_name) -> bool - 创建工作表
- delete_sheet(sheet_name) -> bool - 删除工作表
- copy_sheet(src_sheet, dst_sheet) -> bool - 复制工作表

#### 格式化操作
- set_style(range_str, **styles) -> bool - 设置单元格样式
- merge_cells(range_str) -> bool - 合并单元格
- set_column_width(column, width) -> bool - 设置列宽
- set_row_height(row, height) -> bool - 设置行高
- add_border(range_str, border_style) -> bool - 添加边框

#### 图表和分析
- add_chart(chart_type, data_range, position) -> bool - 添加图表
- create_pivot_table(data_range, pivot_range) -> bool - 创建数据透视表
- add_formula(cell, formula) -> bool - 添加公式

## 参数说明
- file_path: str - Excel文件路径
- sheet_name: str - 工作表名称
- data: List[Dict] | List[List] - 数据列表
- range_str: str - 单元格范围，如 "A1:C10"
- header_row: int - 标题行号，默认1
- start_row/start_col: int - 起始行列号
- styles: dict - 样式参数，如 bold=True, color="red"
- chart_type: str - 图表类型，如 "line", "bar", "pie"
- border_style: str - 边框样式，如 "thin", "thick"
- formula: str - Excel公式，如 "=SUM(A1:A10)"
"""

# TODO: 未来实现Excel处理功能
# 只导出统一处理器
# from .excel_handler import ExcelHandler
# __all__ = ['ExcelHandler']

__all__ = []
