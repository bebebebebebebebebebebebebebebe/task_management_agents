"""QAエンジニア・エージェント"""

from typing import Any, Dict, List

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.personas.base_persona import BasePersonaAgent
from agents.requirement_process.schemas import FunctionalRequirement, PersonaOutput, PersonaRole


class QAEngineerAgent(BasePersonaAgent):
    """QAエンジニア・エージェント

    機能要件に対する受け入れ基準を具体化し、テスト戦略を策定する
    """

    def __init__(self):
        super().__init__(PersonaRole.QA_ENGINEER)

    def define_acceptance_criteria(
        self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput]
    ) -> PersonaOutput:
        """受け入れ基準の定義を実行"""
        return self.execute(business_requirement, previous_outputs)

    def execute(self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput] = None) -> PersonaOutput:
        """QA観点からの要件定義を実行"""

        # UXデザイナーの出力から機能要件を取得
        ux_design = self._extract_relevant_info(previous_outputs, PersonaRole.UX_DESIGNER)
        functional_requirements = ux_design.get('functional_requirements', [])

        # 詳細な受け入れ基準を作成
        detailed_acceptance_criteria = self._create_detailed_acceptance_criteria(functional_requirements)

        # テスト戦略を策定
        test_strategy = self._create_test_strategy(business_requirement, functional_requirements)

        # テストケースを作成
        test_cases = self._create_test_cases(functional_requirements)

        # 品質基準を定義
        quality_standards = self._define_quality_standards(business_requirement)

        deliverables = {
            'detailed_acceptance_criteria': detailed_acceptance_criteria,
            'test_strategy': test_strategy,
            'test_cases': test_cases,
            'quality_standards': quality_standards,
        }

        recommendations = [
            '自動テストの導入により、回帰テストの効率化を推奨',
            'CI/CDパイプラインでのテスト自動実行を推奨',
            'テスト環境の本番環境との整合性確保を推奨',
            'ユーザー受け入れテスト（UAT）の計画的実施を推奨',
            '性能テストの早期実施を推奨',
        ]

        concerns = [
            'テスト環境と本番環境の差異により、本番でのみ発生する問題のリスク',
            '複雑な機能では網羅的なテストケース作成が困難',
            '外部システム依存の機能では、テスト実行が制約される可能性',
            'データ品質に依存する機能では、テストデータの準備が課題',
        ]

        return self._create_output(deliverables, recommendations, concerns)

    def _create_detailed_acceptance_criteria(self, functional_requirements: List[FunctionalRequirement]) -> List[Dict[str, Any]]:
        """詳細な受け入れ基準を作成"""
        detailed_criteria = []

        for req in functional_requirements:
            criteria_detail = {
                'user_story': req.user_story,
                'priority': req.priority,
                'given_when_then': self._create_given_when_then(req),
                'edge_cases': self._identify_edge_cases(req),
                'error_scenarios': self._identify_error_scenarios(req),
                'performance_criteria': self._define_performance_criteria(req),
                'security_criteria': self._define_security_criteria(req),
            }
            detailed_criteria.append(criteria_detail)

        return detailed_criteria

    def _create_given_when_then(self, requirement: FunctionalRequirement) -> List[Dict[str, str]]:
        """Given-When-Then形式の受け入れ基準を作成"""
        scenarios = []

        user_story = requirement.user_story

        # ユーザーストーリーの内容に基づいてシナリオを生成
        if 'データ' in user_story and '管理' in user_story:
            scenarios.extend(
                [
                    {
                        'scenario': 'データ作成の正常系',
                        'given': '適切な権限を持つユーザーがログインしている',
                        'when': '有効なデータを入力してデータ作成を実行する',
                        'then': 'データが正常に作成され、成功メッセージが表示される',
                    },
                    {
                        'scenario': 'データ更新の正常系',
                        'given': '既存のデータが存在し、適切な権限を持つユーザーがログインしている',
                        'when': 'データを修正して更新を実行する',
                        'then': 'データが正常に更新され、変更内容が反映される',
                    },
                    {
                        'scenario': 'データ削除の正常系',
                        'given': '削除対象のデータが存在し、適切な権限を持つユーザーがログインしている',
                        'when': 'データ削除を実行する',
                        'then': 'データが正常に削除され、一覧から除外される',
                    },
                ]
            )

        if 'レポート' in user_story:
            scenarios.extend(
                [
                    {
                        'scenario': 'レポート生成の正常系',
                        'given': 'レポート対象のデータが存在する',
                        'when': 'レポート生成条件を指定してレポート作成を実行する',
                        'then': '指定した条件に基づいてレポートが生成される',
                    },
                    {
                        'scenario': 'レポート出力の正常系',
                        'given': 'レポートが生成されている',
                        'when': 'レポートの出力形式を指定して出力を実行する',
                        'then': '指定した形式でレポートファイルがダウンロードされる',
                    },
                ]
            )

        if 'API' in user_story:
            scenarios.extend(
                [
                    {
                        'scenario': 'API呼び出しの正常系',
                        'given': '有効なAPIキーでAPI認証が完了している',
                        'when': '適切なパラメータでAPIを呼び出す',
                        'then': '期待されるレスポンスが正常に返される',
                    }
                ]
            )

        return scenarios

    def _identify_edge_cases(self, requirement: FunctionalRequirement) -> List[str]:
        """エッジケースを特定"""
        edge_cases = []

        user_story = requirement.user_story

        # 一般的なエッジケース
        edge_cases.extend(
            ['最大データサイズでの動作確認', '最小データサイズでの動作確認', '境界値での動作確認', '同時実行時の動作確認']
        )

        # 機能特有のエッジケース
        if 'データ' in user_story:
            edge_cases.extend(['空データでの処理', '特殊文字を含むデータでの処理', '重複データでの処理', '大量データでの処理性能'])

        if 'レポート' in user_story:
            edge_cases.extend(['データなしでのレポート生成', '大量データでのレポート生成時間', '複雑な条件でのレポート生成'])

        if 'API' in user_story:
            edge_cases.extend(['レート制限に達した場合の動作', 'タイムアウト時の動作', '不正なパラメータでの動作'])

        return edge_cases

    def _identify_error_scenarios(self, requirement: FunctionalRequirement) -> List[Dict[str, str]]:
        """エラーシナリオを特定"""
        error_scenarios = []

        user_story = requirement.user_story

        # 共通エラーシナリオ
        error_scenarios.extend(
            [
                {
                    'scenario': '権限不足エラー',
                    'condition': '適切な権限を持たないユーザーが機能を実行する',
                    'expected_result': '403 Forbiddenエラーが返され、エラーメッセージが表示される',
                },
                {
                    'scenario': 'ネットワークエラー',
                    'condition': 'ネットワーク接続が不安定な状態で機能を実行する',
                    'expected_result': 'ネットワークエラーが適切にハンドリングされ、ユーザーに分かりやすいメッセージが表示される',
                },
            ]
        )

        # 機能特有のエラーシナリオ
        if 'データ' in user_story:
            error_scenarios.extend(
                [
                    {
                        'scenario': 'バリデーションエラー',
                        'condition': '不正な形式のデータを入力する',
                        'expected_result': 'バリデーションエラーが発生し、具体的なエラー内容が表示される',
                    },
                    {
                        'scenario': '重複データエラー',
                        'condition': '既存と重複するデータを作成しようとする',
                        'expected_result': '重複エラーが発生し、重複内容が明示される',
                    },
                ]
            )

        if 'API' in user_story:
            error_scenarios.extend(
                [
                    {
                        'scenario': '認証エラー',
                        'condition': '無効なAPIキーでAPIを呼び出す',
                        'expected_result': '401 Unauthorizedエラーが返される',
                    },
                    {
                        'scenario': 'リクエスト形式エラー',
                        'condition': '不正な形式のリクエストでAPIを呼び出す',
                        'expected_result': '400 Bad Requestエラーが返され、エラー詳細が含まれる',
                    },
                ]
            )

        return error_scenarios

    def _define_performance_criteria(self, requirement: FunctionalRequirement) -> Dict[str, str]:
        """パフォーマンス基準を定義"""
        criteria = {}

        user_story = requirement.user_story
        complexity = requirement.complexity

        # 複雑度に基づく基本性能基準
        if complexity == 'low':
            criteria['response_time'] = '1秒以内'
            criteria['throughput'] = '100リクエスト/秒'
        elif complexity == 'medium':
            criteria['response_time'] = '3秒以内'
            criteria['throughput'] = '50リクエスト/秒'
        else:  # high
            criteria['response_time'] = '5秒以内'
            criteria['throughput'] = '20リクエスト/秒'

        # 機能特有の性能基準
        if 'レポート' in user_story:
            criteria['report_generation_time'] = '30秒以内（標準データ量）'
            criteria['large_report_time'] = '5分以内（大量データ）'

        if 'データ' in user_story and '検索' in user_story:
            criteria['search_response_time'] = '2秒以内'
            criteria['search_accuracy'] = '関連度95%以上'

        if 'API' in user_story:
            criteria['api_response_time'] = '500ms以内'
            criteria['api_availability'] = '99.9%以上'

        return criteria

    def _define_security_criteria(self, requirement: FunctionalRequirement) -> List[str]:
        """セキュリティ基準を定義"""
        criteria = []

        user_story = requirement.user_story

        # 基本セキュリティ基準
        criteria.extend(
            [
                '認証・認可が適切に実装されている',
                '入力値の適切なサニタイゼーションが行われている',
                'SQLインジェクション対策が実装されている',
                'XSS対策が実装されている',
            ]
        )

        # 機能特有のセキュリティ基準
        if 'データ' in user_story:
            criteria.extend(
                [
                    '個人情報の適切な暗号化が行われている',
                    'データアクセスログが記録されている',
                    'データ削除時に完全削除が保証されている',
                ]
            )

        if 'API' in user_story:
            criteria.extend(
                [
                    'API キーの適切な管理が行われている',
                    'レート制限が実装されている',
                    'HTTPS通信が強制されている',
                    'APIのバージョニングが適切に管理されている',
                ]
            )

        if 'レポート' in user_story:
            criteria.extend(['レポートアクセス権限が適切に制御されている', '機密データの適切なマスキングが行われている'])

        return criteria

    def _create_test_strategy(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[FunctionalRequirement]
    ) -> Dict[str, Any]:
        """テスト戦略を策定"""

        # テストレベルの定義
        test_levels = [
            {
                'level': 'ユニットテスト',
                'purpose': '個別コンポーネントの動作確認',
                'coverage_target': '90%以上',
                'automation': '100%自動化',
            },
            {'level': '統合テスト', 'purpose': 'コンポーネント間の連携確認', 'coverage_target': '80%以上', 'automation': '80%自動化'},
            {
                'level': 'システムテスト',
                'purpose': 'システム全体の動作確認',
                'coverage_target': '主要シナリオ100%',
                'automation': '60%自動化',
            },
            {
                'level': 'ユーザー受け入れテスト',
                'purpose': 'ビジネス要件の充足確認',
                'coverage_target': '全機能',
                'automation': '20%自動化',
            },
        ]

        # テストタイプの定義
        test_types = [
            {'type': '機能テスト', 'description': '機能要件の動作確認', 'priority': 'high'},
            {'type': '性能テスト', 'description': 'レスポンス時間・スループットの確認', 'priority': 'high'},
            {'type': 'セキュリティテスト', 'description': 'セキュリティ脆弱性の確認', 'priority': 'high'},
            {'type': 'ユーザビリティテスト', 'description': 'ユーザー操作性の確認', 'priority': 'medium'},
            {'type': '互換性テスト', 'description': 'ブラウザ・OS互換性の確認', 'priority': 'medium'},
        ]

        # リスクベーステスト戦略
        risk_analysis = self._analyze_testing_risks(business_requirement, functional_requirements)

        strategy = {
            'test_levels': test_levels,
            'test_types': test_types,
            'risk_analysis': risk_analysis,
            'test_environment': self._define_test_environment(),
            'test_data_strategy': self._define_test_data_strategy(),
            'automation_strategy': self._define_automation_strategy(),
        }

        return strategy

    def _analyze_testing_risks(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[FunctionalRequirement]
    ) -> List[Dict[str, str]]:
        """テストリスクを分析"""
        risks = []

        # 外部システム連携リスク
        if business_requirement.constraints:
            for constraint in business_requirement.constraints:
                if '連携' in constraint.description:
                    risks.append(
                        {
                            'risk': '外部システム依存によるテスト制約',
                            'impact': 'high',
                            'probability': 'medium',
                            'mitigation': 'モックシステムの作成、契約によるテスト環境提供',
                        }
                    )

        # 複雑な機能のリスク
        high_complexity_count = sum(1 for req in functional_requirements if req.complexity == 'high')
        if high_complexity_count > 3:
            risks.append(
                {
                    'risk': '複雑な機能による網羅的テストの困難性',
                    'impact': 'high',
                    'probability': 'high',
                    'mitigation': 'リスクベーステスト、重要シナリオの優先実施',
                }
            )

        # データ依存のリスク
        data_dependent = any('データ' in req.user_story for req in functional_requirements)
        if data_dependent:
            risks.append(
                {
                    'risk': 'テストデータの品質によるテスト結果への影響',
                    'impact': 'medium',
                    'probability': 'medium',
                    'mitigation': 'テストデータの品質管理、本番類似データの準備',
                }
            )

        return risks

    def _define_test_environment(self) -> Dict[str, Any]:
        """テスト環境の定義"""
        return {
            'environments': [
                {'name': '開発環境', 'purpose': '開発者によるユニット・統合テスト', 'data': '開発用データ'},
                {'name': 'テスト環境', 'purpose': 'QAチームによるシステムテスト', 'data': 'テスト用データ'},
                {'name': 'ステージング環境', 'purpose': '本番環境での最終確認', 'data': '本番類似データ'},
            ],
            'requirements': ['本番環境との構成整合性', 'テストデータの適切な管理', '環境間のデータ同期機能'],
        }

    def _define_test_data_strategy(self) -> Dict[str, Any]:
        """テストデータ戦略の定義"""
        return {
            'data_types': [
                {'type': '正常データ', 'description': '業務で使用される標準的なデータ', 'coverage': 'すべての機能'},
                {'type': '境界値データ', 'description': '最大・最小・境界値のデータ', 'coverage': '入力値検証が必要な機能'},
                {'type': '異常データ', 'description': '不正・不適切なデータ', 'coverage': 'エラーハンドリングが必要な機能'},
            ],
            'data_management': [
                'テストデータの自動生成機能',
                'テストデータのバージョン管理',
                '個人情報の適切なマスキング',
                'テスト後のデータクリーンアップ',
            ],
        }

    def _define_automation_strategy(self) -> Dict[str, Any]:
        """自動化戦略の定義"""
        return {
            'automation_pyramid': {'unit_tests': '70%', 'integration_tests': '20%', 'ui_tests': '10%'},
            'automation_tools': [
                'ユニットテスト: Jest, pytest',
                '統合テスト: Postman, REST Assured',
                'UIテスト: Selenium, Cypress',
                '性能テスト: JMeter, k6',
            ],
            'ci_cd_integration': [
                'コミット時の自動テスト実行',
                'デプロイ前の自動テスト実行',
                'テスト結果の自動レポート生成',
                'テスト失敗時の自動通知',
            ],
        }

    def _create_test_cases(self, functional_requirements: List[FunctionalRequirement]) -> List[Dict[str, Any]]:
        """テストケースを作成"""
        test_cases = []

        for i, req in enumerate(functional_requirements, 1):
            # 正常系テストケース
            test_cases.append(
                {
                    'test_case_id': f'TC_{i:03d}_001',
                    'test_name': f'{req.user_story} - 正常系',
                    'test_type': '機能テスト',
                    'priority': req.priority,
                    'preconditions': '適切な権限でログイン済み',
                    'test_steps': self._generate_normal_test_steps(req),
                    'expected_result': '機能が正常に動作し、期待される結果が得られる',
                    'test_data': '正常データ',
                }
            )

            # 異常系テストケース
            test_cases.append(
                {
                    'test_case_id': f'TC_{i:03d}_002',
                    'test_name': f'{req.user_story} - 異常系',
                    'test_type': '機能テスト',
                    'priority': 'medium',
                    'preconditions': '適切な権限でログイン済み',
                    'test_steps': self._generate_error_test_steps(req),
                    'expected_result': 'エラーが適切にハンドリングされ、分かりやすいメッセージが表示される',
                    'test_data': '異常データ',
                }
            )

        return test_cases

    def _generate_normal_test_steps(self, requirement: FunctionalRequirement) -> List[str]:
        """正常系テストステップを生成"""
        user_story = requirement.user_story

        if 'データ' in user_story and '作成' in user_story:
            return [
                '1. データ作成画面にアクセスする',
                '2. 必要な項目に有効な値を入力する',
                '3. 「作成」ボタンをクリックする',
                '4. 作成完了メッセージを確認する',
                '5. データが一覧に表示されることを確認する',
            ]
        elif 'レポート' in user_story:
            return [
                '1. レポート作成画面にアクセスする',
                '2. レポート条件を設定する',
                '3. 「生成」ボタンをクリックする',
                '4. レポートが生成されることを確認する',
                '5. レポート内容が正確であることを確認する',
            ]
        else:
            return ['1. 機能の画面にアクセスする', '2. 必要な操作を実行する', '3. 結果を確認する']

    def _generate_error_test_steps(self, requirement: FunctionalRequirement) -> List[str]:
        """異常系テストステップを生成"""
        user_story = requirement.user_story

        if 'データ' in user_story:
            return [
                '1. データ作成画面にアクセスする',
                '2. 必須項目を空白または無効な値を入力する',
                '3. 「作成」ボタンをクリックする',
                '4. バリデーションエラーメッセージが表示されることを確認する',
                '5. データが作成されていないことを確認する',
            ]
        else:
            return [
                '1. 機能の画面にアクセスする',
                '2. 無効な操作または無効なデータで機能を実行する',
                '3. エラーメッセージが表示されることを確認する',
            ]

    def _define_quality_standards(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """品質基準を定義"""
        return {
            'functional_quality': {
                'defect_density': '1 defect/KLOC以下',
                'test_coverage': 'コードカバレッジ90%以上',
                'requirement_coverage': '機能要件100%カバー',
            },
            'performance_quality': {
                'response_time': '95%のリクエストが3秒以内',
                'throughput': 'ピーク時100リクエスト/秒',
                'availability': '99.9%以上',
            },
            'security_quality': {
                'vulnerability_scan': '高・中リスク脆弱性ゼロ',
                'penetration_test': '年1回実施',
                'security_review': 'リリース前必須実施',
            },
            'usability_quality': {
                'user_satisfaction': 'ユーザー満足度80%以上',
                'task_completion_rate': '主要タスク95%完了率',
                'error_rate': 'ユーザーエラー率5%以下',
            },
        }
