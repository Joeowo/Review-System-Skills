"""
配置管理模块

使用 Pydantic Settings 实现类型安全的配置管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional, Literal


class LLMConfig(BaseSettings):
    """LLM 配置"""
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    api_key: str = Field(default="")
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = 2000


class CheckpointConfig(BaseSettings):
    """Checkpoint 配置"""
    model_config = SettingsConfigDict(
        env_prefix="CHECKPOINT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    db_path: str = "agent_framework/checkpoints.db"
    cleanup_days: int = Field(default=30, ge=1)


class LogConfig(BaseSettings):
    """日志配置"""
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    level: str = "INFO"
    file_path: Optional[str] = "agent_framework/logs/agent.log"
    rotation: str = "100 MB"
    retention: str = "30 days"


class AgentConfig(BaseSettings):
    """Agent 框架总配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AGENT_",
        extra="ignore"
    )

    # 嵌套配置使用 DefaultFactory
    llm: LLMConfig = Field(default_factory=LLMConfig)
    checkpoint: CheckpointConfig = Field(default_factory=CheckpointConfig)
    log: LogConfig = Field(default_factory=LogConfig)

    confirmation_level: Literal["minimal", "balanced", "thorough"] = "balanced"
    max_retries: int = Field(default=3, ge=1)
    timeout_seconds: int = Field(default=60, ge=1)


# 全局配置实例（延迟加载）
def get_config() -> AgentConfig:
    """获取全局配置实例"""
    return AgentConfig()


config = get_config()
