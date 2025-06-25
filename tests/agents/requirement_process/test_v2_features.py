"""要件定義AIエージェント v2.0機能のテスト"""

from datetime import datetime
from unittest.mock import patch

import pytest

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.error_handler import ErrorHandler, ProcessError
from agents.requirement_process.orchestrator.orchestrator_agent import RequirementProcessOrchestratorAgent
from agents.requirement_process.review_manager import ReviewManager
from agents.requirement_process.schemas import (
    PhaseReview,
    RequirementProcessPhase,
    RequirementProcessState,
    ReviewDecision,
    ReviewFeedback,
    ReviewStatus,
)


class TestReviewManager:
    """ReviewManagerのテスト"""

    def setup_method(self):
        self.review_manager = ReviewManager()

    def test_create_phase_review(self):
        """フェーズレビュー作成のテスト"""
        phase = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS
        content = {'functional_requirements': []}
        summary = 'テスト用の要約'

        phase_review = self.review_manager.create_phase_review(phase, content, summary)

        assert phase_review.phase == phase
        assert phase_review.status == ReviewStatus.PENDING
        assert phase_review.content_summary == summary
        assert phase_review.feedback is None
        assert phase_review.retry_count == 0

    def test_process_user_input_approve(self):
        """ユーザー入力処理（承認）のテスト"""
        user_input = 'approve this content'
        phase = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS

        feedback = self.review_manager.process_user_input(user_input, phase)

        assert feedback.phase == phase
        assert feedback.decision == ReviewDecision.APPROVE
        assert user_input in feedback.comments

    def test_process_user_input_revise(self):
        """ユーザー入力処理（修正依頼）のテスト"""
        user_input = 'revise the requirements'
        phase = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS

        feedback = self.review_manager.process_user_input(user_input, phase)

        assert feedback.phase == phase
        assert feedback.decision == ReviewDecision.REQUEST_REVISION
        assert user_input in feedback.comments

    def test_simulate_user_feedback_auto_approve(self):
        """自動承認の模擬フィードバックテスト"""
        phase = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS

        feedback = self.review_manager.simulate_user_feedback(phase, auto_approve=True)

        assert feedback.phase == phase
        assert feedback.decision == ReviewDecision.APPROVE
        assert '自動承認モード' in feedback.comments[0]

    def test_update_phase_review(self):
        """フェーズレビュー更新のテスト"""
        phase_review = PhaseReview(
            phase=RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            status=ReviewStatus.PENDING,
            content_summary='テスト',
            last_updated=datetime.now().isoformat(),
        )

        feedback = ReviewFeedback(
            phase=RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            decision=ReviewDecision.APPROVE,
            comments=['承認します'],
            specific_feedback={},
            approved_items=['すべて'],
            revision_items=[],
            created_at=datetime.now().isoformat(),
        )

        updated_review = self.review_manager.update_phase_review(phase_review, feedback)

        assert updated_review.feedback == feedback
        assert updated_review.status == ReviewStatus.APPROVED

    def test_should_proceed_to_next_phase(self):
        """次フェーズ進行判定のテスト"""
        # 承認されたレビュー
        approved_review = PhaseReview(
            phase=RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            status=ReviewStatus.APPROVED,
            content_summary='テスト',
            last_updated=datetime.now().isoformat(),
        )

        # 修正依頼のレビュー
        revision_review = PhaseReview(
            phase=RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            status=ReviewStatus.REVISION_REQUESTED,
            content_summary='テスト',
            last_updated=datetime.now().isoformat(),
        )

        assert self.review_manager.should_proceed_to_next_phase(approved_review) is True
        assert self.review_manager.should_proceed_to_next_phase(revision_review) is False

    def test_generate_revision_instructions(self):
        """修正指示生成のテスト"""
        feedback = ReviewFeedback(
            phase=RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            decision=ReviewDecision.REQUEST_REVISION,
            comments=['優先度を見直してください'],
            specific_feedback={'ユーザーストーリー1': '受け入れ基準が不明確'},
            approved_items=['ユーザーストーリー2'],
            revision_items=['ユーザーストーリー1'],
            created_at=datetime.now().isoformat(),
        )

        instructions = self.review_manager.generate_revision_instructions(feedback)

        assert 'general_comments' in instructions
        assert '優先度を見直してください' in instructions['general_comments']
        assert 'specific_revisions' in instructions
        assert 'ユーザーストーリー1: 受け入れ基準が不明確' in instructions['specific_revisions']
        assert 'focus_areas' in instructions
        assert 'ユーザーストーリー1' in instructions['focus_areas']


