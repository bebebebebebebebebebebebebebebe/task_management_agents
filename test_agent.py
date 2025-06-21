#!/usr/bin/env python3
"""ビジネス要件エージェントの動作テスト用スクリプト"""

import asyncio
import uuid

from langchain.schema import AIMessage, HumanMessage
from langgraph.types import Command
from src.agents.biz_requirement.biz_requirement_agent import BizRequirementAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def test_agent():
    """エージェントの基本動作をテストします"""
    logger.info('エージェントテストを開始します...')

    # エージェントを初期化
    agent = BizRequirementAgent()
    graph = agent.build_graph()
    config = {'configurable': {'thread_id': uuid.uuid4()}}

    # 初期化イベントを実行
    logger.info('初期化を実行中...')
    init_events = graph.astream({'messages': []}, stream_mode='values', config=config)

    async for event in init_events:
        if 'messages' in event and event['messages']:
            latest_message = event['messages'][-1]
            if isinstance(latest_message, AIMessage):
                logger.info(f'AI応答: {latest_message.content[:100]}...')

    # テスト用のユーザー入力
    test_inputs = [
        '顧客管理システムのリニューアルプロジェクトを進めたいと思っています。',
        'ヘルプ',
        '現在のシステムが古くて使いにくいという問題があります。売上データの集計も手作業で時間がかかっています。',
        'ドキュメント作成',
    ]

    for i, user_input in enumerate(test_inputs, 1):
        logger.info(f'テスト入力 {i}: {user_input}')

        # ユーザー入力を送信
        stream_events = graph.astream(
            Command(resume=user_input),
            config=config,
            stream_mode='values',
        )

        async for event_value in stream_events:
            if event_value and 'messages' in event_value and event_value['messages']:
                latest_message = event_value['messages'][-1]
                if isinstance(latest_message, AIMessage):
                    logger.info(f'AI応答 {i}: {latest_message.content[:100]}...')

        # 短い待機時間
        await asyncio.sleep(0.5)

    logger.info('エージェントテストが完了しました。')


if __name__ == '__main__':
    asyncio.run(test_agent())
