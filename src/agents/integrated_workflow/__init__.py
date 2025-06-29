from typing import Any, Dict, Optional

from langgraph.graph.graph import CompiledGraph

from agents.integrated_workflow.integrated_workflow_agent import IntegratedWorkflowAgent


def create_workflow_graph(config: Optional[Dict[str, Any]] = None) -> CompiledGraph:
    """統合ワークフローエージェントのグラフを作成

    Args:
        config: エージェント設定
            - enable_persistence (bool): 永続化有効 (default: True)
            - enable_auto_save (bool): 自動保存有効 (default: True)
            - intermediate_save (bool): 中間保存 (default: True)

    Returns:
        CompiledGraph: コンパイル済みエージェントグラフ
    """
    if config is None:
        config = {}

    # デフォルト設定
    enable_persistence = config.get('enable_persistence', True)
    enable_auto_save = config.get('enable_auto_save', True)
    intermediate_save = config.get('intermediate_save', True)

    # エージェント作成
    agent = IntegratedWorkflowAgent(
        enable_persistence=enable_persistence, enable_auto_save=enable_auto_save, intermediate_save=intermediate_save
    )

    return agent.build_graph()


def main():
    """統合ワークフローエージェントのメイン関数（CLI用）"""
    agent = IntegratedWorkflowAgent()
    print(agent.draw_mermaid_graph())


# エクスポート用
__all__ = ['create_workflow_graph', 'IntegratedWorkflowAgent', 'main']


if __name__ == '__main__':
    main()
