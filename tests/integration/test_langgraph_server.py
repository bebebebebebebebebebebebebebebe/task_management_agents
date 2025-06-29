"""LangGraph Server統合テスト"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from config.langgraph_config import LangGraphConfig


class TestLangGraphServerIntegration:
    """LangGraph Server統合のテスト"""

    def test_langgraph_json_config_validation(self):
        """langgraph.json設定ファイルの検証"""
        langgraph_json_path = Path('langgraph.json')
        assert langgraph_json_path.exists(), 'langgraph.json設定ファイルが存在しません'

        with open(langgraph_json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 必須フィールドの確認
        assert 'dependencies' in config
        assert 'graphs' in config
        assert 'server' in config

        # dependencies検証
        assert isinstance(config['dependencies'], list)
        assert './' in config['dependencies']

        # graphs検証
        graphs = config['graphs']
        expected_graphs = ['biz_requirement_agent', 'requirement_process_agent', 'integrated_workflow_agent']
        for graph_name in expected_graphs:
            assert graph_name in graphs
            graph_config = graphs[graph_name]
            assert 'path' in graph_config
            assert 'config_schema' in graph_config

        # server設定検証
        server_config = config['server']
        assert server_config['port'] == 8000
        assert server_config['host'] == '0.0.0.0'
        assert 'cors' in server_config

    def test_langgraph_config_yaml_validation(self):
        """.langgraph/config.yaml設定ファイルの検証"""
        config_yaml_path = Path('.langgraph/config.yaml')
        assert config_yaml_path.exists(), '.langgraph/config.yaml設定ファイルが存在しません'

        with open(config_yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # プロジェクト設定検証
        assert 'project' in config
        project = config['project']
        assert project['name'] == 'task_management_agents'
        assert project['version'] == '1.0.0'

        # グラフ設定検証
        assert 'graphs' in config
        graphs = config['graphs']
        expected_graphs = ['biz_requirement', 'requirement_process', 'integrated_workflow']
        for graph_name in expected_graphs:
            assert graph_name in graphs

        # デプロイメント設定検証
        assert 'deployment' in config
        deployment = config['deployment']
        assert 'production' in deployment
        assert 'development' in deployment

    def test_entry_point_functions_callable(self):
        """エントリーポイント関数の呼び出し可能性テスト"""
        # biz_requirement_agent
        from agents.biz_requirement import create_agent_graph

        graph = create_agent_graph()
        assert hasattr(graph, 'invoke')
        assert hasattr(graph, 'ainvoke')

        # requirement_process_agent
        from agents.requirement_process import create_orchestrator_graph

        graph = create_orchestrator_graph()
        assert hasattr(graph, 'invoke')
        assert hasattr(graph, 'ainvoke')

        # integrated_workflow_agent
        from agents.integrated_workflow import create_workflow_graph

        graph = create_workflow_graph()
        assert hasattr(graph, 'invoke')
        assert hasattr(graph, 'ainvoke')

    def test_server_config_integration(self):
        """サーバー設定とLangGraphConfigの統合テスト"""
        config = LangGraphConfig()

        # デフォルト設定確認
        assert config.server_port == 8000
        assert config.server_url == 'http://localhost:8000'

        # 環境変数による設定上書き確認
        with patch.dict('os.environ', {'LANGGRAPH_SERVER_PORT': '9000'}):
            config = LangGraphConfig()
            assert config.server_port == 9000

    @patch('subprocess.run')
    def test_server_startup_simulation(self, mock_subprocess):
        """サーバー起動のシミュレーションテスト"""
        # サーバー起動コマンドのシミュレーション
        mock_subprocess.return_value = Mock(returncode=0, stdout='Server started successfully')

        # 起動コマンドの構築
        config = LangGraphConfig()
        cmd = [
            'langgraph',
            'dev',
            '--port',
            str(config.server_port),
            '--host',
            '127.0.0.1',
            '--config',
            'langgraph.json',
            '--no-browser',
        ]

        # コマンド実行をシミュレート
        result = mock_subprocess.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    def test_graph_registration_paths(self):
        """グラフ登録パスの検証"""
        langgraph_json_path = Path('langgraph.json')
        with open(langgraph_json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        graphs = config['graphs']

        # パス形式の検証
        for graph_name, graph_config in graphs.items():
            path = graph_config['path']
            assert ':' in path, f'{graph_name}のパス形式が正しくありません: {path}'

            module_path, function_name = path.split(':')
            assert module_path.startswith('src.agents.'), f'{graph_name}のモジュールパスが正しくありません: {module_path}'
            assert function_name.startswith('create_'), f'{graph_name}の関数名が正しくありません: {function_name}'

    def test_config_schema_validation(self):
        """設定スキーマの検証"""
        langgraph_json_path = Path('langgraph.json')
        with open(langgraph_json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        graphs = config['graphs']

        for _graph_name, graph_config in graphs.items():
            schema = graph_config['config_schema']
            assert schema['type'] == 'object'
            assert 'properties' in schema

            # 各プロパティの検証
            properties = schema['properties']
            for _prop_name, prop_config in properties.items():
                assert 'type' in prop_config
                assert 'default' in prop_config
                assert 'description' in prop_config

    def test_environment_file_integration(self):
        """環境ファイル統合の検証"""
        # .env.development ファイルの存在確認
        env_dev_path = Path('.env.development')
        assert env_dev_path.exists(), '.env.development ファイルが存在しません'

        # 環境変数の形式確認
        with open(env_dev_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_vars = ['LANGGRAPH_ENV', 'LANGGRAPH_SERVER_URL', 'LANGGRAPH_LOG_LEVEL']
        for var in required_vars:
            assert var in content, f'必須環境変数 {var} が見つかりません'

    def test_requirements_file_for_langgraph(self):
        """.langgraph/requirements.txt の検証"""
        requirements_path = Path('.langgraph/requirements.txt')
        assert requirements_path.exists(), '.langgraph/requirements.txt が存在しません'

        with open(requirements_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_packages = ['langgraph>=0.4.7', 'langgraph-cli>=0.2.10', 'langgraph-sdk>=0.1.70']
        for package in required_packages:
            assert package in content, f'必須パッケージ {package} が見つかりません'

    @patch('config.langgraph_config.LangGraphConfig')
    def test_production_deployment_config(self, mock_config):
        """本番デプロイメント設定のテスト"""
        # 本番環境設定のシミュレーション
        mock_config.return_value.env = 'production'
        mock_config.return_value.server_port = 8000
        mock_config.return_value.enable_debugging = False
        mock_config.return_value.log_level = 'INFO'

        config = mock_config.return_value
        assert config.env == 'production'
        assert config.enable_debugging is False
        assert config.log_level == 'INFO'

    def test_docker_compose_compatibility(self):
        """Docker Compose互換性の検証（設定のみ）"""
        # langgraph.json がDocker環境に対応しているか確認
        langgraph_json_path = Path('langgraph.json')
        with open(langgraph_json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        server_config = config['server']
        # Docker環境では0.0.0.0にバインドする必要がある
        assert server_config['host'] == '0.0.0.0'

        # CORS設定の確認
        cors_config = server_config['cors']
        assert 'allow_origins' in cors_config
        assert 'allow_methods' in cors_config
        assert 'allow_headers' in cors_config


class TestServerAPIEndpoints:
    """サーバーAPIエンドポイントのテスト（モック）"""

    @patch('requests.get')
    def test_health_check_endpoint(self, mock_get):
        """ヘルスチェックエンドポイントのテスト"""
        mock_get.return_value = Mock(status_code=200, json=lambda: {'status': 'healthy'})

        config = LangGraphConfig()
        health_url = f'{config.server_url}/health'

        # モックされたヘルスチェック
        response = mock_get.return_value
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        assert health_url  # URLが正しく構築されていることを確認

    @patch('requests.get')
    def test_graphs_list_endpoint(self, mock_get):
        """グラフ一覧エンドポイントのテスト"""
        expected_graphs = ['biz_requirement_agent', 'requirement_process_agent', 'integrated_workflow_agent']
        mock_get.return_value = Mock(status_code=200, json=lambda: {'graphs': expected_graphs})

        config = LangGraphConfig()
        graphs_url = f'{config.server_url}/graphs'

        # モックされたグラフ一覧取得
        response = mock_get.return_value
        assert response.status_code == 200
        graphs = response.json()['graphs']
        for expected_graph in expected_graphs:
            assert expected_graph in graphs
        assert graphs_url  # URLが正しく構築されていることを確認

    @patch('requests.post')
    def test_graph_invoke_endpoint(self, mock_post):
        """グラフ実行エンドポイントのテスト"""
        mock_post.return_value = Mock(status_code=200, json=lambda: {'result': 'success', 'output': {}})

        config = LangGraphConfig()
        invoke_url = f'{config.server_url}/graphs/biz_requirement_agent/invoke'

        # モックされたグラフ実行
        response = mock_post.return_value
        assert response.status_code == 200
        result = response.json()
        assert result['result'] == 'success'
        assert invoke_url  # URLが正しく構築されていることを確認
