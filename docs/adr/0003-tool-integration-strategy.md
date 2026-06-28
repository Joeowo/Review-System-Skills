# ADR 0003: 模块集成方式 - 直接导入

**状态**: 已采纳
**日期**: 2026-06-28
**决策者**: Agent 框架设计团队

---

## 上下文

现有模块（AutoResearch、review_agent）需要被封装为 LangChain Tools。

有两种集成方式：

**方式A: 直接导入**
```python
from AutoResearch.autoresearch.main import research_single

def auto_research_tool(topic: str) -> str:
    return research_single(topic, "技术", "comprehensive")
```

**方式B: subprocess 调用**
```python
import subprocess

def auto_research_tool(topic: str) -> str:
    result = subprocess.run([
        "python", "-m", "autoresearch", topic
    ], capture_output=True)
    return result.stdout
```

---

## 决策

采用 **方式A: 直接导入** 作为模块集成方式。

---

## 理由

### 支持直接导入的论据

1. **性能**: 无进程启动开销，调用更快
2. **类型安全**: 可访问类型注解，IDE 支持
3. **错误处理**: Python 异常而非返回码解析
4. **接口灵活性**: 可访问内部接口，不限于 CLI
5. **调试友好**: 可直接调试被调用代码

### 反对 subprocess 的论据

1. **性能开销**: 每次调用启动新进程
2. **错误处理复杂**: 需要解析 stdout/stderr 和返回码
3. **类型丢失**: 字符串输入输出，无类型信息
4. **调试困难**: 无法直接调试被调用模块

### subprocess 的适用场景

- **跨语言调用**: 调用非 Python 模块
- **沙箱隔离**: 需要进程隔离的场景
- **版本切换**: 需要不同 Python 版本

本项目不涉及以上场景。

---

## 后果

### 正面影响

- Tool 调用延迟降低
- 错误处理更精确
- 代码可读性更好
- 测试更容易（可 mock 内部函数）

### 负面影响

- **耦合度**: 直接依赖内部接口，接口变化需要同步更新
- **导入依赖**: Agent 框架启动时需要加载所有被调用模块

### 缓解措施

- **稳定接口**: 与被调用模块约定稳定接口
- **抽象层**: 创建适配器层，隔离变化
- **延迟导入**: 按需导入模块，减少启动时间

---

## 实施细节

### Tool 封装示例

```python
# tools/autoresearch_tools.py
from langchain_core.tools import tool
from AutoResearch.autoresearch.main import research_single, research_deep

@tool
def research_single_tool(topic: str, research_type: str = "通用", depth: str = "comprehensive") -> str:
    """单次研究模式
    
    Args:
        topic: 研究主题
        research_type: 研究类型
        depth: 研究深度
    
    Returns:
        报告文件路径
    """
    try:
        return research_single(topic, research_type, depth)
    except Exception as e:
        return f"研究失败: {str(e)}"

@tool
def research_deep_tool(topic: str, research_type: str = "通用") -> str:
    """深度研究模式"""
    try:
        return research_deep(topic, research_type)
    except Exception as e:
        return f"深度研究失败: {str(e)}"
```

### 适配器层

```python
# tools/adapters.py
"""
适配器层，隔离内部接口变化
"""

class AutoResearchAdapter:
    """AutoResearch 适配器"""
    
    @staticmethod
    def single(topic: str, research_type: str = "通用", depth: str = "comprehensive") -> dict:
        """单次研究，返回结构化结果"""
        from AutoResearch.autoresearch.main import research_single
        
        filepath = research_single(topic, research_type, depth)
        
        # 解析报告文件，返回结构化数据
        return {
            "status": "success",
            "filepath": filepath,
            "topic": topic,
        }
```

---

## 相关决策

- [ADR 0001: 双状态并行管理策略](0001-dual-state-management.md)

---

**文档版本**: 1.0
