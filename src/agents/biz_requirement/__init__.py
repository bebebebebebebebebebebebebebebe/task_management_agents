import asyncio
import uuid

from langchain.schema import AIMessage
from langgraph.types import Command

from agents.biz_requirement.biz_requirement_agent import BizRequirementAgent, check_pointer
from utils.logger import get_logger

logger = get_logger(__name__)

config = {'configurable': {'thread_id': uuid.uuid4()}}


async def event_loop():
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
    logger.info('Biz Requirement Agentを起動します。')
    asyncio.run(event_loop())


if __name__ == '__main__':
    main()
