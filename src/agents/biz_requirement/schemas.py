from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from langgraph.graph import MessagesState, add_messages
from pydantic import BaseModel, Field


class Stakeholder(BaseModel):
    """ステークホルダーの情報を保持するモデル"""

    name: str = Field(..., description='利害関係者の氏名または組織名')
    role: str = Field(..., description='ステークホルダーの役割や立場')
    expectations: str = Field(..., description='ステークホルダーが本プロジェクトに求める成果や価値')


class ProjectGoal(BaseModel):
    """プロジェクトの目的や目標を定義するモデル"""

    objective: str = Field(
        ...,
        description='達成したいプロジェクトの目的や目標（例：「○○の開発によって顧客の満足度を向上させる」）',
    )
    rationale: str = Field(..., description='プロジェクトの目的や目標を達成するための根拠や理由')
    kpi: Optional[str] = Field(
        None,
        description='進捗を測る指標（KPI）や計測方法（例：「顧客満足度調査を実施し、80%以上の満足度を目指す」）',
    )


class ScopeItem(BaseModel):
    """プロジェクトの範囲を定義するモデル"""

    in_scope: str = Field(..., description='プロジェクトの範囲内に含まれるもの（例：「○○の開発」）')
    out_of_scope: str = Field(..., description='プロジェクトに『含めない』機能・範囲（除外対象）')


class NonFunctionalRequirement(BaseModel):
    category: str = Field(..., description='非機能要件カテゴリ（性能, セキュリティ, 可用性, 運用性 など）')
    requirement: str = Field(..., description='カテゴリに対する具体的な要求内容')


class Constraint(BaseModel):
    description: str = Field(..., description='制約事項（例：既存システム連携必須、法規制、予算上限など）')


class Risk(BaseModel):
    situation: str = Field(..., description='想定されるリスク事象')
    probability: str = Field(..., description='発生確率（高／中／低 など）')
    impact: str = Field(..., description='影響度（高／中／低 など）')
    mitigation: Optional[str] = Field(..., description='回避策または軽減策')


class Compliance(BaseModel):
    regulation: str = Field(..., description='適用が必要な法規制・ガイドライン名')
    detail: str = Field(..., description='遵守すべきポイントや条項')


class Budget(BaseModel):
    amount: float = Field(..., description='想定予算の金額')
    currency: str = Field(..., description='通貨単位（例: JPY, USD）')


class Schedule(BaseModel):
    start_date: str = Field(..., description='計画の開始日（YYYY-MM-DD）')
    target_release: str = Field(..., description='目標リリース日（YYYY-MM-DD）')
    milestones: Optional[List[str]] = Field(None, description='主要マイルストーン一覧（任意）')


class ProjectBusinessRequirement(BaseModel):
    """製品やサービスのビジネス要件を定義するモデル（すべてオプショナル）"""

    project_name: Optional[str] = Field(None, description='プロジェクトまたはプロダクトの正式名称')
    description: Optional[str] = Field(None, description='プロジェクトの概要や目的')
    background: Optional[str] = Field(None, description='プロジェクト開始の背景や現状の課題')
    goals: Optional[List[ProjectGoal]] = Field(None, description='プロジェクト目標の一覧')
    stake_holders: Optional[List[Stakeholder]] = Field(None, description='プロジェクトに関わる利害関係者の一覧')
    scopes: Optional[List[ScopeItem]] = Field(None, description='プロジェクトの範囲（スコープ）の定義')
    constraints: Optional[List[Constraint]] = Field(None, description='予算・技術・法規制などの制約事項')
    non_functional: Optional[List[NonFunctionalRequirement]] = Field(None, description='性能・セキュリティ等の非機能要件')
    budget: Optional[Budget] = Field(None, description='プロジェクト予算情報')
    schedule: Optional[Schedule] = Field(None, description='主要日程・マイルストーン')
    assumptions: Optional[List[str]] = Field(None, description='前提条件や依存関係の一覧')
    risks: Optional[List[Risk]] = Field(None, description='リスクと対応策の一覧')
    compliance: Optional[List[Compliance]] = Field(None, description='法規制やガイドラインの遵守事項')
    success_criteria: Optional[List[str]] = Field(None, description='成功とみなす受け入れ基準やKPIの一覧')


class RequirementDocument(BaseModel):
    markdown_text: str = Field(description='マークダウン形式で記述された要求定義書の文書内容')


class OutlineItem(BaseModel):
    """ドキュメントのアウトラインにおける一つの章または主要なセクション"""

    section_title: str = Field(..., description='章のタイトル')
    headings: List[str] = Field(default_factory=list, description='その章に含まれる主要な見出しのリスト')
    section_summary: Optional[str] = Field(None, description='このセクションでカバーすべき内容の簡潔な要約')


class DynamicOutline(BaseModel):
    """AIによって動的に生成されたドキュメントアウトライン"""

    suggested_outline: List[OutlineItem] = Field(..., description='提案されたアウトライン構造')
    thought_process: str = Field(..., description='そのアウトラインを提案した思考プロセスや理由')


class DetailedSectionContent(BaseModel):
    """アウトラインの各項目に対して詳細化されたマークダウンコンテンツ"""

    section_title: str  # どの章に対するものか
    heading: Optional[str] = None  # どの見出しに対するものか (章全体の場合もある)
    markdown_content: str = Field(..., description='生成されたマークダウン形式の本文')
    thought_process: str = Field(..., description='その内容を記述した思考プロセスや理由')


class DetailedSectionContents(BaseModel):
    """アウトラインの各項目に対して詳細化されたマークダウンコンテンツのリスト"""

    detailed_sections: List[DetailedSectionContent]


class RequirementsPhase(str, Enum):
    INTRODUCTION = 'introduction'
    INTERVIEW = 'interview'
    OUTLINE_GENERATION = 'outline_generation'
    DETAIL_GENERATION = 'detail_generation'
    DOCUMENT_INTEGRATION = 'document_integration'


class RequirementState(MessagesState):
    interview_archives: Annotated[Optional[List[Dict[str, Any]]], add_messages] = None
    requirement: Optional[ProjectBusinessRequirement] = None
    interview_complete: Optional[bool] = None
    current_phase: RequirementsPhase = RequirementsPhase.INTRODUCTION
    document: Optional[RequirementDocument] = None
    dynamic_outline: Optional[DynamicOutline] = None
    detailed_sections: Optional[List[DetailedSectionContent]] = Field(default_factory=list)
    asked_for_optional: Optional[bool] = False  # オプション項目を尋ねたかどうか
    technical_level: Optional[str] = None  # ユーザーの専門知識レベル
    skipped_questions: List[str] = Field(default_factory=list)  # スキップした質問
    user_wants_help: Optional[bool] = False  # ヘルプを要求しているかどうか
