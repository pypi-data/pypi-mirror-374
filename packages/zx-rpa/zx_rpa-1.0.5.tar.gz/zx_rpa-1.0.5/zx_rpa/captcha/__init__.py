"""
验证码处理模块 - 提供验证码识别和操作服务

## 引入方式
```python
from zx_rpa.captcha import CaptchaSolver

# 验证码识别
solver = CaptchaSolver()
result = solver.recognize_tujian("image_data", username="user", password="pass", type_id=1)
result = solver.recognize_chaojiying("image_data", username="user", password="pass", type_id=1)
```

## 对外方法
### 识别功能
- recognize_tujian(image, username, password, type_id=1) -> str - 图鉴识别
- recognize_chaojiying(image, username, password, type_id=1) -> str - 超级鹰识别
- check_balance_tujian(username, password) -> dict - 查询图鉴余额
- check_balance_chaojiying(username, password) -> dict - 查询超级鹰余额

### 图片处理功能
- process_image(image) -> str - 本地或网络url图片格式转换为base64
- validate_image(image) -> bool - 验证图片格式
- base64_to_image(base64_data, output_path) -> bool - 将base64转换为本地图片

### 操作功能（预留）
- handle_slide_captcha(element) -> bool - 处理滑动验证码
- handle_click_captcha(element, positions) -> bool - 处理点选验证码

## 参数说明
- image: str - 图片数据（base64编码/文件路径/URL）
- username/password: str - 服务商账号密码
- type_id: int - 验证码类型ID，1=数字英文，2=纯数字等
"""

from .captcha_solver import CaptchaSolver

__all__ = ['CaptchaSolver']
