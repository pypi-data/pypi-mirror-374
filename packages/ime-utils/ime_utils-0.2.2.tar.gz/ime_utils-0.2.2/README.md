# IME-Utils

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/hantang/ime-utils?style=flat-square)
![GitHub release](https://img.shields.io/github/v/release/hantang/ime-utils?style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/hantang/ime-utils?style=flat-square)
![GitHub license](https://img.shields.io/github/license/hantang/ime-utils?style=flat-square)

</div>

中文输入法词库文件（细胞词库）解析工具。

> Chinese IME ciku (aka cell wordlist file) parsing tool.

支持：

- [x] 搜狗拼音（`.scel`）
- [x] 百度拼音（`.bdict`）、百度输入法手机版（`.bcd`）
- [x] QQ 拼音（`.qcel`）、QQ 拼音旧版（6.0 以下词库，`.qpyd`）
- [x] 华宇拼音（紫光输入法）（`.uwl`）

## 使用

- 程序调用：

```python
# 安装
# pip install ime-utils
# uv pip install . # 本地

# 用例：
from ime_utils.parser import SogouParser, BaiduParser

parser = BaiduParser()
files = [
    "医学词汇.bdict",
    "电影明星.bdict",
    "体操基本术语.bdict",
]

for file in files[:]:
    save_file = f"out-{file}.txt"
    if parser.parse(file):
        parser.save_data(save_file, keep_error=False)
```

- 命令行调用

```shell
# 或者 python -m ime_utils -f file-names -o output

# 指定多个文件
ime-utils -f file-name1,file-name2 -o output
# 指定目录，-e保留解析异常词语, -r 目录递归检索文件
ime-utils -d file-dir -o text -e -r
```

## 相关

- [:link: 蔷薇词库转换 nopdan/rose](https://github.com/nopdan/rose)
    ![](https://img.shields.io/github/v/release/nopdan/rose)
    ![](https://img.shields.io/github/license/nopdan/rose)
    ![](https://img.shields.io/github/last-commit/nopdan/rose)

- [:link: 深蓝词库转换 studyzy/imewlconverter](https://github.com/studyzy/imewlconverter)
    ![](https://img.shields.io/github/v/release/studyzy/imewlconverter)
    ![](https://img.shields.io/github/license/studyzy/imewlconverter)
    ![](https://img.shields.io/github/last-commit/studyzy/imewlconverter)
