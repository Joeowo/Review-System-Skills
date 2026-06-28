"""
文件读取工具
支持多种文件格式的读取：md, docx, doc, pdf
"""
from pathlib import Path
from typing import Optional
import logging

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx2txt
except ImportError:
    docx2txt = None

logger = logging.getLogger(__name__)


class FileReader:
    """多格式文件读取器"""

    @staticmethod
    def read(file_path: Path) -> Optional[str]:
        """
        读取文件内容，自动识别格式

        Args:
            file_path: 文件路径

        Returns:
            文件内容文本，失败返回None
        """
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return None

        suffix = file_path.suffix.lower()

        if suffix == ".md":
            return FileReader._read_markdown(file_path)
        elif suffix == ".docx":
            return FileReader._read_docx(file_path)
        elif suffix == ".doc":
            return FileReader._read_doc(file_path)
        elif suffix == ".pdf":
            return FileReader._read_pdf(file_path)
        elif suffix == ".txt":
            return file_path.read_text(encoding="utf-8", errors="ignore")
        else:
            logger.warning(f"不支持的文件格式: {suffix}")
            return None

    @staticmethod
    def _read_markdown(file_path: Path) -> Optional[str]:
        """读取Markdown文件"""
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                return file_path.read_text(encoding="gbk", errors="ignore")
            except Exception as e:
                logger.error(f"读取Markdown失败: {e}")
                return None

    @staticmethod
    def _read_docx(file_path: Path) -> Optional[str]:
        """读取docx文件"""
        if Document is None:
            logger.warning("python-docx未安装，无法读取docx")
            return None

        try:
            doc = Document(str(file_path))
            paragraphs = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            return "\n".join(paragraphs)
        except Exception as e:
            logger.error(f"读取docx失败: {e}")
            return None

    @staticmethod
    def _read_doc(file_path: Path) -> Optional[str]:
        """读取旧版doc文件"""
        # docx2txt也可以处理一些doc文件
        if docx2txt is not None:
            try:
                import io
                import sys
                from contextlib import redirect_stdout

                # 捕获docx2txt的输出
                output = io.StringIO()
                with redirect_stdout(output):
                    docx2txt.process(str(file_path))
                result = output.getvalue()

                if result:
                    return result
            except Exception as e:
                logger.debug(f"docx2txt读取失败: {e}")

        # 如果docx2txt失败，尝试使用win32com（仅Windows）
        try:
            import win32com.client
            import os

            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False

            doc = word.Documents.Open(str(file_path.absolute()))
            text = doc.Content.Text

            doc.Close(False)
            word.Quit()

            return text
        except ImportError:
            logger.warning("pywin32未安装，无法读取doc文件")
        except Exception as e:
            logger.error(f"读取doc失败: {e}")

        return None

    @staticmethod
    def _read_pdf(file_path: Path) -> Optional[str]:
        """读取PDF文件"""
        if pdfplumber is None:
            logger.warning("pdfplumber未安装，无法读取PDF")
            return None

        try:
            text_parts = []
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"读取PDF失败: {e}")
            return None

    @staticmethod
    def is_supported(file_path: Path) -> bool:
        """检查文件格式是否支持"""
        suffix = file_path.suffix.lower()
        return suffix in [".md", ".docx", ".doc", ".pdf", ".txt"]
