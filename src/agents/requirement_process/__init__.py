from agents.requirement_process.orchestrator.orchestrator_agent import RequirementProcessOrchestratorAgent


def main():
    agent = RequirementProcessOrchestratorAgent()
    print(agent.draw_mermaid_graph())


if __name__ == '__main__':
    main()
