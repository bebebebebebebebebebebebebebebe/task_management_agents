import asyncio

from agents.biz_requirement.biz_requirement_agent import BizRequirementAgent


def main():
    print('Starting Biz Requirement Agent...')
    agent = BizRequirementAgent()
    print('Agent initialized:', agent.draw_mermaid_graph())


if __name__ == '__main__':
    main()
