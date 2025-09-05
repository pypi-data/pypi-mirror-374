import logging
from abc import ABC, abstractmethod
from pathlib import Path

from .models import DictCell, DictField, DictMeta, WordEntry
from .utils import byte2str, create_dir
from ime_utils.pinyin.syllable import PINYIN_SYLLABLES


class BaseParser(ABC):
    """
    基类: 输入法细胞词库解析成text文件
    基本流程：
    1. 判断通过文件后缀等判断文件是否符合解析格式
    2. 解析词库词表（如果有）
    3. 解析词语列表
    4. 解析词库元信息并补充额外信息
    """

    encoding: str = "utf-16le"
    suffix: str = ""
    step: int = 2
    code_map: dict[int, str] = None
    dict_cell: DictCell = None
    pinyin_syllables: set[str] = set(PINYIN_SYLLABLES)
    letters: set[str] = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    @abstractmethod
    def parse(self, file_path) -> bool:
        """解析词库文件"""

    @abstractmethod
    def check(self, data: bytes) -> bool:
        pass

    @abstractmethod
    def extract_meta(self, data: bytes) -> DictMeta:
        pass

    @abstractmethod
    def extract_words(self, data: bytes, allow_error: bool = False) -> list[WordEntry]:
        pass

    def read_data(self, file_path: Path | str) -> bytes:
        file = Path(file_path)
        if not file.exists():
            raise FileExistsError(f"{file} does not exits")
        if file.suffix[1:] != self.suffix:
            logging.warning(f"Error suffix = {file.suffix}, expect = {self.suffix}")

        with open(file, "rb") as f:
            return f.read()

    def save_data(self, save_file: Path | str, keep_error: bool = False) -> None:
        if self.dict_cell is None:
            logging.warning("Dict cell data is None")
            return

        save_file = Path(save_file)
        logging.info(f"Save to file {save_file}")
        create_dir(save_file)

        with open(save_file, "w", encoding="utf-8") as f:
            meta = self.dict_cell.metadata.to_str()
            f.write(meta.strip() + "\n\n")

            words = self.dict_cell.words
            for word in words:
                if not keep_error and word.is_error:
                    continue
                f.write(word.to_str() + "\n")

        logging.info("Save done.")

    def _decode_text(
        self, data: bytes, offset: DictField, encoding: str | None = None, is_strip: bool = True
    ) -> str:
        if not encoding:
            encoding = self.encoding
        encode_data = data[offset.start : offset.end] if offset else data
        return byte2str(encode_data, encoding, is_strip)

    def _check_pinyin(self, pinyin_list: str, allow_en: bool = True) -> bool:
        """
        判断拼音需要是否有效
        allow_en允许单个英文字母
        """
        return not all(
            [py in self.pinyin_syllables or (allow_en and py in self.letters) for py in pinyin_list]
        )


class BaseConverter(ABC):
    """
    词库格式转换 # TODO
    """
