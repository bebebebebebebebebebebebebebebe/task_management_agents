"""ペルソナエージェントのテスト"""

from unittest.mock import Mock

import pytest

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.personas.data_architect import DataArchitectAgent
from agents.requirement_process.personas.infrastructure_engineer import InfrastructureEngineerAgent
from agents.requirement_process.personas.qa_engineer import QAEngineerAgent
from agents.requirement_process.personas.security_specialist import SecuritySpecialistAgent
from agents.requirement_process.personas.solution_architect import SolutionArchitectAgent
from agents.requirement_process.personas.system_analyst import SystemAnalystAgent
from agents.requirement_process.personas.ux_designer import UXDesignerAgent
from agents.requirement_process.schemas import PersonaOutput, PersonaRole


class TestSystemAnalystAgent:
    """システムアナリスト・エージェントのテストクラス"""

    def test_init(self):
        """初期化テスト"""
        agent = SystemAnalystAgent()
        assert agent.persona_role == PersonaRole.SYSTEM_ANALYST

    def test_execute(self):
        """実行テスト"""
        agent = SystemAnalystAgent()

        # モックのビジネス要件を作成
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.goals = []
        mock_business_req.stake_holders = []
        mock_business_req.scopes = []
        mock_business_req.constraints = []
        mock_business_req.compliance = []

        # 実行
        result = agent.execute(mock_business_req)

        # 結果の確認
        assert isinstance(result, PersonaOutput)
        assert result.persona_role == PersonaRole.SYSTEM_ANALYST
        assert 'function_candidates' in result.deliverables
        assert 'system_boundaries' in result.deliverables
        assert len(result.recommendations) > 0
        assert len(result.concerns) > 0

    def test_extract_function_candidates(self):
        """機能候補抽出テスト"""
        agent = SystemAnalystAgent()

        # テストデータ
        from agents.biz_requirement.schemas import ProjectGoal

        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.goals = [ProjectGoal(objective='データ管理の効率化', rationale='現在の管理が非効率', kpi='効率50%向上')]
        mock_business_req.stake_holders = []
        mock_business_req.scopes = []

        # 実行
        functions = agent._extract_function_candidates(mock_business_req)

        # 結果の確認
        assert len(functions) > 0
        # データ管理に関連する機能が含まれることを確認
        function_names = [f['name'] for f in functions]
        assert any('管理' in name for name in function_names)


class TestUXDesignerAgent:
    """UXデザイナー・エージェントのテストクラス"""

    def test_init(self):
        """初期化テスト"""
        agent = UXDesignerAgent()
        assert agent.persona_role == PersonaRole.UX_DESIGNER

    def test_execute(self):
        """実行テスト"""
        agent = UXDesignerAgent()

        # モックのビジネス要件と前段階出力を作成
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.stake_holders = []

        mock_previous_output = Mock()
        mock_previous_output.persona_role = PersonaRole.SYSTEM_ANALYST
        mock_previous_output.deliverables = {'function_candidates': []}

        # 実行
        result = agent.execute(mock_business_req, [mock_previous_output])

        # 結果の確認
        assert isinstance(result, PersonaOutput)
        assert result.persona_role == PersonaRole.UX_DESIGNER
        assert 'functional_requirements' in result.deliverables
        assert 'ux_guidelines' in result.deliverables
        assert len(result.recommendations) > 0

    def test_create_user_stories(self):
        """ユーザーストーリー作成テスト"""
        agent = UXDesignerAgent()

        # テストデータ
        from agents.biz_requirement.schemas import Stakeholder

        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.stake_holders = [
            Stakeholder(name='テストユーザー', role='管理者', expectations='システムを効率的に管理したい')
        ]

        function_candidates = [{'name': 'データ管理機能', 'priority': 'high'}]

        # 実行
        stories = agent._create_user_stories(mock_business_req, function_candidates)

        # 結果の確認
        assert len(stories) > 0
        # 管理に関連するストーリーが含まれることを確認
        story_texts = [s['story'] for s in stories]
        assert any('管理' in story for story in story_texts)


class TestQAEngineerAgent:
    """QAエンジニア・エージェントのテストクラス"""

    def test_init(self):
        """初期化テスト"""
        agent = QAEngineerAgent()
        assert agent.persona_role == PersonaRole.QA_ENGINEER

    def test_execute(self):
        """実行テスト"""
        agent = QAEngineerAgent()

        # モックのビジネス要件と前段階出力を作成
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.compliance = []
        mock_business_req.constraints = []
        mock_business_req.non_functional = []
        mock_business_req.scopes = []

        from agents.requirement_process.schemas import FunctionalRequirement

        mock_functional_req = FunctionalRequirement(
            user_story='テストストーリー', acceptance_criteria=['テスト基準'], priority='high', complexity='medium'
        )

        mock_previous_output = Mock()
        mock_previous_output.persona_role = PersonaRole.UX_DESIGNER
        mock_previous_output.deliverables = {'functional_requirements': [mock_functional_req]}

        # 実行
        result = agent.execute(mock_business_req, [mock_previous_output])

        # 結果の確認
        assert isinstance(result, PersonaOutput)
        assert result.persona_role == PersonaRole.QA_ENGINEER
        assert 'test_strategy' in result.deliverables
        assert 'quality_standards' in result.deliverables
        assert len(result.recommendations) > 0

    def test_create_test_cases(self):
        """テストケース作成テスト"""
        agent = QAEngineerAgent()

        # テストデータ
        from agents.requirement_process.schemas import FunctionalRequirement

        functional_reqs = [
            FunctionalRequirement(
                user_story='ユーザーとして、データを作成したい',
                acceptance_criteria=['データが正常に作成される'],
                priority='high',
                complexity='medium',
            )
        ]

        # 実行
        test_cases = agent._create_test_cases(functional_reqs)

        # 結果の確認
        assert len(test_cases) >= 2  # 正常系と異常系
        test_case_names = [tc['test_name'] for tc in test_cases]
        assert any('正常系' in name for name in test_case_names)
        assert any('異常系' in name for name in test_case_names)


