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
    FUNCTIONAL_REVIEW = 'functional_review'
    NON_FUNCTIONAL_REQUIREMENTS = 'non_functional_requirements'
    NON_FUNCTIONAL_REVIEW = 'non_functional_review'
    DATA_ARCHITECTURE = 'data_architecture'
    SOLUTION_ARCHITECTURE = 'solution_architecture'
    SOLUTION_REVIEW = 'solution_review'
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


class ReviewStatus(str, Enum):
    """レビューステータス"""

    PENDING = 'pending'
    APPROVED = 'approved'
    REVISION_REQUESTED = 'revision_requested'
    IN_REVISION = 'in_revision'


class ReviewDecision(str, Enum):
    """レビュー結果の判断"""

    APPROVE = 'approve'
    REQUEST_REVISION = 'request_revision'
    REJECT = 'reject'


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


class ReviewFeedback(BaseModel):
    """ユーザーレビューフィードバック"""

    phase: RequirementProcessPhase = Field(..., description='レビュー対象フェーズ')
    decision: ReviewDecision = Field(..., description='レビュー判断')
    comments: List[str] = Field(default_factory=list, description='コメント・修正依頼')
    specific_feedback: Dict[str, str] = Field(default_factory=dict, description='具体的なフィードバック')
    approved_items: List[str] = Field(default_factory=list, description='承認された項目')
    revision_items: List[str] = Field(default_factory=list, description='修正が必要な項目')
    created_at: str = Field(..., description='フィードバック作成日時')


class PhaseReview(BaseModel):
    """フェーズレビュー情報"""

    phase: RequirementProcessPhase = Field(..., description='レビュー対象フェーズ')
    status: ReviewStatus = Field(default=ReviewStatus.PENDING, description='レビューステータス')
    content_summary: str = Field(..., description='レビュー対象内容の要約')
    feedback: Optional[ReviewFeedback] = Field(default=None, description='ユーザーフィードバック')
    retry_count: int = Field(default=0, description='リトライ回数')
    last_updated: str = Field(..., description='最終更新日時')


class PersonaOutput(BaseModel):
    """ペルソナエージェントの出力"""

    persona_role: PersonaRole = Field(..., description='ペルソナの役割')
    deliverables: Dict[str, Any] = Field(..., description='成果物')
    recommendations: List[str] = Field(..., description='推奨事項')
    concerns: List[str] = Field(default_factory=list, description='懸念事項')
    execution_metadata: Dict[str, Any] = Field(default_factory=dict, description='実行メタデータ')


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

    # レビュー管理 (v2.0新機能)
    phase_reviews: List[PhaseReview] = Field(default_factory=list, description='各フェーズのレビュー情報')
    pending_review: Optional[PhaseReview] = Field(default=None, description='現在レビュー待ちのフェーズ')
    review_feedback: Optional[ReviewFeedback] = Field(default=None, description='最新のユーザーフィードバック')

    # エラーハンドリングとリトライ (v2.0拡張)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    retry_attempts: Dict[str, int] = Field(default_factory=dict, description='各フェーズのリトライ回数')
    max_retry_count: int = Field(default=3, description='最大リトライ回数')
    last_error_phase: Optional[RequirementProcessPhase] = Field(default=None, description='最後にエラーが発生したフェーズ')

    # バージョン管理 (v2.0新機能)
    document_version: str = Field(default='1.0', description='文書バージョン')
    version_history: List[str] = Field(default_factory=list, description='バージョン履歴')
    revision_count: int = Field(default=0, description='改訂回数')

    # 最終成果物
    final_document: Optional[str] = None
    output_file_path: Optional[str] = None

    # プロセス制御フラグ
    is_interactive_mode: bool = Field(default=True, description='対話モードの有効/無効')
    auto_approve: bool = Field(default=False, description='自動承認モード')


class RequirementDocument(BaseModel):
    """要件定義書"""

    title: str = Field(..., description='文書タイトル')
    sections: Dict[str, str] = Field(..., description='各セクションの内容')
    created_at: str = Field(..., description='作成日時')
    version: str = Field(default='1.0', description='バージョン')
