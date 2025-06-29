from typing import Any, Dict, Optional

from langgraph.graph.graph import CompiledGraph

from agents.requirement_process.orchestrator.orchestrator_agent import RequirementProcessOrchestratorAgent
from agents.requirement_process.schemas import RequirementProcessState


def create_orchestrator_graph(config: Optional[Dict[str, Any]] = None) -> CompiledGraph:
    """要件プロセスオーケストレーターエージェントのグラフを作成

    Args:
        config: エージェント設定
            - interactive_mode (bool): インタラクティブモード (default: True)
            - auto_approve (bool): 自動承認 (default: False)
            - max_retry_attempts (int): 最大リトライ回数 (default: 3)

    Returns:
        CompiledGraph: コンパイル済みエージェントグラフ
    """
    if config is None:
        config = {}

    # デフォルト設定
    interactive_mode = config.get('interactive_mode', True)
    auto_approve = config.get('auto_approve', False)
    _ = config.get('max_retry_attempts', 3)  # 将来の拡張用

    # エージェント作成
    agent = RequirementProcessOrchestratorAgent(interactive_mode=interactive_mode, auto_approve=auto_approve)

    return agent.build_graph()


def main():
    """メイン関数（従来のCLI用）"""
    agent = RequirementProcessOrchestratorAgent()
    print(agent.draw_mermaid_graph())


# エクスポート用
__all__ = ['create_orchestrator_graph', 'RequirementProcessOrchestratorAgent', 'main']


if __name__ == '__main__':
    main()
