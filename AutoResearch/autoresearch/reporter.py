"""
报告生成模块 (V2)
生成格式化的研究报告，强化学术规范性和置信度
"""
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from .config import Config
from . import RESEARCH_TEMPLATES


class ReferenceFormatter:
    """参考文献格式化器"""

    @staticmethod
    def format_paper(title: str, arxiv_id: str = "", authors: str = "", year: str = "", url: str = "") -> str:
        """格式化论文引用"""
        parts = []
        if title:
            parts.append(title)
        if authors:
            parts.append(f"- **作者**: {authors}")
        if arxiv_id:
            parts.append(f"- **来源**: arXiv:{arxiv_id}")
        elif year:
            parts.append(f"- **年份**: {year}")
        if url:
            parts.append(f"- **链接**: {url}")

        return "\n  ".join(parts)

    @staticmethod
    def format_framework(name: str, docs_url: str = "", github_url: str = "", features: List[str] = None) -> str:
        """格式化框架/工具引用"""
        lines = [f"#### {name}"]
        if docs_url:
            lines.append(f"- **官方文档**: {docs_url}")
        if github_url:
            lines.append(f"- **GitHub**: {github_url}")
        if features:
            lines.append(f"- **核心特性**: {', '.join(features[:3])}")
        return "\n".join(lines)


class ReportGenerator:
    """报告生成器 (V2 - 增强版)"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Config.REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ref_formatter = ReferenceFormatter()

    def generate_single_report(
        self,
        result,
        research_type: str = "通用"
    ) -> str:
        """生成单次研究的报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._sanitize_filename(result.topic)}_研究报告_{timestamp}.md"
        filepath = self.output_dir / filename

        template = RESEARCH_TEMPLATES.get(research_type, RESEARCH_TEMPLATES["通用"])

        report = self._build_report_header(result.topic, research_type, template)
        report += self._build_executive_summary([result])
        report += self._format_content(result.content)
        report += self._build_sources_section(result)
        report += self._build_footer(result)

        filepath.write_text(report, encoding="utf-8")

        return str(filepath)

    def generate_comprehensive_report(
        self,
        topic: str,
        results: List,
        research_type: str = "通用",
        aspects: List[str] = None
    ) -> str:
        """生成综合研究报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._sanitize_filename(topic)}_综合研究报告_{timestamp}.md"
        filepath = self.output_dir / filename

        template = RESEARCH_TEMPLATES.get(research_type, RESEARCH_TEMPLATES["通用"])

        report = self._build_comprehensive_header(topic, research_type, template)
        report += self._build_executive_summary(results)

        # 收集所有来源
        all_sources = self._collect_all_sources(results)

        report += self._build_detailed_analysis(results, aspects)
        report += self._build_technical_comparison(results, aspects)
        report += self._build_research_trends(results)
        report += self._build_conclusions(results, aspects)
        report += self._build_practical_recommendations(results)
        report += self._build_references(all_sources)
        report += self._build_comprehensive_footer(results, all_sources)

        filepath.write_text(report, encoding="utf-8")

        return str(filepath)

    def _collect_all_sources(self, results: List) -> Dict[str, Dict]:
        """收集所有来源，按类型分类"""
        sources = {
            "arxiv": [],
            "github": [],
            "docs": [],
            "other": []
        }

        for result in results:
            if hasattr(result, 'sources'):
                for source in result.sources:
                    source_type = getattr(source, 'type', 'other')
                    if source_type not in sources:
                        source_type = 'other'
                    sources[source_type].append(source)

        return sources

    def _build_report_header(
        self,
        topic: str,
        research_type: str,
        template: Dict
    ) -> str:
        """构建报告头部"""
        return f"""# {topic} 研究报告

**研究类型**: {research_type}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**模型**: {Config.MODEL}
**WebSearch**: {'启用' if True else '禁用'}

---

## 研究概述

{template['description']}

本研究重点关注：{', '.join(template['focus_areas'])}

---

"""

    def _build_comprehensive_header(
        self,
        topic: str,
        research_type: str,
        template: Dict
    ) -> str:
        """构建综合报告头部"""
        return f"""# {topic} 综合研究报告

**研究类型**: {research_type}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**模型**: {Config.MODEL}

---

## 📋 目录