class TestInfrastructureEngineerAgent:
    """インフラエンジニア・エージェントのテストクラス"""

    def test_init(self):
        """初期化テスト"""
        agent = InfrastructureEngineerAgent()
        assert agent.persona_role == PersonaRole.INFRASTRUCTURE_ENGINEER

    def test_execute(self):
        """実行テスト"""
        agent = InfrastructureEngineerAgent()

        # モックのビジネス要件を作成
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.compliance = []
        mock_business_req.stake_holders = []

        # 実行
        result = agent.execute(mock_business_req)

        # 結果の確認
        assert isinstance(result, PersonaOutput)
        assert result.persona_role == PersonaRole.INFRASTRUCTURE_ENGINEER
        assert 'infrastructure_architecture' in result.deliverables
        assert 'monitoring_requirements' in result.deliverables
        assert len(result.recommendations) > 0


class TestSecuritySpecialistAgent:
    """セキュリティスペシャリスト・エージェントのテストクラス"""

    def test_init(self):
        """初期化テスト"""
        agent = SecuritySpecialistAgent()
        assert agent.persona_role == PersonaRole.SECURITY_SPECIALIST

    def test_execute(self):
        """実行テスト"""
        agent = SecuritySpecialistAgent()

        # モックのビジネス要件を作成
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.compliance = []

        # 実行
        result = agent.execute(mock_business_req)

        # 結果の確認
        assert isinstance(result, PersonaOutput)
        assert result.persona_role == PersonaRole.SECURITY_SPECIALIST
        assert 'security_architecture' in result.deliverables
        assert 'security_requirements' in result.deliverables
        assert len(result.recommendations) > 0

    def test_assess_security_risks(self):
        """セキュリティリスク評価テスト"""
        agent = SecuritySpecialistAgent()

        # テストデータ
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.compliance = []

        functional_reqs = [{'user_story': 'ユーザーとして、データを管理したい'}, {'user_story': 'ユーザーとして、APIにアクセスしたい'}]

        # 実行
        risks = agent._assess_security_risks(mock_business_req, functional_reqs)

        # 結果の確認
        assert len(risks) > 0
        risk_categories = [r['risk_category'] for r in risks]
        assert any('データ保護' in cat for cat in risk_categories)
        assert any('API' in cat for cat in risk_categories)


class TestDataArchitectAgent:
    """データアーキテクト・エージェントのテストクラス"""

    def test_init(self):
        """初期化テスト"""
        agent = DataArchitectAgent()
        assert agent.persona_role == PersonaRole.DATA_ARCHITECT

    def test_execute(self):
        """実行テスト"""
        agent = DataArchitectAgent()

        # モックのビジネス要件を作成
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.compliance = []
        mock_business_req.stake_holders = []
        mock_business_req.constraints = []
        mock_business_req.non_functional = []
        mock_business_req.scopes = []
        mock_business_req.project_name = 'テストプロジェクト'
        mock_business_req.description = 'テスト概要'
        mock_business_req.goals = []

        # 実行
        result = agent.execute(mock_business_req)

        # 結果の確認
        assert isinstance(result, PersonaOutput)
        assert result.persona_role == PersonaRole.DATA_ARCHITECT
        assert 'data_models' in result.deliverables
        assert 'database_design' in result.deliverables
        assert len(result.recommendations) > 0


class TestSolutionArchitectAgent:
    """ソリューションアーキテクト・エージェントのテストクラス"""

    def test_init(self):
        """初期化テスト"""
        agent = SolutionArchitectAgent()
        assert agent.persona_role == PersonaRole.SOLUTION_ARCHITECT

    def test_execute(self):
        """実行テスト"""
        agent = SolutionArchitectAgent()

        # モックのビジネス要件を作成
        mock_business_req = Mock(spec=ProjectBusinessRequirement)
        mock_business_req.stake_holders = []

        # 実行
        result = agent.execute(mock_business_req)

        # 結果の確認
        assert isinstance(result, PersonaOutput)
        assert result.persona_role == PersonaRole.SOLUTION_ARCHITECT
        assert 'system_architecture' in result.deliverables
        assert 'technology_stack' in result.deliverables
        assert len(result.recommendations) > 0

    def test_consolidate_requirements(self):
        """要件統合テスト"""
        agent = SolutionArchitectAgent()

        # モックの前段階出力を作成
        mock_outputs = [
            Mock(persona_role=PersonaRole.UX_DESIGNER, deliverables={'functional_requirements': [{'test': 'functional'}]}),
            Mock(persona_role=PersonaRole.INFRASTRUCTURE_ENGINEER, deliverables={'infrastructure_architecture': {'test': 'infra'}}),
        ]

        # 実行
        result = agent._consolidate_requirements(mock_outputs)

        # 結果の確認
        assert 'functional_requirements' in result
        assert 'infrastructure_requirements' in result
        assert len(result['functional_requirements']) == 1
        assert result['infrastructure_requirements']['test'] == 'infra'


@pytest.fixture
def sample_business_requirement():
    """サンプルビジネス要件のフィクスチャ"""
    return ProjectBusinessRequirement(
        project_name='テストプロジェクト', description='テスト用のプロジェクト説明', background='テスト用の背景情報'
    )