class TestErrorHandler:
    """ErrorHandlerのテスト"""

    def setup_method(self):
        self.error_handler = ErrorHandler(max_retry_count=2, base_delay=0.1)

    def test_execute_with_retry_success(self):
        """リトライ機能付き実行（成功）のテスト"""
        state = RequirementProcessState()
        phase = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS

        def successful_operation():
            return 'success'

        result, updated_state = self.error_handler.execute_with_retry(successful_operation, phase, state)

        assert result == 'success'
        assert updated_state.get('retry_attempts', {}).get(phase.value, 0) == 0

    def test_execute_with_retry_failure_then_success(self):
        """リトライ機能付き実行（失敗後成功）のテスト"""
        state = RequirementProcessState()
        phase = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS
        call_count = 0

        def failing_then_succeeding_operation():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception('一回目は失敗')
            return 'success'

        # delayを短くするためのpatch
        with patch('time.sleep'):
            result, updated_state = self.error_handler.execute_with_retry(failing_then_succeeding_operation, phase, state)

        assert result == 'success'
        assert updated_state.get('retry_attempts', {}).get(phase.value, 0) == 0
        assert len(updated_state.get('errors', [])) >= 1  # 少なくとも1つのエラーが記録される

    def test_execute_with_retry_max_retries_exceeded(self):
        """最大リトライ回数超過のテスト"""
        state = RequirementProcessState()
        phase = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS

        def always_failing_operation():
            raise Exception('常に失敗')

        with patch('time.sleep'):
            with pytest.raises(ProcessError) as exc_info:
                self.error_handler.execute_with_retry(always_failing_operation, phase, state)

        assert exc_info.value.phase == phase
        assert exc_info.value.retry_count == 2

    def test_handle_critical_error(self):
        """重篤なエラーハンドリングのテスト"""
        state = RequirementProcessState()
        phase = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS
        error = Exception('重篤なエラー')

        with patch.object(self.error_handler, '_save_emergency_state'):
            updated_state = self.error_handler.handle_critical_error(error, phase, state)

        assert updated_state.get('last_error_phase') == phase
        assert len(updated_state.get('errors', [])) >= 1
        assert 'CRITICAL' in updated_state.get('errors', [])[-1]

    def test_check_error_threshold(self):
        """エラー閾値チェックのテスト"""
        state = RequirementProcessState()

        # 正常な状態
        assert self.error_handler.check_error_threshold(state) is True

        # エラーが多すぎる状態
        state['errors'] = ['error'] * 15
        assert self.error_handler.check_error_threshold(state) is False

        # リトライが多すぎる状態
        state = RequirementProcessState()
        state['retry_attempts'] = {'phase1': 10, 'phase2': 10}
        assert self.error_handler.check_error_threshold(state) is False

    def test_generate_error_report(self):
        """エラーレポート生成のテスト"""
        state = RequirementProcessState()
        state['errors'] = ['エラー1', 'エラー2']
        state['retry_attempts'] = {'functional_requirements': 2}
        state['last_error_phase'] = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS

        report = self.error_handler.generate_error_report(state)

        assert 'エラーレポート' in report
        assert 'エラー1' in report
        assert 'functional_requirements: 2回リトライ' in report
        assert str(RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS) in report

    def test_suggest_recovery_action(self):
        """復旧アクション提案のテスト"""
        state = RequirementProcessState()
        state['retry_attempts'] = {'functional_requirements': 3}
        state['last_error_phase'] = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS

        suggestions = self.error_handler.suggest_recovery_action(state)

        assert 'immediate' in suggestions
        assert 'manual_intervention' in suggestions

    def test_reset_error_state(self):
        """エラー状態リセットのテスト"""
        state = RequirementProcessState()
        state['errors'] = ['エラー1']
        state['retry_attempts'] = {'phase1': 2}
        state['last_error_phase'] = RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS

        # 全体リセット
        reset_state = self.error_handler.reset_error_state(state)

        assert len(reset_state.get('errors', [])) == 0
        assert len(reset_state.get('retry_attempts', {})) == 0
        assert reset_state.get('last_error_phase') is None

        # 特定フェーズのリセット
        state['retry_attempts'] = {'functional_requirements': 2}
        reset_state = self.error_handler.reset_error_state(state, RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS)

        assert reset_state.get('retry_attempts', {})['functional_requirements'] == 0


