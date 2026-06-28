"""
测试 API 文档生成脚本

验证 scripts/generate_api_docs.py 的功能
"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestGenerateModuleDocs:
    """测试 generate_module_docs 函数"""

    def test_generates_docs_for_existing_module(self, temp_dir):
        """应该能为存在的模块生成文档"""
        from scripts.generate_api_docs import generate_module_docs

        # 使用实际的 core.state 模块
        output_path = temp_dir / "core_state.md"

        result = generate_module_docs("core.state", str(output_path))

        assert result is True
        assert output_path.exists()

    def test_creates_output_directory_if_not_exists(self, temp_dir):
        """如果输出目录不存在应该创建"""
        from scripts.generate_api_docs import generate_module_docs

        output_path = temp_dir / "api" / "state.md"

        result = generate_module_docs("core.state", str(output_path))

        assert result is True
        assert output_path.exists()
        assert (temp_dir / "api").is_dir()

    def test_returns_false_for_nonexistent_module(self, temp_dir):
        """对于不存在的模块应该返回 False"""
        from scripts.generate_api_docs import generate_module_docs

        output_path = temp_dir / "nonexistent.md"

        result = generate_module_docs("nonexistent.module", str(output_path))

        assert result is False
        assert not output_path.exists()

    def test_includes_class_definitions(self, temp_dir):
        """生成的文档应该包含类定义"""
        from scripts.generate_api_docs import generate_module_docs

        output_path = temp_dir / "core_state.md"

        generate_module_docs("core.state", str(output_path))

        content = output_path.read_text(encoding="utf-8")
        # core.state 应该有 AgentState
        assert "AgentState" in content

    def test_includes_function_signatures(self, temp_dir):
        """生成的文档应该包含函数签名"""
        from scripts.generate_api_docs import generate_module_docs

        output_path = temp_dir / "checkpoint.md"

        generate_module_docs("core.checkpoint", str(output_path))

        content = output_path.read_text(encoding="utf-8")
        # checkpoint 应该有函数定义
        assert "def" in content or "class" in content


class TestGenerateAllApiDocs:
    """测试 generate_all_api_docs 函数"""

    def test_generates_docs_for_all_modules(self, temp_dir):
        """应该为所有模块生成文档"""
        from scripts.generate_api_docs import generate_all_api_docs

        result = generate_all_api_docs(str(temp_dir))

        # 返回的应该是文件列表且不为空
        assert isinstance(result, list)
        assert len(result) > 0

        # 检查生成的文件
        api_dir = Path(temp_dir)
        assert (api_dir / "core.md").exists()
        assert (api_dir / "workflows.md").exists()

    def test_returns_list_of_generated_files(self, temp_dir):
        """应该返回生成的文件列表"""
        from scripts.generate_api_docs import generate_all_api_docs

        files = generate_all_api_docs(str(temp_dir))

        assert isinstance(files, list)
        assert len(files) > 0


class TestExtractDocstring:
    """测试 extract_docstring 函数"""

    def test_extracts_function_docstring(self):
        """应该能提取函数的 docstring"""
        from scripts.generate_api_docs import extract_docstring

        def test_function():
            """这是测试函数的文档"""
            pass

        doc = extract_docstring(test_function)
        assert "测试函数的文档" in doc

    def test_returns_empty_for_no_docstring(self):
        """对于没有 docstring 的函数应该返回空字符串"""
        from scripts.generate_api_docs import extract_docstring

        def no_doc_function():
            pass

        doc = extract_docstring(no_doc_function)
        assert doc == ""


class TestFormatSignature:
    """测试 format_signature 函数"""

    def test_formats_simple_function_signature(self):
        """应该能格式化简单的函数签名"""
        from scripts.generate_api_docs import format_signature

        def simple_func(arg1: str, arg2: int) -> bool:
            pass

        sig = format_signature(simple_func)
        assert "arg1" in sig
        assert "arg2" in sig

    def test_formats_class_method_signature(self):
        """应该能格式化类方法签名"""
        from scripts.generate_api_docs import format_signature

        class TestClass:
            def method(self, value: str) -> None:
                pass

        sig = format_signature(TestClass.method)
        assert "value" in sig
