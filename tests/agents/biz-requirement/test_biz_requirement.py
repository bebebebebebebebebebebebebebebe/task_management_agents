import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agents.biz_requirement.biz_requirement_agent import BizRequirementAgent
from agents.biz_requirement.schemas import ProjectBusinessRequirement, RequirementsPhase, RequirementState


class TestBizRequirementAgent:
    @pytest.fixture
    def setup_agent(self):
        """エージェントのセットアップ"""
        agent = BizRequirementAgent()
        return agent

    @pytest.fixture
    def sample_state(self):
        """テスト用のサンプル状態"""
        return RequirementState(messages=[], current_phase=RequirementsPhase.INTRODUCTION, requirement=None, interview_complete=False)

    @pytest.fixture
    def sample_requirement(self):
        """テスト用のサンプル要件"""
        return ProjectBusinessRequirement(
            project_name='サンプルプロジェクト', background='現在のシステムに課題がある', goals=[], stake_holders=[], scopes=[]
        )

    def test_agent_initialization(self, setup_agent):
        """エージェントの初期化テスト"""
        agent = setup_agent
        assert agent is not None
        assert hasattr(agent, 'workflow')

    def test_build_graph(self, setup_agent):
        """グラフ構築のテスト"""
        agent = setup_agent
        graph = agent.build_graph()
        assert graph is not None

    def test_draw_mermaid_graph(self, setup_agent):
        """Mermaidグラフ描画のテスト"""
        agent = setup_agent
        mermaid_graph = agent.draw_mermaid_graph()
        assert isinstance(mermaid_graph, str)
        assert 'graph TD' in mermaid_graph

    def test_decide_entry_point(self, setup_agent, sample_state):
        """エントリーポイント決定のテスト"""
        agent = setup_agent

        # ヘルプ要求の場合
        state_with_help = sample_state.copy()
        state_with_help['user_wants_help'] = True
        result = agent._decide_entry_point(state_with_help)
        assert result == 'help'

        # フォローアップフェーズの場合
        state_followup = sample_state.copy()
        state_followup['current_phase'] = RequirementsPhase.INTERVIEW
        result = agent._decide_entry_point(state_followup)
        assert result == 'followup'

        # デフォルトの場合
        result = agent._decide_entry_point(sample_state)
        assert result == 'intro'

    def test_get_missing_mandatory_fields(self, setup_agent, sample_requirement):
        """必須フィールド不足検出のテスト"""
        agent = setup_agent

        # 空の要件の場合
        missing = agent._get_missing_mandatory_fields(None)
        assert len(missing) == 5  # MANDATORY定数の数

        # 一部フィールドが設定されている場合
        missing = agent._get_missing_mandatory_fields(sample_requirement)
        assert 'project_name' not in missing  # 設定済み
        assert 'background' not in missing  # 設定済み
        assert 'goals' in missing or 'stake_holders' in missing or 'scopes' in missing  # 空のリスト

    def test_handle_special_commands(self, setup_agent, sample_state):
        """特殊コマンド処理のテスト"""
        agent = setup_agent

        # ヘルプコマンドのテスト
        result = agent._handle_special_commands(sample_state, 'ヘルプ')
        assert result is not None
        assert result.get('user_wants_help') is True

        # ドキュメント作成コマンドのテスト
        result = agent._handle_special_commands(sample_state, 'ドキュメント作成')
        assert result is not None
        assert result.get('current_phase') == RequirementsPhase.OUTLINE_GENERATION
        assert result.get('interview_complete') is True

        # 通常のメッセージの場合
        result = agent._handle_special_commands(sample_state, '通常のメッセージ')
        assert result is None

    def test_get_last_user_message(self, setup_agent):
        """最後のユーザーメッセージ取得のテスト"""
        agent = setup_agent

        # メッセージがない場合
        state = RequirementState(messages=[])
        result = agent._get_last_user_message(state)
        assert result == ''

        # HumanMessageがある場合
        state = RequirementState(messages=[HumanMessage(content='テストメッセージ')])
        result = agent._get_last_user_message(state)
        assert result == 'テストメッセージ'

        # AIMessageが最後の場合
        state = RequirementState(messages=[HumanMessage(content='ユーザーメッセージ'), AIMessage(content='AIメッセージ')])
        result = agent._get_last_user_message(state)
        assert result == ''

    def test_introduction_node(self, setup_agent, sample_state):
        """導入ノードのテスト"""
        agent = setup_agent
        result = agent._introduction_node(sample_state)

        assert result['current_phase'] == RequirementsPhase.INTERVIEW
        assert len(result['messages']) > 0
        assert isinstance(result['messages'][-1], AIMessage)
        assert 'ドキュメント作成をサポート' in result['messages'][-1].content

    def test_help_node(self, setup_agent, sample_state):
        """ヘルプノードのテスト"""
        agent = setup_agent
        result = agent._help_node(sample_state)

        assert result['user_wants_help'] is False
        assert len(result['messages']) > 0
        assert isinstance(result['messages'][-1], AIMessage)
        assert '専門用語の説明' in result['messages'][-1].content

    def test_update_requirements(self, setup_agent, sample_requirement):
        """要件更新のテスト（LLM呼び出しなし）"""
        agent = setup_agent

        # モックなしの単純なテスト - 基本的な動作確認
        state = RequirementState(messages=[HumanMessage(content='テストメッセージ')], requirement=sample_requirement)

        # LLMを呼び出さないパスのテスト
        state['user_wants_help'] = True
        result = agent._update_requirements(state, 'ヘルプが欲しいです')
        assert isinstance(result, ProjectBusinessRequirement)

    def test_build_questions(self, setup_agent):
        """質問文構築のテスト"""
        agent = setup_agent
        missing_fields = ['project_name', 'background']
        questions = agent._build_questions(missing_fields)

        assert isinstance(questions, str)
        assert 'プロジェクト・システム開発の名前' in questions
        assert 'プロジェクトを始めようと思った理由' in questions
