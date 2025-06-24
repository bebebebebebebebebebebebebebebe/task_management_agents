"""インフラエンジニア・エージェント"""

from typing import Any, Dict, List

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.personas.base_persona import BasePersonaAgent
from agents.requirement_process.schemas import NonFunctionalRequirement, PersonaOutput, PersonaRole


class InfrastructureEngineerAgent(BasePersonaAgent):
    """インフラエンジニア・エージェント

    インフラストラクチャの観点から非機能要件を定義し、運用要件を策定する
    """

    def __init__(self):
        super().__init__(PersonaRole.INFRASTRUCTURE_ENGINEER)

    def define_requirements(
        self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput]
    ) -> PersonaOutput:
        """インフラ要件の定義を実行"""
        return self.execute(business_requirement, previous_outputs)

    def execute(self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput] = None) -> PersonaOutput:
        """インフラ観点からの要件定義を実行"""

        # 機能要件を分析してインフラ要件を導出
        functional_requirements = self._extract_functional_requirements(previous_outputs)

        # 非機能要件を定義
        non_functional_requirements = self._define_non_functional_requirements(business_requirement, functional_requirements)

        # インフラアーキテクチャを設計
        infrastructure_architecture = self._design_infrastructure_architecture(business_requirement, functional_requirements)

        # 運用要件を定義
        operational_requirements = self._define_operational_requirements(business_requirement)

        # 監視・アラート要件を定義
        monitoring_requirements = self._define_monitoring_requirements(business_requirement)

        # 災害復旧要件を定義
        disaster_recovery = self._define_disaster_recovery_requirements(business_requirement)

        deliverables = {
            'non_functional_requirements': non_functional_requirements,
            'infrastructure_architecture': infrastructure_architecture,
            'operational_requirements': operational_requirements,
            'monitoring_requirements': monitoring_requirements,
            'disaster_recovery': disaster_recovery,
        }

        recommendations = [
            'クラウドネイティブアーキテクチャの採用により、スケーラビリティと可用性を向上',
            'Infrastructure as Code (IaC)による環境構築の自動化を推奨',
            'コンテナ化によるポータビリティとデプロイメント効率の向上を推奨',
            'マイクロサービスアーキテクチャによる疎結合設計を推奨',
            '継続的な性能監視とアラート機能の実装を推奨',
        ]

        concerns = [
            'クラウドベンダーロックインのリスク',
            '複雑なマイクロサービス構成での運用コストの増加',
            'セキュリティ要件とパフォーマンス要件のトレードオフ',
            '災害復旧時の復旧時間目標（RTO）達成の困難性',
        ]

        return self._create_output(deliverables, recommendations, concerns)

    def _extract_functional_requirements(self, previous_outputs: List[PersonaOutput]) -> List[Dict[str, Any]]:
        """前段階の機能要件を抽出"""
        functional_requirements = []

        if previous_outputs:
            for output in previous_outputs:
                if output.persona_role in [PersonaRole.UX_DESIGNER, PersonaRole.QA_ENGINEER]:
                    if 'functional_requirements' in output.deliverables:
                        functional_requirements.extend(output.deliverables['functional_requirements'])

        return functional_requirements

    def _define_non_functional_requirements(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[Dict[str, Any]]
    ) -> List[NonFunctionalRequirement]:
        """非機能要件を定義"""

        non_functional_reqs = []

        # 性能要件
        performance_reqs = self._define_performance_requirements(business_requirement, functional_requirements)
        non_functional_reqs.extend(performance_reqs)

        # 可用性要件
        availability_reqs = self._define_availability_requirements(business_requirement)
        non_functional_reqs.extend(availability_reqs)

        # スケーラビリティ要件
        scalability_reqs = self._define_scalability_requirements(business_requirement, functional_requirements)
        non_functional_reqs.extend(scalability_reqs)

        # 運用性要件
        operability_reqs = self._define_operability_requirements(business_requirement)
        non_functional_reqs.extend(operability_reqs)

        return non_functional_reqs

    def _define_performance_requirements(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[Dict[str, Any]]
    ) -> List[NonFunctionalRequirement]:
        """性能要件を定義"""

        requirements = []

        # 基本性能要件
        requirements.append(
            NonFunctionalRequirement(
                category='性能',
                requirement='Webページの応答時間',
                target_value='95%のリクエストで3秒以内',
                test_method='負荷テストツール（JMeter）による測定',
            )
        )

        requirements.append(
            NonFunctionalRequirement(
                category='性能',
                requirement='APIの応答時間',
                target_value='95%のAPIコールで1秒以内',
                test_method='APIテストツール（Postman, k6）による測定',
            )
        )

        requirements.append(
            NonFunctionalRequirement(
                category='性能',
                requirement='スループット',
                target_value='ピーク時100リクエスト/秒',
                test_method='段階的負荷テストによる測定',
            )
        )

        # データベース性能要件
        has_data_operations = any('データ' in str(req) for req in functional_requirements)
        if has_data_operations:
            requirements.append(
                NonFunctionalRequirement(
                    category='性能',
                    requirement='データベースクエリ性能',
                    target_value='単純クエリ100ms以内、複雑クエリ1秒以内',
                    test_method='データベース性能監視ツールによる測定',
                )
            )

        # レポート生成性能要件
        has_reporting = any('レポート' in str(req) for req in functional_requirements)
        if has_reporting:
            requirements.append(
                NonFunctionalRequirement(
                    category='性能',
                    requirement='レポート生成時間',
                    target_value='標準レポート30秒以内、大量データレポート5分以内',
                    test_method='レポート生成時間の実測による検証',
                )
            )

        return requirements

    def _define_availability_requirements(self, business_requirement: ProjectBusinessRequirement) -> List[NonFunctionalRequirement]:
        """可用性要件を定義"""

        requirements = []

        # システム可用性
        requirements.append(
            NonFunctionalRequirement(
                category='可用性',
                requirement='システム稼働率',
                target_value='99.9%以上（月間ダウンタイム44分以内）',
                test_method='監視ツールによる稼働時間測定',
            )
        )

        # 計画メンテナンス
        requirements.append(
            NonFunctionalRequirement(
                category='可用性',
                requirement='計画メンテナンス時間',
                target_value='月1回、4時間以内',
                test_method='メンテナンス履歴の記録と分析',
            )
        )

        # 障害復旧時間
        requirements.append(
            NonFunctionalRequirement(
                category='可用性', requirement='障害復旧時間（RTO）', target_value='4時間以内', test_method='障害復旧演習による実測'
            )
        )

        # データ復旧ポイント
        requirements.append(
            NonFunctionalRequirement(
                category='可用性',
                requirement='データ復旧ポイント（RPO）',
                target_value='1時間以内',
                test_method='バックアップ・リストア演習による検証',
            )
        )

        return requirements

    def _define_scalability_requirements(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[Dict[str, Any]]
    ) -> List[NonFunctionalRequirement]:
        """スケーラビリティ要件を定義"""

        requirements = []

        # 水平スケーリング
        requirements.append(
            NonFunctionalRequirement(
                category='スケーラビリティ',
                requirement='水平スケーリング',
                target_value='負荷に応じて自動で2-10インスタンスでスケール',
                test_method='負荷テストによるオートスケーリング検証',
            )
        )

        # データ容量スケーリング
        requirements.append(
            NonFunctionalRequirement(
                category='スケーラビリティ',
                requirement='データ容量',
                target_value='初期1TB、年間50%成長に対応',
                test_method='容量監視とストレージ拡張テスト',
            )
        )

        # 同時接続数
        requirements.append(
            NonFunctionalRequirement(
                category='スケーラビリティ',
                requirement='同時接続数',
                target_value='1,000同時接続まで対応',
                test_method='接続数負荷テストによる検証',
            )
        )

        # ユーザー数スケーリング
        if business_requirement.stake_holders:
            user_count = len(business_requirement.stake_holders) * 10  # 推定ユーザー数
            requirements.append(
                NonFunctionalRequirement(
                    category='スケーラビリティ',
                    requirement='ユーザー数対応',
                    target_value=f'{user_count}アクティブユーザーまで対応',
                    test_method='ユーザー負荷シミュレーションテスト',
                )
            )

        return requirements

    def _define_operability_requirements(self, business_requirement: ProjectBusinessRequirement) -> List[NonFunctionalRequirement]:
        """運用性要件を定義"""

        requirements = []

        # デプロイメント
        requirements.append(
            NonFunctionalRequirement(
                category='運用性',
                requirement='デプロイメント時間',
                target_value='30分以内',
                test_method='デプロイメント自動化による時間測定',
            )
        )

        # ログ管理
        requirements.append(
            NonFunctionalRequirement(
                category='運用性',
                requirement='ログ保持期間',
                target_value='アプリケーションログ3ヶ月、監査ログ1年',
                test_method='ログローテーション設定の確認',
            )
        )

        # バックアップ
        requirements.append(
            NonFunctionalRequirement(
                category='運用性',
                requirement='バックアップ頻度',
                target_value='データベース：日次、システム設定：週次',
                test_method='バックアップスケジュールと復元テスト',
            )
        )

        # 監視
        requirements.append(
            NonFunctionalRequirement(
                category='運用性',
                requirement='監視カバレッジ',
                target_value='重要コンポーネント100%監視',
                test_method='監視項目チェックリストによる確認',
            )
        )

        return requirements

    def _design_infrastructure_architecture(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """インフラアーキテクチャを設計"""

        # システム構成の基本方針を決定
        architecture_pattern = self._determine_architecture_pattern(functional_requirements)

        # クラウドプロバイダーの選定
        cloud_provider = self._select_cloud_provider(business_requirement)

        # コンピューティングリソース設計
        compute_resources = self._design_compute_resources(functional_requirements)

        # ストレージ設計
        storage_design = self._design_storage(functional_requirements)

        # ネットワーク設計
        network_design = self._design_network(business_requirement)

        # セキュリティ設計
        security_design = self._design_security_infrastructure(business_requirement)

        return {
            'architecture_pattern': architecture_pattern,
            'cloud_provider': cloud_provider,
            'compute_resources': compute_resources,
            'storage_design': storage_design,
            'network_design': network_design,
            'security_design': security_design,
        }

    def _determine_architecture_pattern(self, functional_requirements: List[Dict[str, Any]]) -> Dict[str, str]:
        """アーキテクチャパターンを決定"""

        # 機能の複雑さと数から判断
        requirement_count = len(functional_requirements)
        has_complex_features = any('high' in str(req) for req in functional_requirements)

        if requirement_count > 10 or has_complex_features:
            return {
                'pattern': 'マイクロサービス',
                'rationale': '複雑な機能要件に対応し、独立性とスケーラビリティを確保',
                'benefits': ['各サービスの独立デプロイ可能', '技術スタックの多様性', '障害の局所化'],
            }
        else:
            return {
                'pattern': 'モノリシック（レイヤードアーキテクチャ）',
                'rationale': 'シンプルな構成で開発・運用コストを抑制',
                'benefits': ['シンプルなデプロイメント', '運用コストの削減', '開発チームの負担軽減'],
            }

    def _select_cloud_provider(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """クラウドプロバイダーを選定"""

        # デフォルトでAWSを選択（実際は要件に基づいて選定）
        provider = {
            'primary': 'AWS',
            'rationale': '豊富なサービス群と実績、エンタープライズサポート',
            'services': {
                'compute': 'EC2, ECS/Fargate',
                'database': 'RDS, DynamoDB',
                'storage': 'S3, EBS',
                'networking': 'VPC, ALB/NLB',
                'monitoring': 'CloudWatch',
                'security': 'IAM, WAF, Security Groups',
            },
            'backup_option': 'Google Cloud Platform（マルチクラウド戦略）',
        }

        # 規制要件の確認
        if business_requirement.compliance:
            provider['compliance_features'] = ['SOC 2 Type II準拠', 'ISO 27001認証', 'GDPR対応機能', '監査ログ機能']

        return provider

    def _design_compute_resources(self, functional_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """コンピューティングリソースを設計"""

        # 基本構成
        compute_design = {
            'application_tier': {
                'service': 'ECS Fargate',
                'configuration': 'CPU: 2vCPU, Memory: 4GB',
                'scaling': 'Auto Scaling（2-10インスタンス）',
                'rationale': 'コンテナ化による可搬性とスケーラビリティ',
            },
            'web_tier': {
                'service': 'Application Load Balancer',
                'configuration': 'SSL終端、ヘルスチェック機能',
                'availability_zones': '複数AZ配置',
                'rationale': '高可用性と負荷分散',
            },
            'background_processing': {
                'service': 'SQS + Lambda',
                'configuration': 'イベント駆動処理',
                'scaling': 'オンデマンドスケーリング',
                'rationale': 'コスト効率的な非同期処理',
            },
        }

        # API機能がある場合
        has_api = any('API' in str(req) for req in functional_requirements)
        if has_api:
            compute_design['api_gateway'] = {
                'service': 'Amazon API Gateway',
                'configuration': 'REST API, レート制限, 認証',
                'features': ['API キー管理', 'リクエスト・レスポンス変換'],
                'rationale': 'API管理とセキュリティの統一',
            }

        return compute_design

    def _design_storage(self, functional_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ストレージを設計"""

        storage_design = {
            'primary_database': {
                'service': 'Amazon RDS (PostgreSQL)',
                'configuration': 'Multi-AZ, 自動バックアップ',
                'storage': 'gp3 SSD, 100GB初期容量',
                'rationale': 'ACID特性とリレーショナルデータモデルの要求',
            },
            'file_storage': {
                'service': 'Amazon S3',
                'configuration': 'Standard tier, バージョニング有効',
                'backup': 'Cross-Region Replication',
                'rationale': '高耐久性とコスト効率性',
            },
            'caching': {
                'service': 'Amazon ElastiCache (Redis)',
                'configuration': '1GB, クラスター無効',
                'rationale': 'アプリケーション性能の向上',
            },
        }

        # レポート機能がある場合
        has_reporting = any('レポート' in str(req) for req in functional_requirements)
        if has_reporting:
            storage_design['data_warehouse'] = {
                'service': 'Amazon Redshift Serverless',
                'configuration': '分析ワークロード用',
                'rationale': '大量データの高速分析',
            }

        return storage_design

    def _design_network(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """ネットワークを設計"""

        return {
            'vpc_design': {
                'cidr': '10.0.0.0/16',
                'availability_zones': '3AZ構成',
                'subnets': {
                    'public': '10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24',
                    'private': '10.0.11.0/24, 10.0.12.0/24, 10.0.13.0/24',
                    'database': '10.0.21.0/24, 10.0.22.0/24, 10.0.23.0/24',
                },
            },
            'security_groups': {
                'web_tier': 'HTTP/HTTPS（80,443）のみ許可',
                'app_tier': 'Web tierからのアクセスのみ許可',
                'db_tier': 'App tierからのDBポートのみ許可',
            },
            'load_balancer': {
                'type': 'Application Load Balancer',
                'configuration': 'インターネット向け, SSL証明書',
                'health_check': 'HTTP health check endpoint',
            },
            'dns': {'service': 'Route 53', 'configuration': 'カスタムドメイン, health check'},
        }

    def _design_security_infrastructure(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """セキュリティインフラを設計"""

        security_design = {
            'network_security': {
                'waf': 'AWS WAF v2（OWASP Top 10対策）',
                'ddos_protection': 'AWS Shield Standard',
                'vpc_flow_logs': '有効化（監査目的）',
            },
            'access_control': {
                'iam': 'IAM Role-based access control',
                'mfa': '管理者アカウントでMFA必須',
                'key_management': 'AWS KMS（暗号化キー管理）',
            },
            'data_protection': {
                'encryption_at_rest': 'RDS/S3暗号化有効',
                'encryption_in_transit': 'SSL/TLS通信の強制',
                'backup_encryption': 'バックアップデータの暗号化',
            },
            'monitoring': {'cloudtrail': 'API呼び出しログ記録', 'config': 'リソース設定変更の監視', 'guardduty': '脅威検知サービス'},
        }

        # コンプライアンス要件がある場合
        if business_requirement.compliance:
            security_design['compliance'] = {
                'audit_logging': '全操作ログの記録と保管',
                'access_review': '四半期ごとのアクセス権限レビュー',
                'vulnerability_scanning': '週次の脆弱性スキャン',
                'penetration_testing': '年次のペネトレーションテスト',
            }

        return security_design

    def _define_operational_requirements(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """運用要件を定義"""

        return {
            'deployment': {
                'strategy': 'Blue-Green Deployment',
                'automation': 'CI/CD pipeline（GitHub Actions）',
                'rollback': '自動ロールバック機能',
                'deployment_window': '平日9:00-17:00（営業時間外推奨）',
            },
            'maintenance': {
                'patching_schedule': '月次（第2土曜日深夜）',
                'maintenance_window': '4時間以内',
                'notification': '事前48時間前に通知',
                'emergency_patch': '24時間以内の緊急対応',
            },
            'backup': {
                'database_backup': '日次（RDS自動バックアップ）',
                'file_backup': 'S3 Cross-Region Replication',
                'system_backup': '週次（AMIスナップショット）',
                'retention_period': 'DB：35日、ファイル：1年、システム：3ヶ月',
            },
            'support': {
                'business_hours': '平日9:00-18:00',
                'emergency_support': '24/7対応（重大障害時）',
                'response_time': 'P1：1時間、P2：4時間、P3：1営業日',
                'escalation': '2時間でエスカレーション',
            },
        }

    def _define_monitoring_requirements(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """監視・アラート要件を定義"""

        return {
            'infrastructure_monitoring': {
                'metrics': [
                    'CPU使用率（閾値：80%）',
                    'メモリ使用率（閾値：85%）',
                    'ディスク使用率（閾値：80%）',
                    'ネットワーク通信量',
                ],
                'tools': 'CloudWatch, CloudWatch Logs',
                'retention': 'メトリクス：1年、ログ：3ヶ月',
            },
            'application_monitoring': {
                'metrics': ['レスポンス時間', 'エラー率（閾値：5%）', 'スループット', 'アプリケーションエラー'],
                'tools': 'CloudWatch Application Insights',
                'custom_metrics': 'ビジネスKPI監視',
            },
            'database_monitoring': {
                'metrics': ['接続数（閾値：80%）', 'クエリ実行時間', 'デッドロック発生数', 'ストレージ使用量'],
                'tools': 'RDS Performance Insights',
                'slow_query_log': '有効化',
            },
            'alerting': {
                'channels': ['Email', 'Slack', 'SMS（重大障害）'],
                'escalation_rules': ['P1：即座に通知', 'P2：15分後に再通知', 'P3：1時間後に再通知'],
                'on_call_rotation': '平日・休日の運用体制',
            },
        }

    def _define_disaster_recovery_requirements(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """災害復旧要件を定義"""

        return {
            'recovery_objectives': {
                'rto': '4時間（Recovery Time Objective）',
                'rpo': '1時間（Recovery Point Objective）',
                'rationale': 'ビジネス継続性とデータ保護のバランス',
            },
            'backup_strategy': {
                'database': {
                    'method': 'RDS自動バックアップ + 手動スナップショット',
                    'frequency': '日次自動 + 重要変更前手動',
                    'retention': '35日間',
                    'cross_region': '別リージョンにレプリケーション',
                },
                'application': {'method': 'EC2 AMIスナップショット', 'frequency': '週次', 'retention': '3ヶ月'},
                'files': {'method': 'S3 Cross-Region Replication', 'frequency': 'リアルタイム', 'retention': '1年間'},
            },
            'recovery_procedures': {
                'database_recovery': [
                    '1. 最新バックアップの特定',
                    '2. 別AZでのDB復元',
                    '3. アプリケーション接続先変更',
                    '4. データ整合性確認',
                ],
                'application_recovery': [
                    '1. 最新AMIからインスタンス起動',
                    '2. 設定ファイルの復元',
                    '3. 動作確認テスト',
                    '4. ロードバランサーへの追加',
                ],
                'full_system_recovery': [
                    '1. 災害影響範囲の特定',
                    '2. 復旧優先順位の決定',
                    '3. 別リージョンでのシステム復旧',
                    '4. DNSの切り替え',
                    '5. 全機能の動作確認',
                ],
            },
            'testing': {
                'frequency': '四半期ごと',
                'scope': '部分復旧テスト（月次）、全体復旧テスト（年次）',
                'documentation': '復旧手順書の更新',
                'validation': '復旧時間とデータ整合性の確認',
            },
        }
