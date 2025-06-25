"""オーケストレーター・エージェントのテスト"""

from unittest.mock import Mock, patch

import pytest

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.orchestrator.orchestrator_agent import RequirementProcessOrchestratorAgent
from agents.requirement_process.schemas import RequirementProcessPhase, RequirementProcessState


class TestRequirementProcessOrchestratorAgent:
    """要件定義プロセス オーケストレーター・エージェントのテストクラス"""

    def test_init(self):
        """初期化テスト"""
        orchestrator = RequirementProcessOrchestratorAgent()

        # ペルソナエージェントが正しく初期化されていることを確認
        assert orchestrator.persona_agents is not None
        assert len(orchestrator.persona_agents) == 7  # 7つのペルソナエージェント

    def test_build_graph(self):
        """ワークフローグラフ構築テスト"""
        orchestrator = RequirementProcessOrchestratorAgent()

        # ワークフローグラフが正しく構築されることを確認
        graph = orchestrator.build_graph()
        assert graph is not None

    def test_initialize_process(self):
        """プロセス初期化テスト"""
        orchestrator = RequirementProcessOrchestratorAgent()

        # 初期状態を作成
        initial_state = RequirementProcessState(business_requirement=Mock(spec=ProjectBusinessRequirement), messages=[])

        # 初期化を実行
        result = orchestrator._initialize_process(initial_state)

        # 結果を確認
        assert result['current_phase'] == RequirementProcessPhase.SYSTEM_ANALYSIS
        assert len(result['messages']) == 1
        assert 'プロセスを開始' in result['messages'][0]['content'] or 'v2.0 を開始' in result['messages'][0]['content']

    @patch('agents.requirement_process.orchestrator.orchestrator_agent.logger')
    def test_execute_system_analysis(self, mock_logger):
        """システム分析フェーズテスト"""
        orchestrator = RequirementProcessOrchestratorAgent()

        # モックの設定
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_output = Mock()
        orchestrator.persona_agents[orchestrator.persona_agents.__iter__().__next__()].execute = Mock(return_value=mock_output)

        # 初期状態を作成
        state = RequirementProcessState(business_requirement=mock_business_req, persona_outputs=[], completed_phases=[], messages=[])

        # システム分析を実行
        result = orchestrator._execute_system_analysis(state)

        # 結果を確認
        assert result['current_phase'] == RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS
        assert len(result['completed_phases']) == 1
        assert RequirementProcessPhase.SYSTEM_ANALYSIS in result['completed_phases']
        mock_logger.info.assert_called()

    def test_consolidate_outputs(self):
        """成果物統合テスト"""
        orchestrator = RequirementProcessOrchestratorAgent()

        # モックの成果物を作成
        mock_outputs = [
            Mock(
                deliverables={
                    'functional_requirements': [{'test': 'functional'}],
                    'non_functional_requirements': [{'test': 'non_functional'}],
                }
            ),
            Mock(deliverables={'data_models': [{'test': 'data_model'}], 'system_architecture': {'test': 'architecture'}}),
        ]

        # 統合を実行
        result = orchestrator._consolidate_outputs(mock_outputs)

        # 結果を確認
        assert 'functional_requirements' in result
        assert 'non_functional_requirements' in result
        assert 'data_models' in result
        assert 'system_architecture' in result
        assert len(result['functional_requirements']) == 1
        assert result['system_architecture']['test'] == 'architecture'

    def test_create_requirement_document(self):
        """要件定義書作成テスト"""
        orchestrator = RequirementProcessOrchestratorAgent()

        # モックの状態を作成
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.project_name = 'テストプロジェクト'
        mock_business_req.description = 'テスト説明'
        mock_business_req.background = 'テスト背景'
        mock_business_req.goals = []
        mock_business_req.scopes = []

        state = RequirementProcessState(
            business_requirement=mock_business_req,
            functional_requirements=[],
            non_functional_requirements=[],
            data_models=[],
            table_definitions=[],
            system_architecture=None,
            persona_outputs=[],
        )

        # ドキュメント作成を実行
        document = orchestrator._create_requirement_document(state)

        # 結果を確認
        assert document.title == 'テストプロジェクト 要件定義書'
        assert '1. 概要' in document.sections
        assert '2. 機能要件' in document.sections
        assert '3. 非機能要件' in document.sections

    def test_format_list(self):
        """リストフォーマットテスト"""
        orchestrator = RequirementProcessOrchestratorAgent()

        # テストデータ
        test_items = ['項目1', '項目2', '項目3']

        # フォーマット実行
        result = orchestrator._format_list(test_items)

        # 結果を確認
        expected = '- 項目1\n- 項目2\n- 項目3'
        assert result == expected

    @patch('agents.requirement_process.orchestrator.orchestrator_agent.datetime')
    @patch('builtins.open')
    @patch('pathlib.Path.mkdir')
    def test_save_document(self, mock_mkdir, mock_open, mock_datetime):
        """ドキュメント保存テスト"""
        orchestrator = RequirementProcessOrchestratorAgent()

        # モックの設定
        mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
        mock_datetime.now.return_value.isoformat.return_value = '2024-01-01T12:00:00'

        # テストドキュメント
        from agents.requirement_process.schemas import RequirementDocument

        document = RequirementDocument(
            title='テスト要件定義書', sections={'1. テスト': 'テスト内容'}, created_at='2024-01-01T12:00:00', version='1.0'
        )

        # 保存実行
        file_path = orchestrator._save_document(document)

        # 結果を確認
        assert 'requirement_specification_20240101_120000.md' in file_path
        mock_mkdir.assert_called_once()
        mock_open.assert_called_once()


@pytest.fixture
def sample_business_requirement():
    """サンプルビジネス要件のフィクスチャ"""
    return ProjectBusinessRequirement(project_name='サンプルプロジェクト', description='サンプル説明', background='サンプル背景')
