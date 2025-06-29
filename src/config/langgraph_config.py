"""LangGraph統合設定

LangGraphプラットフォーム統合に必要な設定管理を提供します。
"""

import json
import os
from typing import List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class LangGraphConfig(BaseSettings):
    """LangGraph統合設定"""

    # 基本設定
    env: str = Field(default='development', description='実行環境')
    server_url: str = Field(default='http://localhost:8000', description='LangGraph ServerのURL')
    log_level: str = Field(default='INFO', description='ログレベル')
    enable_debugging: bool = Field(default=False, description='デバッグモードの有効化')

    # API Keys
    google_api_key: Optional[str] = Field(default=None, description='Google API Key')
    openai_api_key: Optional[str] = Field(default=None, description='OpenAI API Key')
    langsmith_api_key: Optional[str] = Field(default=None, description='LangSmith API Key')
    tavily_api_key: Optional[str] = Field(default=None, description='Tavily API Key')

    # LangGraph Server設定
    server_port: int = Field(default=8000, description='サーバーポート')
    server_host: str = Field(default='0.0.0.0', description='サーバーホスト')  # noqa: S104
    cors_origins: List[str] = Field(default=['*'], description='CORS許可オリジン')

    # 機能フラグ
    enable_auto_save: bool = Field(default=True, description='自動保存機能の有効化')
    enable_persistence: bool = Field(default=True, description='永続化機能の有効化')
    enable_monitoring: bool = Field(default=True, description='監視機能の有効化')

    # パフォーマンス設定
    max_concurrent_requests: int = Field(default=100, description='最大同時リクエスト数')
    request_timeout: int = Field(default=300, description='リクエストタイムアウト（秒）')
    worker_processes: int = Field(default=1, description='ワーカープロセス数')

    model_config = {
        'env_prefix': 'LANGGRAPH_',
        'env_file': '.env',
        'extra': 'ignore',  # 既存の環境変数を無視
    }


def get_config() -> LangGraphConfig:
    """設定インスタンスを取得

    Returns:
        LangGraphConfig: 設定インスタンス
    """
    return LangGraphConfig()


def load_config_from_file(config_path: str) -> dict:
    """設定ファイルから設定を読み込み

    Args:
        config_path: 設定ファイルのパス

    Returns:
        dict: 設定辞書

    Raises:
        ValueError: サポートされていないファイル形式の場合
        FileNotFoundError: ファイルが見つからない場合
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f'Config file not found: {config_path}')

    try:
        if config_path.endswith('.json'):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif config_path.endswith(('.yml', '.yaml')):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f'Unsupported config file format: {config_path}')
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise ValueError(f'Invalid config file format: {e}') from e


def create_env_file(config: LangGraphConfig, env_file_path: str) -> None:
    """設定から環境変数ファイルを作成

    Args:
        config: LangGraph設定
        env_file_path: 環境変数ファイルのパス
    """
    env_content = f"""# LangGraph設定 (自動生成)
LANGGRAPH_ENV={config.env}
LANGGRAPH_SERVER_URL={config.server_url}
LANGGRAPH_LOG_LEVEL={config.log_level}
LANGGRAPH_ENABLE_DEBUGGING={str(config.enable_debugging).lower()}

# API Keys
"""
    if config.google_api_key:
        env_content += f'LANGGRAPH_GOOGLE_API_KEY={config.google_api_key}\n'
    if config.openai_api_key:
        env_content += f'LANGGRAPH_OPENAI_API_KEY={config.openai_api_key}\n'
    if config.langsmith_api_key:
        env_content += f'LANGGRAPH_LANGSMITH_API_KEY={config.langsmith_api_key}\n'
    if config.tavily_api_key:
        env_content += f'LANGGRAPH_TAVILY_API_KEY={config.tavily_api_key}\n'

    env_content += f"""
# Server設定
LANGGRAPH_SERVER_PORT={config.server_port}
LANGGRAPH_SERVER_HOST={config.server_host}

# 機能フラグ
LANGGRAPH_ENABLE_AUTO_SAVE={str(config.enable_auto_save).lower()}
LANGGRAPH_ENABLE_PERSISTENCE={str(config.enable_persistence).lower()}
LANGGRAPH_ENABLE_MONITORING={str(config.enable_monitoring).lower()}

# パフォーマンス設定
LANGGRAPH_MAX_CONCURRENT_REQUESTS={config.max_concurrent_requests}
LANGGRAPH_REQUEST_TIMEOUT={config.request_timeout}
LANGGRAPH_WORKER_PROCESSES={config.worker_processes}
"""

    with open(env_file_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
