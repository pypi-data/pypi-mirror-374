import argparse
import sys
import time
from pathlib import Path
from typing import Type

from ime_utils.core.base import BaseParser


def show_progress(iterable, prefix="", suffix="", length=50, file=sys.stderr):
    """A simple progress bar for iterables"""
    count = len(iterable)
    start = time.time()

    def format_time(seconds):
        m, s = divmod(seconds, 60)
        return f"{int(m):02d}:{int(s):02d}"

    for i, item in enumerate(iterable):
        yield item
        elapsed = time.time() - start
        percent = (i + 1) / count
        filled = int(length * percent)
        bar = "█" * filled + " " * (length - filled)
        eta = (elapsed / (i + 1)) * (count - i - 1) if i > 0 else 0
        print(
            f"\r{prefix} |{bar}| {i + 1}/{count} "
            f"[{format_time(elapsed)}<{format_time(eta)}, "
            f"{percent:.1%}] {suffix}",
            end="",
            file=file,
            flush=True,
        )
    print(file=file)  # New line after completion


class ParserFactory:
    """解析器工厂"""

    def __init__(self):
        self._parsers: dict[str, Type[BaseParser]] = {}

    def register_parser(self, parser_class: Type[BaseParser]) -> None:
        if hasattr(parser_class, "suffix"):
            suffix = parser_class.suffix
            self._parsers[suffix] = parser_class

    def get_parser(self, suffix: str) -> BaseParser:
        """根据文件获取合适的解析器"""
        suffix = suffix.lstrip(".").lower()
        if suffix in self._parsers:
            return self._parsers[suffix]

        raise ValueError(f"不支持的文件格式: {suffix}")

    def get_suffixes(self) -> list[str]:
        return list(self._parsers.keys())


class ParserToolkit:
    """输入法词库工具：读取并保存"""

    def __init__(self):
        self.factory = ParserFactory()
        self._register_parsers()

    def _register_parsers(self):
        # 动态导入并注册所有解析器
        from ime_utils.parser import (
            BaiduMobileParser,
            BaiduParser,
            HuayuParser,
            QQParser,
            QQV1Parser,
            SogouParser,
        )

        parsers = [
            SogouParser,
            BaiduParser,
            BaiduMobileParser,
            QQParser,
            QQV1Parser,
            HuayuParser,
        ]
        for parser in parsers:
            self.factory.register_parser(parser)

    def process(self, file_path: Path, save_file: Path, keep_error: bool) -> bool:
        parser = self.get_parser(file_path)
        if parser.parse(file_path):
            return parser.save_data(save_file, keep_error)
        return False

    def get_parser(self, file_path: Path) -> BaseParser:
        return self.factory.get_parser(file_path.suffix)()

    @property
    def suffixes(self) -> list[str]:
        return self.factory.get_suffixes()


def process(file_names: str, input_dir: str, output_dir: str, keep_error: bool) -> None:
    toolkit = ParserToolkit()
    files: list[Path] = []
    if file_names:
        for file_name in file_names.split(","):
            files.append(Path(file_name.strip()))
    if input_dir:
        files += Path(input_dir).glob("*.*")

    # 过滤
    suffixes = toolkit.suffixes
    groups = {}
    for file_names in files:
        suffix = file_names.suffix.lstrip(".").lower()
        if file_names.exists() and suffix in suffixes:
            if suffix not in groups:
                groups[suffix] = []
            groups[suffix].append(file_names)
    count = sum(map(len, groups.values()))
    print(f"待处理文件 = {len(files)}，过滤词库文件后 = {count}")
    if count == 0:
        print("文件不存在或者后缀格式不支持，请尝试其他文件")
        return
    print(f"解析文件将保存到 {output_dir}")

    stats = {}
    ignores = {}
    for suffix, file_list in groups.items():
        print(f"正在处理：词库 = {suffix}")
        stats[suffix] = 0
        ignores[suffix] = 0
        for file_names in show_progress(file_list, f"处理 {suffix:5}", "进度"):
            save_file = Path(output_dir, f"{file_names.stem}.txt")
            if save_file.exists():
                # print(f"忽略文件：{file}, 输出文件已存在")
                ignores[suffix] += 1
                continue
            if toolkit.process(file_names, save_file, keep_error):
                stats[suffix] += 1
    print(stats, ignores)
    result = "\n".join(
        [
            "文件类型\t总数 / 成功 / 忽略",
            "-" * 40,
        ]
        + [
            f"文件（{suffix}）\t{len(file_list):4d} / {stats[suffix]:4d} / {ignores[suffix]:4d}"
            for suffix, file_list in groups.items()
        ]
        + [
            "=" * 40,
            f"结果合计\t{count:4d} / {sum(stats.values()):4d} / {sum(ignores.values()):4d}",
        ]
    )
    print(f"处理完成：\n\n{result}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="输入法词库解析工具")
    parser.add_argument("-f", "--file", type=str, default=None, help="词库文件（逗号分隔多个文件）")
    parser.add_argument("-d", "--dir", type=str, default=None, help="词库目录")
    parser.add_argument("-o", "--out", type=str, default=".", help="保存目录")
    parser.add_argument("-e", "--keep-error", action="store_true", help="保留解析异常词语")

    args = parser.parse_args()
    print(f"args = {args}")
    if not args.file and not args.dir:
        parser.print_help()
        print("\n 请配置 -f 指定词库文件，或 -d 指定词库目录")
        return 1

    process(args.file, args.dir, args.out, args.keep_error)

    return 0


if __name__ == "__main__":
    sys.exit(main())
