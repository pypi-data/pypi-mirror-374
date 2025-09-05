# IME-Utils

Chinese IME ciku (aka cell wordlist file) parsing tool.

支持：

- [x] 搜狗拼音（`.scel`）
- [x] 百度拼音（`.bdict`）、百度输入法手机版（`.bcd`）
- [x] QQ 拼音（`.qcel`）、QQ 拼音旧版（6.0 以下词库，`.qpyd`）
- [x] 华宇拼音（紫光输入法）（`.uwl`）

调用

```python
# 安装：uv pip install .
# 用例：
from ime_utils.parser import SogouParser, BaiduParser

parser = BaiduParser()
files = [
    "医学词汇.bdict",
    "电影明星.bdict",
    "体操基本术语.bdict",
]

for file in files[:]:
    if parser.parse(file):
        parser.save_data(f"out-{file}.txt", keep_error=False)
```
