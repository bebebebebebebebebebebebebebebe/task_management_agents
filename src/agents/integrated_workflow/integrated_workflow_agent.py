"""統合ワークフローエージェント

このモジュールは、ビジネス要件収集から要件定義書生成までの
一元化されたワークフローを提供します。

ワークフロー概要:
1. ビジネス要件収集 (BizRequirementAgent)
2. 要件定義プロセス実行 (RequirementProcessOrchestratorAgent)
3. 統合された要件定義書の出力

統合により以下の利点が得られます:
- シームレスなユーザー体験
- データフローの自動化
- エラーハンドリングの統一
- プロセス全体の可視化
"""

import asyncio
import json
import os
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph

from agents.biz_requirement.biz_requirement_agent import BizRequirementAgent
from agents.biz_requirement.schemas import ProjectBusinessRequirement, RequirementState
from agents.core.agent_builder import AgentGraphBuilder
from agents.requirement_process.main import run_requirement_process
from agents.requirement_process.schemas import RequirementProcessState
from utils.logger import get_logger

logger = get_logger(__name__)


class IntegratedWorkflowState(RequirementState):
    """統合ワークフローの状態管理

    ビジネス要件収集と要件定義プロセスの両方の状態を管理します。
    """

    workflow_phase: Optional[str] = None  # 'biz_requirement' | 'requirement_process' | 'completion'
    business_requirement: Optional[ProjectBusinessRequirement] = None
    requirement_process_result: Optional[Dict[str, Any]] = None
    final_output_path: Optional[str] = None
    error_message: Optional[str] = None


