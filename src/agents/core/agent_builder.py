"""AIエージェントのワークフローグラフを構築するための抽象基底クラス。

このモジュールは、LangGraphを使用してAIエージェントのワークフローを定義し、
状態管理とグラフ構築の基盤を提供します。
"""

import abc

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel


class AgentGraphBuilder(abc.ABC):
    """AIエージェントのワークフローグラフを構築するための抽象基底クラス。

    LangGraphのStateGraphを使用して、エージェントの状態遷移ワークフローを
    定義するためのテンプレートを提供します。具象クラスは`build_graph`メソッドを
    実装してエージェント固有のワークフローを定義する必要があります。

    Attributes:
        workflow (StateGraph): エージェントのワークフローを定義するStateGraphインスタンス
    """

    def __init__(
        self,
        state_object: type[dict[str, any]] | type[BaseModel],
    ):
        """AgentGraphBuilderを初期化します。

        Args:
            state_object: エージェントの状態を定義する型。辞書型またはPydanticモデル。
        """
        self.workflow = StateGraph(state_schema=state_object)

    @abc.abstractmethod
    def build_graph(self) -> CompiledGraph:
        """エージェントのワークフローグラフを構築します。

        このメソッドは具象クラスで実装する必要があります。
        エージェント固有のノード、エッジ、条件分岐を定義して
        完全なワークフローグラフを作成します。

        Returns:
            CompiledGraph: コンパイル済みのワークフローグラフ
        """
        pass

    def draw_mermaid_graph(self) -> str:
        """ワークフローグラフをMermaid形式で可視化します。

        構築されたワークフローグラフをMermaid記法の文字列として出力し、
        グラフの構造を視覚的に確認できるようにします。

        Returns:
            str: Mermaid形式のグラフ記述文字列
        """
        graph = self.build_graph()
        return graph.get_graph().draw_mermaid()
