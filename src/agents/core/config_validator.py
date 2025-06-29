"""エージェント設定バリデーション

各エージェントの設定をバリデーションするためのPydanticモデルとユーティリティ関数を提供します。
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, validator


class AgentConfig(BaseModel):
    """エージェント共通設定"""

    interactive_mode: bool = Field(default=True, description='インタラクティブモードの有効化')
    auto_save: bool = Field(default=True, description='自動保存機能の有効化')
    max_retry_attempts: int = Field(default=3, ge=1, description='最大リトライ回数')


class BizRequirementConfig(AgentConfig):
    """ビジネス要件定義エージェント設定"""

    output_dir: str = Field(default='outputs', description='出力ディレクトリのパス')

    @validator('output_dir')
    def validate_output_dir(cls, v):  # noqa: N805
        if not v or not isinstance(v, str):
            raise ValueError('output_dir must be a non-empty string')
        return v


class RequirementProcessConfig(AgentConfig):
    """要件プロセスエージェント設定"""

    auto_approve: bool = Field(default=False, description='自動承認モードの有効化')


class IntegratedWorkflowConfig(AgentConfig):
    """統合ワークフローエージェント設定"""

    enable_persistence: bool = Field(default=True, description='永続化機能の有効化')
    enable_auto_save: bool = Field(default=True, description='自動保存機能の有効化')
    intermediate_save: bool = Field(default=True, description='中間保存機能の有効化')


def validate_config(config: Dict[str, Any], config_class: type) -> Dict[str, Any]:
    """設定をバリデーション

    Args:
        config: 設定辞書
        config_class: バリデーション用のPydanticモデルクラス

    Returns:
        バリデーション済み設定辞書

    Raises:
        ValueError: 設定値が無効な場合
    """
    try:
        validated = config_class(**config)
        return validated.dict()
    except Exception as e:
        raise ValueError(f'Invalid configuration: {e}') from e


def validate_biz_requirement_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """ビジネス要件定義エージェント設定をバリデーション"""
    return validate_config(config, BizRequirementConfig)


def validate_requirement_process_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """要件プロセスエージェント設定をバリデーション"""
    return validate_config(config, RequirementProcessConfig)


def validate_integrated_workflow_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """統合ワークフローエージェント設定をバリデーション"""
    return validate_config(config, IntegratedWorkflowConfig)
