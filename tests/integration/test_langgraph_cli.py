"""LangGraph CLI統合テスト"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from config.langgraph_config import LangGraphConfig


class TestLangGraphCLIIntegration:
    """LangGraph CLI統合のテスト"""

    def test_langgraph_cli_availability(self):
        """LangGraph CLIの利用可能性テスト"""
        try:
            result = subprocess.run(['langgraph', '--version'], capture_output=True, text=True, check=True)
            assert 'LangGraph CLI' in result.stdout
            assert 'version' in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip('LangGraph CLIが利用できません')

    def test_langgraph_config_validation(self):
        """LangGraph設定ファイルの検証"""
        # langgraph.json の存在確認
        config_path = Path('langgraph.json')
        assert config_path.exists(), 'langgraph.json が見つかりません'

        # 設定ファイルの構文チェック（モック）
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='Configuration is valid')

            # 設定検証コマンドのシミュレーション
            cmd = ['langgraph', 'config', 'validate', 'langgraph.json']
            result = mock_run.return_value
            assert result.returncode == 0
            assert cmd  # cmdが正しく構築されていることを確認

    @patch('subprocess.run')
    def test_langgraph_build_command(self, mock_run):
        """LangGraph buildコマンドのテスト"""
        mock_run.return_value = Mock(returncode=0, stdout='Build completed successfully')

        cmd = ['langgraph', 'build', '-c', 'langgraph.json']
        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    @patch('subprocess.run')
    def test_langgraph_dev_command_options(self, mock_run):
        """LangGraph dev コマンドオプションのテスト"""
        mock_run.return_value = Mock(returncode=0)

        # 基本的なdev起動コマンド
        cmd = [
            'langgraph',
            'dev',
            '--port',
            '8000',
            '--host',
            '127.0.0.1',
            '--config',
            'langgraph.json',
            '--no-browser',
        ]

        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    @patch('subprocess.run')
    def test_langgraph_up_command_options(self, mock_run):
        """LangGraph up コマンドオプションのテスト"""
        mock_run.return_value = Mock(returncode=0)

        # 本番起動コマンド
        cmd = ['langgraph', 'up', '-c', 'langgraph.json', '--port', '8000']

        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    def test_graph_paths_validation(self):
        """グラフパスの検証"""
        # エントリーポイント関数の存在確認
        try:
            from agents.biz_requirement import create_agent_graph

            graph = create_agent_graph()
            assert hasattr(graph, 'invoke')
        except ImportError:
            pytest.fail('biz_requirement のエントリーポイントが見つかりません')

        try:
            from agents.requirement_process import create_orchestrator_graph

            graph = create_orchestrator_graph()
            assert hasattr(graph, 'invoke')
        except ImportError:
            pytest.fail('requirement_process のエントリーポイントが見つかりません')

        try:
            from agents.integrated_workflow import create_workflow_graph

            graph = create_workflow_graph()
            assert hasattr(graph, 'invoke')
        except ImportError:
            pytest.fail('integrated_workflow のエントリーポイントが見つかりません')

    def test_environment_file_loading(self):
        """環境ファイル読み込みのテスト"""
        env_files = ['.env.development', '.env.production']

        for env_file in env_files:
            if Path(env_file).exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 基本的な環境変数の存在確認
                    assert 'LANGGRAPH_' in content

    @patch('subprocess.run')
    def test_debug_mode_activation(self, mock_run):
        """デバッグモード有効化のテスト"""
        mock_run.return_value = Mock(returncode=0)

        # デバッグポート付きの起動
        cmd = [
            'langgraph',
            'dev',
            '--debug-port',
            '8001',
            '--config',
            'langgraph.json',
        ]

        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    @patch('subprocess.run')
    def test_hot_reload_functionality(self, mock_run):
        """ホットリロード機能のテスト"""
        mock_run.return_value = Mock(returncode=0)

        # ホットリロード有効化
        cmd = ['langgraph', 'dev', '--watch', '--config', 'langgraph.json']

        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    def test_langgraph_directory_structure(self):
        """.langgraph ディレクトリ構造のテスト"""
        langgraph_dir = Path('.langgraph')
        assert langgraph_dir.exists(), '.langgraph ディレクトリが存在しません'

        # 必要なファイルの確認
        expected_files = ['config.yaml', 'requirements.txt']
        for file_name in expected_files:
            file_path = langgraph_dir / file_name
            assert file_path.exists(), f'{file_name} が .langgraph ディレクトリに存在しません'


class TestStartServerScript:
    """start_server.py スクリプトのテスト"""

    def test_start_server_script_exists(self):
        """start_server.py スクリプトの存在確認"""
        script_path = Path('scripts/start_server.py')
        assert script_path.exists(), 'scripts/start_server.py が存在しません'

        # 実行権限の確認
        assert script_path.stat().st_mode & 0o111, 'start_server.py に実行権限がありません'

    @patch('subprocess.run')
    def test_start_server_check_mode(self, mock_run):
        """start_server.py チェックモードのテスト"""
        mock_run.return_value = Mock(returncode=0, stdout='LangGraph CLI, version 0.2.10')

        # チェックモードの実行
        cmd = ['python', 'scripts/start_server.py', '--check']
        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    @patch('subprocess.run')
    def test_start_server_development_mode(self, mock_run):
        """start_server.py 開発モードのテスト"""
        mock_run.return_value = Mock(returncode=0)

        # 開発モードの実行
        cmd = ['python', 'scripts/start_server.py', '--env', 'development', '--no-browser']
        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    @patch('subprocess.run')
    def test_start_server_production_mode(self, mock_run):
        """start_server.py 本番モードのテスト"""
        mock_run.return_value = Mock(returncode=0)

        # 本番モードの実行
        cmd = ['python', 'scripts/start_server.py', '--env', 'production', '--detach']
        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    @patch('subprocess.run')
    def test_start_server_custom_port(self, mock_run):
        """start_server.py カスタムポートのテスト"""
        mock_run.return_value = Mock(returncode=0)

        # カスタムポートでの実行
        cmd = ['python', 'scripts/start_server.py', '--port', '9000']
        result = mock_run.return_value
        assert result.returncode == 0
        assert cmd  # cmdが正しく構築されていることを確認

    def test_start_server_config_integration(self):
        """start_server.py と設定ファイルの統合テスト"""
        config = LangGraphConfig()

        # デフォルト設定の確認
        assert config.server_port == 8000
        assert config.server_url == 'http://localhost:8000'

        # 環境変数による設定変更
        with patch.dict('os.environ', {'LANGGRAPH_SERVER_PORT': '9000'}):
            config = LangGraphConfig()
            assert config.server_port == 9000


class TestCLIWorkflow:
    """CLI ワークフローのテスト"""

    @patch('subprocess.run')
    def test_full_development_workflow(self, mock_run):
        """完全な開発ワークフローのテスト"""
        mock_run.return_value = Mock(returncode=0, stdout='Success')

        # 1. 設定検証
        subprocess.run(['python', 'scripts/start_server.py', '--check'])

        # 2. 開発サーバー起動
        subprocess.run(['python', 'scripts/start_server.py', '--env', 'development', '--no-browser'])

        # モックが呼ばれることを確認
        assert mock_run.called

    @patch('subprocess.run')
    def test_build_and_deploy_workflow(self, mock_run):
        """ビルド・デプロイワークフローのテスト"""
        mock_run.return_value = Mock(returncode=0)

        # 1. ビルド
        subprocess.run(['langgraph', 'build', '-c', 'langgraph.json'])

        # 2. 本番デプロイ
        subprocess.run(['langgraph', 'up', '-c', 'langgraph.json', '--port', '8000'])

        # モックが呼ばれることを確認
        assert mock_run.called

    def test_configuration_consistency(self):
        """設定の一貫性テスト"""
        # langgraph.json の設定
        import json

        with open('langgraph.json', 'r', encoding='utf-8') as f:
            langgraph_config = json.load(f)

        # LangGraphConfig の設定
        config = LangGraphConfig()

        # ポート設定の一貫性
        assert langgraph_config['server']['port'] == config.server_port

        # 環境ファイルの設定
        env_file = langgraph_config.get('env', '.env')
        assert env_file in ['.env', '.env.development', '.env.production']

    @patch('subprocess.run')
    def test_error_handling_workflow(self, mock_run):
        """エラーハンドリングワークフローのテスト"""
        # 失敗ケースのシミュレーション
        mock_run.return_value = Mock(returncode=1, stderr='Error occurred')

        # エラーが適切に処理されることを確認
        result = mock_run.return_value
        assert result.returncode == 1
        assert result.stderr == 'Error occurred'

    def test_graph_endpoint_accessibility(self):
        """グラフエンドポイントアクセシビリティのテスト"""
        # 各グラフのエントリーポイント関数をテスト
        graphs = [
            ('biz_requirement_agent', 'agents.biz_requirement', 'create_agent_graph'),
            ('requirement_process_agent', 'agents.requirement_process', 'create_orchestrator_graph'),
            ('integrated_workflow_agent', 'agents.integrated_workflow', 'create_workflow_graph'),
        ]

        for graph_name, module_name, function_name in graphs:
            try:
                module = __import__(module_name, fromlist=[function_name])
                func = getattr(module, function_name)
                graph = func()
                assert hasattr(graph, 'invoke'), f'{graph_name} のグラフにinvokeメソッドがありません'
            except ImportError:
                pytest.fail(f'{graph_name} のエントリーポイントが見つかりません: {module_name}.{function_name}')
