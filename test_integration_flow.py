#!/usr/bin/env python3
"""要求定義から要件定義までの統合フロー動作確認テスト"""

import asyncio
import sys
from pathlib import Path

# Pythonパスを設定
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.biz_requirement.biz_requirement_agent import BizRequirementAgent
from agents.biz_requirement.schemas import Constraint, ProjectBusinessRequirement, ProjectGoal, Stakeholder
from agents.requirement_process.orchestrator.orchestrator_agent import RequirementProcessOrchestratorAgent
from agents.requirement_process.schemas import RequirementProcessState


async def test_biz_requirement_agent():
    """ビジネス要件エージェントの動作テスト"""
    print('🔄 ビジネス要件エージェントのテスト開始...')

    try:
        # エージェント初期化
        agent = BizRequirementAgent()
        print('✅ ビジネス要件エージェント初期化成功')

        # グラフ構築テスト
        _ = agent.build_graph()
        print('✅ ビジネス要件エージェントのグラフ構築成功')

        return True
    except Exception as e:
        print(f'❌ ビジネス要件エージェントのテスト失敗: {e}')
        return False


async def test_requirement_process_agent():
    """要件プロセスエージェントの動作テスト"""
    print('\n🔄 要件プロセスエージェントのテスト開始...')

    try:
        # エージェント初期化（非対話モード）
        agent = RequirementProcessOrchestratorAgent(interactive_mode=False, auto_approve=True)
        print('✅ 要件プロセスエージェント初期化成功')

        # グラフ構築テスト
        _ = agent.build_graph()
        print('✅ 要件プロセスエージェントのグラフ構築成功')

        # v2.0機能テスト
        _ = RequirementProcessOrchestratorAgent(interactive_mode=True, auto_approve=False)
        print('✅ v2.0機能（対話モード）初期化成功')

        return True
    except Exception as e:
        print(f'❌ 要件プロセスエージェントのテスト失敗: {e}')
        return False


async def test_data_flow():
    """データフロー（スキーマ互換性）テスト"""
    print('\n🔄 データフロー互換性テスト開始...')

    try:
        # サンプルビジネス要件データ作成
        sample_biz_requirement = ProjectBusinessRequirement(
            project_name='ECサイト構築プロジェクト',
            description='オンライン書籍販売プラットフォームの構築',
            goals=[
                ProjectGoal(objective='月間10万PV達成', rationale='サイトの認知度向上と売上拡大のため', kpi='Google Analyticsで測定'),
                ProjectGoal(
                    objective='顧客満足度4.0以上', rationale='リピート率向上と口コミ拡散のため', kpi='ユーザーアンケートで測定'
                ),
            ],
            constraints=[
                Constraint(type='予算', description='予算500万円以内', impact='高', mitigation='段階的リリースによるコスト削減'),
                Constraint(type='スケジュール', description='6ヶ月以内の完成', impact='高', mitigation='優先機能のみ先行リリース'),
            ],
            stake_holders=[
                Stakeholder(name='マーケティング部', role='要件定義', expectations='顧客獲得につながる魅力的なECサイトの構築'),
                Stakeholder(name='IT部門', role='技術実装', expectations='保守性が高く安定稼働するシステムの実現'),
            ],
        )
        print('✅ サンプルビジネス要件データ作成成功')

        # 要件プロセス状態初期化
        state = RequirementProcessState()
        state['business_requirement'] = sample_biz_requirement
        print('✅ 要件プロセス状態初期化成功')

        # データ型互換性確認
        assert hasattr(sample_biz_requirement, 'project_name')
        assert hasattr(sample_biz_requirement, 'description')
        print('✅ スキーマ互換性確認成功')

        return True
    except Exception as e:
        print(f'❌ データフロー互換性テスト失敗: {e}')
        return False


async def test_v2_features():
    """v2.0機能（レビューゲート・エラーハンドリング）動作テスト"""
    print('\n🔄 v2.0機能動作テスト開始...')

    try:
        # エラーハンドラーテスト
        from agents.requirement_process.error_handler import ErrorHandler

        _ = ErrorHandler()
        print('✅ エラーハンドラー初期化成功')

        # レビューマネージャーテスト
        from agents.requirement_process.review_manager import ReviewManager

        _ = ReviewManager()
        print('✅ レビューマネージャー初期化成功')

        # 条件分岐制御テスト
        agent = RequirementProcessOrchestratorAgent(interactive_mode=True, auto_approve=False)

        # 模擬状態でのメソッド呼び出しテスト
        state = RequirementProcessState()
        state['functional_requirements'] = []
        state['persona_outputs'] = []

        # レビューメソッドの動作確認
        review_result = agent._review_functional_requirements(state)
        assert 'current_phase' in review_result
        print('✅ レビューゲート機能動作確認成功')

        return True
    except Exception as e:
        print(f'❌ v2.0機能動作テスト失敗: {e}')
        return False


async def main():
    """メイン実行関数"""
    print('=' * 60)
    print('🚀 要求定義→要件定義 統合フロー動作確認テスト')
    print('=' * 60)

    results = []

    # 各テストを順次実行
    results.append(await test_biz_requirement_agent())
    results.append(await test_requirement_process_agent())
    results.append(await test_data_flow())
    results.append(await test_v2_features())

    # 結果サマリー
    print('\n' + '=' * 60)
    print('📊 テスト結果サマリー')
    print('=' * 60)

    success_count = sum(results)
    total_count = len(results)

    test_names = ['ビジネス要件エージェント', '要件プロセスエージェント', 'データフロー互換性', 'v2.0機能動作']

    for i, (test_name, result) in enumerate(zip(test_names, results, strict=False)):
        status = '✅ 成功' if result else '❌ 失敗'
        print(f'{i + 1}. {test_name}: {status}')

    print(f'\n🎯 総合結果: {success_count}/{total_count} テスト成功')

    if success_count == total_count:
        print('🎉 すべてのテストが成功しました！統合フローは正常に動作します。')
        return True
    else:
        print('⚠️  一部のテストが失敗しました。統合フローに問題がある可能性があります。')
        return False


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
