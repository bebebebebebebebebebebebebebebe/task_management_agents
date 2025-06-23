"""UXデザイナー・エージェント"""

from typing import Any, Dict, List

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.personas.base_persona import BasePersonaAgent
from agents.requirement_process.schemas import FunctionalRequirement, PersonaOutput, PersonaRole


class UXDesignerAgent(BasePersonaAgent):
    """UXデザイナー・エージェント

    ユーザー視点から機能要件を具体化し、ユーザーストーリーを作成する
    """

    def __init__(self):
        super().__init__(PersonaRole.UX_DESIGNER)

    def design_requirements(
        self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput]
    ) -> PersonaOutput:
        """機能要件の詳細設計を実行"""
        return self.execute(business_requirement, previous_outputs)

    def execute(self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput] = None) -> PersonaOutput:
        """UX設計を実行"""

        # システムアナリストの出力から機能候補を取得
        system_analysis = self._extract_relevant_info(previous_outputs, PersonaRole.SYSTEM_ANALYST)
        function_candidates = system_analysis.get('function_candidates', [])

        # ユーザーストーリーを作成
        user_stories = self._create_user_stories(business_requirement, function_candidates)

        # 機能要件を作成
        functional_requirements = self._create_functional_requirements(user_stories)

        # UI/UXガイドラインを作成
        ux_guidelines = self._create_ux_guidelines(business_requirement)

        # ユーザージャーニーマップを作成
        user_journeys = self._create_user_journeys(business_requirement, functional_requirements)

        deliverables = {
            'functional_requirements': functional_requirements,
            'user_stories': user_stories,
            'ux_guidelines': ux_guidelines,
            'user_journeys': user_journeys,
        }

        recommendations = [
            'ユーザーテストを実施して実際のユーザビリティを検証することを推奨',
            'アクセシビリティ要件（WCAG 2.1準拠）を考慮した設計を推奨',
            'レスポンシブデザインによるマルチデバイス対応を推奨',
            'ユーザーフィードバック収集機能の実装を推奨',
        ]

        concerns = [
            'ユーザーの多様性により、すべてのユーザーに最適なUXを提供することが困難',
            '技術的制約によりUX要件が制限される可能性',
            'パフォーマンス要件とUX要件のトレードオフが発生する可能性',
        ]

        return self._create_output(deliverables, recommendations, concerns)

    def _create_user_stories(
        self, business_requirement: ProjectBusinessRequirement, function_candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """ユーザーストーリーを作成"""
        user_stories = []

        # ステークホルダーごとにユーザーストーリーを作成
        if business_requirement.stake_holders:
            for stakeholder in business_requirement.stake_holders:
                stories = self._create_stories_for_stakeholder(stakeholder, function_candidates)
                user_stories.extend(stories)

        # 機能候補からユーザーストーリーを作成
        for function in function_candidates:
            story = self._create_story_from_function(function)
            if story:
                user_stories.append(story)

        return user_stories

    def _create_stories_for_stakeholder(self, stakeholder, function_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """特定のステークホルダーのユーザーストーリーを作成"""
        stories = []

        # ステークホルダーの期待から基本的なストーリーを作成
        base_story = {'user_type': stakeholder.role, 'user_name': stakeholder.name, 'expectations': stakeholder.expectations}

        # 期待内容からストーリーを推定
        if '管理' in stakeholder.expectations:
            stories.append(
                {
                    **base_story,
                    'story': f'{stakeholder.role}として、システムを効率的に管理したい',
                    'reason': '業務効率を向上させるため',
                    'priority': 'high',
                }
            )

        if '分析' in stakeholder.expectations or 'レポート' in stakeholder.expectations:
            stories.append(
                {
                    **base_story,
                    'story': f'{stakeholder.role}として、データを分析・可視化したい',
                    'reason': '適切な意思決定を行うため',
                    'priority': 'high',
                }
            )

        if '通知' in stakeholder.expectations:
            stories.append(
                {
                    **base_story,
                    'story': f'{stakeholder.role}として、重要な情報をタイムリーに受け取りたい',
                    'reason': '迅速な対応を行うため',
                    'priority': 'medium',
                }
            )

        return stories

    def _create_story_from_function(self, function: Dict[str, Any]) -> Dict[str, Any]:
        """機能候補からユーザーストーリーを作成"""
        function_to_story_map = {
            'データ管理機能': {
                'story': 'ユーザーとして、データを簡単に作成・更新・削除したい',
                'reason': '効率的にデータ管理を行うため',
            },
            'レポート機能': {'story': 'ユーザーとして、データをレポートとして出力したい', 'reason': '分析結果を共有するため'},
            'API機能': {
                'story': '開発者として、システムのデータにAPI経由でアクセスしたい',
                'reason': '他システムとの連携を実現するため',
            },
            'Web機能': {'story': 'ユーザーとして、Webブラウザから機能を利用したい', 'reason': 'いつでもどこからでもアクセスするため'},
        }

        function_name = function.get('name', '')
        if function_name in function_to_story_map:
            story_template = function_to_story_map[function_name]
            return {
                'user_type': 'ユーザー',
                'story': story_template['story'],
                'reason': story_template['reason'],
                'priority': function.get('priority', 'medium'),
                'related_function': function_name,
            }

        return None

    def _create_functional_requirements(self, user_stories: List[Dict[str, Any]]) -> List[FunctionalRequirement]:
        """ユーザーストーリーから機能要件を作成"""
        functional_requirements = []

        for story in user_stories:
            # ユーザーストーリーから受け入れ基準を生成
            acceptance_criteria = self._generate_acceptance_criteria(story)

            # 複雑度を推定
            complexity = self._estimate_complexity(story)

            functional_req = FunctionalRequirement(
                user_story=story['story'],
                acceptance_criteria=acceptance_criteria,
                priority=story.get('priority', 'medium'),
                complexity=complexity,
            )

            functional_requirements.append(functional_req)

        return functional_requirements

    def _generate_acceptance_criteria(self, story: Dict[str, Any]) -> List[str]:
        """ユーザーストーリーから受け入れ基準を生成"""
        criteria = []

        story_text = story['story']

        # ストーリー内容から基本的な受け入れ基準を生成
        if 'データ' in story_text and '管理' in story_text:
            criteria.extend(
                [
                    'データの作成・更新・削除が正常に動作すること',
                    'データの検索・フィルタリングが正常に動作すること',
                    'データの整合性が保たれること',
                    'エラー時に適切なメッセージが表示されること',
                ]
            )

        if 'レポート' in story_text:
            criteria.extend(
                [
                    'レポートが正確なデータで生成されること',
                    '複数の出力形式（PDF、Excel等）に対応すること',
                    'レポート生成が妥当な時間内で完了すること',
                    'レポートのレイアウトが適切であること',
                ]
            )

        if 'API' in story_text:
            criteria.extend(
                [
                    'RESTful APIの設計原則に従うこと',
                    '適切なHTTPステータスコードを返すこと',
                    'APIドキュメントが提供されること',
                    '認証・認可が適切に実装されること',
                ]
            )

        if 'Web' in story_text:
            criteria.extend(
                [
                    'レスポンシブデザインに対応すること',
                    '主要ブラウザで正常に動作すること',
                    'ページの読み込み時間が妥当であること',
                    'アクセシビリティに配慮されていること',
                ]
            )

        # 基本的な受け入れ基準を追加
        if not criteria:
            criteria.extend(
                ['機能が仕様通りに動作すること', 'エラーハンドリングが適切に実装されること', 'ユーザビリティが考慮されていること']
            )

        return criteria

    def _estimate_complexity(self, story: Dict[str, Any]) -> str:
        """ストーリーの複雑度を推定"""
        story_text = story['story']

        # 複雑度を決定するキーワード
        high_complexity_keywords = ['連携', 'API', '分析', 'レポート', '管理']
        medium_complexity_keywords = ['作成', '更新', '削除', '検索']

        high_count = sum(1 for keyword in high_complexity_keywords if keyword in story_text)
        medium_count = sum(1 for keyword in medium_complexity_keywords if keyword in story_text)

        if high_count >= 2:
            return 'high'
        elif high_count >= 1 or medium_count >= 2:
            return 'medium'
        else:
            return 'low'

    def _create_ux_guidelines(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """UI/UXガイドラインを作成"""
        guidelines = {
            'design_principles': [
                'ユーザー中心設計',
                'シンプルで直感的なインターフェース',
                '一貫性のあるデザイン',
                'アクセシビリティの確保',
            ],
            'ui_components': [
                'レスポンシブナビゲーション',
                'データテーブル（ソート・フィルタ機能付き）',
                'フォーム（バリデーション機能付き）',
                'モーダルダイアログ',
                '通知・アラートシステム',
            ],
            'interaction_patterns': [
                'CRUD操作の統一的なフロー',
                'エラー状態の明確な表示',
                'ローディング状態の表示',
                'ユーザーフィードバックの提供',
            ],
            'accessibility_requirements': [
                'WCAG 2.1 AA準拠',
                'キーボードナビゲーション対応',
                'スクリーンリーダー対応',
                '色覚障害への配慮',
            ],
        }

        # ステークホルダーの特性に応じたガイドライン調整
        if business_requirement.stake_holders:
            technical_users = any('開発' in s.role or '技術' in s.role for s in business_requirement.stake_holders)
            if technical_users:
                guidelines['ui_components'].extend(['APIドキュメント表示', 'デバッグ情報表示', '設定管理インターフェース'])

        return guidelines

    def _create_user_journeys(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[FunctionalRequirement]
    ) -> List[Dict[str, Any]]:
        """ユーザージャーニーマップを作成"""
        user_journeys = []

        # 主要なユーザージャーニーを定義
        journeys = [
            {
                'journey_name': '初回ログイン〜基本設定',
                'steps': ['アカウント作成/ログイン', 'プロフィール設定', 'システム設定', 'チュートリアル完了'],
                'touchpoints': ['ログイン画面', '設定画面', 'ヘルプシステム'],
                'pain_points': ['複雑な設定', '不明確な手順'],
                'opportunities': ['オンボーディングの改善', 'ガイド機能の強化'],
            },
            {
                'journey_name': '日常的なデータ操作',
                'steps': ['データ検索', 'データ表示・確認', 'データ編集', '変更保存・確認'],
                'touchpoints': ['検索機能', 'データテーブル', '編集フォーム'],
                'pain_points': ['検索の遅さ', '複雑な編集フォーム'],
                'opportunities': ['検索の高速化', 'フォームの簡素化'],
            },
        ]

        # 機能要件に基づいてジャーニーを調整
        for req in functional_requirements:
            if 'レポート' in req.user_story:
                journeys.append(
                    {
                        'journey_name': 'レポート作成・共有',
                        'steps': ['レポート条件設定', 'データ取得・処理', 'レポート確認', 'レポート出力・共有'],
                        'touchpoints': ['条件設定画面', 'プレビュー機能', '出力機能'],
                        'pain_points': ['条件設定の複雑さ', '処理時間の長さ'],
                        'opportunities': ['テンプレート機能', 'バックグラウンド処理'],
                    }
                )

        user_journeys.extend(journeys)
        return user_journeys
