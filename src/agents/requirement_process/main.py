"""要件定義プロセス エージェント v2.0 のメインエントリーポイント"""

import argparse
import asyncio
import logging
from typing import Any, Dict

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.orchestrator.orchestrator_agent import RequirementProcessOrchestratorAgent
from agents.requirement_process.schemas import RequirementProcessState


def setup_logging():
    """ログ設定"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def run_requirement_process(
    business_requirement: ProjectBusinessRequirement, interactive_mode: bool = True, auto_approve: bool = False
) -> Dict[str, Any]:
    """要件定義プロセス v2.0 を実行

    Args:
        business_requirement: ビジネス要件
        interactive_mode: 対話モード（ユーザーレビューゲート有効）
        auto_approve: 自動承認モード
    """

    # オーケストレーター・エージェント v2.0 を初期化
    orchestrator = RequirementProcessOrchestratorAgent(interactive_mode=interactive_mode, auto_approve=auto_approve)

    # 初期状態を設定（v2.0拡張フィールド含む）
    initial_state = RequirementProcessState(
        business_requirement=business_requirement,
        messages=[],
        persona_outputs=[],
        completed_phases=[],
        active_personas=[],
        functional_requirements=[],
        non_functional_requirements=[],
        data_models=[],
        table_definitions=[],
        errors=[],
        warnings=[],
        # v2.0新機能
        phase_reviews=[],
        pending_review=None,
        review_feedback=None,
        retry_attempts={},
        max_retry_count=3,
        last_error_phase=None,
        document_version='1.0',
        version_history=[],
        revision_count=0,
        is_interactive_mode=interactive_mode,
        auto_approve=auto_approve,
    )

    # ワークフローグラフを構築・実行
    workflow = orchestrator.build_graph()

    try:
        # プロセスを実行
        logging.info(f'要件定義プロセス v2.0 を開始 (対話モード: {interactive_mode}, 自動承認: {auto_approve})')
        result = await workflow.ainvoke(initial_state)

        logging.info('要件定義プロセス v2.0 が正常に完了しました')
        return result

    except Exception as e:
        logging.error(f'要件定義プロセス実行中にエラーが発生しました: {e}')

        # エラーレポートを生成
        if hasattr(orchestrator, 'error_handler'):
            error_report = orchestrator.error_handler.generate_error_report(initial_state)
            logging.error(f'エラーレポート:\n{error_report}')

        raise


def create_sample_business_requirement() -> ProjectBusinessRequirement:
    """サンプル用のビジネス要件を作成"""
    from agents.biz_requirement.schemas import (
        Budget,
        Constraint,
        NonFunctionalRequirement,
        ProjectGoal,
        Schedule,
        ScopeItem,
        Stakeholder,
    )

    return ProjectBusinessRequirement(
        project_name='タスク管理システム',
        description='チーム向けのタスク管理・プロジェクト管理システムの開発',
        background='現在のタスク管理が非効率で、チーム間の連携に課題がある',
        goals=[
            ProjectGoal(
                objective='チームの生産性向上とタスクの可視化',
                rationale='タスクの進捗が見えにくく、デッドラインの管理が困難',
                kpi='タスク完了率20%向上、チーム間連携効率30%向上',
            )
        ],
        stake_holders=[
            Stakeholder(
                name='プロジェクトマネージャー',
                role='プロジェクト管理責任者',
                expectations='プロジェクト全体の進捗を効率的に管理したい',
            ),
            Stakeholder(name='開発チーム', role='システム開発担当', expectations='タスクの優先度と進捗を明確に把握したい'),
            Stakeholder(name='QAチーム', role='品質保証担当', expectations='テスト項目の管理と品質状況を可視化したい'),
        ],
        scopes=[
            ScopeItem(
                in_scope='Webベースのタスク管理機能、ユーザー管理、レポート機能',
                out_of_scope='モバイルアプリケーション、外部システム連携',
            )
        ],
        constraints=[Constraint(description='6ヶ月以内でのリリース必須'), Constraint(description='既存の認証システムとの連携が必要')],
        non_functional=[
            NonFunctionalRequirement(category='性能', requirement='レスポンス時間3秒以内'),
            NonFunctionalRequirement(category='セキュリティ', requirement='個人情報保護法準拠'),
        ],
        budget=Budget(amount=5000000, currency='JPY'),
        schedule=Schedule(start_date='2024-01-01', target_release='2024-06-30'),
    )


def parse_arguments():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(
        description='要件定義AIエージェント v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py                     # デフォルト（対話モード）
  python main.py --auto-approve      # 自動承認モード
  python main.py --non-interactive   # 非対話モード（v1.0互換）
  python main.py --demo              # デモモード（高速実行）
        """,
    )

    parser.add_argument('--interactive', action='store_true', default=True, help='対話モードを有効にする（デフォルト）')
    parser.add_argument('--non-interactive', action='store_true', help='非対話モード（v1.0互換）')
    parser.add_argument('--auto-approve', action='store_true', help='自動承認モード（レビューを自動で承認）')
    parser.add_argument('--demo', action='store_true', help='デモモード（対話+自動承認）')

    return parser.parse_args()


