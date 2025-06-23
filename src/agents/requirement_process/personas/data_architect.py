"""データアーキテクト・エージェント"""

from typing import Any, Dict, List

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.personas.base_persona import BasePersonaAgent
from agents.requirement_process.schemas import DataModel, PersonaOutput, PersonaRole, TableDefinition


class DataArchitectAgent(BasePersonaAgent):
    """データアーキテクト・エージェント

    データ中心の観点から論理データモデルとDB設計を策定する
    """

    def __init__(self):
        super().__init__(PersonaRole.DATA_ARCHITECT)

    def design_data_model(
        self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput]
    ) -> PersonaOutput:
        """データモデル設計を実行"""
        return self.execute(business_requirement, previous_outputs)

    def execute(self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput] = None) -> PersonaOutput:
        """データアーキテクチャ設計を実行"""

        # 機能要件を分析してデータ要件を抽出
        functional_requirements = self._extract_functional_requirements(previous_outputs)
        data_requirements = self._analyze_data_requirements(business_requirement, functional_requirements)

        # 論理データモデルを設計
        logical_data_models = self._design_logical_data_models(data_requirements)

        # 物理データベース設計
        database_design = self._design_physical_database(logical_data_models)

        # テーブル定義を作成
        table_definitions = self._create_table_definitions(logical_data_models)

        # データ統合・連携設計
        data_integration = self._design_data_integration(business_requirement, data_requirements)

        # データ品質・ガバナンス設計
        data_governance = self._design_data_governance(business_requirement)

        # データアーキテクチャ戦略
        data_architecture_strategy = self._define_data_architecture_strategy(data_requirements)

        deliverables = {
            'data_models': logical_data_models,
            'table_definitions': table_definitions,
            'database_design': database_design,
            'data_integration': data_integration,
            'data_governance': data_governance,
            'data_architecture_strategy': data_architecture_strategy,
        }

        recommendations = [
            'マイクロサービス対応のデータベース分散戦略の採用',
            'データレイク・データウェアハウスによる分析基盤の構築',
            'CDC（Change Data Capture）によるリアルタイムデータ連携',
            'データ品質監視とデータリネージュ管理の実装',
            'GDPR対応のためのデータ匿名化・仮名化機能の実装',
            'バックアップ・復旧戦略の定期的な見直しと改善',
        ]

        concerns = [
            'データ整合性の複雑性：分散データベース環境での一貫性確保',
            'スケーラビリティ限界：大量データ処理時の性能劣化リスク',
            'データマイグレーション：既存システムからの移行時のデータ損失リスク',
            'プライバシー規制：個人データ処理における法的制約',
            'ベンダーロックイン：特定データベース製品への依存リスク',
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

    def _analyze_data_requirements(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """データ要件を分析"""

        data_requirements = {
            'data_entities': [],
            'data_flows': [],
            'data_volumes': {},
            'data_types': [],
            'integration_requirements': [],
            'compliance_requirements': [],
        }

        # ビジネス要件からデータエンティティを抽出
        entities = self._extract_entities_from_business_requirements(business_requirement)
        data_requirements['data_entities'] = entities

        # 機能要件からデータフローを分析
        flows = self._analyze_data_flows_from_functional_requirements(functional_requirements)
        data_requirements['data_flows'] = flows

        # データボリュームを推定
        volumes = self._estimate_data_volumes(business_requirement, functional_requirements)
        data_requirements['data_volumes'] = volumes

        # データタイプを分類
        types = self._classify_data_types(entities, functional_requirements)
        data_requirements['data_types'] = types

        # 統合要件を特定
        integration = self._identify_integration_requirements(business_requirement)
        data_requirements['integration_requirements'] = integration

        # コンプライアンス要件を分析
        compliance = self._analyze_compliance_data_requirements(business_requirement)
        data_requirements['compliance_requirements'] = compliance

        return data_requirements

    def _extract_entities_from_business_requirements(self, business_requirement: ProjectBusinessRequirement) -> List[Dict[str, Any]]:
        """ビジネス要件からデータエンティティを抽出"""
        entities = []

        # 基本的なエンティティ
        base_entities = [
            {
                'name': 'User',
                'description': 'システムユーザー',
                'category': 'master',
                'attributes': ['user_id', 'username', 'email', 'role', 'created_at'],
                'relationships': ['has_many_sessions', 'belongs_to_organization'],
            },
            {
                'name': 'Session',
                'description': 'ユーザーセッション',
                'category': 'transactional',
                'attributes': ['session_id', 'user_id', 'login_time', 'logout_time', 'ip_address'],
                'relationships': ['belongs_to_user'],
            },
            {
                'name': 'AuditLog',
                'description': '監査ログ',
                'category': 'operational',
                'attributes': ['log_id', 'user_id', 'action', 'timestamp', 'details'],
                'relationships': ['belongs_to_user'],
            },
        ]

        entities.extend(base_entities)

        # ステークホルダーから組織エンティティを抽出
        if business_requirement.stake_holders:
            entities.append(
                {
                    'name': 'Organization',
                    'description': '組織・部門',
                    'category': 'master',
                    'attributes': ['org_id', 'name', 'type', 'parent_org_id', 'created_at'],
                    'relationships': ['has_many_users', 'has_many_child_organizations'],
                }
            )

        # プロジェクト情報からプロジェクトエンティティを抽出
        if business_requirement.project_name:
            entities.append(
                {
                    'name': 'Project',
                    'description': 'プロジェクト情報',
                    'category': 'master',
                    'attributes': ['project_id', 'name', 'description', 'status', 'start_date', 'end_date'],
                    'relationships': ['has_many_tasks', 'belongs_to_organization'],
                }
            )

        # 制約から設定エンティティを抽出
        if business_requirement.constraints:
            entities.append(
                {
                    'name': 'Configuration',
                    'description': 'システム設定',
                    'category': 'master',
                    'attributes': ['config_id', 'key', 'value', 'category', 'updated_at'],
                    'relationships': [],
                }
            )

        return entities

    def _analyze_data_flows_from_functional_requirements(self, functional_requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """機能要件からデータフローを分析"""
        flows = []

        for req in functional_requirements:
            req_text = str(req)

            # CRUD操作のデータフロー
            if 'データ' in req_text and '作成' in req_text:
                flows.append(
                    {
                        'flow_name': 'データ作成フロー',
                        'source': 'User Input',
                        'destination': 'Database',
                        'data_type': 'Master Data',
                        'frequency': 'On-demand',
                        'volume': 'Small',
                        'security_level': 'Medium',
                    }
                )

            if 'データ' in req_text and '更新' in req_text:
                flows.append(
                    {
                        'flow_name': 'データ更新フロー',
                        'source': 'User Input',
                        'destination': 'Database',
                        'data_type': 'Master Data',
                        'frequency': 'On-demand',
                        'volume': 'Small',
                        'security_level': 'Medium',
                    }
                )

            if 'レポート' in req_text:
                flows.append(
                    {
                        'flow_name': 'レポート生成フロー',
                        'source': 'Database',
                        'destination': 'Report Engine',
                        'data_type': 'Analytical Data',
                        'frequency': 'Batch',
                        'volume': 'Large',
                        'security_level': 'High',
                    }
                )

            if 'API' in req_text:
                flows.append(
                    {
                        'flow_name': 'API データ交換フロー',
                        'source': 'External System',
                        'destination': 'Application Database',
                        'data_type': 'Integration Data',
                        'frequency': 'Real-time',
                        'volume': 'Medium',
                        'security_level': 'High',
                    }
                )

        return flows

    def _estimate_data_volumes(
        self, business_requirement: ProjectBusinessRequirement, functional_requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """データボリュームを推定"""

        # ユーザー数からの推定
        estimated_users = len(business_requirement.stake_holders) * 10 if business_requirement.stake_holders else 100

        volumes = {
            'estimated_users': estimated_users,
            'transactions_per_day': estimated_users * 50,
            'data_growth_rate': '20% per year',
            'storage_requirements': {'initial': '10GB', 'year_1': '50GB', 'year_3': '200GB', 'year_5': '500GB'},
            'backup_requirements': {'daily_backup_size': '5GB', 'retention_period': '1 year', 'total_backup_storage': '1.8TB'},
        }

        # 機能要件からボリューム調整
        has_reporting = any('レポート' in str(req) for req in functional_requirements)
        if has_reporting:
            volumes['reporting_data'] = {
                'historical_data': '3 years',
                'aggregated_data': '100MB per month',
                'report_storage': '50MB per report',
            }

        has_api = any('API' in str(req) for req in functional_requirements)
        if has_api:
            volumes['api_traffic'] = {
                'requests_per_day': estimated_users * 100,
                'peak_requests_per_hour': estimated_users * 20,
                'data_transfer': '1GB per day',
            }

        return volumes

    def _classify_data_types(
        self, entities: List[Dict[str, Any]], functional_requirements: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """データタイプを分類"""

        data_types = [
            {
                'type': 'Master Data',
                'description': 'マスターデータ（ユーザー、組織、設定等）',
                'characteristics': '低頻度更新、高整合性要求',
                'storage_strategy': 'RDBMS',
            },
            {
                'type': 'Transactional Data',
                'description': 'トランザクションデータ（セッション、操作履歴等）',
                'characteristics': '高頻度生成、ACID特性要求',
                'storage_strategy': 'RDBMS',
            },
            {
                'type': 'Operational Data',
                'description': '運用データ（ログ、監査証跡等）',
                'characteristics': '大量生成、長期保存、検索最適化',
                'storage_strategy': 'Time-series DB or Document DB',
            },
        ]

        # 機能要件に基づく追加データタイプ
        has_reporting = any('レポート' in str(req) for req in functional_requirements)
        if has_reporting:
            data_types.append(
                {
                    'type': 'Analytical Data',
                    'description': '分析データ（集計データ、KPI等）',
                    'characteristics': '読み取り専用、大量データ処理',
                    'storage_strategy': 'Data Warehouse',
                }
            )

        has_api = any('API' in str(req) for req in functional_requirements)
        if has_api:
            data_types.append(
                {
                    'type': 'Integration Data',
                    'description': '統合データ（外部システム連携データ）',
                    'characteristics': 'スキーマ柔軟性、変換処理',
                    'storage_strategy': 'Document DB or Message Queue',
                }
            )

        return data_types

    def _identify_integration_requirements(self, business_requirement: ProjectBusinessRequirement) -> List[Dict[str, Any]]:
        """統合要件を特定"""
        integrations = []

        # 制約から外部システム統合を特定
        if business_requirement.constraints:
            for constraint in business_requirement.constraints:
                if '連携' in constraint.description or '統合' in constraint.description:
                    integrations.append(
                        {
                            'type': 'External System Integration',
                            'description': constraint.description,
                            'integration_pattern': 'API-based',
                            'data_format': 'JSON/XML',
                            'frequency': 'Real-time or Batch',
                            'security_requirements': ['Authentication', 'Authorization', 'Encryption'],
                        }
                    )

        # 基本的な統合要件
        integrations.extend(
            [
                {
                    'type': 'Authentication System',
                    'description': '認証システムとの統合',
                    'integration_pattern': 'SAML/OAuth',
                    'data_format': 'Token-based',
                    'frequency': 'Real-time',
                    'security_requirements': ['Multi-factor Authentication', 'Token Validation'],
                },
                {
                    'type': 'Monitoring System',
                    'description': '監視システムとの統合',
                    'integration_pattern': 'Metrics Export',
                    'data_format': 'Prometheus/CloudWatch',
                    'frequency': 'Continuous',
                    'security_requirements': ['Secure Metrics Endpoint'],
                },
            ]
        )

        return integrations

    def _analyze_compliance_data_requirements(self, business_requirement: ProjectBusinessRequirement) -> List[Dict[str, str]]:
        """コンプライアンスデータ要件を分析"""
        compliance_reqs = []

        # 基本的なデータ保護要件
        compliance_reqs.extend(
            [
                {
                    'requirement': 'Data Encryption',
                    'description': '個人情報・機密データの暗号化',
                    'implementation': 'AES-256 encryption at rest and in transit',
                    'validation': 'Encryption status verification',
                },
                {
                    'requirement': 'Access Logging',
                    'description': 'データアクセスの完全な監査証跡',
                    'implementation': 'Comprehensive audit logging',
                    'validation': 'Log completeness and integrity checks',
                },
                {
                    'requirement': 'Data Retention',
                    'description': 'データ保持・削除ポリシーの実装',
                    'implementation': 'Automated data lifecycle management',
                    'validation': 'Retention policy compliance monitoring',
                },
            ]
        )

        # 特定の法規制要件
        if business_requirement.compliance:
            for compliance in business_requirement.compliance:
                regulation = compliance.regulation.lower()
                if 'gdpr' in regulation:
                    compliance_reqs.extend(
                        [
                            {
                                'requirement': 'Right to be Forgotten',
                                'description': 'データ主体の削除権への対応',
                                'implementation': 'Complete data deletion capability',
                                'validation': 'Data deletion verification',
                            },
                            {
                                'requirement': 'Data Portability',
                                'description': 'データポータビリティの権利への対応',
                                'implementation': 'Structured data export functionality',
                                'validation': 'Export format and completeness verification',
                            },
                        ]
                    )

        return compliance_reqs

    def _design_logical_data_models(self, data_requirements: Dict[str, Any]) -> List[DataModel]:
        """論理データモデルを設計"""
        logical_models = []

        entities = data_requirements.get('data_entities', [])

        for entity in entities:
            data_model = DataModel(entity_name=entity['name'], attributes=entity['attributes'], relationships=entity['relationships'])
            logical_models.append(data_model)

        # ドメイン固有のモデルを追加
        domain_models = self._create_domain_specific_models(data_requirements)
        logical_models.extend(domain_models)

        return logical_models

    def _create_domain_specific_models(self, data_requirements: Dict[str, Any]) -> List[DataModel]:
        """ドメイン固有のデータモデルを作成"""
        domain_models = []

        # データフローがある場合のフローモデル
        if data_requirements.get('data_flows'):
            domain_models.append(
                DataModel(
                    entity_name='DataFlow',
                    attributes=['flow_id', 'source_system', 'target_system', 'data_type', 'frequency', 'last_execution'],
                    relationships=['has_many_flow_executions'],
                )
            )

            domain_models.append(
                DataModel(
                    entity_name='DataFlowExecution',
                    attributes=['execution_id', 'flow_id', 'start_time', 'end_time', 'status', 'records_processed', 'error_message'],
                    relationships=['belongs_to_data_flow'],
                )
            )

        # 統合要件がある場合の統合モデル
        if data_requirements.get('integration_requirements'):
            domain_models.append(
                DataModel(
                    entity_name='ExternalSystem',
                    attributes=['system_id', 'name', 'endpoint', 'auth_type', 'api_version', 'status', 'last_sync'],
                    relationships=['has_many_integration_logs'],
                )
            )

            domain_models.append(
                DataModel(
                    entity_name='IntegrationLog',
                    attributes=['log_id', 'system_id', 'operation', 'timestamp', 'request_payload', 'response_payload', 'status'],
                    relationships=['belongs_to_external_system'],
                )
            )

        return domain_models

    def _design_physical_database(self, logical_models: List[DataModel]) -> Dict[str, Any]:
        """物理データベース設計"""

        return {
            'database_strategy': self._define_database_strategy(logical_models),
            'partitioning_strategy': self._define_partitioning_strategy(logical_models),
            'indexing_strategy': self._define_indexing_strategy(logical_models),
            'replication_strategy': self._define_replication_strategy(),
            'backup_strategy': self._define_backup_strategy(),
            'performance_optimization': self._define_performance_optimization(),
        }

    def _define_database_strategy(self, logical_models: List[DataModel]) -> Dict[str, Any]:
        """データベース戦略を定義"""

        # モデル数と複雑さから戦略を決定
        model_count = len(logical_models)
        has_complex_relationships = any(len(model.relationships) > 3 for model in logical_models)

        if model_count > 10 or has_complex_relationships:
            strategy = 'Microservices Database Pattern'
            implementation = {
                'primary_db': 'PostgreSQL (RDBMS)',
                'analytical_db': 'Amazon Redshift (Data Warehouse)',
                'cache_db': 'Redis (Cache)',
                'document_db': 'DynamoDB (NoSQL)',
                'time_series_db': 'InfluxDB (Logs/Metrics)',
            }
        else:
            strategy = 'Single Database Pattern'
            implementation = {'primary_db': 'PostgreSQL (RDBMS)', 'cache_db': 'Redis (Cache)', 'backup_db': 'PostgreSQL Read Replica'}

        return {
            'strategy': strategy,
            'implementation': implementation,
            'rationale': 'スケーラビリティとデータ整合性のバランス',
            'migration_path': '段階的なマイクロサービス化',
        }

    def _define_partitioning_strategy(self, logical_models: List[DataModel]) -> Dict[str, Any]:
        """パーティショニング戦略を定義"""

        partitioning_rules = []

        for model in logical_models:
            if 'Log' in model.entity_name or 'Audit' in model.entity_name:
                partitioning_rules.append(
                    {
                        'table': model.entity_name,
                        'type': 'Range Partitioning',
                        'column': 'timestamp',
                        'interval': 'Monthly',
                        'retention': '12 months',
                        'rationale': '時系列データの効率的な管理',
                    }
                )
            elif 'User' in model.entity_name:
                partitioning_rules.append(
                    {
                        'table': model.entity_name,
                        'type': 'Hash Partitioning',
                        'column': 'user_id',
                        'partitions': 8,
                        'rationale': '負荷分散とクエリ性能向上',
                    }
                )

        return {
            'strategy': 'Hybrid Partitioning',
            'rules': partitioning_rules,
            'benefits': ['クエリ性能向上', 'メンテナンス効率化', 'ストレージ最適化'],
        }

    def _define_indexing_strategy(self, logical_models: List[DataModel]) -> Dict[str, Any]:
        """インデックス戦略を定義"""

        indexing_rules = []

        for model in logical_models:
            # 主キーインデックス（自動）
            indexing_rules.append(
                {
                    'table': model.entity_name,
                    'index_name': f'pk_{model.entity_name.lower()}',
                    'type': 'Primary Key',
                    'columns': [f'{model.entity_name.lower()}_id'],
                    'rationale': '一意性制約と高速検索',
                }
            )

            # 外部キーインデックス
            for relationship in model.relationships:
                if 'belongs_to' in relationship:
                    foreign_table = relationship.replace('belongs_to_', '')
                    indexing_rules.append(
                        {
                            'table': model.entity_name,
                            'index_name': f'idx_{model.entity_name.lower()}_{foreign_table}_id',
                            'type': 'Foreign Key Index',
                            'columns': [f'{foreign_table}_id'],
                            'rationale': 'JOIN性能向上',
                        }
                    )

            # 検索用インデックス
            if 'name' in model.attributes:
                indexing_rules.append(
                    {
                        'table': model.entity_name,
                        'index_name': f'idx_{model.entity_name.lower()}_name',
                        'type': 'B-tree Index',
                        'columns': ['name'],
                        'rationale': '名前検索の高速化',
                    }
                )

            # 時系列インデックス
            if any(attr in model.attributes for attr in ['created_at', 'timestamp', 'updated_at']):
                indexing_rules.append(
                    {
                        'table': model.entity_name,
                        'index_name': f'idx_{model.entity_name.lower()}_timestamp',
                        'type': 'B-tree Index',
                        'columns': ['created_at'],
                        'rationale': '時系列クエリの高速化',
                    }
                )

        return {
            'strategy': 'Selective Indexing',
            'rules': indexing_rules,
            'maintenance': ['月次インデックス使用率分析', '不要インデックスの削除', 'インデックス再構築の実施'],
        }

    def _define_replication_strategy(self) -> Dict[str, Any]:
        """レプリケーション戦略を定義"""
        return {
            'primary_replica': {
                'type': 'Master-Slave Replication',
                'purpose': '読み取り負荷分散',
                'lag_tolerance': '1 second',
                'failover_time': '30 seconds',
            },
            'cross_region_replica': {
                'type': 'Cross-Region Replication',
                'purpose': '災害復旧',
                'lag_tolerance': '5 minutes',
                'failover_time': '15 minutes',
            },
            'analytical_replica': {
                'type': 'ETL-based Replication',
                'purpose': '分析処理',
                'frequency': 'Hourly',
                'transformation': 'Data aggregation and cleansing',
            },
        }

    def _define_backup_strategy(self) -> Dict[str, Any]:
        """バックアップ戦略を定義"""
        return {
            'full_backup': {'frequency': 'Weekly', 'retention': '3 months', 'storage': 'Cross-region S3', 'encryption': 'AES-256'},
            'incremental_backup': {'frequency': 'Daily', 'retention': '1 month', 'storage': 'Same-region S3', 'encryption': 'AES-256'},
            'transaction_log_backup': {
                'frequency': 'Every 15 minutes',
                'retention': '7 days',
                'storage': 'Local and S3',
                'encryption': 'AES-256',
            },
            'backup_testing': {
                'frequency': 'Monthly',
                'procedure': 'Restore to test environment',
                'validation': 'Data integrity and consistency checks',
            },
        }

    def _define_performance_optimization(self) -> Dict[str, Any]:
        """性能最適化を定義"""
        return {
            'connection_pooling': {'pool_size': '20 connections', 'max_connections': '100', 'idle_timeout': '30 minutes'},
            'query_optimization': {
                'slow_query_threshold': '1 second',
                'explain_plan_analysis': 'Weekly review',
                'query_cache': 'Enabled for read queries',
            },
            'memory_optimization': {
                'buffer_pool_size': '70% of available RAM',
                'query_cache_size': '256MB',
                'sort_buffer_size': '2MB',
            },
            'storage_optimization': {
                'ssd_storage': 'For high IOPS workloads',
                'compression': 'Enabled for historical data',
                'archival': 'Move old data to cheaper storage',
            },
        }

    def _create_table_definitions(self, logical_models: List[DataModel]) -> List[TableDefinition]:
        """テーブル定義を作成"""
        table_definitions = []

        for model in logical_models:
            columns = self._create_column_definitions(model)
            constraints = self._create_constraints(model)

            table_def = TableDefinition(table_name=model.entity_name.lower(), columns=columns, constraints=constraints)
            table_definitions.append(table_def)

        return table_definitions

    def _create_column_definitions(self, model: DataModel) -> List[Dict[str, str]]:
        """カラム定義を作成"""
        columns = []

        for attr in model.attributes:
            column_def = self._map_attribute_to_column(attr, model.entity_name)
            columns.append(column_def)

        return columns

    def _map_attribute_to_column(self, attribute: str, entity_name: str) -> Dict[str, str]:
        """属性をカラム定義にマッピング"""

        # ID系カラム
        if attribute.endswith('_id'):
            return {'name': attribute, 'type': 'BIGINT', 'constraint': 'NOT NULL'}

        # 日時系カラム
        elif attribute in ['created_at', 'updated_at', 'timestamp', 'login_time', 'logout_time']:
            return {'name': attribute, 'type': 'TIMESTAMP WITH TIME ZONE', 'constraint': 'NOT NULL DEFAULT CURRENT_TIMESTAMP'}

        # 文字列系カラム
        elif attribute in ['name', 'username', 'email', 'description', 'title']:
            return {'name': attribute, 'type': 'VARCHAR(255)', 'constraint': 'NOT NULL'}

        # テキスト系カラム
        elif attribute in ['details', 'content', 'message', 'payload']:
            return {'name': attribute, 'type': 'TEXT', 'constraint': 'NULL'}

        # 数値系カラム
        elif attribute in ['count', 'amount', 'size', 'records_processed']:
            return {'name': attribute, 'type': 'INTEGER', 'constraint': 'NOT NULL DEFAULT 0'}

        # Boolean系カラム
        elif attribute in ['status', 'is_active', 'is_deleted']:
            return {'name': attribute, 'type': 'BOOLEAN', 'constraint': 'NOT NULL DEFAULT TRUE'}

        # IPアドレス
        elif attribute == 'ip_address':
            return {'name': attribute, 'type': 'INET', 'constraint': 'NULL'}

        # デフォルト
        else:
            return {'name': attribute, 'type': 'VARCHAR(255)', 'constraint': 'NULL'}

    def _create_constraints(self, model: DataModel) -> List[str]:
        """制約を作成"""
        constraints = []

        # 主キー制約
        pk_column = f'{model.entity_name.lower()}_id'
        constraints.append(f'PRIMARY KEY ({pk_column})')

        # 外部キー制約
        for relationship in model.relationships:
            if 'belongs_to' in relationship:
                foreign_table = relationship.replace('belongs_to_', '')
                foreign_key = f'{foreign_table}_id'
                constraints.append(f'FOREIGN KEY ({foreign_key}) REFERENCES {foreign_table}({foreign_table}_id)')

        # ユニーク制約
        if 'email' in model.attributes:
            constraints.append('UNIQUE (email)')

        if 'username' in model.attributes:
            constraints.append('UNIQUE (username)')

        # チェック制約
        if 'email' in model.attributes:
            constraints.append("CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')")

        return constraints

    def _design_data_integration(
        self, business_requirement: ProjectBusinessRequirement, data_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """データ統合・連携設計"""

        return {
            'integration_patterns': self._define_integration_patterns(),
            'data_pipeline': self._design_data_pipeline(data_requirements),
            'api_design': self._design_data_apis(),
            'event_streaming': self._design_event_streaming(),
            'batch_processing': self._design_batch_processing(),
        }

    def _define_integration_patterns(self) -> List[Dict[str, Any]]:
        """統合パターンを定義"""
        return [
            {
                'pattern': 'API Gateway Pattern',
                'use_case': '外部システムとのリアルタイム連携',
                'technology': 'Amazon API Gateway + Lambda',
                'benefits': ['統一インターフェース', 'セキュリティ制御', 'レート制限'],
            },
            {
                'pattern': 'Event-Driven Architecture',
                'use_case': '非同期データ処理',
                'technology': 'Amazon EventBridge + SQS',
                'benefits': ['疎結合', 'スケーラビリティ', '障害分離'],
            },
            {
                'pattern': 'ETL Pipeline',
                'use_case': 'バッチデータ処理',
                'technology': 'AWS Glue + S3 + Redshift',
                'benefits': ['大量データ処理', 'データ変換', 'スケジュール実行'],
            },
            {
                'pattern': 'Change Data Capture',
                'use_case': 'リアルタイムデータ同期',
                'technology': 'AWS DMS + Kinesis',
                'benefits': ['低遅延', '変更検知', '増分同期'],
            },
        ]

    def _design_data_pipeline(self, data_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """データパイプラインを設計"""

        return {
            'ingestion_layer': {
                'real_time': 'Amazon Kinesis Data Streams',
                'batch': 'AWS Glue + S3',
                'api': 'API Gateway + Lambda',
                'file_upload': 'S3 + Event Notifications',
            },
            'processing_layer': {
                'stream_processing': 'Kinesis Analytics',
                'batch_processing': 'AWS Glue Jobs',
                'transformation': 'Lambda Functions',
                'validation': 'Data Quality Rules',
            },
            'storage_layer': {
                'raw_data': 'S3 Data Lake',
                'processed_data': 'Redshift Data Warehouse',
                'operational_data': 'RDS PostgreSQL',
                'cache': 'ElastiCache Redis',
            },
            'orchestration': {
                'workflow_engine': 'AWS Step Functions',
                'scheduling': 'EventBridge Rules',
                'monitoring': 'CloudWatch + SNS',
                'error_handling': 'Dead Letter Queues',
            },
        }

    def _design_data_apis(self) -> Dict[str, Any]:
        """データAPIを設計"""
        return {
            'rest_apis': {
                'standard': 'RESTful design principles',
                'versioning': 'URI versioning (/v1/, /v2/)',
                'pagination': 'Cursor-based pagination',
                'filtering': 'Query parameter filtering',
            },
            'graphql_api': {
                'use_case': '複雑なデータ取得',
                'schema': 'Type-safe schema definition',
                'resolver': 'Efficient data fetching',
                'caching': 'Query result caching',
            },
            'streaming_api': {
                'protocol': 'WebSocket + Server-Sent Events',
                'use_case': 'Real-time data updates',
                'authentication': 'JWT token validation',
                'rate_limiting': 'Connection-based limits',
            },
            'bulk_api': {
                'format': 'JSON/CSV bulk operations',
                'async_processing': 'Background job processing',
                'status_tracking': 'Job status API',
                'error_reporting': 'Detailed error responses',
            },
        }

    def _design_event_streaming(self) -> Dict[str, Any]:
        """イベントストリーミングを設計"""
        return {
            'event_schema': {
                'format': 'JSON with Avro schema',
                'versioning': 'Schema evolution support',
                'validation': 'Schema registry',
                'metadata': 'Event metadata tracking',
            },
            'event_routing': {
                'topics': 'Domain-based topic organization',
                'partitioning': 'Event key-based partitioning',
                'retention': '7 days for operational events',
                'replication': 'Cross-AZ replication',
            },
            'event_processing': {
                'consumers': 'Parallel event processing',
                'error_handling': 'Retry with exponential backoff',
                'dead_letter': 'Failed event storage',
                'monitoring': 'Consumer lag monitoring',
            },
        }

    def _design_batch_processing(self) -> Dict[str, Any]:
        """バッチ処理を設計"""
        return {
            'scheduling': {
                'cron_jobs': 'Time-based scheduling',
                'event_driven': 'File arrival triggers',
                'dependencies': 'Job dependency management',
                'retry_logic': 'Automatic retry on failure',
            },
            'data_processing': {
                'etl_jobs': 'Extract, Transform, Load',
                'data_quality': 'Validation and cleansing',
                'aggregation': 'Summary and reporting data',
                'archival': 'Historical data management',
            },
            'monitoring': {
                'job_status': 'Success/failure tracking',
                'performance': 'Execution time monitoring',
                'resource_usage': 'CPU/memory utilization',
                'alerting': 'Failure notifications',
            },
        }

    def _design_data_governance(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """データガバナンスを設計"""
        return {
            'data_catalog': self._design_data_catalog(),
            'data_lineage': self._design_data_lineage(),
            'data_quality': self._design_data_quality_framework(),
            'data_privacy': self._design_data_privacy_controls(business_requirement),
            'data_lifecycle': self._design_data_lifecycle_management(),
        }

    def _design_data_catalog(self) -> Dict[str, Any]:
        """データカタログを設計"""
        return {
            'metadata_management': {
                'technical_metadata': 'Schema, types, constraints',
                'business_metadata': 'Descriptions, ownership, usage',
                'operational_metadata': 'Access patterns, performance',
                'lineage_metadata': 'Data flow and transformations',
            },
            'search_discovery': {
                'full_text_search': 'Content and metadata search',
                'faceted_search': 'Category-based filtering',
                'recommendations': 'Related dataset suggestions',
                'usage_analytics': 'Popular datasets tracking',
            },
            'governance_features': {
                'data_classification': 'Sensitivity level tagging',
                'access_controls': 'Permission-based access',
                'approval_workflows': 'Data access approval',
                'compliance_tracking': 'Regulatory compliance status',
            },
        }

    def _design_data_lineage(self) -> Dict[str, Any]:
        """データリネージュを設計"""
        return {
            'lineage_tracking': {
                'column_level': 'Field-level transformation tracking',
                'table_level': 'Dataset relationship mapping',
                'process_level': 'ETL job dependency tracking',
                'system_level': 'Cross-system data flow',
            },
            'impact_analysis': {
                'downstream_impact': 'Change impact assessment',
                'root_cause_analysis': 'Data quality issue tracing',
                'dependency_mapping': 'Critical path identification',
                'change_management': 'Schema change coordination',
            },
            'visualization': {
                'graph_representation': 'Interactive lineage graphs',
                'timeline_view': 'Historical lineage changes',
                'impact_heatmap': 'Critical dependency highlighting',
                'export_capabilities': 'Documentation generation',
            },
        }

    def _design_data_quality_framework(self) -> Dict[str, Any]:
        """データ品質フレームワークを設計"""
        return {
            'quality_dimensions': {
                'completeness': 'Missing value detection',
                'accuracy': 'Data correctness validation',
                'consistency': 'Cross-system consistency checks',
                'timeliness': 'Data freshness monitoring',
                'validity': 'Format and constraint validation',
                'uniqueness': 'Duplicate detection',
            },
            'quality_rules': {
                'business_rules': 'Domain-specific validation',
                'technical_rules': 'Format and type checking',
                'reference_data': 'Master data validation',
                'cross_reference': 'Inter-table consistency',
            },
            'monitoring_alerting': {
                'continuous_monitoring': 'Real-time quality checks',
                'threshold_alerting': 'Quality metric alerts',
                'trend_analysis': 'Quality degradation detection',
                'reporting': 'Quality scorecards and reports',
            },
        }

    def _design_data_privacy_controls(self, business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
        """データプライバシー制御を設計"""

        privacy_controls = {
            'data_classification': {
                'pii_detection': 'Personal information identification',
                'sensitivity_tagging': 'Data sensitivity classification',
                'inventory_management': 'PII inventory tracking',
                'risk_assessment': 'Privacy risk evaluation',
            },
            'access_controls': {
                'role_based_access': 'RBAC for sensitive data',
                'attribute_based_access': 'ABAC for fine-grained control',
                'dynamic_masking': 'Real-time data masking',
                'field_level_security': 'Column-level permissions',
            },
            'data_protection': {
                'encryption': 'At-rest and in-transit encryption',
                'tokenization': 'PII tokenization',
                'anonymization': 'Data anonymization techniques',
                'pseudonymization': 'Reversible data de-identification',
            },
        }

        # GDPR要件がある場合
        if business_requirement.compliance:
            for compliance in business_requirement.compliance:
                if 'gdpr' in compliance.regulation.lower():
                    privacy_controls['gdpr_compliance'] = {
                        'consent_management': 'User consent tracking',
                        'right_to_access': 'Data subject access requests',
                        'right_to_rectification': 'Data correction capabilities',
                        'right_to_erasure': 'Data deletion (right to be forgotten)',
                        'data_portability': 'Structured data export',
                    }

        return privacy_controls

    def _design_data_lifecycle_management(self) -> Dict[str, Any]:
        """データライフサイクル管理を設計"""
        return {
            'lifecycle_stages': {
                'creation': 'Data ingestion and initial storage',
                'active_use': 'Operational data processing',
                'archival': 'Long-term storage transition',
                'disposal': 'Secure data deletion',
            },
            'retention_policies': {
                'operational_data': '3 years active retention',
                'analytical_data': '7 years with archival',
                'audit_logs': '10 years for compliance',
                'backup_data': '1 year with graduated deletion',
            },
            'automation': {
                'lifecycle_automation': 'Automated stage transitions',
                'policy_enforcement': 'Retention policy automation',
                'cost_optimization': 'Storage tier optimization',
                'compliance_monitoring': 'Retention compliance tracking',
            },
        }

    def _define_data_architecture_strategy(self, data_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """データアーキテクチャ戦略を定義"""
        return {
            'architecture_principles': [
                'データの単一ソース（Single Source of Truth）',
                'スキーマファースト設計',
                'イベント駆動アーキテクチャ',
                'マイクロサービス対応のデータ分散',
                'クラウドネイティブ設計',
            ],
            'technology_choices': {
                'primary_database': 'PostgreSQL (ACID compliance)',
                'cache_layer': 'Redis (In-memory cache)',
                'search_engine': 'Elasticsearch (Full-text search)',
                'message_queue': 'Amazon SQS (Async processing)',
                'data_warehouse': 'Amazon Redshift (Analytics)',
                'object_storage': 'Amazon S3 (File storage)',
            },
            'scalability_strategy': {
                'horizontal_scaling': 'Read replicas and sharding',
                'vertical_scaling': 'Instance size optimization',
                'caching_strategy': 'Multi-level caching',
                'cdn_strategy': 'Static content distribution',
            },
            'evolution_roadmap': {
                'phase_1': 'Monolithic database with read replicas',
                'phase_2': 'Microservices with database per service',
                'phase_3': 'Event-driven architecture with CQRS',
                'phase_4': 'Data mesh with domain-oriented data ownership',
            },
        }
