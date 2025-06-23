"""要件定義プロセスのためのスキーマ定義"""

from enum import Enum
from typing import Any, Dict, List, Optional

from langgraph.graph import MessagesState, add_messages
from pydantic import BaseModel, Field

from agents.biz_requirement.schemas import ProjectBusinessRequirement


class RequirementProcessPhase(str, Enum):
    """要件定義プロセスの各フェーズ"""

    INITIALIZATION = 'initialization'
    SYSTEM_ANALYSIS = 'system_analysis'
    FUNCTIONAL_REQUIREMENTS = 'functional_requirements'
    NON_FUNCTIONAL_REQUIREMENTS = 'non_functional_requirements'
    DATA_ARCHITECTURE = 'data_architecture'
    SOLUTION_ARCHITECTURE = 'solution_architecture'
    INTEGRATION = 'integration'
    COMPLETE = 'complete'


class PersonaRole(str, Enum):
    """ペルソナエージェントの役割"""

    SYSTEM_ANALYST = 'system_analyst'
    UX_DESIGNER = 'ux_designer'
    QA_ENGINEER = 'qa_engineer'
    INFRASTRUCTURE_ENGINEER = 'infrastructure_engineer'
    SECURITY_SPECIALIST = 'security_specialist'
    DATA_ARCHITECT = 'data_architect'
    SOLUTION_ARCHITECT = 'solution_architect'


class FunctionalRequirement(BaseModel):
    """機能要件"""

    user_story: str = Field(..., description='ユーザーストーリー')
    acceptance_criteria: List[str] = Field(..., description='受け入れ基準')
    priority: str = Field(..., description='優先度（高/中/低）')
    complexity: str = Field(..., description='複雑度（高/中/低）')


class NonFunctionalRequirement(BaseModel):
    """非機能要件"""

    category: str = Field(..., description='カテゴリ（性能/セキュリティ/可用性など）')
    requirement: str = Field(..., description='要件内容')
    target_value: str = Field(..., description='目標値')
    test_method: str = Field(..., description='テスト方法')


class DataModel(BaseModel):
    """データモデル"""

    entity_name: str = Field(..., description='エンティティ名')
    attributes: List[str] = Field(..., description='属性リスト')
    relationships: List[str] = Field(..., description='関連エンティティ')


class TableDefinition(BaseModel):
    """テーブル定義"""

    table_name: str = Field(..., description='テーブル名')
    columns: List[Dict[str, str]] = Field(..., description='カラム定義')
    constraints: List[str] = Field(..., description='制約')


class SystemArchitecture(BaseModel):
    """システム構成"""

    architecture_type: str = Field(..., description='アーキテクチャタイプ')
    components: List[str] = Field(..., description='コンポーネント一覧')
    technology_stack: Dict[str, str] = Field(..., description='技術スタック')
    deployment_strategy: str = Field(..., description='デプロイメント戦略')


class PersonaOutput(BaseModel):
    """ペルソナエージェントの出力"""

    persona_role: PersonaRole = Field(..., description='ペルソナの役割')
    deliverables: Dict[str, Any] = Field(..., description='成果物')
    recommendations: List[str] = Field(..., description='推奨事項')
    concerns: List[str] = Field(default_factory=list, description='懸念事項')


class RequirementProcessState(MessagesState):
    """要件定義プロセスの状態管理"""

    # 基本情報
    business_requirement: Optional[ProjectBusinessRequirement] = None
    current_phase: RequirementProcessPhase = RequirementProcessPhase.INITIALIZATION

    # 各フェーズの成果物
    functional_requirements: List[FunctionalRequirement] = Field(default_factory=list)
    non_functional_requirements: List[NonFunctionalRequirement] = Field(default_factory=list)
    data_models: List[DataModel] = Field(default_factory=list)
    table_definitions: List[TableDefinition] = Field(default_factory=list)
    system_architecture: Optional[SystemArchitecture] = None

    # ペルソナエージェントの出力
    persona_outputs: List[PersonaOutput] = Field(default_factory=list)

    # プロセス管理
    completed_phases: List[RequirementProcessPhase] = Field(default_factory=list)
    active_personas: List[PersonaRole] = Field(default_factory=list)

    # 最終成果物
    final_document: Optional[str] = None
    output_file_path: Optional[str] = None

    # エラーハンドリング
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class RequirementDocument(BaseModel):
    """要件定義書"""

    title: str = Field(..., description='文書タイトル')
    sections: Dict[str, str] = Field(..., description='各セクションの内容')
    created_at: str = Field(..., description='作成日時')
    version: str = Field(default='1.0', description='バージョン')