class IntegratedWorkflowAgent(AgentGraphBuilder):
    """統合ワークフローエージェント

    ビジネス要件収集から要件定義書生成までの
    全プロセスを統合管理するエージェントです。

    Features:
    - ビジネス要件エージェントとの連携
    - 要件定義プロセスエージェントとの連携
    - エラーハンドリングとリカバリー
    - 進捗状況の可視化
    - 統合された出力ドキュメント
    """

    def __init__(self):
        """IntegratedWorkflowAgentを初期化します"""
        super().__init__(state_object=IntegratedWorkflowState)
        self._compiled_graph = None
        self._biz_requirement_agent = BizRequirementAgent()
        self._checkpointer = InMemorySaver()

    def build_graph(self) -> CompiledGraph:
        """統合ワークフローグラフを構築します"""
        if self._compiled_graph is not None:
            return self._compiled_graph

        # ノードの追加
        self.workflow.add_node('start', self._start_node)
        self.workflow.add_node('biz_requirement_collection', self._biz_requirement_collection_node)
        self.workflow.add_node('requirement_process_execution', self._requirement_process_execution_node)
        self.workflow.add_node('document_integration', self._document_integration_node)
        self.workflow.add_node('error_handler', self._error_handler_node)
        self.workflow.add_node('completion', self._completion_node)

        # エントリーポイント設定
        self.workflow.set_entry_point('start')

        # エッジの設定
        self.workflow.add_edge('start', 'biz_requirement_collection')
        self.workflow.add_conditional_edges(
            'biz_requirement_collection',
            self._decide_after_biz_requirement,
            {
                'requirement_process': 'requirement_process_execution',
                'continue_biz': 'biz_requirement_collection',
                'error': 'error_handler',
            },
        )
        self.workflow.add_conditional_edges(
            'requirement_process_execution',
            self._decide_after_requirement_process,
            {'document_integration': 'document_integration', 'error': 'error_handler'},
        )
        self.workflow.add_edge('document_integration', 'completion')
        self.workflow.add_edge('error_handler', 'completion')
        self.workflow.add_edge('completion', END)

        self._compiled_graph = self.workflow.compile(checkpointer=self._checkpointer)
        return self._compiled_graph

    def _start_node(self, state: IntegratedWorkflowState) -> IntegratedWorkflowState:
        """ワークフロー開始ノード"""
        logger.info('統合ワークフロー開始')

        welcome_message = """
🚀 統合要件定義ワークフローへようこそ！

このシステムでは、以下の流れで要件定義書を作成します：

**フェーズ1: ビジネス要件収集**
- プロジェクトの背景・目的の整理
- ステークホルダーの特定
- スコープ・制約の明確化

**フェーズ2: 要件定義プロセス**
- システム分析・機能要件定義
- 非機能要件・データ設計
- アーキテクチャ設計・品質管理

**フェーズ3: 統合ドキュメント生成**
- 全ての情報を統合した要件定義書の生成

まずはビジネス要件の収集から始めましょう。
プロジェクトについて自由に教えてください！
        """

        return {
            'messages': [AIMessage(content=welcome_message)],
            'workflow_phase': 'biz_requirement',
            'current_phase': state.get('current_phase'),
        }

    async def _biz_requirement_collection_node(self, state: IntegratedWorkflowState) -> IntegratedWorkflowState:
        """ビジネス要件収集ノード"""
        logger.info('ビジネス要件収集フェーズ実行中')

        try:
            # ビジネス要件エージェントのグラフを構築
            biz_workflow = self._biz_requirement_agent.build_graph()

            # 現在の状態をビジネス要件エージェント用に変換
            biz_state = {k: v for k, v in state.items() if k in RequirementState.__annotations__}

            # ビジネス要件収集を実行
            result = await biz_workflow.ainvoke(biz_state)

            # 結果を統合ワークフロー状態に反映
            updated_state = {
                'messages': result.get('messages', []),
                'requirement': result.get('requirement'),
                'current_phase': result.get('current_phase'),
                'document': result.get('document'),
                'workflow_phase': 'biz_requirement',
            }

            # ビジネス要件が完了した場合の判定
            if result.get('current_phase') == END and result.get('requirement'):
                updated_state['business_requirement'] = result['requirement']
                logger.info('ビジネス要件収集が完了しました')

            return updated_state

        except Exception as e:
            logger.error(f'ビジネス要件収集中にエラー: {e}')
            return {'error_message': f'ビジネス要件収集中にエラーが発生しました: {str(e)}', 'workflow_phase': 'error'}

    async def _requirement_process_execution_node(self, state: IntegratedWorkflowState) -> IntegratedWorkflowState:
        """要件定義プロセス実行ノード"""
        logger.info('要件定義プロセス実行フェーズ開始')

        business_requirement = state.get('business_requirement')
        if not business_requirement:
            return {'error_message': 'ビジネス要件が取得できませんでした', 'workflow_phase': 'error'}

        try:
            # 要件定義プロセス実行メッセージを追加
            process_message = """
📋 ビジネス要件の収集が完了しました！

次のフェーズとして、要件定義プロセスを実行します：
- システム分析による機能要件の特定
- 非機能要件とデータ設計の策定
- セキュリティ・インフラ要件の定義
- システムアーキテクチャの設計

このプロセスには数分かかる場合があります...
            """

            current_messages = state.get('messages', [])
            current_messages.append(AIMessage(content=process_message))

            # 要件定義プロセスを実行
            process_result = await run_requirement_process(business_requirement)

            return {
                'messages': current_messages,
                'business_requirement': business_requirement,
                'requirement_process_result': process_result,
                'workflow_phase': 'requirement_process',
            }

        except Exception as e:
            logger.error(f'要件定義プロセス実行中にエラー: {e}')
            return {'error_message': f'要件定義プロセス実行中にエラーが発生しました: {str(e)}', 'workflow_phase': 'error'}

    def _document_integration_node(self, state: IntegratedWorkflowState) -> IntegratedWorkflowState:
        """ドキュメント統合ノード"""
        logger.info('統合ドキュメント生成フェーズ開始')

        try:
            business_requirement = state.get('business_requirement')
            process_result = state.get('requirement_process_result')

            if not business_requirement or not process_result:
                return {'error_message': '統合に必要なデータが不足しています', 'workflow_phase': 'error'}

            # 統合ドキュメントを生成
            integrated_document = self._create_integrated_document(business_requirement, process_result)

            # ファイル保存
            project_name = business_requirement.project_name or 'プロジェクト名未設定'
            output_path = f'outputs/{project_name.replace(" ", "_")}_integrated_requirement.md'

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(integrated_document)

            logger.info(f'統合ドキュメントを保存: {output_path}')

            return {'final_output_path': output_path, 'workflow_phase': 'completion'}

        except Exception as e:
            logger.error(f'ドキュメント統合中にエラー: {e}')
            return {'error_message': f'ドキュメント統合中にエラーが発生しました: {str(e)}', 'workflow_phase': 'error'}

    def _error_handler_node(self, state: IntegratedWorkflowState) -> IntegratedWorkflowState:
        """エラーハンドリングノード"""
        error_message = state.get('error_message', '不明なエラーが発生しました')
        logger.error(f'ワークフローエラー: {error_message}')

        error_response = f"""
❌ エラーが発生しました

エラー内容: {error_message}

申し訳ございませんが、処理を継続できませんでした。
もう一度最初からやり直してください。
        """

        current_messages = state.get('messages', [])
        current_messages.append(AIMessage(content=error_response))

        return {'messages': current_messages, 'workflow_phase': 'completion'}

    def _completion_node(self, state: IntegratedWorkflowState) -> IntegratedWorkflowState:
        """完了ノード"""
        output_path = state.get('final_output_path')

        if output_path:
            completion_message = f"""
✅ 統合要件定義ワークフローが完了しました！

📄 **生成された統合要件定義書**
ファイルパス: `{output_path}`

**含まれる内容:**
- ビジネス要件の詳細
- 機能要件・非機能要件
- データ設計・システムアーキテクチャ
- セキュリティ・インフラ要件
- 品質管理・テスト計画

ご質問やフィードバックがありましたら、お気軽にお声がけください。
            """
        else:
            completion_message = """
ワークフローは完了しましたが、一部のプロセスでエラーが発生しました。
詳細は上記のメッセージをご確認ください。
            """

        current_messages = state.get('messages', [])
        current_messages.append(AIMessage(content=completion_message))

        return {'messages': current_messages, 'workflow_phase': 'completion'}

    def _decide_after_biz_requirement(self, state: IntegratedWorkflowState) -> str:
        """ビジネス要件収集後の遷移判定"""
        if state.get('error_message'):
            return 'error'
        elif state.get('current_phase') == END and state.get('business_requirement'):
            return 'requirement_process'
        else:
            return 'continue_biz'

    def _decide_after_requirement_process(self, state: IntegratedWorkflowState) -> str:
        """要件定義プロセス後の遷移判定"""
        if state.get('error_message'):
            return 'error'
        else:
            return 'document_integration'

    def _create_integrated_document(self, business_requirement: ProjectBusinessRequirement, process_result: Dict[str, Any]) -> str:
        """統合ドキュメントを生成"""
        project_name = business_requirement.project_name or 'プロジェクト名未設定'

        # ドキュメントテンプレート
        document = f"""# {project_name} - 統合要件定義書

## 目次 {{#table-of-contents}}
- [プロジェクト概要](#project-overview)
- [ビジネス要件](#business-requirements)
- [機能要件](#functional-requirements)
- [非機能要件](#non-functional-requirements)
- [データ設計](#data-design)
- [システムアーキテクチャ](#system-architecture)
- [セキュリティ要件](#security-requirements)
- [インフラ要件](#infrastructure-requirements)
- [品質管理・テスト計画](#quality-management)

---

## プロジェクト概要 {{#project-overview}}

**プロジェクト名**: {project_name}

**プロジェクト概要**: {business_requirement.description or 'N/A'}

**背景**: {business_requirement.background or 'N/A'}

### 主要目標
"""

        # ビジネス目標の追加
        if business_requirement.goals:
            for goal in business_requirement.goals:
                document += f"""
- **目標**: {goal.objective}
  - **理由**: {goal.rationale}
  - **KPI**: {goal.kpi}
"""

        document += """
---

## ビジネス要件 {{#business-requirements}}

### ステークホルダー
"""

        # ステークホルダー情報の追加
        if business_requirement.stake_holders:
            document += """
| 役割 | 期待値 |
|------|--------|
"""
            for stakeholder in business_requirement.stake_holders:
                document += f'| {stakeholder.role} | {stakeholder.expectations} |\n'

        # スコープ情報の追加
        if business_requirement.scopes:
            document += """
### プロジェクトスコープ

| 含む項目 | 含まない項目 |
|----------|-------------|
"""
            for scope in business_requirement.scopes:
                document += f'| {scope.in_scope} | {scope.out_of_scope} |\n'

        # 機能要件の追加
        document += """
---

## 機能要件 {{#functional-requirements}}
"""

        if process_result.get('functional_requirements'):
            for i, req in enumerate(process_result['functional_requirements'], 1):
                document += f"""
### FR-{i:03d}: {req.get('name', 'N/A')}
- **優先度**: {req.get('priority', 'N/A')}
- **説明**: {req.get('description', 'N/A')}
- **受入条件**: {req.get('acceptance_criteria', 'N/A')}
"""

        # 非機能要件の追加
        document += """
---

## 非機能要件 {{#non-functional-requirements}}
"""

        if process_result.get('non_functional_requirements'):
            for category, requirements in process_result['non_functional_requirements'].items():
                document += f"""
### {category}
"""
                for req in requirements:
                    document += f'- {req}\n'

        # データ設計の追加
        document += """
---

## データ設計 {{#data-design}}
"""

        if process_result.get('data_models'):
            document += """
### データモデル
"""
            for model in process_result['data_models']:
                document += f"""
#### {model.get('name', 'N/A')}
- **説明**: {model.get('description', 'N/A')}
- **属性**: {', '.join(model.get('attributes', []))}
"""

        # システムアーキテクチャの追加
        document += """
---

## システムアーキテクチャ {{#system-architecture}}
"""

        if process_result.get('system_architecture'):
            arch = process_result['system_architecture']
            document += f"""
### アーキテクチャパターン
{arch.get('pattern', 'N/A')}

### 技術スタック
{arch.get('technology_stack', 'N/A')}

### システム構成
{arch.get('system_components', 'N/A')}
"""

        # 最終出力時刻の追加
        from datetime import datetime

        document += f"""
---

## ドキュメント情報

- **生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **生成ツール**: 統合要件定義ワークフロー
- **バージョン**: 1.0

---

*このドキュメントは自動生成されました。詳細な内容については、各担当者と協議の上で調整してください。*
"""

        return document


async def main():
    """統合ワークフローのメイン実行関数"""
    agent = IntegratedWorkflowAgent()
    workflow = agent.build_graph()

    print('統合要件定義ワークフローを開始します...')

    try:
        # 初期状態でワークフローを実行
        result = await workflow.ainvoke({'messages': []})

        # 結果表示
        if result.get('final_output_path'):
            print(f'\n✅ 統合要件定義書が生成されました: {result["final_output_path"]}')
        else:
            print('\n❌ ワークフローは完了しましたが、エラーが発生しました。')

    except Exception as e:
        print(f'\n❌ 統合ワークフローでエラーが発生しました: {e}')


if __name__ == '__main__':
    asyncio.run(main())
