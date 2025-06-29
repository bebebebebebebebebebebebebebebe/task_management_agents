"""統合ワークフローエージェント

ビジネス要件定義エージェントと要件プロセスエージェントを統合し、
シームレスなワークフローを提供します。
"""

import logging
from typing import Any, Dict, Optional

from langgraph.graph import END, START
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel

from agents.biz_requirement import create_agent_graph as create_biz_agent
from agents.core.agent_builder import AgentGraphBuilder
from agents.requirement_process import create_orchestrator_graph as create_process_agent

logger = logging.getLogger(__name__)


class IntegratedWorkflowState(BaseModel):
    """統合ワークフローの状態"""

    current_phase: str = 'init'
    business_requirement: Optional[Dict[str, Any]] = None
    technical_specification: Optional[Dict[str, Any]] = None
    workflow_complete: bool = False
    error_message: Optional[str] = None


class IntegratedWorkflowAgent(AgentGraphBuilder):
    """統合ワークフローエージェント"""

    def __init__(self, enable_persistence: bool = True, enable_auto_save: bool = True, intermediate_save: bool = True):
        super().__init__(state_object=IntegratedWorkflowState)
        self.enable_persistence = enable_persistence
        self.enable_auto_save = enable_auto_save
        self.intermediate_save = intermediate_save

        # 子エージェントのグラフ
        self.biz_agent_graph = create_biz_agent({'interactive_mode': False, 'auto_save': enable_auto_save})
        self.process_agent_graph = create_process_agent({'interactive_mode': False, 'auto_approve': False})

    def build_graph(self) -> CompiledGraph:
        """統合ワークフローグラフを構築"""

        # ノード追加
        self.workflow.add_node('start_workflow', self._start_workflow)
        self.workflow.add_node('business_requirement_phase', self._business_requirement_phase)
        self.workflow.add_node('technical_specification_phase', self._technical_specification_phase)
        self.workflow.add_node('complete_workflow', self._complete_workflow)
        self.workflow.add_node('handle_error', self._handle_error)

        # エッジ追加
        self.workflow.add_edge(START, 'start_workflow')
        self.workflow.add_edge('start_workflow', 'business_requirement_phase')

        # 条件分岐
        self.workflow.add_conditional_edges(
            'business_requirement_phase',
            self._check_business_requirement_complete,
            {'success': 'technical_specification_phase', 'error': 'handle_error'},
        )

        self.workflow.add_conditional_edges(
            'technical_specification_phase',
            self._check_technical_specification_complete,
            {'success': 'complete_workflow', 'error': 'handle_error'},
        )

        self.workflow.add_edge('complete_workflow', END)
        self.workflow.add_edge('handle_error', END)

        return self.workflow.compile()

    def _start_workflow(self, state: IntegratedWorkflowState) -> Dict[str, Any]:
        """ワークフロー開始"""
        logger.info('統合ワークフローを開始します')
        return {'current_phase': 'business_requirement', 'workflow_complete': False}

    def _business_requirement_phase(self, state: IntegratedWorkflowState) -> Dict[str, Any]:
        """ビジネス要件定義フェーズ"""
        try:
            logger.info('ビジネス要件定義フェーズを実行中...')

            # ビジネス要件定義エージェントを実行
            # ここではダミーのレスポンスを返す（実装は後で詳細化）
            business_requirement = {
                'project_name': 'Generated Project',
                'background': 'Generated background',
                'goals': ['Generated goal 1', 'Generated goal 2'],
                'status': 'completed',
            }

            if self.intermediate_save:
                logger.info('中間結果を保存しました')

            return {'current_phase': 'technical_specification', 'business_requirement': business_requirement}

        except Exception as e:
            logger.error(f'ビジネス要件定義フェーズでエラー: {e}')
            return {'current_phase': 'error', 'error_message': str(e)}

    def _technical_specification_phase(self, state: IntegratedWorkflowState) -> Dict[str, Any]:
        """技術仕様定義フェーズ"""
        try:
            logger.info('技術仕様定義フェーズを実行中...')

            if not state.business_requirement:
                raise ValueError('ビジネス要件が設定されていません')

            # 要件プロセスエージェントを実行
            # ここではダミーのレスポンスを返す（実装は後で詳細化）
            technical_specification = {
                'functional_requirements': ['Requirement 1', 'Requirement 2'],
                'non_functional_requirements': ['Performance requirement'],
                'architecture': 'Generated architecture',
                'status': 'completed',
            }

            if self.intermediate_save:
                logger.info('技術仕様を保存しました')

            return {'current_phase': 'complete', 'technical_specification': technical_specification}

        except Exception as e:
            logger.error(f'技術仕様定義フェーズでエラー: {e}')
            return {'current_phase': 'error', 'error_message': str(e)}

    def _complete_workflow(self, state: IntegratedWorkflowState) -> Dict[str, Any]:
        """ワークフロー完了"""
        logger.info('統合ワークフローが完了しました')

        if self.enable_auto_save:
            logger.info('最終結果を保存しました')

        return {'current_phase': 'completed', 'workflow_complete': True}

    def _handle_error(self, state: IntegratedWorkflowState) -> Dict[str, Any]:
        """エラーハンドリング"""
        logger.error(f'ワークフローエラー: {state.error_message}')
        return {'current_phase': 'failed', 'workflow_complete': False}

    def _check_business_requirement_complete(self, state: IntegratedWorkflowState) -> str:
        """ビジネス要件定義完了チェック"""
        if state.error_message:
            return 'error'
        if state.business_requirement and state.business_requirement.get('status') == 'completed':
            return 'success'
        return 'error'

    def _check_technical_specification_complete(self, state: IntegratedWorkflowState) -> str:
        """技術仕様定義完了チェック"""
        if state.error_message:
            return 'error'
        if state.technical_specification and state.technical_specification.get('status') == 'completed':
            return 'success'
        return 'error'
