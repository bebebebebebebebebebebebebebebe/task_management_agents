"""要件定義プロセスを管理するオーケストレーター・エージェント"""

import logging
from datetime import datetime
from typing import Any, Dict

from langgraph.graph import END, START

from agents.core.agent_builder import AgentGraphBuilder
from agents.requirement_process.personas.data_architect import DataArchitectAgent
from agents.requirement_process.personas.infrastructure_engineer import InfrastructureEngineerAgent
from agents.requirement_process.personas.qa_engineer import QAEngineerAgent
from agents.requirement_process.personas.security_specialist import SecuritySpecialistAgent
from agents.requirement_process.personas.solution_architect import SolutionArchitectAgent
from agents.requirement_process.personas.system_analyst import SystemAnalystAgent
from agents.requirement_process.personas.ux_designer import UXDesignerAgent
from agents.requirement_process.schemas import (
    PersonaRole,
    RequirementDocument,
    RequirementProcessPhase,
    RequirementProcessState,
)

logger = logging.getLogger(__name__)


class RequirementProcessOrchestratorAgent(AgentGraphBuilder):
    """要件定義プロセスを管理するオーケストレーター・エージェント"""

    def __init__(self):
        super().__init__(state_object=RequirementProcessState)
        self._setup_persona_agents()

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
        """オーケストレーター・エージェントのワークフローグラフを構築"""

        # ノードを追加
        self.workflow.add_node('initialize', self._initialize_process)
        self.workflow.add_node('system_analysis', self._execute_system_analysis)
        self.workflow.add_node('functional_req_phase', self._execute_functional_requirements)
        self.workflow.add_node('non_functional_req_phase', self._execute_non_functional_requirements)
        self.workflow.add_node('data_arch_phase', self._execute_data_architecture)
        self.workflow.add_node('solution_arch_phase', self._execute_solution_architecture)
        self.workflow.add_node('integrate_results', self._integrate_results)
        self.workflow.add_node('generate_document', self._generate_document)

        # エッジを追加
        self.workflow.add_edge(START, 'initialize')
        self.workflow.add_edge('initialize', 'system_analysis')
        self.workflow.add_edge('system_analysis', 'functional_req_phase')
        self.workflow.add_edge('functional_req_phase', 'non_functional_req_phase')
        self.workflow.add_edge('non_functional_req_phase', 'data_arch_phase')
        self.workflow.add_edge('data_arch_phase', 'solution_arch_phase')
        self.workflow.add_edge('solution_arch_phase', 'integrate_results')
        self.workflow.add_edge('integrate_results', 'generate_document')
        self.workflow.add_edge('generate_document', END)

        return self.workflow.compile()

    def _initialize_process(self, state: RequirementProcessState) -> Dict[str, Any]:
        """プロセスの初期化"""
        logger.info('要件定義プロセスを初期化しています...')

        return {
            'current_phase': RequirementProcessPhase.SYSTEM_ANALYSIS,
            'messages': [{'role': 'system', 'content': '要件定義プロセスを開始しました'}],
        }

    def _execute_system_analysis(self, state: RequirementProcessState) -> Dict[str, Any]:
        """システム分析フェーズの実行"""
        logger.info('システム分析フェーズを実行しています...')

        # システムアナリストエージェントを呼び出し
        analyst_output = self.persona_agents[PersonaRole.SYSTEM_ANALYST].execute(state['business_requirement'])

        return {
            'current_phase': RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            'persona_outputs': state['persona_outputs'] + [analyst_output],
            'completed_phases': state['completed_phases'] + [RequirementProcessPhase.SYSTEM_ANALYSIS],
            'messages': [{'role': 'system', 'content': 'システム分析が完了しました'}],
        }

    def _execute_functional_requirements(self, state: RequirementProcessState) -> Dict[str, Any]:
        """機能要件定義フェーズの実行"""
        logger.info('機能要件定義フェーズを実行しています...')

        # UXデザイナーとQAエンジニアを並行実行
        ux_output = self.persona_agents[PersonaRole.UX_DESIGNER].execute(state['business_requirement'], state['persona_outputs'])

        qa_output = self.persona_agents[PersonaRole.QA_ENGINEER].execute(state['business_requirement'], state['persona_outputs'])

        return {
            'current_phase': RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS,
            'persona_outputs': state['persona_outputs'] + [ux_output, qa_output],
            'completed_phases': state['completed_phases'] + [RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS],
            'messages': [{'role': 'system', 'content': '機能要件定義が完了しました'}],
        }

    def _execute_non_functional_requirements(self, state: RequirementProcessState) -> Dict[str, Any]:
        """非機能要件定義フェーズの実行"""
        logger.info('非機能要件定義フェーズを実行しています...')

        # インフラエンジニアとセキュリティスペシャリストを並行実行
        infra_output = self.persona_agents[PersonaRole.INFRASTRUCTURE_ENGINEER].execute(
            state['business_requirement'], state['persona_outputs']
        )

        security_output = self.persona_agents[PersonaRole.SECURITY_SPECIALIST].execute(
            state['business_requirement'], state['persona_outputs']
        )

        return {
            'current_phase': RequirementProcessPhase.DATA_ARCHITECTURE,
            'persona_outputs': state['persona_outputs'] + [infra_output, security_output],
            'completed_phases': state['completed_phases'] + [RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS],
            'messages': [{'role': 'system', 'content': '非機能要件定義が完了しました'}],
        }

    def _execute_data_architecture(self, state: RequirementProcessState) -> Dict[str, Any]:
        """データアーキテクチャ設計フェーズの実行"""
        logger.info('データアーキテクチャ設計フェーズを実行しています...')

        # データアーキテクトエージェントを呼び出し
        data_output = self.persona_agents[PersonaRole.DATA_ARCHITECT].execute(state['business_requirement'], state['persona_outputs'])

        return {
            'current_phase': RequirementProcessPhase.SOLUTION_ARCHITECTURE,
            'persona_outputs': state['persona_outputs'] + [data_output],
            'completed_phases': state['completed_phases'] + [RequirementProcessPhase.DATA_ARCHITECTURE],
            'messages': [{'role': 'system', 'content': 'データアーキテクチャ設計が完了しました'}],
        }

    def _execute_solution_architecture(self, state: RequirementProcessState) -> Dict[str, Any]:
        """ソリューションアーキテクチャ設計フェーズの実行"""
        logger.info('ソリューションアーキテクチャ設計フェーズを実行しています...')

        # ソリューションアーキテクトエージェントを呼び出し
        solution_output = self.persona_agents[PersonaRole.SOLUTION_ARCHITECT].execute(
            state['business_requirement'], state['persona_outputs']
        )

        return {
            'current_phase': RequirementProcessPhase.INTEGRATION,
            'persona_outputs': state['persona_outputs'] + [solution_output],
            'completed_phases': state['completed_phases'] + [RequirementProcessPhase.SOLUTION_ARCHITECTURE],
            'messages': [{'role': 'system', 'content': 'ソリューションアーキテクチャ設計が完了しました'}],
        }

    def _integrate_results(self, state: RequirementProcessState) -> Dict[str, Any]:
        """各エージェントの成果物を統合"""
        logger.info('成果物を統合しています...')

        # 各ペルソナの成果物を統合
        integrated_data = self._consolidate_outputs(state['persona_outputs'])

        return {
            'current_phase': RequirementProcessPhase.COMPLETE,
            'completed_phases': state['completed_phases'] + [RequirementProcessPhase.INTEGRATION],
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
