import abc

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel


class AgentGraphBuilder(abc.ABC):
    def __init__(
        self,
        state_object: type[dict[str, any]] | type[BaseModel],
    ):
        self.workflow = StateGraph(state_schema=state_object)

    @abc.abstractmethod
    def build_graph(self) -> CompiledGraph:
        pass

    def draw_mermaid_graph(self) -> str:
        graph = self.build_graph()
        return graph.get_graph().draw_mermaid()
