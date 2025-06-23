"""要件定義プロセス エージェントのメインエントリーポイント"""

import asyncio
import logging
from typing import Any, Dict

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.orchestrator.orchestrator_agent import RequirementProcessOrchestratorAgent
from agents.requirement_process.schemas import RequirementProcessState


def setup_logging():
    """ログ設定"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def run_requirement_process(business_requirement: ProjectBusinessRequirement) -> Dict[str, Any]:
    """要件定義プロセスを実行"""

    # オーケストレーター・エージェントを初期化
    orchestrator = RequirementProcessOrchestratorAgent()

    # 初期状態を設定
    initial_state = RequirementProcessState(business_requirement=business_requirement, messages=[])

    # ワークフローグラフを構築・実行
    workflow = orchestrator.build_graph()

    try:
        # プロセスを実行
        result = await workflow.ainvoke(initial_state)

        logging.info('要件定義プロセスが正常に完了しました')
        return result

    except Exception as e:
        logging.error(f'要件定義プロセス実行中にエラーが発生しました: {e}')
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


async def main():
    """メイン関数"""
    setup_logging()

    # サンプルビジネス要件を作成
    business_requirement = create_sample_business_requirement()

    try:
        # 要件定義プロセスを実行
        result = await run_requirement_process(business_requirement)

        print('\n' + '=' * 50)
        print('要件定義プロセス完了')
        print('=' * 50)

        if result.get('output_file_path'):
            print(f'出力ファイル: {result["output_file_path"]}')

        if result.get('final_document'):
            print('生成されたセクション:')
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

    except Exception as e:
        print(f'エラーが発生しました: {e}')
        return 1

    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)
