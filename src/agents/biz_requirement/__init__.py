import asyncio
import uuid
from typing import Any, Dict, Optional

from langchain.schema import AIMessage
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Command

from agents.biz_requirement.biz_requirement_agent import BizRequirementAgent, check_pointer
from agents.biz_requirement.schemas import RequirementState
from utils.logger import get_logger

logger = get_logger(__name__)

config = {'configurable': {'thread_id': uuid.uuid4()}}


async def event_loop():
    import sys

    # テスト環境でインタラクティブ実行を回避
    if not hasattr(sys.stdin, 'isatty') or not sys.stdin.isatty():
        logger.info('非インタラクティブ環境を検出、event_loopを終了します')
        return

    logger.info('Starting Biz Requirement Agent...')
    agent = BizRequirementAgent()
    graph = agent.build_graph()

    init_events = graph.astream({'messages': []}, stream_mode='values', config=config)

    async for event in init_events:
        if 'messages' in event:
            logger.info(f'Messages count: {len(event["messages"])}')
            if event['messages'] and isinstance(event['messages'][-1], AIMessage):
                print(event['messages'][-1].content)

    while True:
        user_input = input('\nあなた: ')
        if user_input.lower() in ['quit', 'exit', 'q', '終了']:
            logger.info('プログラムを終了します。')
            break
        if not user_input.strip():
            print('無効な入力です。再度入力してください。')
            continue

        stream_events = graph.astream(
            Command(resume=user_input),
            config=config,
            stream_mode='values',
        )

        async for event_value in stream_events:
            current_state = event_value

            if current_state and 'messages' in current_state and current_state['messages']:
                if isinstance(current_state['messages'][-1], AIMessage):
                    logger.info(f'Messages count: {len(current_state["messages"])}')
                    print(current_state['messages'][-1].content)


def main():
    """メイン関数"""
    import sys

    # テスト環境でインタラクティブ実行を回避
    if not hasattr(sys.stdin, 'isatty') or not sys.stdin.isatty():
        logger.info('非インタラクティブ環境を検出、mainを終了します')
        return

    logger.info('Biz Requirement Agentを起動します。')
    asyncio.run(event_loop())


def create_agent_graph(config: Optional[Dict[str, Any]] = None) -> CompiledGraph:
    """ビジネス要件定義エージェントのグラフを作成

    Args:
        config: エージェント設定
            - interactive_mode (bool): インタラクティブモード (default: True)
            - auto_save (bool): 自動保存 (default: True)
            - output_dir (str): 出力ディレクトリ (default: "outputs")

    Returns:
        CompiledGraph: コンパイル済みエージェントグラフ
    """
    if config is None:
        config = {}

    # デフォルト設定（将来の拡張用）
    _ = config.get('interactive_mode', True)
    _ = config.get('auto_save', True)
    _ = config.get('output_dir', 'outputs')

    # エージェント作成（現在は設定を使用せずデフォルトインスタンス）
    agent = BizRequirementAgent()

    return agent.build_graph()


# エクスポート用
__all__ = ['create_agent_graph', 'BizRequirementAgent', 'main', 'event_loop']


if __name__ == '__main__':
    main()