async def main():
    """メイン関数 v2.0"""
    setup_logging()

    # コマンドライン引数を解析
    args = parse_arguments()

    # 実行モードを決定
    if args.non_interactive:
        interactive_mode = False
        auto_approve = False
        mode_name = '非対話モード（v1.0互換）'
    elif args.demo:
        interactive_mode = True
        auto_approve = True
        mode_name = 'デモモード'
    else:
        interactive_mode = not args.non_interactive
        auto_approve = args.auto_approve
        mode_name = f'対話モード（自動承認: {auto_approve}）'

    print('\n' + '=' * 60)
    print('要件定義AIエージェント v2.0')
    print('=' * 60)
    print(f'実行モード: {mode_name}')
    print('=' * 60)

    # サンプルビジネス要件を作成
    business_requirement = create_sample_business_requirement()

    try:
        # 要件定義プロセス v2.0 を実行
        result = await run_requirement_process(business_requirement, interactive_mode=interactive_mode, auto_approve=auto_approve)

        print('\n' + '=' * 50)
        print('要件定義プロセス v2.0 完了')
        print('=' * 50)

        # v2.0新機能の結果を表示
        if result.get('document_version'):
            print(f'文書バージョン: {result["document_version"]}')

        if result.get('revision_count', 0) > 0:
            print(f'改訂回数: {result["revision_count"]}回')

        if result.get('phase_reviews'):
            print(f'実行されたレビュー: {len(result["phase_reviews"])}件')
            for review in result['phase_reviews']:
                status_str = '承認' if review.status == 'approved' else '修正依頼'
                print(f'  - {review.phase}: {status_str}')

        if result.get('output_file_path'):
            print(f'出力ファイル: {result["output_file_path"]}')

        if result.get('final_document'):
            print('\n生成されたセクション:')
            for section, _ in result['final_document'].items():
                print(f'- {section}')

        print('\n統合された要件:')
        if result.get('functional_requirements'):
            print(f'- 機能要件: {len(result["functional_requirements"])}件')
        if result.get('non_functional_requirements'):
            print(f'- 非機能要件: {len(result["non_functional_requirements"])}件')
        if result.get('data_models'):
            print(f'- データモデル: {len(result["data_models"])}件')
        if result.get('system_architecture'):
            print('- システムアーキテクチャ: 設計完了')

        # エラー統計
        if result.get('errors') or result.get('retry_attempts'):
            print('\n品質統計:')
            if result.get('errors'):
                print(f'- 発生したエラー: {len(result["errors"])}件')
            if result.get('retry_attempts'):
                total_retries = sum(result['retry_attempts'].values())
                if total_retries > 0:
                    print(f'- 総リトライ回数: {total_retries}回')

        print('\n✅ 要件定義プロセス v2.0 が正常に完了しました')

    except Exception as e:
        print(f'\n❌ エラーが発生しました: {e}')
        return 1

    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
