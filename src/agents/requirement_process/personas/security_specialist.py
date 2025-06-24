"""セキュリティスペシャリスト・エージェント"""

from typing import Any, Dict, List

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.personas.base_persona import BasePersonaAgent
from agents.requirement_process.schemas import NonFunctionalRequirement, PersonaOutput, PersonaRole


class SecuritySpecialistAgent(BasePersonaAgent):
    """セキュリティスペシャリスト・エージェント

    セキュリティ観点から非機能要件を定義し、セキュリティ対策を策定する
    """

    def __init__(self):
        super().__init__(PersonaRole.SECURITY_SPECIALIST)

    def define_security_requirements(
        self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput]
    ) -> PersonaOutput:
        """セキュリティ要件の定義を実行"""
        return self.execute(business_requirement, previous_outputs)

    def execute(self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput] = None) -> PersonaOutput:
        """セキュリティ観点からの要件定義を実行"""

        # 機能要件を分析してセキュリティリスクを評価
        functional_requirements = self._extract_functional_requirements(previous_outputs)
        security_risks = self._assess_security_risks(business_requirement, functional_requirements)

        # セキュリティ非機能要件を定義
        security_requirements = self._define_security_non_functional_requirements(
            business_requirement, functional_requirements, security_risks
        )

        # セキュリティアーキテクチャを設計
        security_architecture = self._design_security_architecture(business_requirement, functional_requirements)

        # セキュリティ運用要件を定義
        security_operations = self._define_security_operations(business_requirement)

        # コンプライアンス要件を定義
        compliance_requirements = self._define_compliance_requirements(business_requirement)

        # セキュリティテスト要件を定義
        security_testing = self._define_security_testing_requirements(functional_requirements)

        deliverables = {
            'security_risks': security_risks,
            'security_requirements': security_requirements,
            'security_architecture': security_architecture,
            'security_operations': security_operations,
            'compliance_requirements': compliance_requirements,
            'security_testing': security_testing,
        }

        recommendations = [
            'ゼロトラストアーキテクチャの採用により、内部脅威への対策を強化',
            'DevSecOpsプロセスの導入により、開発段階からセキュリティを組み込み',
            'セキュリティ監視（SIEM/SOC）の24/7体制構築を推奨',
            '定期的な脆弱性診断とペネトレーションテストの実施',
            'セキュリティ意識向上のための従業員研修プログラムの実施',
            'インシデント対応計画（CSIRT）の策定と定期的な訓練実施',
        ]

        concerns = [
            'セキュリティ要件とユーザビリティのトレードオフ',
            '新しいセキュリティ脅威への継続的な対応コスト',
            'サードパーティ製品のセキュリティ脆弱性リスク',
            '内部関係者による情報漏洩リスク',
            'クラウドサービスのセキュリティ設定ミスリスク',
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

    def _assess_security_risks(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """セキュリティリスクを評価"""

        risks = []

        # データ処理に関するリスク
        has_data_processing = any('データ' in str(req) for req in functional_requirements)
        if has_data_processing:
            risks.append(
                {
                    'risk_category': 'データ保護',
                    'risk_description': '個人情報・機密データの不正アクセス・漏洩',
                    'impact': 'high',
                    'probability': 'medium',
                    'threat_actors': ['外部攻撃者', '内部関係者', '第三者プロバイダー'],
                    'attack_vectors': ['SQLインジェクション', '権限昇格', '設定ミス'],
                }
            )

        # API機能に関するリスク
        has_api = any('API' in str(req) for req in functional_requirements)
        if has_api:
            risks.append(
                {
                    'risk_category': 'APIセキュリティ',
                    'risk_description': 'API経由での不正アクセス・データ窃取',
                    'impact': 'high',
                    'probability': 'medium',
                    'threat_actors': ['外部攻撃者', 'ボット'],
                    'attack_vectors': ['APIキー窃取', 'レート制限回避', '認証回避'],
                }
            )

        # Web機能に関するリスク
        has_web = any('Web' in str(req) for req in functional_requirements)
        if has_web:
            risks.append(
                {
                    'risk_category': 'Webアプリケーション',
                    'risk_description': 'OWASP Top 10脆弱性による攻撃',
                    'impact': 'high',
                    'probability': 'high',
                    'threat_actors': ['外部攻撃者', 'スクリプトキディ'],
                    'attack_vectors': ['XSS', 'CSRF', 'セッション管理不備'],
                }
            )

        # 認証・認可に関するリスク
        risks.append(
            {
                'risk_category': '認証・認可',
                'risk_description': '不正ログイン・権限昇格',
                'impact': 'high',
                'probability': 'medium',
                'threat_actors': ['外部攻撃者', '内部関係者'],
                'attack_vectors': ['ブルートフォース', 'パスワードリスト攻撃', '権限設定ミス'],
            }
        )

        # インフラストラクチャに関するリスク
        risks.append(
            {
                'risk_category': 'インフラ',
                'risk_description': 'クラウドインフラの設定ミス・不正アクセス',
                'impact': 'high',
                'probability': 'medium',
                'threat_actors': ['外部攻撃者', '内部関係者'],
                'attack_vectors': ['設定ミス', 'クレデンシャル窃取', 'サイドチャネル攻撃'],
            }
        )

        # コンプライアンス関連リスク
        if business_requirement.compliance:
            risks.append(
                {
                    'risk_category': 'コンプライアンス',
                    'risk_description': '法規制違反による罰金・業務停止',
                    'impact': 'high',
                    'probability': 'low',
                    'threat_actors': ['監督官庁', '監査法人'],
                    'attack_vectors': ['監査', '報告義務違反', 'データ保護規則違反'],
                }
            )

        return risks

    def _define_security_non_functional_requirements(
        self,
        business_requirement: ProjectBusinessRequirement,
        functional_requirements: List[Dict[str, Any]],
        security_risks: List[Dict[str, Any]],
    ) -> List[NonFunctionalRequirement]:
        """セキュリティ非機能要件を定義"""

        requirements = []

        # 認証・認可要件
        requirements.extend(self._define_authentication_requirements())

        # データ保護要件
        requirements.extend(self._define_data_protection_requirements(functional_requirements))

        # 通信セキュリティ要件
        requirements.extend(self._define_communication_security_requirements())

        # 監査・ログ要件
        requirements.extend(self._define_audit_logging_requirements(business_requirement))

        # 脆弱性管理要件
        requirements.extend(self._define_vulnerability_management_requirements())

        # インシデント対応要件
        requirements.extend(self._define_incident_response_requirements())

        return requirements

    def _define_authentication_requirements(self) -> List[NonFunctionalRequirement]:
        """認証・認可要件を定義"""
        return [
            NonFunctionalRequirement(
                category='認証・認可',
                requirement='パスワードポリシー',
                target_value='最小8文字、英数字記号組み合わせ、90日間有効',
                test_method='パスワード作成・変更時の自動検証',
            ),
            NonFunctionalRequirement(
                category='認証・認可',
                requirement='多要素認証（MFA）',
                target_value='管理者アカウント必須、一般ユーザー推奨',
                test_method='認証フロー動作テスト',
            ),
            NonFunctionalRequirement(
                category='認証・認可',
                requirement='セッション管理',
                target_value='アイドル30分でタイムアウト、絶対タイムアウト8時間',
                test_method='セッション有効期限の自動テスト',
            ),
            NonFunctionalRequirement(
                category='認証・認可',
                requirement='アカウントロック',
                target_value='5回ログイン失敗で15分間ロック',
                test_method='ブルートフォース攻撃シミュレーション',
            ),
            NonFunctionalRequirement(
                category='認証・認可',
                requirement='権限分離',
                target_value='最小権限の原則、Role-Based Access Control',
                test_method='権限マトリックスによる検証',
            ),
        ]

    def _define_data_protection_requirements(self, functional_requirements: List[Dict[str, Any]]) -> List[NonFunctionalRequirement]:
        """データ保護要件を定義"""
        requirements = [
            NonFunctionalRequirement(
                category='データ保護',
                requirement='保存時暗号化',
                target_value='AES-256による暗号化、キー管理システム使用',
                test_method='暗号化状態の確認とキーローテーションテスト',
            ),
            NonFunctionalRequirement(
                category='データ保護',
                requirement='通信時暗号化',
                target_value='TLS 1.3以上、HTTP Strict Transport Security',
                test_method='SSL/TLS設定の脆弱性診断',
            ),
            NonFunctionalRequirement(
                category='データ保護',
                requirement='データマスキング',
                target_value='本番以外環境で個人情報をマスキング',
                test_method='データマスキング状態の確認',
            ),
            NonFunctionalRequirement(
                category='データ保護',
                requirement='データ削除',
                target_value='論理削除後30日で物理削除、完全削除保証',
                test_method='データ復旧不可能性の確認',
            ),
        ]

        # 個人情報を扱う場合の追加要件
        has_personal_data = any('個人' in str(req) for req in functional_requirements)
        if has_personal_data:
            requirements.append(
                NonFunctionalRequirement(
                    category='データ保護',
                    requirement='個人情報管理',
                    target_value='GDPR/個人情報保護法準拠、データ主体の権利対応',
                    test_method='個人情報取扱いプロセスの監査',
                )
            )

        return requirements

    def _define_communication_security_requirements(self) -> List[NonFunctionalRequirement]:
        """通信セキュリティ要件を定義"""
        return [
            NonFunctionalRequirement(
                category='通信セキュリティ',
                requirement='HTTPS強制',
                target_value='全通信でHTTPS必須、HTTP自動リダイレクト',
                test_method='HTTPアクセス時のリダイレクト確認',
            ),
            NonFunctionalRequirement(
                category='通信セキュリティ',
                requirement='セキュリティヘッダー',
                target_value='HSTS, CSP, X-Frame-Options等の実装',
                test_method='セキュリティヘッダーの自動検証',
            ),
            NonFunctionalRequirement(
                category='通信セキュリティ',
                requirement='API暗号化',
                target_value='機密データのフィールドレベル暗号化',
                test_method='API通信内容の暗号化確認',
            ),
            NonFunctionalRequirement(
                category='通信セキュリティ',
                requirement='ネットワーク分離',
                target_value='DMZ、内部ネットワークの適切な分離',
                test_method='ネットワークアクセス制御テスト',
            ),
        ]

    def _define_audit_logging_requirements(self, business_requirement: ProjectBusinessRequirement) -> List[NonFunctionalRequirement]:
        """監査・ログ要件を定義"""
        requirements = [
            NonFunctionalRequirement(
                category='監査・ログ',
                requirement='アクセスログ',
                target_value='全アクセスログの記録、改ざん防止',
                test_method='ログ生成とログ改ざん検知テスト',
            ),
            NonFunctionalRequirement(
                category='監査・ログ',
                requirement='操作ログ',
                target_value='CRUD操作の詳細ログ、ユーザー特定可能',
                test_method='操作ログの完全性確認',
            ),
            NonFunctionalRequirement(
                category='監査・ログ',
                requirement='セキュリティイベント',
                target_value='認証失敗、権限エラー等の即座通知',
                test_method='セキュリティイベント検知テスト',
            ),
            NonFunctionalRequirement(
                category='監査・ログ',
                requirement='ログ保持',
                target_value='1年間保持、改ざん検知機能',
                test_method='ログ保持期間とバックアップ確認',
            ),
        ]

        # コンプライアンス要件がある場合
        if business_requirement.compliance:
            requirements.append(
                NonFunctionalRequirement(
                    category='監査・ログ',
                    requirement='監査証跡',
                    target_value='法的証拠能力のある監査証跡、検索可能',
                    test_method='監査レポート生成機能の確認',
                )
            )

        return requirements

    def _define_vulnerability_management_requirements(self) -> List[NonFunctionalRequirement]:
        """脆弱性管理要件を定義"""
        return [
            NonFunctionalRequirement(
                category='脆弱性管理',
                requirement='脆弱性スキャン',
                target_value='週次自動スキャン、高リスクは24時間以内対応',
                test_method='脆弱性スキャンツールによる検証',
            ),
            NonFunctionalRequirement(
                category='脆弱性管理',
                requirement='パッチ管理',
                target_value='重要パッチは48時間以内適用',
                test_method='パッチ適用履歴の確認',
            ),
            NonFunctionalRequirement(
                category='脆弱性管理',
                requirement='ペネトレーションテスト',
                target_value='年1回外部業者による実施',
                test_method='ペネトレーションテスト報告書確認',
            ),
            NonFunctionalRequirement(
                category='脆弱性管理',
                requirement='セキュリティコードレビュー',
                target_value='全コミットのセキュリティチェック',
                test_method='SAST/DASTツールによる自動検証',
            ),
        ]

    def _define_incident_response_requirements(self) -> List[NonFunctionalRequirement]:
        """インシデント対応要件を定義"""
        return [
            NonFunctionalRequirement(
                category='インシデント対応',
                requirement='検知時間',
                target_value='セキュリティインシデント15分以内検知',
                test_method='インシデント検知シミュレーション',
            ),
            NonFunctionalRequirement(
                category='インシデント対応',
                requirement='初動対応',
                target_value='検知後30分以内に初動対応開始',
                test_method='インシデント対応手順の訓練',
            ),
            NonFunctionalRequirement(
                category='インシデント対応',
                requirement='証拠保全',
                target_value='フォレンジック対応、証拠保全手順',
                test_method='証拠保全手順の確認',
            ),
            NonFunctionalRequirement(
                category='インシデント対応',
                requirement='復旧時間',
                target_value='重大インシデント4時間以内復旧',
                test_method='インシデント復旧演習',
            ),
        ]

    def _design_security_architecture(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """セキュリティアーキテクチャを設計"""

        return {
            'security_model': self._define_security_model(),
            'network_security': self._design_network_security(),
            'application_security': self._design_application_security(functional_requirements),
            'data_security': self._design_data_security(),
            'identity_management': self._design_identity_management(),
            'monitoring_security': self._design_security_monitoring(),
        }

    def _define_security_model(self) -> Dict[str, Any]:
        """セキュリティモデルを定義"""
        return {
            'model': 'ゼロトラストアーキテクチャ',
            'principles': ['信頼の前提を置かない', '最小権限の原則', '継続的な検証', '明示的な確認'],
            'implementation': {
                'network': 'マイクロセグメンテーション',
                'identity': '多要素認証必須',
                'device': 'デバイス証明書認証',
                'data': '暗号化とアクセス制御',
            },
        }

    def _design_network_security(self) -> Dict[str, Any]:
        """ネットワークセキュリティを設計"""
        return {
            'perimeter_security': {
                'waf': 'AWS WAF（OWASP Top 10対策）',
                'ddos_protection': 'AWS Shield Advanced',
                'load_balancer': 'セキュリティグループによる制御',
            },
            'network_segmentation': {
                'dmz': 'Webサーバー配置（10.0.1.0/24）',
                'application_tier': 'アプリサーバー（10.0.11.0/24）',
                'database_tier': 'DBサーバー（10.0.21.0/24）',
                'management': '管理ネットワーク（10.0.31.0/24）',
            },
            'access_control': {
                'security_groups': '最小権限ベースの設定',
                'nacl': 'ネットワークACLによる追加制御',
                'vpc_endpoints': 'プライベート通信の確保',
            },
            'monitoring': {
                'vpc_flow_logs': '全通信ログの記録',
                'intrusion_detection': 'AWS GuardDuty',
                'traffic_analysis': 'VPC Traffic Mirroring',
            },
        }

    def _design_application_security(self, functional_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """アプリケーションセキュリティを設計"""

        security_controls = {
            'input_validation': {
                'sanitization': '全入力値のサニタイゼーション',
                'validation': 'ホワイトリスト方式の検証',
                'encoding': '出力時の適切なエンコーディング',
            },
            'authentication': {
                'method': 'JWT + OAuth 2.0',
                'session_management': 'セキュアなセッション管理',
                'password_hashing': 'bcrypt/Argon2による暗号化',  # pragma: allowlist secret
            },
            'authorization': {
                'model': 'RBAC（Role-Based Access Control）',
                'implementation': 'カスタムミドルウェア',
                'policy_engine': '動的権限評価エンジン',
            },
            'error_handling': {
                'custom_error_pages': 'システム情報の非公開',
                'logging': 'セキュリティエラーの詳細記録',
                'monitoring': 'エラーパターンの監視',
            },
        }

        # API機能がある場合の追加制御
        has_api = any('API' in str(req) for req in functional_requirements)
        if has_api:
            security_controls['api_security'] = {
                'rate_limiting': 'APIレート制限（100req/min）',
                'api_keys': 'APIキー管理とローテーション',  # pragma: allowlist secret
                'cors': '適切なCORS設定',
                'api_gateway': 'AWS API Gateway統合',
            }

        return security_controls

    def _design_data_security(self) -> Dict[str, Any]:
        """データセキュリティを設計"""
        return {
            'encryption': {
                'at_rest': 'AES-256（AWS KMS管理）',
                'in_transit': 'TLS 1.3',
                'in_processing': 'アプリケーションレベル暗号化',
                'key_management': 'AWS KMS + ハードウェアSM',
            },
            'data_classification': {
                'public': '一般公開データ',
                'internal': '社内限定データ',
                'confidential': '機密データ',
                'restricted': '最高機密データ',
            },
            'access_control': {
                'field_level': 'フィールドレベル暗号化',
                'row_level': '行レベルセキュリティ',
                'column_level': 'カラムレベル権限制御',
                'dynamic_masking': '動的データマスキング',
            },
            'data_loss_prevention': {
                'dlp_scanning': 'データ漏洩検知スキャン',
                'egress_filtering': '送信データフィルタリング',
                'endpoint_protection': 'エンドポイントDLP',
                'cloud_dlp': 'クラウドDLPサービス',
            },
        }

    def _design_identity_management(self) -> Dict[str, Any]:
        """ID管理を設計"""
        return {
            'identity_provider': {
                'primary': 'AWS Cognito',
                'enterprise': 'LDAP/Active Directory統合',
                'social': 'Google/Microsoft OAuth',
            },
            'user_lifecycle': {
                'provisioning': '自動ユーザープロビジョニング',
                'deprovisioning': '離職時の自動アカウント無効化',
                'role_management': '動的ロール割り当て',
                'access_review': '四半期アクセス権限レビュー',
            },
            'privileged_access': {
                'pam': '特権アクセス管理システム',
                'jit_access': 'Just-in-Time アクセス',
                'session_recording': '特権セッション記録',
                'approval_workflow': '承認ワークフロー',
            },
            'federation': {'saml': 'SAML 2.0対応', 'oidc': 'OpenID Connect対応', 'trust_relationships': '信頼関係の管理'},
        }

    def _design_security_monitoring(self) -> Dict[str, Any]:
        """セキュリティ監視を設計"""
        return {
            'siem': {
                'platform': 'AWS Security Hub + CloudTrail',
                'log_sources': [
                    'アプリケーションログ',
                    'Webサーバーログ',
                    'データベースログ',
                    'ネットワークログ',
                    'セキュリティデバイスログ',
                ],
                'correlation_rules': 'カスタムセキュリティルール',
                'alerting': 'リアルタイムアラート',
            },
            'threat_detection': {
                'behavioral_analysis': 'ユーザー行動分析',
                'anomaly_detection': '異常検知機械学習',
                'threat_intelligence': '脅威インテリジェンス統合',
                'indicators': 'IoC（Indicators of Compromise）',
            },
            'incident_response': {
                'playbooks': '自動対応プレイブック',
                'orchestration': 'SOAR（Security Orchestration）',
                'forensics': 'デジタルフォレンジック機能',
                'communication': 'インシデント通信プラットフォーム',
            },
        }

    def _define_security_operations(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """セキュリティ運用要件を定義"""
        return {
            'security_team': {
                'structure': 'CISO, セキュリティエンジニア, SOCアナリスト',
                'responsibilities': ['セキュリティポリシー策定', 'インシデント対応', '脆弱性管理', 'セキュリティ教育'],
                'training': '年次セキュリティ研修必須',
            },
            'security_processes': {
                'policy_review': '年次セキュリティポリシー見直し',
                'risk_assessment': '四半期リスクアセスメント',
                'security_metrics': 'KPI測定とレポート',
                'continuous_improvement': 'セキュリティプロセス改善',
            },
            'third_party_security': {
                'vendor_assessment': 'ベンダーセキュリティ評価',
                'contracts': 'セキュリティ条項の契約組み込み',
                'monitoring': '第三者アクセスの監視',
                'review': '定期的なセキュリティレビュー',
            },
        }

    def _define_compliance_requirements(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """コンプライアンス要件を定義"""

        compliance_reqs = {
            'general_requirements': {
                'data_protection': 'GDPR/個人情報保護法対応',
                'security_standards': 'ISO 27001/SOC 2準拠',
                'audit_requirements': '内部監査・外部監査対応',
                'documentation': 'セキュリティ文書の整備',
            },
            'data_governance': {
                'data_inventory': 'データ棚卸しと分類',
                'retention_policy': 'データ保持・削除ポリシー',
                'consent_management': '同意管理システム',
                'data_subject_rights': 'データ主体の権利対応',
            },
            'reporting': {
                'breach_notification': '72時間以内の漏洩報告',
                'compliance_reporting': '定期的なコンプライアンス報告',
                'audit_trails': '監査証跡の保管',
                'documentation': '手順書・記録の整備',
            },
        }

        # 特定の法規制がある場合
        if business_requirement.compliance:
            for compliance in business_requirement.compliance:
                regulation = compliance.regulation.lower()
                if 'gdpr' in regulation:
                    compliance_reqs['gdpr_specific'] = {
                        'lawful_basis': '処理の法的根拠の明確化',
                        'privacy_by_design': 'プライバシー・バイ・デザイン',
                        'dpo': 'データ保護責任者の任命',
                        'dpia': 'データ保護影響評価の実施',
                    }
                elif 'sox' in regulation:
                    compliance_reqs['sox_specific'] = {
                        'internal_controls': '内部統制システムの構築',
                        'change_management': '変更管理プロセス',
                        'segregation': '職務分離の実装',
                        'documentation': '統制文書の整備',
                    }

        return compliance_reqs

    def _define_security_testing_requirements(self, functional_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """セキュリティテスト要件を定義"""
        return {
            'static_testing': {
                'sast': 'Static Application Security Testing',
                'tools': 'SonarQube, CodeQL',
                'frequency': '全コミット時',
                'coverage': 'セキュリティルール100%適用',
            },
            'dynamic_testing': {
                'dast': 'Dynamic Application Security Testing',
                'tools': 'OWASP ZAP, Burp Suite',
                'frequency': '週次自動実行',
                'scope': '全Webアプリケーション',
            },
            'penetration_testing': {
                'internal': '四半期内部ペネトレーションテスト',
                'external': '年次外部ペネトレーションテスト',
                'scope': 'ネットワーク、アプリケーション、物理',
                'methodology': 'OWASP Testing Guide, NIST SP 800-115',
            },
            'security_reviews': {
                'architecture_review': '設計段階でのセキュリティレビュー',
                'code_review': 'セキュリティ観点のコードレビュー',
                'configuration_review': 'セキュリティ設定レビュー',
                'deployment_review': 'デプロイ前セキュリティチェック',
            },
        }
