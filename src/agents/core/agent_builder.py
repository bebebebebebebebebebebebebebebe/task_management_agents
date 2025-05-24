import abc
from typing import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel


class AgentGraphBuilder(abc.ABC):
    def __init__(
        self,
        state: StateGraph | dict[str, any] | BaseModel,
    ):
        self.state = state
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        if isinstance(self.state, StateGraph):
            return self.state

        return StateGraph(state_schema=self.state)

    @abc.abstractmethod
    def build_graph(self) -> CompiledGraph:
        pass

    def drraw_mermaid_graph(self) -> str:
        graph = self.build_graph()
        return graph.get_graph().draw_mermaid()


