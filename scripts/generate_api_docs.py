"""
API 文档生成脚本

自动从代码生成 API 文档
"""

import sys
import inspect
from pathlib import Path
from typing import Any, List, Optional


# 添加 agent_framework 到路径
framework_root = Path(__file__).parent.parent / "agent_framework"
if str(framework_root) not in sys.path:
    sys.path.insert(0, str(framework_root))


def extract_docstring(obj: Any) -> str:
    """提取对象的 docstring

    Args:
        obj: Python 对象

    Returns:
        Docstring 内容，如果没有则返回空字符串
    """
    return inspect.getdoc(obj) or ""


def format_signature(func: Any) -> str:
    """格式化函数签名

    Args:
        func: 函数对象

    Returns:
        格式化的签名字符串
    """
    try:
        sig = inspect.signature(func)
        return str(sig)
    except (ValueError, TypeError):
        return ""


def generate_class_doc(cls: type, level: int = 0) -> str:
    """生成类的文档

    Args:
        cls: 类对象
        level: 标题层级

    Returns:
        Markdown 格式的类文档
    """
    indent = " " * 4
    lines = []

    # 类标题
    header = "#" * (level + 2)
    lines.append(f"{header} class {cls.__name__}")
    lines.append("")

    # Docstring
    doc = extract_docstring(cls)
    if doc:
        lines.append(f"{indent}{doc}")
        lines.append("")

    # 方法列表
    methods = []
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        if not name.startswith("_"):
            methods.append((name, method))

    if methods:
        lines.append(f"{indent}**方法**:")
        lines.append("")

        for name, method in methods:
            sig = format_signature(method)
            doc = extract_docstring(method)

            lines.append(f"{indent}- `{name}{sig}`")
            if doc:
                lines.append(f"{indent}  - {doc.splitlines()[0] if doc else ''}")
        lines.append("")

    return "\n".join(lines)


def generate_function_doc(func: Any, level: int = 0) -> str:
    """生成函数的文档

    Args:
        func: 函数对象
        level: 标题层级

    Returns:
        Markdown 格式的函数文档
    """
    indent = " " * 4
    lines = []

    # 函数标题
    header = "#" * (level + 2)
    name = func.__name__
    sig = format_signature(func)

    lines.append(f"{header} {name}{sig}")
    lines.append("")

    # Docstring
    doc = extract_docstring(func)
    if doc:
        lines.append(f"{indent}{doc}")
        lines.append("")

    return "\n".join(lines)


def generate_module_docs(module_name: str, output_path: str) -> bool:
    """生成模块文档

    Args:
        module_name: 模块名称（如 "core.state"）
        output_path: 输出文件路径

    Returns:
        是否成功生成
    """
    try:
        # 导入模块
        parts = module_name.split(".")
        module = __import__(module_name)

        for part in parts[1:]:
            module = getattr(module, part)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        lines = []

        # 标题
        lines.append(f"# API: {module_name}")
        lines.append("")
        lines.append(f"模块: `{module.__name__}`")
        lines.append("")

        # 模块 docstring
        module_doc = extract_docstring(module)
        if module_doc:
            lines.append("## 描述")
            lines.append("")
            lines.append(module_doc)
            lines.append("")

        # 类列表
        classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                if not name.startswith("_"):
                    classes.append((name, obj))

        # 函数列表
        functions = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                if not name.startswith("_"):
                    functions.append((name, obj))

        # 生成类文档
        if classes:
            lines.append("## 类")
            lines.append("")
            for name, cls in classes:
                lines.append(generate_class_doc(cls, level=2))

        # 生成函数文档
        if functions:
            lines.append("## 函数")
            lines.append("")
            for name, func in functions:
                lines.append(generate_function_doc(func, level=2))

        # 写入文件
        output_file.write_text("\n".join(lines), encoding="utf-8")
        return True

    except Exception as e:
        print(f"Error generating docs for {module_name}: {e}")
        return False


def generate_all_api_docs(output_dir: str) -> List[str]:
    """生成所有 API 文档

    Args:
        output_dir: 输出目录

    Returns:
        生成的唯一文件列表
    """
    # 定义要生成文档的模块
    modules = [
        ("core.state", "core.md"),
        ("core.checkpoint", "core.md"),
        ("core.exceptions", "core.md"),
        ("workflows.f1_learning_research", "workflows.md"),
        ("workflows.f2_qa_enhanced", "workflows.md"),
        ("workflows.f3_academic_writing", "workflows.md"),
        ("workflows.f4_review_planning", "workflows.md"),
        ("config.settings", "config.md"),
    ]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = set()

    for module_name, filename in modules:
        file_path = output_path / filename

        # 生成模块文档
        success = generate_module_docs(module_name, str(file_path))

        if success:
            generated_files.add(str(file_path))

    return sorted(list(generated_files))


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成 API 文档")
    parser.add_argument(
        "--module",
        help="指定模块名称（如 core.state）"
    )
    parser.add_argument(
        "--output",
        default="docs/api",
        help="输出目录"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="生成所有模块的文档"
    )

    args = parser.parse_args()

    if args.all:
        files = generate_all_api_docs(args.output)
        print(f"生成 {len(files)} 个文件:")
        for f in files:
            print(f"  - {f}")
    elif args.module:
        output_path = Path(args.output) / f"{args.module.replace('.', '_')}.md"
        success = generate_module_docs(args.module, str(output_path))
        if success:
            print(f"✓ 生成文档: {output_path}")
        else:
            print(f"✗ 生成失败: {args.module}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