class TestOrchestratorV2Features:
    """オーケストレーター v2.0機能のテスト"""

    def setup_method(self):
        self.orchestrator = RequirementProcessOrchestratorAgent(interactive_mode=True, auto_approve=False)

    def test_init_with_v2_features(self):
        """v2.0機能初期化のテスト"""
        assert hasattr(self.orchestrator, 'review_manager')
        assert hasattr(self.orchestrator, 'error_handler')
        assert self.orchestrator.interactive_mode is True
        assert self.orchestrator.auto_approve is False

    def test_build_graph_interactive_mode(self):
        """対話モードでのグラフ構築テスト"""
        graph = self.orchestrator.build_graph()

        # グラフが正常にコンパイルされることを確認
        assert graph is not None

    def test_build_graph_non_interactive_mode(self):
        """非対話モードでのグラフ構築テスト"""
        orchestrator = RequirementProcessOrchestratorAgent(interactive_mode=False, auto_approve=True)
        graph = orchestrator.build_graph()

        assert graph is not None

    def test_initialize_process_v2(self):
        """v2.0初期化処理のテスト"""
        state = RequirementProcessState()

        result = self.orchestrator._initialize_process(state)

        assert result['current_phase'] == RequirementProcessPhase.SYSTEM_ANALYSIS
        assert result['is_interactive_mode'] is True
        assert result['auto_approve'] is False
        assert result['document_version'] == '1.0'
        assert len(result['version_history']) == 1
        assert 'retry_attempts' in result
        assert 'phase_reviews' in result

    def test_review_functional_requirements(self):
        """機能要件レビューのテスト"""
        state = RequirementProcessState()

        result = self.orchestrator._review_functional_requirements(state)

        assert result['current_phase'] == RequirementProcessPhase.FUNCTIONAL_REVIEW
        assert 'pending_review' in result
        assert 'review_feedback' in result
        assert 'phase_reviews' in result

    def test_decide_functional_next_step_approved(self):
        """機能要件レビュー判定（承認）のテスト"""
        state = RequirementProcessState()
        state['review_feedback'] = ReviewFeedback(
            phase=RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            decision=ReviewDecision.APPROVE,
            comments=[],
            specific_feedback={},
            approved_items=[],
            revision_items=[],
            created_at=datetime.now().isoformat(),
        )

        decision = self.orchestrator._decide_functional_next_step(state)
        assert decision == 'approved'

    def test_decide_functional_next_step_revise(self):
        """機能要件レビュー判定（修正）のテスト"""
        state = RequirementProcessState()
        state['review_feedback'] = ReviewFeedback(
            phase=RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            decision=ReviewDecision.REQUEST_REVISION,
            comments=[],
            specific_feedback={},
            approved_items=[],
            revision_items=[],
            created_at=datetime.now().isoformat(),
        )

        decision = self.orchestrator._decide_functional_next_step(state)
        assert decision == 'revise'

    def test_revise_functional_requirements(self):
        """機能要件修正処理のテスト"""
        state = RequirementProcessState()
        state['review_feedback'] = ReviewFeedback(
            phase=RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS,
            decision=ReviewDecision.REQUEST_REVISION,
            comments=['修正が必要です'],
            specific_feedback={},
            approved_items=[],
            revision_items=[],
            created_at=datetime.now().isoformat(),
        )
        state['retry_attempts'] = {}
        state['document_version'] = '1.0'
        state['version_history'] = ['1.0 - 初期版']
        state['revision_count'] = 0

        result = self.orchestrator._revise_functional_requirements(state)

        assert result['current_phase'] == RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS
        assert result['retry_attempts']['functional_requirements'] == 1
        assert result['document_version'] == '1.1'
        assert '1.1 - 機能要件修正' in result['version_history']
        assert result['revision_count'] == 1

    def test_increment_version(self):
        """バージョン増分のテスト"""
        assert self.orchestrator._increment_version('1.0') == '1.1'
        assert self.orchestrator._increment_version('1.5') == '1.6'
        assert self.orchestrator._increment_version('2.9') == '2.10'
        assert self.orchestrator._increment_version('invalid') == '1.1'


class TestIntegrationV2:
    """v2.0機能の統合テスト"""

    def test_complete_workflow_with_auto_approve(self):
        """自動承認モードでの完全ワークフローテスト"""
        orchestrator = RequirementProcessOrchestratorAgent(interactive_mode=True, auto_approve=True)

        # サンプルビジネス要件を作成
        business_requirement = ProjectBusinessRequirement(
            project_name='テストプロジェクト',
            description='テスト用のプロジェクト',
            background='テスト背景',
            goals=[],
            stake_holders=[],
            scopes=[],
            constraints=[],
            non_functional=[],
            budget=None,
            schedule=None,
        )

        initial_state = RequirementProcessState()
        initial_state['business_requirement'] = business_requirement

        # 初期化処理のテスト
        init_result = orchestrator._initialize_process(initial_state)

        assert init_result['is_interactive_mode'] is True
        assert init_result['auto_approve'] is True
        assert init_result['document_version'] == '1.0'

    def test_review_cycle_with_revision(self):
        """修正サイクルを含むレビューテスト"""
        orchestrator = RequirementProcessOrchestratorAgent(interactive_mode=True, auto_approve=False)

        state = RequirementProcessState()

        # レビュー実行
        review_result = orchestrator._review_functional_requirements(state)

        # レビュー結果を状態に適用（dictスタイルで）
        for key, value in review_result.items():
            state[key] = value

        # 修正が必要な場合の処理
        if state.get('review_feedback') and state['review_feedback'].decision == ReviewDecision.REQUEST_REVISION:
            revision_result = orchestrator._revise_functional_requirements(state)

            assert revision_result['current_phase'] == RequirementProcessPhase.FUNCTIONAL_REQUIREMENTS
            assert 'retry_attempts' in revision_result
            assert 'version_history' in revision_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
