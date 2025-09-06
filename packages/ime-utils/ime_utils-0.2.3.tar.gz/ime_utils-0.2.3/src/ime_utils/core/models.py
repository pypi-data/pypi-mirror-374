import re
from dataclasses import dataclass


@dataclass
class WordEntry:
    """词库文件单个词结构"""

    word: str  # 词语
    coding: list[str]  # 编码：一般为拼音
    weight: int  # 词频/权重
    is_pinyin: bool = True  # 是否拼音编码
    is_error: bool = False  # 是否解析异常

    def to_str(
        self, separator: str = "\t", coding_separator: str = " ", keep_weight: bool = True
    ) -> str:
        coding_str = self.coding_to_str(coding_separator)
        weight = self.weight if self.weight and self.weight > 0 else 0
        data = [self.word, coding_str] + ([weight] if keep_weight else [])
        return separator.join(map(str, data))

    def coding_to_str(self, coding_separator: str = " ") -> str:
        return coding_separator.join(self.coding)


@dataclass
class DictMeta:
    """词库文件元信息：词库名等配置内容"""

    file: str = ""  # 词库文件名
    name: str = ""  # 词库名
    category: str = ""  # 词库分类
    version: str = ""  # 版本
    description: str = ""  # 描述信息
    author: str = ""  # 作者
    examples: list[str] = list()  # 词库示例
    count: int | str = ""  # 词条数量（可能来自词库文件内置数据）
    count_actual: int = 0  # 实际解析统计词条数据
    count_error: int = 0  # 实际解析统计词条数据

    def to_str(self, extra: str = "", keep_all: bool = False) -> str:
        """
        keep_all: 保留空白字段
        """
        prefix = "# "
        separator = ": "
        words = ""
        if self.examples:
            words = " ".join([re.sub(r"\s+", "", v) for v in self.examples])
        info_list: list[list[str]] = [
            ["文件名称", self.file],
            ["词库名称", self.name],
            ["词库分类", self.category],
            ["词库版本", self.version],
            ["词库作者", self.author],
            ["词库描述", self.description],
            ["词条样例", words],
            ["词条数量", str(self.count)],
            ["解析词数", str(self.count_actual)],
            ["解析异常", str(self.count_error)],
        ]
        info_list2: list[list[str]] = [
            [key, re.sub(r"[\r\n\s，]+", " ", value).strip()]
            for key, value in info_list
            if keep_all or value or key in ["词条数量", "解析词数"]
        ]
        info_text = ["".join([prefix, key, separator, value]) for key, value in info_list2]
        if extra:
            info_text.append(extra)
        return "\n".join(info_text)


@dataclass
class DictCell:
    """词库文件"""

    metadata: DictMeta
    words: list[WordEntry] = []


@dataclass
class DictField:
    start: int
    end: int | None = None


@dataclass
class DictStruct:
    """词库文件结构分段"""

    name: DictField = DictField(0)  # 词库名位置
    category: DictField = DictField(0)  # 词库分类
    version: DictField = DictField(0)  # 版本
    description: DictField = DictField(0)  # 描述信息
    author: DictField = DictField(0)  # 作者
    examples: DictField = DictField(0)  # 词库示例
    count: DictField = DictField(0)  # 词条数量
    code_len: DictField = DictField(0)  # 编码映射表长度
    code_map: DictField = DictField(0)  # 编码映射表（一般为拼音）
    words: DictField = DictField(0)  # 词语列表
    extra: DictField = DictField(0)  # 额外字段

    def init_end(self, var_list: list[DictField]):
        # 根据后一字段补全end
        n = len(var_list)
        for i in range(1, n):
            if var_list[i]:
                var_list[i - 1].end = var_list[i].start
