"""統合ワークフローエージェントのテスト"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from agents.biz_requirement.schemas import ProjectBusinessRequirement, ProjectGoal, ScopeItem, Stakeholder
from agents.integrated_workflow.integrated_workflow_agent import IntegratedWorkflowAgent, IntegratedWorkflowState


class TestIntegratedWorkflowAgent:
    """統合ワークフローエージェントのテストクラス"""

    @pytest.fixture
    def agent(self):
        """テスト用のエージェントインスタンス"""
        return IntegratedWorkflowAgent()

    @pytest.fixture
    def sample_business_requirement(self):
        """テスト用のビジネス要件"""
        return ProjectBusinessRequirement(
            project_name='テストプロジェクト',
            description='テスト用のプロジェクト',
            background='テストプロジェクトの背景',
            goals=[ProjectGoal(objective='テスト目標', rationale='テスト理由', kpi='テストKPI')],
            stake_holders=[Stakeholder(name='テストユーザー', role='テスト役割', expectations='テスト期待値')],
            scopes=[ScopeItem(in_scope='含む項目', out_of_scope='含まない項目')],
        )

    @pytest.fixture
    def sample_process_result(self):
        """テスト用の要件定義プロセス結果"""
        return {
            'functional_requirements': [
                {
                    'name': 'テスト機能要件',
                    'priority': 'High',
                    'description': 'テスト用の機能要件',
                    'acceptance_criteria': 'テスト受入条件',
                }
            ],
            'non_functional_requirements': {'Performance': ['レスポンス時間3秒以内'], 'Security': ['認証機能必須']},
            'data_models': [{'name': 'ユーザーモデル', 'description': 'ユーザー情報', 'attributes': ['id', 'name', 'email']}],
            'system_architecture': {'pattern': 'MVC', 'technology_stack': 'Python/FastAPI', 'system_components': 'Web, DB, Cache'},
        }

    def test_agent_initialization(self, agent):
        """エージェント初期化のテスト"""
        assert agent is not None
        assert agent._compiled_graph is None
        assert agent._biz_requirement_agent is not None
        assert agent._checkpointer is not None

    def test_build_graph(self, agent):
        """グラフ構築のテスト"""
        graph = agent.build_graph()

        assert graph is not None
        assert agent._compiled_graph is not None

        # 2回目の呼び出しでは同じインスタンスが返される
        graph2 = agent.build_graph()
        assert graph is graph2

    def test_start_node(self, agent):
        """開始ノードのテスト"""
        state = IntegratedWorkflowState()
        result = agent._start_node(state)

        assert result['workflow_phase'] == 'biz_requirement'
        assert len(result['messages']) == 1
        assert '統合要件定義ワークフローへようこそ' in result['messages'][0].content

    @pytest.mark.asyncio
    async def test_biz_requirement_collection_node_success(self, agent):
        """ビジネス要件収集ノード成功ケースのテスト"""
        state = IntegratedWorkflowState(messages=[], workflow_phase='biz_requirement')

        # モックの設定
        from langgraph.graph import END

        mock_result = {
            'messages': [],
            'requirement': ProjectBusinessRequirement(project_name='テスト'),
            'current_phase': END,
            'document': Mock(),
        }

        with patch.object(agent._biz_requirement_agent, 'build_graph') as mock_build:
            mock_workflow = AsyncMock()
            mock_workflow.ainvoke.return_value = mock_result
            mock_build.return_value = mock_workflow

            result = await agent._biz_requirement_collection_node(state)

            assert result['workflow_phase'] == 'biz_requirement'
            assert result['business_requirement'] is not None

    @pytest.mark.asyncio
    async def test_biz_requirement_collection_node_fallback(self, agent):
        """ビジネス要件収集ノードのフォールバック機能テスト"""
        state = IntegratedWorkflowState()

        # 非インタラクティブ環境では正常にデモモードに切り替わることを確認
        result = await agent._biz_requirement_collection_node(state)

        assert result['workflow_phase'] == 'biz_requirement'
        assert result['business_requirement'] is not None
        assert result['current_phase'] == 'END'

    @pytest.mark.asyncio
    async def test_requirement_process_execution_node_success(self, agent, sample_business_requirement, sample_process_result):
        """要件定義プロセス実行ノード成功ケースのテスト"""
        state = IntegratedWorkflowState(business_requirement=sample_business_requirement, messages=[])

        with patch('agents.integrated_workflow.integrated_workflow_agent.run_requirement_process', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = sample_process_result

            result = await agent._requirement_process_execution_node(state)

            assert result['workflow_phase'] == 'requirement_process'
            assert result['requirement_process_result'] is not None
            assert len(result['messages']) > 0

    @pytest.mark.asyncio
    async def test_requirement_process_execution_node_no_business_req(self, agent):
        """要件定義プロセス実行ノード - ビジネス要件なしのテスト"""
        state = IntegratedWorkflowState()

        result = await agent._requirement_process_execution_node(state)

        assert result['workflow_phase'] == 'error'
        assert 'ビジネス要件が取得できませんでした' in result['error_message']

    @pytest.mark.asyncio
    async def test_requirement_process_execution_node_error(self, agent, sample_business_requirement):
        """要件定義プロセス実行ノードエラーケースのテスト"""
        state = IntegratedWorkflowState(business_requirement=sample_business_requirement)

        with patch('agents.integrated_workflow.integrated_workflow_agent.run_requirement_process', new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = Exception('プロセスエラー')

            # デモ用の結果も失敗させる
            with patch.object(agent, '_create_demo_process_result') as mock_demo:
                mock_demo.side_effect = Exception('デモエラー')

                result = await agent._requirement_process_execution_node(state)

                assert result['workflow_phase'] == 'error'
                assert 'デモエラー' in result['error_message']

    def test_document_integration_node_success(self, agent, sample_business_requirement, sample_process_result):
        """ドキュメント統合ノード成功ケースのテスト"""
        state = IntegratedWorkflowState(
            business_requirement=sample_business_requirement, requirement_process_result=sample_process_result
        )

        with patch('builtins.open', create=True) as mock_open, patch('os.makedirs'):
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = agent._document_integration_node(state)

            assert result['workflow_phase'] == 'completion'
            assert result['final_output_path'] is not None
            assert 'テストプロジェクト_integrated_requirement.md' in result['final_output_path']

            # ファイル書き込みが呼ばれることを確認
            mock_file.write.assert_called_once()

    def test_document_integration_node_missing_data(self, agent):
        """ドキュメント統合ノード - データ不足のテスト"""
        state = IntegratedWorkflowState()

        result = agent._document_integration_node(state)

        assert result['workflow_phase'] == 'error'
        assert '統合に必要なデータが不足しています' in result['error_message']

    def test_error_handler_node(self, agent):
        """エラーハンドリングノードのテスト"""
        state = IntegratedWorkflowState(error_message='テストエラーメッセージ', messages=[])

        result = agent._error_handler_node(state)

        assert result['workflow_phase'] == 'completion'
        assert len(result['messages']) == 1
        assert 'テストエラーメッセージ' in result['messages'][0].content

    def test_completion_node_success(self, agent):
        """完了ノード成功ケースのテスト"""
        state = IntegratedWorkflowState(final_output_path='/test/path/output.md', messages=[])

        result = agent._completion_node(state)

        assert len(result['messages']) == 1
        assert '統合要件定義ワークフローが完了しました' in result['messages'][0].content
        assert '/test/path/output.md' in result['messages'][0].content

    def test_completion_node_error(self, agent):
        """完了ノードエラーケースのテスト"""
        state = IntegratedWorkflowState(messages=[])

        result = agent._completion_node(state)

        assert len(result['messages']) == 1
        assert 'エラーが発生しました' in result['messages'][0].content

    def test_decide_after_biz_requirement(self, agent):
        """ビジネス要件後の遷移判定テスト"""
        # エラーケース
        state_error = IntegratedWorkflowState(error_message='エラー')
        assert agent._decide_after_biz_requirement(state_error) == 'error'

        # 完了ケース
        state_complete = IntegratedWorkflowState(current_phase='END', business_requirement=ProjectBusinessRequirement())
        assert agent._decide_after_biz_requirement(state_complete) == 'requirement_process'

        # 継続ケース
        state_continue = IntegratedWorkflowState()
        assert agent._decide_after_biz_requirement(state_continue) == 'continue_biz'

    def test_decide_after_requirement_process(self, agent):
        """要件定義プロセス後の遷移判定テスト"""
        # エラーケース
        state_error = IntegratedWorkflowState(error_message='エラー')
        assert agent._decide_after_requirement_process(state_error) == 'error'

        # 正常ケース
        state_normal = IntegratedWorkflowState()
        assert agent._decide_after_requirement_process(state_normal) == 'document_integration'

    def test_create_integrated_document(self, agent, sample_business_requirement, sample_process_result):
        """統合ドキュメント生成のテスト"""
        document = agent._create_integrated_document(sample_business_requirement, sample_process_result)

        assert 'テストプロジェクト - 統合要件定義書' in document
        assert '目次' in document
        assert 'プロジェクト概要' in document
        assert 'ビジネス要件' in document
        assert 'テスト目標' in document
        assert 'テスト役割' in document
        assert 'テスト機能要件' in document
        assert 'ユーザーモデル' in document

    @pytest.mark.asyncio
    async def test_main_function_success(self):
        """メイン関数成功ケースのテスト"""
        with patch('agents.integrated_workflow.integrated_workflow_agent.IntegratedWorkflowAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_workflow = AsyncMock()
            mock_workflow.ainvoke.return_value = {'final_output_path': '/test/output.md'}
            mock_agent.build_graph.return_value = mock_workflow
            mock_agent_class.return_value = mock_agent

            from agents.integrated_workflow.integrated_workflow_agent import main

            with patch('builtins.print') as mock_print:
                await main()

                # 成功メッセージが出力されることを確認
                print_calls = [call[0][0] for call in mock_print.call_args_list]
                success_message = any('✅ 統合要件定義書が生成されました' in msg for msg in print_calls)
                assert success_message
