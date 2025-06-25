"""要件定義プロセスを管理するオーケストレーター・エージェント v2.0"""

import logging
from datetime import datetime
from typing import Any, Dict

from langgraph.graph import END, START

from agents.core.agent_builder import AgentGraphBuilder
from agents.requirement_process.error_handler import ErrorHandler, ProcessError
from agents.requirement_process.personas.data_architect import DataArchitectAgent
from agents.requirement_process.personas.infrastructure_engineer import InfrastructureEngineerAgent
from agents.requirement_process.personas.qa_engineer import QAEngineerAgent
from agents.requirement_process.personas.security_specialist import SecuritySpecialistAgent
from agents.requirement_process.personas.solution_architect import SolutionArchitectAgent
from agents.requirement_process.personas.system_analyst import SystemAnalystAgent
from agents.requirement_process.personas.ux_designer import UXDesignerAgent
from agents.requirement_process.review_manager import ReviewManager
from agents.requirement_process.schemas import (
    PersonaRole,
    RequirementDocument,
    RequirementProcessPhase,
    RequirementProcessState,
    ReviewDecision,
    ReviewStatus,
)

logger = logging.getLogger(__name__)


class RequirementProcessOrchestratorAgent(AgentGraphBuilder):
    """要件定義プロセスを管理するオーケストレーター・エージェント v2.0

    v2.0新機能:
    - ユーザーレビューゲート機能
    - 高度なエラーハンドリングとリトライ
    - 条件分岐制御
    - バージョン管理
    """

    def __init__(self, interactive_mode: bool = True, auto_approve: bool = False):
        super().__init__(state_object=RequirementProcessState)
        self._setup_persona_agents()

        # v2.0新機能マネージャー
        self.review_manager = ReviewManager()
        self.error_handler = ErrorHandler()

        # 設定
        self.interactive_mode = interactive_mode
        self.auto_approve = auto_approve

    def _get_state_value(self, state, key, default=None):
        """状態から値を安全に取得（dictとPydanticモデル両方に対応）"""
        return getattr(state, key, default) or state.get(key, default) if hasattr(state, 'get') else getattr(state, key, default)

    def _setup_persona_agents(self):
        """ペルソナエージェントのインスタンスを準備"""
        self.persona_agents = {
            PersonaRole.SYSTEM_ANALYST: SystemAnalystAgent(),
            PersonaRole.UX_DESIGNER: UXDesignerAgent(),
            PersonaRole.QA_ENGINEER: QAEngineerAgent(),
            PersonaRole.INFRASTRUCTURE_ENGINEER: InfrastructureEngineerAgent(),
            PersonaRole.SECURITY_SPECIALIST: SecuritySpecialistAgent(),
            PersonaRole.DATA_ARCHITECT: DataArchitectAgent(),
            PersonaRole.SOLUTION_ARCHITECT: SolutionArchitectAgent(),
        }

    def build_graph(self):
        """オーケストレーター・エージェントのワークフローグラフを構築 v2.0"""

        # 基本ノード
        self.workflow.add_node('initialize', self._initialize_process)
        self.workflow.add_node('system_analysis', self._execute_system_analysis)
        self.workflow.add_node('functional_req_phase', self._execute_functional_requirements)
        self.workflow.add_node('non_functional_req_phase', self._execute_non_functional_requirements)
        self.workflow.add_node('data_arch_phase', self._execute_data_architecture)
        self.workflow.add_node('solution_arch_phase', self._execute_solution_architecture)
        self.workflow.add_node('integrate_results', self._integrate_results)
        self.workflow.add_node('generate_document', self._generate_document)

        # v2.0新機能: レビューゲートノード
        self.workflow.add_node('functional_review', self._review_functional_requirements)
        self.workflow.add_node('non_functional_review', self._review_non_functional_requirements)
        self.workflow.add_node('solution_review', self._review_solution_architecture)

        # v2.0新機能: 修正処理ノード
        self.workflow.add_node('revise_functional', self._revise_functional_requirements)
        self.workflow.add_node('revise_non_functional', self._revise_non_functional_requirements)
        self.workflow.add_node('revise_solution', self._revise_solution_architecture)

        # 基本フロー
        self.workflow.add_edge(START, 'initialize')
        self.workflow.add_edge('initialize', 'system_analysis')
        self.workflow.add_edge('system_analysis', 'functional_req_phase')

        # v2.0新機能: 条件分岐エッジ
        if self.interactive_mode:
            # レビューゲート付きフロー
            self.workflow.add_edge('functional_req_phase', 'functional_review')
            self.workflow.add_conditional_edges(
                'functional_review',
                self._decide_functional_next_step,
                {
                    'approved': 'non_functional_req_phase',
                    'revise': 'revise_functional',
                },
            )
            self.workflow.add_edge('revise_functional', 'functional_review')

            self.workflow.add_edge('non_functional_req_phase', 'non_functional_review')
            self.workflow.add_conditional_edges(
                'non_functional_review',
                self._decide_non_functional_next_step,
                {
                    'approved': 'data_arch_phase',
                    'revise': 'revise_non_functional',
                },
            )
            self.workflow.add_edge('revise_non_functional', 'non_functional_review')

            self.workflow.add_edge('solution_arch_phase', 'solution_review')
            self.workflow.add_conditional_edges(
                'solution_review',
                self._decide_solution_next_step,
                {
                    'approved': 'integrate_results',
                    'revise': 'revise_solution',
                },
            )
            self.workflow.add_edge('revise_solution', 'solution_review')
        else:
            # 従来の直線フロー
            self.workflow.add_edge('functional_req_phase', 'non_functional_req_phase')
            self.workflow.add_edge('solution_arch_phase', 'integrate_results')

        self.workflow.add_edge('data_arch_phase', 'solution_arch_phase')
        self.workflow.add_edge('integrate_results', 'generate_document')
        self.workflow.add_edge('generate_document', END)

        return self.workflow.compile()

    def _initialize_process(self, state: RequirementProcessState) -> Dict[str, Any]:
        """プロセスの初期化 v2.0"""
        logger.info('要件定義プロセス v2.0 を初期化しています...')

        # v2.0設定
        initial_update = {
            'current_phase': RequirementProcessPhase.SYSTEM_ANALYSIS,
            'is_interactive_mode': self.interactive_mode,
            'auto_approve': self.auto_approve,
            'document_version': '1.0',
            'version_history': ['1.0 - 初期版'],
            'retry_attempts': {},
            'phase_reviews': [],
            'messages': [{'role': 'system', 'content': f'要件定義プロセス v2.0 を開始しました (対話モード: {self.interactive_mode})'}],
        }

        logger.info(f'対話モード: {self.interactive_mode}, 自動承認: {self.auto_approve}')
        return initial_update

    def _execute_system_analysis(self, state: RequirementProcessState) -> Dict[str, Any]:
        """システム分析フェーズの実行"""
        logger.info('システム分析フェーズを実行しています...')

        # 状態オブジェクトの安全なアクセス（dictとPydanticモデル両方に対応）
        business_requirement = self._get_state_value(state, 'business_requirement')
        persona_outputs = self._get_state_value(state, 'persona_outputs', [])
        completed_phases = self._get_state_value(state, 'completed_phases', [])

        # システムアナリストエージェントを呼び出し
        analyst_output = self.persona_agents[PersonaRole.SYSTEM_ANALYST].execute(business_requirement)

        return {
            'current_phase': RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            'persona_outputs': persona_outputs + [analyst_output],
            'completed_phases': completed_phases + [RequirementProcessPhase.SYSTEM_ANALYSIS],
            'messages': [{'role': 'system', 'content': 'システム分析が完了しました'}],
        }

    def _execute_functional_requirements(self, state: RequirementProcessState) -> Dict[str, Any]:
        """機能要件定義フェーズの実行"""
        logger.info('機能要件定義フェーズを実行しています...')

        # 状態オブジェクトの安全なアクセス
        business_requirement = self._get_state_value(state, 'business_requirement')
        persona_outputs = self._get_state_value(state, 'persona_outputs', [])
        completed_phases = self._get_state_value(state, 'completed_phases', [])

        # UXデザイナーとQAエンジニアを並行実行
        ux_output = self.persona_agents[PersonaRole.UX_DESIGNER].execute(business_requirement, persona_outputs)

        qa_output = self.persona_agents[PersonaRole.QA_ENGINEER].execute(business_requirement, persona_outputs)

        return {
            'current_phase': RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS,
            'persona_outputs': persona_outputs + [ux_output, qa_output],
            'completed_phases': completed_phases + [RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS],
            'messages': [{'role': 'system', 'content': '機能要件定義が完了しました'}],
        }

    def _execute_non_functional_requirements(self, state: RequirementProcessState) -> Dict[str, Any]:
        """非機能要件定義フェーズの実行"""
        logger.info('非機能要件定義フェーズを実行しています...')

        # インフラエンジニアとセキュリティスペシャリストを並行実行
        infra_output = self.persona_agents[PersonaRole.INFRASTRUCTURE_ENGINEER].execute(
            self._get_state_value(state, 'business_requirement'), self._get_state_value(state, 'persona_outputs', [])
        )

        security_output = self.persona_agents[PersonaRole.SECURITY_SPECIALIST].execute(
            self._get_state_value(state, 'business_requirement'), self._get_state_value(state, 'persona_outputs', [])
        )

        return {
            'current_phase': RequirementProcessPhase.DATA_ARCHITECTURE,
            'persona_outputs': self._get_state_value(state, 'persona_outputs', []) + [infra_output, security_output],
            'completed_phases': self._get_state_value(state, 'completed_phases', [])
            + [RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS],
            'messages': [{'role': 'system', 'content': '非機能要件定義が完了しました'}],
        }

    def _execute_data_architecture(self, state: RequirementProcessState) -> Dict[str, Any]:
        """データアーキテクチャ設計フェーズの実行"""
        logger.info('データアーキテクチャ設計フェーズを実行しています...')

        # データアーキテクトエージェントを呼び出し
        data_output = self.persona_agents[PersonaRole.DATA_ARCHITECT].execute(
            self._get_state_value(state, 'business_requirement'), self._get_state_value(state, 'persona_outputs', [])
        )

        return {
            'current_phase': RequirementProcessPhase.SOLUTION_ARCHITECTURE,
            'persona_outputs': self._get_state_value(state, 'persona_outputs', []) + [data_output],
            'completed_phases': self._get_state_value(state, 'completed_phases', []) + [RequirementProcessPhase.DATA_ARCHITECTURE],
            'messages': [{'role': 'system', 'content': 'データアーキテクチャ設計が完了しました'}],
        }

    def _execute_solution_architecture(self, state: RequirementProcessState) -> Dict[str, Any]:
        """ソリューションアーキテクチャ設計フェーズの実行"""
        logger.info('ソリューションアーキテクチャ設計フェーズを実行しています...')

        # ソリューションアーキテクトエージェントを呼び出し
        solution_output = self.persona_agents[PersonaRole.SOLUTION_ARCHITECT].execute(
            self._get_state_value(state, 'business_requirement'), self._get_state_value(state, 'persona_outputs', [])
        )

        return {
            'current_phase': RequirementProcessPhase.INTEGRATION,
            'persona_outputs': self._get_state_value(state, 'persona_outputs', []) + [solution_output],
            'completed_phases': self._get_state_value(state, 'completed_phases', []) + [RequirementProcessPhase.SOLUTION_ARCHITECTURE],
            'messages': [{'role': 'system', 'content': 'ソリューションアーキテクチャ設計が完了しました'}],
        }

    def _integrate_results(self, state: RequirementProcessState) -> Dict[str, Any]:
        """各エージェントの成果物を統合"""
        logger.info('成果物を統合しています...')

        # 各ペルソナの成果物を統合
        integrated_data = self._consolidate_outputs(self._get_state_value(state, 'persona_outputs', []))

        return {
            'current_phase': RequirementProcessPhase.COMPLETE,
            'completed_phases': self._get_state_value(state, 'completed_phases', []) + [RequirementProcessPhase.INTEGRATION],
            'messages': [{'role': 'system', 'content': '成果物統合が完了しました'}],
            **integrated_data,
        }

    def _generate_document(self, state: RequirementProcessState) -> Dict[str, Any]:
        """最終的な要件定義書を生成"""
        logger.info('要件定義書を生成しています...')

        document = self._create_requirement_document(state)
        output_path = self._save_document(document)

        return {
            'final_document': document.sections,
            'output_file_path': output_path,
            'messages': [{'role': 'system', 'content': f'要件定義書が生成されました: {output_path}'}],
        }

    def _consolidate_outputs(self, persona_outputs) -> Dict[str, Any]:
        """ペルソナエージェントの出力を統合"""
        consolidated = {
            'functional_requirements': [],
            'non_functional_requirements': [],
            'data_models': [],
            'table_definitions': [],
            'system_architecture': None,
        }

        for output in persona_outputs:
            deliverables = output.deliverables

            if 'functional_requirements' in deliverables:
                consolidated['functional_requirements'].extend(deliverables['functional_requirements'])

            if 'non_functional_requirements' in deliverables:
                consolidated['non_functional_requirements'].extend(deliverables['non_functional_requirements'])

            if 'data_models' in deliverables:
                consolidated['data_models'].extend(deliverables['data_models'])

            if 'table_definitions' in deliverables:
                consolidated['table_definitions'].extend(deliverables['table_definitions'])

            if 'system_architecture' in deliverables:
                consolidated['system_architecture'] = deliverables['system_architecture']

        return consolidated

    def _create_requirement_document(self, state: RequirementProcessState) -> RequirementDocument:
        """要件定義書を作成"""
        sections = {
            '1. 概要': self._generate_overview_section(state),
            '2. 機能要件': self._generate_functional_requirements_section(state),
            '3. 非機能要件': self._generate_non_functional_requirements_section(state),
            '4. データ設計': self._generate_data_design_section(state),
            '5. システム構成': self._generate_system_architecture_section(state),
            '6. 実装方針': self._generate_implementation_strategy_section(state),
        }

        return RequirementDocument(
            title=f'{state["business_requirement"].project_name} 要件定義書',
            sections=sections,
            created_at=datetime.now().isoformat(),
            version='1.0',
        )

    def _generate_overview_section(self, state: RequirementProcessState) -> str:
        """概要セクションを生成"""
        br = state['business_requirement']
        return f"""
## プロジェクト概要

**プロジェクト名**: {br.project_name or 'N/A'}

**概要**: {br.description or 'N/A'}

**背景**: {br.background or 'N/A'}

## 目標
{self._format_goals(br.goals) if br.goals else 'N/A'}

## スコープ
{self._format_scopes(br.scopes) if br.scopes else 'N/A'}
"""

    def _generate_functional_requirements_section(self, state: RequirementProcessState) -> str:
        """機能要件セクションを生成"""
        content = '## 機能要件一覧\n\n'

        for i, req in enumerate(state['functional_requirements'], 1):
            content += f"""
### {i}. {req.user_story}

**優先度**: {req.priority}
**複雑度**: {req.complexity}

**受け入れ基準**:
{self._format_list(req.acceptance_criteria)}

---
"""

        return content

    def _generate_non_functional_requirements_section(self, state: RequirementProcessState) -> str:
        """非機能要件セクションを生成"""
        content = '## 非機能要件一覧\n\n'

        by_category = {}
        for req in state['non_functional_requirements']:
            if req.category not in by_category:
                by_category[req.category] = []
            by_category[req.category].append(req)

        for category, reqs in by_category.items():
            content += f'### {category}\n\n'
            for req in reqs:
                content += f"""
**要件**: {req.requirement}
**目標値**: {req.target_value}
**テスト方法**: {req.test_method}

"""

        return content

    def _generate_data_design_section(self, state: RequirementProcessState) -> str:
        """データ設計セクションを生成"""
        content = '## データ設計\n\n'

        if state['data_models']:
            content += '### 論理データモデル\n\n'
            for model in state['data_models']:
                content += f"""
#### {model.entity_name}

**属性**:
{self._format_list(model.attributes)}

**関連**:
{self._format_list(model.relationships)}

"""

        if state['table_definitions']:
            content += '### テーブル定義\n\n'
            for table in state['table_definitions']:
                content += f"""
#### {table.table_name}

**カラム定義**:
| カラム名 | データ型 | 制約 |
|----------|----------|------|
"""
                for col in table.columns:
                    content += f'| {col.get("name", "")} | {col.get("type", "")} | {col.get("constraint", "")} |\n'

                content += f"""
**制約**:
{self._format_list(table.constraints)}

"""

        return content

    def _generate_system_architecture_section(self, state: RequirementProcessState) -> str:
        """システム構成セクションを生成"""
        if not state['system_architecture']:
            return '## システム構成\n\nTBD\n'

        arch = state['system_architecture']
        content = f"""
## システム構成

**アーキテクチャタイプ**: {arch.architecture_type}

**コンポーネント**:
{self._format_list(arch.components)}

**技術スタック**:
"""
        for key, value in arch.technology_stack.items():
            content += f'- **{key}**: {value}\n'

        content += f"""
**デプロイメント戦略**: {arch.deployment_strategy}
"""

        return content

    def _generate_implementation_strategy_section(self, state: RequirementProcessState) -> str:
        """実装方針セクションを生成"""
        content = '## 実装方針\n\n'

        # 各ペルソナの推奨事項を統合
        recommendations = []
        for output in state['persona_outputs']:
            recommendations.extend(output.recommendations)

        if recommendations:
            content += '### 推奨事項\n'
            content += self._format_list(recommendations)

        # 懸念事項も追加
        concerns = []
        for output in state['persona_outputs']:
            concerns.extend(output.concerns)

        if concerns:
            content += '\n### 懸念事項・リスク\n'
            content += self._format_list(concerns)

        return content

    def _format_goals(self, goals) -> str:
        """目標をフォーマット"""
        content = ''
        for i, goal in enumerate(goals, 1):
            content += f"""
{i}. **{goal.objective}**
   - 根拠: {goal.rationale}
   - KPI: {goal.kpi or 'N/A'}
"""
        return content

    def _format_scopes(self, scopes) -> str:
        """スコープをフォーマット"""
        content = ''
        for i, scope in enumerate(scopes, 1):
            content += f"""
{i}. **対象**: {scope.in_scope}
   - **対象外**: {scope.out_of_scope}
"""
        return content

    def _format_list(self, items) -> str:
        """リストをマークダウン形式でフォーマット"""
        return '\n'.join([f'- {item}' for item in items])

    def _save_document(self, document: RequirementDocument) -> str:
        """ドキュメントをファイルに保存"""
        from pathlib import Path

        output_dir = Path('outputs')
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'requirement_specification_{timestamp}.md'
        file_path = output_dir / filename

        # マークダウンファイルとして保存
        content = f'# {document.title}\n\n'
        content += f'**作成日時**: {document.created_at}\n'
        content += f'**バージョン**: {document.version}\n\n'

        for section_title, section_content in document.sections.items():
            content += f'# {section_title}\n\n{section_content}\n\n'

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f'要件定義書を保存しました: {file_path}')
        return str(file_path)

    # =====================================
    # v2.0新機能: レビューゲート機能
    # =====================================

    def _review_functional_requirements(self, state: RequirementProcessState) -> Dict[str, Any]:
        """機能要件のレビューゲート"""
        logger.info('機能要件のユーザーレビューを開始します...')

        # レビュー対象の内容を準備
        functional_requirements = state.get('functional_requirements', [])
        persona_outputs = state.get('persona_outputs', [])
        content = {
            'functional_requirements': functional_requirements,
            'persona_outputs': [output for output in persona_outputs if output.persona_role in ['ux_designer', 'qa_engineer']],
        }

        # フェーズレビューを作成
        phase_review = self.review_manager.create_phase_review(
            RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            content,
            f'{len(functional_requirements)}個の機能要件が定義されました',
        )

        # ユーザーレビューの実行
        if self.auto_approve:
            feedback = self.review_manager.simulate_user_feedback(RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS, auto_approve=True)
        else:
            # レビュー内容をプレゼンテーション
            presentation = self.review_manager.present_for_review(phase_review, content)
            logger.info(f'レビュー内容:\n{presentation}')

            # 模擬ユーザーフィードバック（実際の実装では入力待ち）
            feedback = self.review_manager.simulate_user_feedback(RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS)

        # レビュー結果を更新
        phase_review = self.review_manager.update_phase_review(phase_review, feedback)

        return {
            'current_phase': RequirementProcessPhase.FUNCTIONAL_REVIEW,
            'pending_review': phase_review,
            'review_feedback': feedback,
            'phase_reviews': state.get('phase_reviews', []) + [phase_review],
            'messages': [{'role': 'system', 'content': f'機能要件レビュー完了: {feedback.decision}'}],
        }

    def _review_non_functional_requirements(self, state: RequirementProcessState) -> Dict[str, Any]:
        """非機能要件のレビューゲート"""
        logger.info('非機能要件のユーザーレビューを開始します...')

        non_functional_requirements = state.get('non_functional_requirements', [])
        persona_outputs = state.get('persona_outputs', [])
        content = {
            'non_functional_requirements': non_functional_requirements,
            'persona_outputs': [
                output for output in persona_outputs if output.persona_role in ['infrastructure_engineer', 'security_specialist']
            ],
        }

        phase_review = self.review_manager.create_phase_review(
            RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS,
            content,
            f'{len(non_functional_requirements)}個の非機能要件が定義されました',
        )

        if self.auto_approve:
            feedback = self.review_manager.simulate_user_feedback(
                RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS, auto_approve=True
            )
        else:
            presentation = self.review_manager.present_for_review(phase_review, content)
            logger.info(f'レビュー内容:\n{presentation}')
            feedback = self.review_manager.simulate_user_feedback(RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS)

        phase_review = self.review_manager.update_phase_review(phase_review, feedback)

        return {
            'current_phase': RequirementProcessPhase.NON_FUNCTIONAL_REVIEW,
            'pending_review': phase_review,
            'review_feedback': feedback,
            'phase_reviews': state.get('phase_reviews', []) + [phase_review],
            'messages': [{'role': 'system', 'content': f'非機能要件レビュー完了: {feedback.decision}'}],
        }

    def _review_solution_architecture(self, state: RequirementProcessState) -> Dict[str, Any]:
        """ソリューションアーキテクチャのレビューゲート"""
        logger.info('ソリューションアーキテクチャのユーザーレビューを開始します...')

        system_architecture = state.get('system_architecture')
        persona_outputs = state.get('persona_outputs', [])
        content = {
            'system_architecture': system_architecture,
            'persona_outputs': [output for output in persona_outputs if output.persona_role == 'solution_architect'],
        }

        phase_review = self.review_manager.create_phase_review(
            RequirementProcessPhase.SOLUTION_ARCHITECTURE, content, 'システム構成と技術スタックが提案されました'
        )

        if self.auto_approve:
            feedback = self.review_manager.simulate_user_feedback(RequirementProcessPhase.SOLUTION_ARCHITECTURE, auto_approve=True)
        else:
            presentation = self.review_manager.present_for_review(phase_review, content)
            logger.info(f'レビュー内容:\n{presentation}')
            feedback = self.review_manager.simulate_user_feedback(RequirementProcessPhase.SOLUTION_ARCHITECTURE)

        phase_review = self.review_manager.update_phase_review(phase_review, feedback)

        return {
            'current_phase': RequirementProcessPhase.SOLUTION_REVIEW,
            'pending_review': phase_review,
            'review_feedback': feedback,
            'phase_reviews': state.get('phase_reviews', []) + [phase_review],
            'messages': [{'role': 'system', 'content': f'ソリューションアーキテクチャレビュー完了: {feedback.decision}'}],
        }

    # =====================================
    # v2.0新機能: 条件分岐判定
    # =====================================

    def _decide_functional_next_step(self, state: RequirementProcessState) -> str:
        """機能要件レビュー後の次ステップ判定"""
        review_feedback = state.get('review_feedback')
        if review_feedback and review_feedback.decision == ReviewDecision.APPROVE:
            return 'approved'
        return 'revise'

    def _decide_non_functional_next_step(self, state: RequirementProcessState) -> str:
        """非機能要件レビュー後の次ステップ判定"""
        review_feedback = state.get('review_feedback')
        if review_feedback and review_feedback.decision == ReviewDecision.APPROVE:
            return 'approved'
        return 'revise'

    def _decide_solution_next_step(self, state: RequirementProcessState) -> str:
        """ソリューションアーキテクチャレビュー後の次ステップ判定"""
        review_feedback = state.get('review_feedback')
        if review_feedback and review_feedback.decision == ReviewDecision.APPROVE:
            return 'approved'
        return 'revise'

    # =====================================
    # v2.0新機能: 修正処理
    # =====================================

    def _revise_functional_requirements(self, state: RequirementProcessState) -> Dict[str, Any]:
        """機能要件の修正処理"""
        logger.info('機能要件の修正を実行しています...')

        review_feedback = state.get('review_feedback')
        if review_feedback:
            # 修正指示を生成
            revision_instructions = self.review_manager.generate_revision_instructions(review_feedback)
            logger.info(f'修正指示: {revision_instructions}')

            # リトライカウント更新
            retry_attempts = state.get('retry_attempts', {})
            retry_count = retry_attempts.get('functional_requirements', 0) + 1

            # バージョン更新
            document_version = state.get('document_version', '1.0')
            new_version = self._increment_version(document_version)

            # 修正実行（実際の実装では修正されたペルソナエージェント再実行）
            return {
                'current_phase': RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
                'retry_attempts': {**retry_attempts, 'functional_requirements': retry_count},
                'document_version': new_version,
                'version_history': state.get('version_history', []) + [f'{new_version} - 機能要件修正'],
                'revision_count': state.get('revision_count', 0) + 1,
                'messages': [{'role': 'system', 'content': f'機能要件を修正中 (試行 {retry_count})'}],
            }

        return {'messages': [{'role': 'system', 'content': '修正処理をスキップしました'}]}

    def _revise_non_functional_requirements(self, state: RequirementProcessState) -> Dict[str, Any]:
        """非機能要件の修正処理"""
        logger.info('非機能要件の修正を実行しています...')

        review_feedback = state.get('review_feedback')
        if review_feedback:
            revision_instructions = self.review_manager.generate_revision_instructions(review_feedback)
            logger.info(f'修正指示: {revision_instructions}')

            retry_attempts = state.get('retry_attempts', {})
            retry_count = retry_attempts.get('non_functional_requirements', 0) + 1
            document_version = state.get('document_version', '1.0')
            new_version = self._increment_version(document_version)

            return {
                'current_phase': RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS,
                'retry_attempts': {**retry_attempts, 'non_functional_requirements': retry_count},
                'document_version': new_version,
                'version_history': state.get('version_history', []) + [f'{new_version} - 非機能要件修正'],
                'revision_count': state.get('revision_count', 0) + 1,
                'messages': [{'role': 'system', 'content': f'非機能要件を修正中 (試行 {retry_count})'}],
            }

        return {'messages': [{'role': 'system', 'content': '修正処理をスキップしました'}]}

    def _revise_solution_architecture(self, state: RequirementProcessState) -> Dict[str, Any]:
        """ソリューションアーキテクチャの修正処理"""
        logger.info('ソリューションアーキテクチャの修正を実行しています...')

        review_feedback = state.get('review_feedback')
        if review_feedback:
            revision_instructions = self.review_manager.generate_revision_instructions(review_feedback)
            logger.info(f'修正指示: {revision_instructions}')

            retry_attempts = state.get('retry_attempts', {})
            retry_count = retry_attempts.get('solution_architecture', 0) + 1
            document_version = state.get('document_version', '1.0')
            new_version = self._increment_version(document_version)

            return {
                'current_phase': RequirementProcessPhase.SOLUTION_ARCHITECTURE,
                'retry_attempts': {**retry_attempts, 'solution_architecture': retry_count},
                'document_version': new_version,
                'version_history': state.get('version_history', []) + [f'{new_version} - アーキテクチャ修正'],
                'revision_count': state.get('revision_count', 0) + 1,
                'messages': [{'role': 'system', 'content': f'ソリューションアーキテクチャを修正中 (試行 {retry_count})'}],
            }

        return {'messages': [{'role': 'system', 'content': '修正処理をスキップしました'}]}

    # =====================================
    # v2.0新機能: バージョン管理
    # =====================================

    def _increment_version(self, current_version: str) -> str:
        """バージョン番号を増分"""
        try:
            major, minor = current_version.split('.')
            return f'{major}.{int(minor) + 1}'
        except (ValueError, IndexError):
            return '1.1'
