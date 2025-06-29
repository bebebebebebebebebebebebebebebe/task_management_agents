"""LangGraph設定のテスト"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest
import yaml

from config.langgraph_config import LangGraphConfig, create_env_file, get_config, load_config_from_file


class TestLangGraphConfig:
    """LangGraph設定のテスト"""

    def test_default_config(self):
        """デフォルト設定のテスト"""
        config = LangGraphConfig()
        assert config.env == 'development'
        assert config.server_url == 'http://localhost:8000'
        assert config.server_port == 8000
        assert config.enable_auto_save is True

    def test_env_override(self):
        """環境変数による設定上書きのテスト"""
        with patch.dict(os.environ, {'LANGGRAPH_ENV': 'production', 'LANGGRAPH_SERVER_PORT': '9000'}):
            config = LangGraphConfig()
            assert config.env == 'production'
            assert config.server_port == 9000

    def test_get_config(self):
        """get_config関数のテスト"""
        config = get_config()
        assert isinstance(config, LangGraphConfig)

    def test_load_json_config(self):
        """JSON設定ファイル読み込みのテスト"""
        config_data = {'server_port': 8080, 'env': 'test'}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            loaded_config = load_config_from_file(temp_path)
            assert loaded_config['server_port'] == 8080
            assert loaded_config['env'] == 'test'
        finally:
            os.unlink(temp_path)

    def test_load_yaml_config(self):
        """YAML設定ファイル読み込みのテスト"""
        config_data = {'server_port': 8080, 'env': 'test'}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            loaded_config = load_config_from_file(temp_path)
            assert loaded_config['server_port'] == 8080
            assert loaded_config['env'] == 'test'
        finally:
            os.unlink(temp_path)

    def test_load_unsupported_format(self):
        """サポートされていないファイル形式のテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('unsupported format')
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match='Unsupported config file format'):
                load_config_from_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        """存在しないファイルのテスト"""
        with pytest.raises(FileNotFoundError):
            load_config_from_file('nonexistent_file.json')

    def test_create_env_file(self):
        """環境変数ファイル作成のテスト"""
        config = LangGraphConfig(
            env='test',
            server_port=8080,
            google_api_key='test_key',  # pragma: allowlist secret
            enable_debugging=True,
        )

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name

        try:
            create_env_file(config, temp_path)

            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert 'LANGGRAPH_ENV=test' in content
            assert 'LANGGRAPH_SERVER_PORT=8080' in content
            assert 'LANGGRAPH_GOOGLE_API_KEY=test_key' in content  # pragma: allowlist secret
            assert 'LANGGRAPH_ENABLE_DEBUGGING=true' in content
        finally:
            os.unlink(temp_path)

    def test_config_validation(self):
        """設定バリデーションのテスト"""
        # 有効な設定
        config = LangGraphConfig(server_port=8000, max_concurrent_requests=100)
        assert config.server_port == 8000
        assert config.max_concurrent_requests == 100

        # 無効な型
        with pytest.raises(ValueError):
            LangGraphConfig(server_port='invalid')

    def test_cors_origins_list(self):
        """CORS設定のテスト"""
        config = LangGraphConfig()
        assert isinstance(config.cors_origins, list)
        assert '*' in config.cors_origins

        # カスタムCORS設定
        custom_config = LangGraphConfig(cors_origins=['https://example.com', 'https://app.com'])
        assert len(custom_config.cors_origins) == 2
        assert 'https://example.com' in custom_config.cors_origins