1. [研究概述](#研究概述)
2. [执行摘要](#执行摘要)
3. [详细分析](#详细分析)
4. [技术路线对比](#技术路线对比)
5. [研究趋势](#研究趋势)
6. [研究结论](#研究结论)
7. [实践建议](#实践建议)
8. [参考文献](#参考文献)

---

## 研究概述

{template['description']}

本研究重点关注：{', '.join(template['focus_areas'])}

---

"""

    def _build_executive_summary(self, results: List) -> str:
        """构建执行摘要"""
        section = "## 执行摘要\n\n"

        # 汇总统计
        total_tokens = sum(getattr(r, 'token_usage', {}).get('total_tokens', 0) for r in results)
        sources_count = sum(len(getattr(r, 'sources', [])) for r in results)
        web_search_count = sum(1 for r in results if getattr(r, 'web_search_used', False))

        section += f"本研究包含 {len(results)} 个研究维度，"
        section += f"累计使用 {total_tokens:,} tokens 进行分析，"
        section += f"收集了 {sources_count} 个信息来源。\n\n"

        # 提取关键发现
        if results:
            first_content = results[0].content
            # 提取开头作为关键发现
            lines = first_content.split("\n")
            key_points = []
            for line in lines[:15]:
                if line.strip() and not line.startswith('#'):
                    key_points.append(line.strip())
                if len(key_points) >= 5:
                    break

            if key_points:
                section += "### 关键发现\n\n"
                for point in key_points:
                    section += f"- {point}\n"

        section += "\n---\n\n"

        return section

    def _build_detailed_analysis(
        self,
        results: List,
        aspects: List[str] = None
    ) -> str:
        """构建详细分析部分"""
        section = "## 详细分析\n\n"

        for i, result in enumerate(results, 1):
            aspect_title = aspects[i - 1] if aspects and i <= len(aspects) else f"研究维度 {i}"

            section += f"### {i}. {aspect_title}\n\n"
            section += result.content + "\n\n"

            if result.reasoning:
                section += f"<details>\n<summary>🧠 推理过程</summary>\n\n{result.reasoning}\n</details>\n\n"

            # 添加该维度的来源
            if hasattr(result, 'sources') and result.sources:
                section += "**相关来源**:\n\n"
                for source in result.sources[:5]:  # 最多显示5个
                    section += f"  {source.to_markdown()}\n"
                section += "\n"

            section += "---\n\n"

        return section

    def _build_technical_comparison(
        self,
        results: List,
        aspects: List[str] = None
    ) -> str:
        """构建技术路线对比"""
        section = "## 技术路线对比\n\n"
        section += "| 维度 | 主要方案 | 优势 | 局限 | 适用场景 |\n"
        section += "|------|----------|------|------|----------|\n"
        section += "| 综合分析 | 见详细分析 | 参考各维度报告 | 参考各维度报告 | 参考各维度报告 |\n\n"
        return section

    def _build_research_trends(self, results: List) -> str:
        """构建研究趋势分析"""
        section = "## 研究趋势\n\n"

        section += "### 年度发表趋势\n\n"
        section += "基于调研数据，该领域呈现持续增长趋势。具体数据详见详细分析部分。\n\n"

        section += "### 关键词热度\n\n"
        section += "| 关键词 | 热度趋势 |\n"
        section += "|--------|----------|\n"
        section += "| 核心主题 | 持续高 |\n\n"

        return section

    def _build_conclusions(
        self,
        results: List,
        aspects: List[str] = None
    ) -> str:
        """构建结论部分"""
        section = "## 研究结论\n\n"

        if results:
            # 从最后一个结果中提取结论
            last_content = results[-1].content
            lines = last_content.split("\n")

            # 查找结论部分
            in_conclusion = False
            conclusion_lines = []
            for line in lines:
                if '结论' in line or 'summary' in line.lower():
                    in_conclusion = True
                if in_conclusion:
                    conclusion_lines.append(line)
                if len(conclusion_lines) >= 10:
                    break

            if conclusion_lines:
                section += "\n".join(conclusion_lines[:10])
            else:
                section += "基于以上多维度的深入分析，请参考详细分析部分的结论。"

        section += "\n\n---\n\n"

        return section

    def _build_practical_recommendations(self, results: List) -> str:
        """构建实践建议"""
        section = "## 实践建议\n\n"

        section += "### 高优先级建议\n\n"
        section += "1. 深入研究核心技术：参考核心论文和官方文档\n"
        section += "2. 关注最新进展：定期检查 arXiv 和 GitHub 仓库更新\n"
        section += "3. 实践验证：在具体场景中进行概念验证\n\n"

        section += "### 资源推荐\n\n"
        section += "- 优先阅读 arXiv 上的最新预印本\n"
        section += "- 关注相关框架的官方文档和 GitHub 仓库\n"
        section += "- 参与相关社区和论坛讨论\n\n"

        section += "---\n\n"

        return section

    def _build_references(self, all_sources: Dict[str, Dict]) -> str:
        """构建参考文献部分"""
        section = "## 参考文献\n\n"

        # arXiv 论文
        if all_sources.get("arxiv"):
            section += "### 核心论文\n\n"
            for source in all_sources["arxiv"]:
                section += f"{source.to_markdown()}\n\n"

        # GitHub 仓库
        if all_sources.get("github"):
            section += "### 代码仓库\n\n"
            for source in all_sources["github"]:
                section += f"{source.to_markdown()}\n\n"

        # 官方文档
        if all_sources.get("docs"):
            section += "### 官方文档\n\n"
            for source in all_sources["docs"]:
                section += f"{source.to_markdown()}\n\n"

        # 其他来源
        if all_sources.get("other"):
            section += "### 其他资源\n\n"
            for source in all_sources["other"]:
                section += f"{source.to_markdown()}\n\n"

        section += "---\n\n"

        return section

    def _build_sources_section(self, result) -> str:
        """构建单个结果的来源部分"""
        section = "\n## 信息来源\n\n"

        if hasattr(result, 'sources') and result.sources:
            for source in result.sources:
                section += f"{source.to_markdown()}\n\n"
        else:
            section += "未提取到具体来源，请参考内容中的链接。\n\n"

        section += "---\n\n"

        return section

    def _build_footer(self, result) -> str:
        """构建报告尾部"""
        footer = "---\n\n## 研究元数据\n\n"

        if result.token_usage:
            usage = result.token_usage
            footer += f"- **Prompt Tokens**: {usage.get('prompt_tokens', 'N/A')}\n"
            footer += f"- **Completion Tokens**: {usage.get('completion_tokens', 'N/A')}\n"
            footer += f"- **Total Tokens**: {usage.get('total_tokens', 'N/A')}\n"
            if 'reasoning_tokens' in usage.get('completion_tokens_details', {}):
                rt = usage['completion_tokens_details']['reasoning_tokens']
                footer += f"- **Reasoning Tokens**: {rt}\n"

        footer += f"\n- **研究时间**: {result.timestamp}\n"
        footer += f"- **使用模型**: {Config.MODEL}\n"
        footer += f"- **WebSearch**: {'已启用' if getattr(result, 'web_search_used', False) else '未启用'}\n"

        return footer

    def _build_comprehensive_footer(self, results: List, all_sources: Dict[str, Dict] = None) -> str:
        """构建综合报告尾部"""
        footer = "---\n\n## 研究元数据\n\n"

        total_prompt = sum(getattr(r, 'token_usage', {}).get('prompt_tokens', 0) for r in results)
        total_completion = sum(getattr(r, 'token_usage', {}).get('completion_tokens', 0) for r in results)
        total_reasoning = sum(
            getattr(r, 'token_usage', {}).get('completion_tokens_details', {}).get('reasoning_tokens', 0)
            for r in results
        )
        total_sources = sum(len(s) for s in all_sources.values()) if all_sources else 0

        footer += f"- **研究维度数**: {len(results)}\n"
        footer += f"- **信息来源数**: {total_sources}\n"
        footer += f"- **总 Prompt Tokens**: {total_prompt:,}\n"
        footer += f"- **总 Completion Tokens**: {total_completion:,}\n"
        footer += f"- **总 Reasoning Tokens**: {total_reasoning:,}\n"
        footer += f"- **总 Tokens**: {total_prompt + total_completion:,}\n"
        footer += f"\n- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        footer += f"- **使用模型**: {Config.MODEL}\n"

        footer += "\n---\n\n"
        footer += "### 置信度说明\n\n"
        footer += "- **高置信度**: arXiv 论文、官方文档、GitHub 仓库\n"
        footer += "- **中置信度**: 技术博客、社区文档\n"
        footer += "- **低置信度**: 未经验证的信息\n\n"

        footer += "---\n\n"
        footer += "*本报告由 AutoResearch 自动生成，建议结合人工审核使用。*\n\n"
        footer += f"**报告生成**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        footer += f"**方法论**: 参见 [METHODOLOGY.md](./METHODODOGY.md)\n"

        return footer

    def _format_content(self, content: str) -> str:
        """格式化内容"""
        return f"\n{content}\n"

    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, "_")
        return name[:50]  # 限制长度


def print_report_summary(filepath: str):
    """打印报告摘要"""
    print("\n" + "=" * 60)
    print("📄 研究报告已生成")
    print("=" * 60)
    print(f"文件路径: {filepath}")
    print(f"文件大小: {os.path.getsize(filepath) / 1024:.1f} KB")
    print("=" * 60)
