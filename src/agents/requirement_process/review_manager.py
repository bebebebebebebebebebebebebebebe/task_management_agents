"""ユーザーレビューゲート機能の管理"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.requirement_process.schemas import (
    PhaseReview,
    RequirementProcessPhase,
    ReviewDecision,
    ReviewFeedback,
    ReviewStatus,
)

logger = logging.getLogger(__name__)


class ReviewManager:
    """ユーザーレビューゲート機能を管理するクラス"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_phase_review(
        self,
        phase: RequirementProcessPhase,
        content: Any,
        content_summary: str = None,
    ) -> PhaseReview:
        """フェーズレビューを作成"""
        if content_summary is None:
            content_summary = self._generate_content_summary(phase, content)

        return PhaseReview(
            phase=phase,
            status=ReviewStatus.PENDING,
            content_summary=content_summary,
            feedback=None,
            retry_count=0,
            last_updated=datetime.now().isoformat(),
        )

    def present_for_review(self, phase_review: PhaseReview, content: Any) -> str:
        """ユーザーレビュー用のプレゼンテーション文を生成"""
        presentation = self._format_review_presentation(phase_review, content)
        self.logger.info(f'フェーズ {phase_review.phase} のレビューを開始します')
        return presentation

    def process_user_input(self, user_input: str, phase: RequirementProcessPhase) -> ReviewFeedback:
        """ユーザー入力を解析してレビューフィードバックを生成"""
        decision = self._parse_decision(user_input)
        comments = self._extract_comments(user_input)
        specific_feedback = self._extract_specific_feedback(user_input)

        return ReviewFeedback(
            phase=phase,
            decision=decision,
            comments=comments,
            specific_feedback=specific_feedback,
            approved_items=self._extract_approved_items(user_input) if decision == ReviewDecision.APPROVE else [],
            revision_items=self._extract_revision_items(user_input) if decision == ReviewDecision.REQUEST_REVISION else [],
            created_at=datetime.now().isoformat(),
        )

    def simulate_user_feedback(self, phase: RequirementProcessPhase, auto_approve: bool = False) -> ReviewFeedback:
        """テスト・デモ用の模擬ユーザーフィードバック生成"""
        if auto_approve:
            return ReviewFeedback(
                phase=phase,
                decision=ReviewDecision.APPROVE,
                comments=['自動承認モードにより承認されました'],
                specific_feedback={},
                approved_items=['すべての項目'],
                revision_items=[],
                created_at=datetime.now().isoformat(),
            )

        # フェーズに応じた模擬フィードバック
        simulated_feedback = self._get_simulated_feedback_for_phase(phase)
        return ReviewFeedback(
            phase=phase,
            decision=simulated_feedback['decision'],
            comments=simulated_feedback['comments'],
            specific_feedback=simulated_feedback['specific_feedback'],
            approved_items=simulated_feedback.get('approved_items', []),
            revision_items=simulated_feedback.get('revision_items', []),
            created_at=datetime.now().isoformat(),
        )

    def update_phase_review(self, phase_review: PhaseReview, feedback: ReviewFeedback) -> PhaseReview:
        """フェーズレビューをフィードバックで更新"""
        phase_review.feedback = feedback
        phase_review.status = ReviewStatus.APPROVED if feedback.decision == ReviewDecision.APPROVE else ReviewStatus.REVISION_REQUESTED
        phase_review.last_updated = datetime.now().isoformat()

        self.logger.info(f'フェーズ {phase_review.phase} のレビューが更新されました: {phase_review.status}')
        return phase_review

    def should_proceed_to_next_phase(self, phase_review: PhaseReview) -> bool:
        """次のフェーズに進むべきかどうかを判定"""
        return phase_review.status == ReviewStatus.APPROVED

    def generate_revision_instructions(self, feedback: ReviewFeedback) -> Dict[str, List[str]]:
        """修正指示を生成"""
        instructions = {
            'general_comments': feedback.comments,
            'specific_revisions': [],
            'focus_areas': [],
        }

        # 具体的なフィードバックから修正指示を生成
        for item, comment in feedback.specific_feedback.items():
            instructions['specific_revisions'].append(f'{item}: {comment}')

        # 修正が必要な項目をフォーカスエリアに追加
        instructions['focus_areas'] = feedback.revision_items

        return instructions

    def _generate_content_summary(self, phase: RequirementProcessPhase, content: Any) -> str:
        """コンテンツの要約を生成"""
        phase_summaries = {
            RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS: '機能要件とユーザーストーリーが定義されました',
            RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS: '非機能要件とテスト方針が定義されました',
            RequirementProcessPhase.SOLUTION_ARCHITECTURE: 'システム構成と技術スタックが提案されました',
        }

        return phase_summaries.get(phase, f'{phase} フェーズの成果物が生成されました')

    def _format_review_presentation(self, phase_review: PhaseReview, content: Any) -> str:
        """レビュー用プレゼンテーション文をフォーマット"""
        presentation = f"""
{'=' * 60}
【ユーザーレビューゲート】
{'=' * 60}

フェーズ: {phase_review.phase}
ステータス: {phase_review.status}

{phase_review.content_summary}

{self._format_content_for_review(phase_review.phase, content)}

{'=' * 60}
この内容で承認しますか？

選択肢:
1. 承認 (approve) - 次のステップに進みます
2. 修正依頼 (revise) - 具体的な修正点をお聞かせください
3. 詳細確認 (details) - より詳しい内容を確認します

あなたの判断:
"""
        return presentation

    def _format_content_for_review(self, phase: RequirementProcessPhase, content: Any) -> str:
        """フェーズ別のコンテンツフォーマット"""
        if phase == RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS:
            return self._format_functional_requirements_for_review(content)
        elif phase == RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS:
            return self._format_non_functional_requirements_for_review(content)
        elif phase == RequirementProcessPhase.SOLUTION_ARCHITECTURE:
            return self._format_solution_architecture_for_review(content)
        else:
            return '詳細な内容は生成された文書をご確認ください。'

    def _format_functional_requirements_for_review(self, content: Any) -> str:
        """機能要件のレビュー用フォーマット"""
        if not content.get('functional_requirements'):
            return '機能要件がまだ生成されていません。'

        formatted = '【生成された機能要件】\n\n'
        for i, req in enumerate(content['functional_requirements'], 1):
            formatted += f'{i}. {req.user_story}\n'
            formatted += f'   優先度: {req.priority} | 複雑度: {req.complexity}\n'
            formatted += f'   受け入れ基準: {", ".join(req.acceptance_criteria[:2])}...\n\n'

        return formatted

    def _format_non_functional_requirements_for_review(self, content: Any) -> str:
        """非機能要件のレビュー用フォーマット"""
        if not content.get('non_functional_requirements'):
            return '非機能要件がまだ生成されていません。'

        formatted = '【生成された非機能要件】\n\n'
        by_category = {}
        for req in content['non_functional_requirements']:
            if req.category not in by_category:
                by_category[req.category] = []
            by_category[req.category].append(req)

        for category, reqs in by_category.items():
            formatted += f'■ {category}\n'
            for req in reqs[:3]:  # 最初の3つのみ表示
                formatted += f'  - {req.requirement} (目標値: {req.target_value})\n'
            formatted += '\n'

        return formatted

    def _format_solution_architecture_for_review(self, content: Any) -> str:
        """ソリューションアーキテクチャのレビュー用フォーマット"""
        if not content.get('system_architecture'):
            return 'システム構成がまだ生成されていません。'

        arch = content['system_architecture']
        formatted = f"""【提案されたシステム構成】

アーキテクチャタイプ: {arch.architecture_type}

主要コンポーネント:
{chr(10).join([f'- {comp}' for comp in arch.components[:5]])}

技術スタック:
{chr(10).join([f'- {key}: {value}' for key, value in list(arch.technology_stack.items())[:5]])}

デプロイメント戦略: {arch.deployment_strategy}
"""
        return formatted

    def _parse_decision(self, user_input: str) -> ReviewDecision:
        """ユーザー入力から判断を解析"""
        user_input_lower = user_input.lower().strip()

        if any(keyword in user_input_lower for keyword in ['approve', '承認', 'ok', 'yes', '良い']):
            return ReviewDecision.APPROVE
        elif any(keyword in user_input_lower for keyword in ['revise', '修正', 'change', '変更', 'no']):
            return ReviewDecision.REQUEST_REVISION
        else:
            # デフォルトは承認
            return ReviewDecision.APPROVE

    def _extract_comments(self, user_input: str) -> List[str]:
        """ユーザー入力からコメントを抽出"""
        # 簡単な実装: 入力全体をコメントとして扱う
        return [user_input.strip()] if user_input.strip() else []

    def _extract_specific_feedback(self, user_input: str) -> Dict[str, str]:
        """ユーザー入力から具体的なフィードバックを抽出"""
        # TODO: より高度なパースロジックを実装
        return {}

    def _extract_approved_items(self, user_input: str) -> List[str]:
        """承認された項目を抽出"""
        # 簡単な実装
        return ['すべての項目']

    def _extract_revision_items(self, user_input: str) -> List[str]:
        """修正が必要な項目を抽出"""
        # TODO: より高度なパースロジックを実装
        return ['ユーザー指定項目']

    def _get_simulated_feedback_for_phase(self, phase: RequirementProcessPhase) -> Dict[str, Any]:
        """フェーズ別の模擬フィードバック"""
        feedback_scenarios = {
            RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS: {
                'decision': ReviewDecision.APPROVE,
                'comments': ['機能要件の定義が適切です', 'ユーザーストーリーが明確で理解しやすいです'],
                'specific_feedback': {'優先度設定': '妥当です', '受け入れ基準': '具体的で測定可能です'},
                'approved_items': ['全ユーザーストーリー', '受け入れ基準'],
            },
            RequirementProcessPhase.NON_FUNCTIONAL_REQUIREMENTS: {
                'decision': ReviewDecision.APPROVE,
                'comments': ['非機能要件が包括的に定義されています', 'テスト方法が明確です'],
                'specific_feedback': {'性能要件': '妥当な目標値です', 'セキュリティ要件': '十分な考慮がされています'},
                'approved_items': ['性能要件', 'セキュリティ要件', '可用性要件'],
            },
            RequirementProcessPhase.SOLUTION_ARCHITECTURE: {
                'decision': ReviewDecision.APPROVE,
                'comments': ['技術スタックの選択が適切です', 'アーキテクチャが要件を満たしています'],
                'specific_feedback': {'技術選定': '最新で信頼性が高いです', 'デプロイメント': '実用的な戦略です'},
                'approved_items': ['システム構成', '技術スタック', 'デプロイメント戦略'],
            },
        }

        return feedback_scenarios.get(
            phase,
            {
                'decision': ReviewDecision.APPROVE,
                'comments': ['内容を確認し、承認します'],
                'specific_feedback': {},
                'approved_items': ['すべての項目'],
            },
        )
