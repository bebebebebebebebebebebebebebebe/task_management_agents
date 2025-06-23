"""システムアナリスト・エージェント"""

from typing import Any, Dict, List

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.personas.base_persona import BasePersonaAgent
from agents.requirement_process.schemas import PersonaOutput, PersonaRole


class SystemAnalystAgent(BasePersonaAgent):
    """システムアナリスト・エージェント

    ビジネス要件から機能候補を洗い出し、システム全体の構造を分析する
    """

    def __init__(self):
        super().__init__(PersonaRole.SYSTEM_ANALYST)

    def analyze(self, business_requirement: ProjectBusinessRequirement) -> PersonaOutput:
        """ビジネス要件を分析し、機能候補リストを生成"""
        return self.execute(business_requirement)

    def execute(self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput] = None) -> PersonaOutput:
        """システム分析を実行"""

        # ビジネス要件から機能候補を抽出
        function_candidates = self._extract_function_candidates(business_requirement)

        # システム境界を定義
        system_boundaries = self._define_system_boundaries(business_requirement)

        # 外部システム連携を特定
        external_integrations = self._identify_external_integrations(business_requirement)

        # データフローを分析
        data_flows = self._analyze_data_flows(business_requirement)

        deliverables = {
            'function_candidates': function_candidates,
            'system_boundaries': system_boundaries,
            'external_integrations': external_integrations,
            'data_flows': data_flows,
        }

        recommendations = [
            '機能の優先順位付けを行い、MVPとしての最小機能セットを定義することを推奨',
            '外部システム連携については、APIの可用性と安定性を事前検証することを推奨',
            'データフローの複雑性を考慮し、段階的な実装アプローチを検討することを推奨',
        ]

        concerns = [
            '要件の曖昧性により、後工程での要件変更リスクが存在',
            '外部システム依存度が高い場合、システム全体の可用性に影響する可能性',
        ]

        return self._create_output(deliverables, recommendations, concerns)

    def _extract_function_candidates(self, business_requirement: ProjectBusinessRequirement) -> List[Dict[str, Any]]:
        """ビジネス要件から機能候補を抽出"""
        function_candidates = []

        # プロジェクト目標から機能を推定
        if business_requirement.goals:
            for goal in business_requirement.goals:
                functions = self._derive_functions_from_goal(goal.objective)
                function_candidates.extend(functions)

        # ステークホルダーの期待から機能を推定
        if business_requirement.stake_holders:
            for stakeholder in business_requirement.stake_holders:
                functions = self._derive_functions_from_expectations(stakeholder.expectations)
                function_candidates.extend(functions)

        # スコープから機能を推定
        if business_requirement.scopes:
            for scope in business_requirement.scopes:
                functions = self._derive_functions_from_scope(scope.in_scope)
                function_candidates.extend(functions)

        # 重複を除去し、優先度を設定
        unique_functions = self._deduplicate_and_prioritize(function_candidates)

        return unique_functions

    def _derive_functions_from_goal(self, objective: str) -> List[Dict[str, Any]]:
        """プロジェクト目標から機能を推定"""
        functions = []

        # キーワードベースの簡単な機能推定
        keywords_to_functions = {
            '管理': [
                {'name': 'データ管理機能', 'description': 'データの作成・更新・削除・検索', 'priority': 'high'},
                {'name': '権限管理機能', 'description': 'ユーザー権限の設定・管理', 'priority': 'medium'},
            ],
            '効率': [
                {'name': '自動化機能', 'description': '手動作業の自動化', 'priority': 'high'},
                {'name': 'バッチ処理機能', 'description': '大量データの一括処理', 'priority': 'medium'},
            ],
            '分析': [
                {'name': 'レポート機能', 'description': 'データの可視化・レポート出力', 'priority': 'high'},
                {'name': 'ダッシュボード機能', 'description': 'リアルタイムデータ表示', 'priority': 'medium'},
            ],
            '通知': [
                {'name': '通知機能', 'description': 'イベント発生時の通知送信', 'priority': 'medium'},
                {'name': 'アラート機能', 'description': '異常検知とアラート', 'priority': 'high'},
            ],
        }

        for keyword, keyword_functions in keywords_to_functions.items():
            if keyword in objective:
                functions.extend(keyword_functions)

        return functions

    def _derive_functions_from_expectations(self, expectations: str) -> List[Dict[str, Any]]:
        """ステークホルダーの期待から機能を推定"""
        functions = []

        # 期待内容から機能を推定（簡略化版）
        if '使いやすい' in expectations:
            functions.append({'name': 'UI/UX機能', 'description': '直感的で使いやすいユーザーインターフェース', 'priority': 'high'})

        if '早い' in expectations or '高速' in expectations:
            functions.append({'name': 'パフォーマンス最適化', 'description': '高速な処理・応答時間の実現', 'priority': 'high'})

        if 'セキュア' in expectations or 'セキュリティ' in expectations:
            functions.append({'name': 'セキュリティ機能', 'description': 'データ保護・不正アクセス防止', 'priority': 'high'})

        return functions

    def _derive_functions_from_scope(self, scope: str) -> List[Dict[str, Any]]:
        """スコープから機能を推定"""
        functions = []

        # スコープ内容から基本機能を推定
        if 'API' in scope:
            functions.append({'name': 'API機能', 'description': 'RESTful APIの提供', 'priority': 'high'})

        if 'Web' in scope or 'ウェブ' in scope:
            functions.append({'name': 'Web機能', 'description': 'Webアプリケーション機能', 'priority': 'high'})

        if 'モバイル' in scope:
            functions.append({'name': 'モバイル機能', 'description': 'モバイルアプリケーション対応', 'priority': 'medium'})

        return functions

    def _deduplicate_and_prioritize(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重複した機能を除去し、優先度を設定"""
        unique_functions = []
        seen_names = set()

        for func in functions:
            if func['name'] not in seen_names:
                unique_functions.append(func)
                seen_names.add(func['name'])

        # 優先度でソート
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        unique_functions.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return unique_functions

    def _define_system_boundaries(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """システム境界を定義"""
        boundaries = {'internal_systems': [], 'external_systems': [], 'user_groups': [], 'data_boundaries': []}

        # ステークホルダーからユーザーグループを抽出
        if business_requirement.stake_holders:
            for stakeholder in business_requirement.stake_holders:
                boundaries['user_groups'].append(
                    {
                        'name': stakeholder.name,
                        'role': stakeholder.role,
                        'access_level': self._determine_access_level(stakeholder.role),
                    }
                )

        # 制約から外部システムを特定
        if business_requirement.constraints:
            for constraint in business_requirement.constraints:
                if '連携' in constraint.description or 'システム' in constraint.description:
                    boundaries['external_systems'].append(
                        {'name': '外部システム', 'description': constraint.description, 'integration_type': 'API連携'}
                    )

        return boundaries

    def _determine_access_level(self, role: str) -> str:
        """役割からアクセスレベルを決定"""
        admin_roles = ['管理者', 'システム管理者', 'マネージャー']
        if any(admin_role in role for admin_role in admin_roles):
            return 'admin'
        elif 'ユーザー' in role:
            return 'user'
        else:
            return 'readonly'

    def _identify_external_integrations(self, business_requirement: ProjectBusinessRequirement) -> List[Dict[str, Any]]:
        """外部システム連携を特定"""
        integrations = []

        # 制約から外部連携を特定
        if business_requirement.constraints:
            for constraint in business_requirement.constraints:
                if any(keyword in constraint.description for keyword in ['連携', 'API', '外部']):
                    integrations.append(
                        {
                            'type': '外部システム連携',
                            'description': constraint.description,
                            'criticality': 'high',
                            'integration_method': 'API',
                        }
                    )

        # 法規制遵守から外部連携を特定
        if business_requirement.compliance:
            for compliance in business_requirement.compliance:
                integrations.append(
                    {
                        'type': 'コンプライアンス連携',
                        'description': f'{compliance.regulation}への対応',
                        'criticality': 'high',
                        'integration_method': 'データ連携',
                    }
                )

        return integrations

    def _analyze_data_flows(self, business_requirement: ProjectBusinessRequirement) -> List[Dict[str, Any]]:
        """データフローを分析"""
        data_flows = []

        # 基本的なデータフローを推定
        data_flows.extend(
            [
                {
                    'flow_name': 'ユーザー入力データ',
                    'source': 'フロントエンド',
                    'destination': 'バックエンド',
                    'data_type': 'リクエストデータ',
                    'frequency': 'リアルタイム',
                },
                {
                    'flow_name': 'アプリケーションデータ',
                    'source': 'バックエンド',
                    'destination': 'データベース',
                    'data_type': 'ビジネスデータ',
                    'frequency': 'リアルタイム',
                },
                {
                    'flow_name': 'レスポンスデータ',
                    'source': 'バックエンド',
                    'destination': 'フロントエンド',
                    'data_type': 'レスポンスデータ',
                    'frequency': 'リアルタイム',
                },
            ]
        )

        # 外部システム連携がある場合のデータフロー
        if business_requirement.constraints:
            for constraint in business_requirement.constraints:
                if '連携' in constraint.description:
                    data_flows.append(
                        {
                            'flow_name': '外部システム連携データ',
                            'source': 'バックエンド',
                            'destination': '外部システム',
                            'data_type': '連携データ',
                            'frequency': 'バッチまたはリアルタイム',
                        }
                    )

        return data_flows
