"""エラーハンドリングとリトライ機能の管理"""

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

from agents.requirement_process.schemas import RequirementProcessPhase, RequirementProcessState

logger = logging.getLogger(__name__)


class ProcessError(Exception):
    """プロセス実行エラー"""

    def __init__(self, message: str, phase: RequirementProcessPhase, retry_count: int = 0):
        super().__init__(message)
        self.phase = phase
        self.retry_count = retry_count
        self.timestamp = datetime.now().isoformat()


class ErrorHandler:
    """エラーハンドリングとリトライ機能を管理するクラス"""

    def __init__(self, max_retry_count: int = 3, base_delay: float = 1.0):
        self.max_retry_count = max_retry_count
        self.base_delay = base_delay
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute_with_retry(
        self,
        operation: Callable,
        phase: RequirementProcessPhase,
        state: RequirementProcessState,
        *args,
        **kwargs,
    ) -> Tuple[Any, RequirementProcessState]:
        """リトライ機能付きでオペレーションを実行"""
        retry_attempts = state.get('retry_attempts', {})
        retry_count = retry_attempts.get(phase.value, 0)

        for attempt in range(retry_count, self.max_retry_count + 1):
            try:
                self.logger.info(f'フェーズ {phase} を実行中 (試行 {attempt + 1}/{self.max_retry_count + 1})')

                # オペレーション実行
                result = operation(*args, **kwargs)

                # 成功時はリトライカウントをリセット
                if 'retry_attempts' not in state:
                    state['retry_attempts'] = {}
                state['retry_attempts'][phase.value] = 0
                self._log_success(phase, attempt)

                return result, state

            except Exception as e:
                retry_count = attempt + 1
                if 'retry_attempts' not in state:
                    state['retry_attempts'] = {}
                state['retry_attempts'][phase.value] = retry_count
                state['last_error_phase'] = phase

                error_message = f'フェーズ {phase} でエラーが発生: {str(e)}'
                if 'errors' not in state:
                    state['errors'] = []
                state['errors'].append(f'{datetime.now().isoformat()}: {error_message}')

                self.logger.error(f'{error_message} (試行 {retry_count})')

                if retry_count >= self.max_retry_count:
                    # 最大リトライ回数に達した場合
                    final_error = ProcessError(
                        f'フェーズ {phase} で最大リトライ回数({self.max_retry_count})に達しました: {str(e)}',
                        phase,
                        retry_count,
                    )
                    if 'errors' not in state:
                        state['errors'] = []
                    state['errors'].append(f'{datetime.now().isoformat()}: {str(final_error)}')
                    self._log_final_failure(phase, retry_count, e)
                    raise final_error from e

                # 指数バックオフで待機
                delay = self._calculate_backoff_delay(retry_count)
                self.logger.info(f'{delay:.1f}秒後にリトライします...')
                time.sleep(delay)

        # ここには到達しないはずだが、安全のため
        raise ProcessError(f'フェーズ {phase} で予期しないエラー', phase, retry_count)

    def handle_critical_error(
        self, error: Exception, phase: RequirementProcessPhase, state: RequirementProcessState
    ) -> RequirementProcessState:
        """重篤なエラーのハンドリング"""
        error_message = f'重篤なエラーが発生しました - フェーズ {phase}: {str(error)}'
        self.logger.critical(error_message)

        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f'{datetime.now().isoformat()}: CRITICAL - {error_message}')
        state['last_error_phase'] = phase

        # 安全な状態保存
        self._save_emergency_state(state)

        return state

    def check_error_threshold(self, state: RequirementProcessState) -> bool:
        """エラー閾値チェック"""
        total_errors = len(state.get('errors', []))
        total_retries = sum(state.get('retry_attempts', {}).values())

        # エラーが多すぎる場合は停止
        if total_errors > 10 or total_retries > 15:
            self.logger.warning(f'エラー閾値を超えました (エラー: {total_errors}, リトライ: {total_retries})')
            return False

        return True

    def generate_error_report(self, state: RequirementProcessState) -> str:
        """エラーレポートを生成"""
        errors = state.get('errors', [])
        retry_attempts = state.get('retry_attempts', {})

        if not errors and not retry_attempts:
            return 'エラーは発生していません。'

        report = ['エラーレポート', '=' * 40]

        if errors:
            report.append('\n【発生したエラー】')
            for error in errors[-5:]:  # 最新5件のみ
                report.append(f'- {error}')

        if retry_attempts:
            report.append('\n【リトライ状況】')
            for phase, count in retry_attempts.items():
                if count > 0:
                    report.append(f'- {phase}: {count}回リトライ')

        last_error_phase = state.get('last_error_phase')
        if last_error_phase:
            report.append(f'\n最後にエラーが発生したフェーズ: {last_error_phase}')

        return '\n'.join(report)

    def suggest_recovery_action(self, state: RequirementProcessState) -> Dict[str, str]:
        """復旧アクションの提案"""
        suggestions = {}

        last_error_phase = state.get('last_error_phase')
        if last_error_phase:
            phase = last_error_phase
            retry_attempts = state.get('retry_attempts', {})
            retry_count = retry_attempts.get(phase.value, 0)

            if retry_count >= self.max_retry_count:
                suggestions['immediate'] = f'フェーズ {phase} を手動で確認してください'
                suggestions['manual_intervention'] = 'パラメータの調整または入力データの確認が必要です'
            else:
                suggestions['retry'] = f'フェーズ {phase} の再実行を試行できます'

        errors = state.get('errors', [])
        if len(errors) > 5:
            suggestions['review'] = '多数のエラーが発生しています。システム設定を見直してください'

        return suggestions

    def reset_error_state(
        self, state: RequirementProcessState, phase: Optional[RequirementProcessPhase] = None
    ) -> RequirementProcessState:
        """エラー状態のリセット"""
        if phase:
            # 特定フェーズのエラー状態をリセット
            if 'retry_attempts' not in state:
                state['retry_attempts'] = {}
            state['retry_attempts'][phase.value] = 0
            self.logger.info(f'フェーズ {phase} のエラー状態をリセットしました')
        else:
            # 全体のエラー状態をリセット
            state['retry_attempts'] = {}
            state['errors'] = []
            state['warnings'] = []
            state['last_error_phase'] = None
            self.logger.info('全体のエラー状態をリセットしました')

        return state

    def _calculate_backoff_delay(self, retry_count: int) -> float:
        """指数バックオフ遅延の計算"""
        return self.base_delay * (2 ** (retry_count - 1))

    def _log_success(self, phase: RequirementProcessPhase, attempt: int):
        """成功ログ"""
        if attempt > 0:
            self.logger.info(f'フェーズ {phase} が {attempt + 1}回目の試行で成功しました')
        else:
            self.logger.info(f'フェーズ {phase} が正常に完了しました')

    def _log_final_failure(self, phase: RequirementProcessPhase, retry_count: int, error: Exception):
        """最終失敗ログ"""
        self.logger.error(f'フェーズ {phase} が最大リトライ回数({retry_count})に達して失敗しました: {str(error)}')

    def _save_emergency_state(self, state: RequirementProcessState):
        """緊急時の状態保存"""
        try:
            import json
            from pathlib import Path

            output_dir = Path('outputs/emergency')
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            emergency_file = output_dir / f'emergency_state_{timestamp}.json'

            # 保存可能な状態データを抽出
            save_data = {
                'timestamp': timestamp,
                'current_phase': state.get('current_phase'),
                'completed_phases': state.get('completed_phases', []),
                'errors': state.get('errors', []),
                'warnings': state.get('warnings', []),
                'retry_attempts': state.get('retry_attempts', {}),
                'last_error_phase': state.get('last_error_phase'),
            }

            with open(emergency_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f'緊急状態を保存しました: {emergency_file}')

        except Exception as e:
            self.logger.error(f'緊急状態の保存に失敗しました: {str(e)}')
