"""
AutoResearch 功能测试
演示强化置信度的功能
"""
from autoresearch.researcher import SourceExtractor, Source
from autoresearch.reporter import ReferenceFormatter


def test_source_extraction():
    """测试来源提取"""
    print("=" * 60)
    print("测试 1: 来源提取功能")
    print("=" * 60)

    test_content = """
    # Agent Skills 研究

    根据 **COCONUT** (arXiv:2412.06769) 的研究，潜在空间推理是一个重要方向。

    另一篇重要论文是 [Interlat](https://arxiv.org/html/2511.09149v1) 关于 Agent 间通信。

    相关代码可以在 [GitHub](https://github.com/facebookresearch/coconut) 找到。

    官方文档见 https://docs.langchain.com/
    """

    extractor = SourceExtractor()
    sources = extractor.extract_sources_from_content(test_content)

    print(f"\n从内容中提取到 {len(sources)} 个来源：\n")
    for source in sources:
        print(f"  📄 {source.title}")
        print(f"     类型: {source.type}")
        print(f"     置信度: {source.confidence}")
        print(f"     arXiv ID: {source.arxiv_id or 'N/A'}")
        print(f"     链接: {source.url}")
        print()


def test_reference_formatting():
    """测试参考文献格式化"""
    print("\n" + "=" * 60)
    print("测试 2: 参考文献格式化")
    print("=" * 60)

    formatter = ReferenceFormatter()

    # 测试论文格式化
    paper = formatter.format_paper(
        title="Agent Skills for Large Language Models",
        arxiv_id="2602.12430",
        authors="Xu, R. & Yan, Y.",
        year="2026",
        url="https://arxiv.org/abs/2602.12430"
    )

    print("\n📚 论文引用格式：")
    print(paper)

    # 测试框架格式化
    framework = formatter.format_framework(
        name="LangGraph",
        docs_url="https://docs.langchain.com/",
        github_url="https://github.com/langchain-ai/langgraph",
        features=["状态图编排", "多Agent协作", "实时监控"]
    )

    print("\n🔧 框架引用格式：")
    print(framework)


def test_confidence_classification():
    """测试置信度分类"""
    print("\n" + "=" * 60)
    print("测试 3: 置信度自动分类")
    print("=" * 60)

    test_urls = [
        ("https://arxiv.org/abs/2412.06769", "arXiv 论文"),
        ("https://github.com/langchain-ai/langgraph", "GitHub 仓库"),
        ("https://docs.langchain.com/", "官方文档"),
        ("https://blog.example.com/post", "技术博客"),
        ("https://example.com/random", "未知来源"),
    ]

    extractor = SourceExtractor()

    print("\nURL 类型自动分类：\n")
    for url, description in test_urls:
        source_type = extractor.classify_url(url)
        confidence = 'high' if source_type in ['arxiv', 'github', 'docs'] else 'medium'
        print(f"  {description:20} → 类型: {source_type:10} | 置信度: {confidence}")


def main():
    """运行所有测试"""
    print("\n" + "🚀 " + "AutoResearch V2 功能测试" + "\n")

    test_source_extraction()
    test_reference_formatting()
    test_confidence_classification()

    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
    print("\nV2 版本新增功能：")
    print("  1. 🔗 来源自动提取和分类")
    print("  2. 📚 标准化的参考文献格式")
    print("  3. 🎯 置信度自动标注")
    print("  4. 📊 增强的报告结构")
    print("  5. ✅ 质量检查清单")
    print()


if __name__ == "__main__":
    main()
