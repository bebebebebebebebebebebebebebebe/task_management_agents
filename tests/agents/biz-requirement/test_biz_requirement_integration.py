import tempfile
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.biz_requirement.biz_requirement_agent import BizRequirementAgent
from agents.biz_requirement.schemas import RequirementsPhase, RequirementState


class TestBizRequirementAgentIntegration:
    """BizRequirementAgentの統合テスト"""

    @pytest.fixture
    def temp_output_dir(self):
        """テスト用の一時出力ディレクトリ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs_dir = Path(temp_dir) / 'outputs'
            outputs_dir.mkdir(exist_ok=True)
            yield outputs_dir

    @pytest.fixture
    def mock_llm_responses(self):
        """LLMレスポンスのモック"""
        responses = {
            'requirement_extraction': {
                'project_name': 'テストプロジェクト',
                'background': 'システム改善が必要',
                'goals': ['効率向上', 'コスト削減'],
                'stake_holders': ['開発チーム', 'ユーザー'],
                'scopes': ['機能A', '機能B'],
                'constraints': ['予算制限', '期限制約'],
                'success_criteria': ['パフォーマンス向上', 'ユーザー満足度向上'],
                'out_of_scope': ['機能C'],
                'assumptions': ['技術的前提'],
                'risks': ['技術リスク'],
                'deliverables': ['要件定義書', 'プロトタイプ'],
                'timeline': ['フェーズ1: 2週間', 'フェーズ2: 4週間'],
            },
            'outline_generation': {
                'sections': [
                    {'title': '1. プロジェクト概要', 'description': '概要説明'},
                    {'title': '2. ビジネス要件', 'description': '要件詳細'},
                    {'title': '3. 制約事項', 'description': '制約内容'},
                ]
            },
            'detail_generation': {
                '1. プロジェクト概要': 'プロジェクトの詳細な概要内容',
                '2. ビジネス要件': 'ビジネス要件の詳細内容',
                '3. 制約事項': '制約事項の詳細内容',
            },
            'document_integration': """# テストプロジェクト要件定義書

## 1. プロジェクト概要
プロジェクトの詳細な概要内容

## 2. ビジネス要件
ビジネス要件の詳細内容

## 3. 制約事項
制約事項の詳細内容
""",
        }
        return responses

    @pytest.mark.asyncio
    async def test_full_workflow_execution(self, mock_llm_responses):
        """完全なワークフローの実行テスト"""
        agent = BizRequirementAgent()

        # LLMの応答をモック
        with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_llm_class:
            mock_llm = AsyncMock()
            mock_llm_class.return_value = mock_llm

            # 各段階でのLLM応答を設定
            def mock_ainvoke(messages, **_kwargs):
                content = str(messages[-1].content) if messages else ''

                if '要件を抽出' in content:
                    return MagicMock(content=str(mock_llm_responses['requirement_extraction']))
                elif 'アウトライン' in content:
                    return MagicMock(content=str(mock_llm_responses['outline_generation']))
                elif '詳細内容' in content:
                    return MagicMock(content=mock_llm_responses['detail_generation']['1. プロジェクト概要'])
                elif '統合' in content:
                    return MagicMock(content=mock_llm_responses['document_integration'])
                else:
                    return MagicMock(content='一般的な応答')

            mock_llm.ainvoke = mock_ainvoke

            # グラフを構築
            graph = agent.build_graph()
            config = {'configurable': {'thread_id': str(uuid.uuid4())}}

            # 初期状態
            initial_state = RequirementState(
                messages=[], current_phase=RequirementsPhase.INTRODUCTION, requirement=None, interview_complete=False
            )

            # ワークフローを実行（導入フェーズ）
            result = await graph.ainvoke(initial_state, config)

            # 結果の検証
            assert result is not None
            assert 'messages' in result
            assert len(result['messages']) > 0
            assert result['current_phase'] == RequirementsPhase.INTERVIEW

    @pytest.mark.asyncio
    async def test_document_creation_flow(self, mock_llm_responses):
        """ドキュメント作成フローのテスト"""
        agent = BizRequirementAgent()

        with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_llm_class:
            mock_llm = AsyncMock()
            mock_llm_class.return_value = mock_llm

            # ドキュメント作成用のLLM応答を設定
            def mock_ainvoke(messages, **_kwargs):
                content = str(messages[-1].content) if messages else ''

                if 'アウトライン' in content:
                    return MagicMock(content=str(mock_llm_responses['outline_generation']))
                elif '統合' in content:
                    return MagicMock(content=mock_llm_responses['document_integration'])
                else:
                    return MagicMock(content='詳細内容')

            mock_llm.ainvoke = mock_ainvoke

            # ファイル書き込みをモック
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file

                # グラフを構築
                graph = agent.build_graph()
                config = {'configurable': {'thread_id': str(uuid.uuid4())}}

                # ドキュメント作成開始状態
                initial_state = RequirementState(
                    messages=[],
                    current_phase=RequirementsPhase.OUTLINE_GENERATION,
                    requirement=mock_llm_responses['requirement_extraction'],
                    interview_complete=True,
                )

                # ワークフローを実行
                result = await graph.ainvoke(initial_state, config)

                # 結果の検証
                assert result is not None
                # ワークフローが実行され、中断またはステップが進んだことを確認
                assert 'current_phase' in result

    def test_agent_graph_structure(self):
        """エージェントのグラフ構造テスト"""
        agent = BizRequirementAgent()
        graph = agent.build_graph()

        # グラフが正常に構築されることを確認
        assert graph is not None

        # Mermaidグラフが生成できることを確認
        mermaid = agent.draw_mermaid_graph()
        assert isinstance(mermaid, str)
        assert 'graph TD' in mermaid

        # 主要なノードが含まれていることを確認
        expected_nodes = ['intro', 'followup', 'help', 'outline_generation', 'detail_generation', 'document_integration']
        for node in expected_nodes:
            assert node in mermaid

    @pytest.mark.asyncio
    async def test_error_handling_in_workflow(self):
        """ワークフロー内でのエラーハンドリングテスト"""
        agent = BizRequirementAgent()

        with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_llm_class:
            # LLMでエラーを発生させる
            mock_llm = AsyncMock()
            mock_llm.ainvoke.side_effect = Exception('LLMエラー')
            mock_llm_class.return_value = mock_llm

            graph = agent.build_graph()
            config = {'configurable': {'thread_id': str(uuid.uuid4())}}

            initial_state = RequirementState(
                messages=[], current_phase=RequirementsPhase.INTRODUCTION, requirement=None, interview_complete=False
            )

            # エラーが適切に処理されることを確認
            try:
                result = await graph.ainvoke(initial_state, config)
                # エラーがキャッチされ、適切な応答が返されることを確認
                assert result is not None
            except Exception as e:
                # 予期されるエラーの場合は適切に処理されることを確認
                assert 'LLMエラー' in str(e) or 'error' in str(e).lower()

    def test_state_transitions(self):
        """状態遷移のテスト"""
        agent = BizRequirementAgent()

        # 各状態からの遷移をテスト
        test_cases = [
            {'current_phase': RequirementsPhase.INTRODUCTION, 'expected_next': 'intro'},
            {'current_phase': RequirementsPhase.INTERVIEW, 'expected_next': 'followup'},
        ]

        for case in test_cases:
            state = RequirementState(messages=[], current_phase=case['current_phase'], requirement=None, interview_complete=False)

            result = agent._decide_entry_point(state)
            assert result == case['expected_next']
