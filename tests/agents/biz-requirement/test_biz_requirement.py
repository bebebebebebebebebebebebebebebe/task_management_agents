import pytest

from agents.biz_requirement import BizRequirementAgent


class TestBizRequirementAgent:
    @pytest.fixture
    def setup_agent(self):
        """Fixture to set up the BizRequirementAgent before each test."""
        self.agent = BizRequirementAgent()
        return self.agent

    def test_setup_agent(self, setup_agent):
        agent = setup_agent
        assert agent is not None, 'BizRequirementAgent should be initialized'
        assert hasattr(agent, 'workflow'), 'Agent should have a workflow attribute'

    def test_draw_mermaid_graph(self, setup_agent):
        mermaid_graph = setup_agent.draw_mermaid_graph()
        assert isinstance(mermaid_graph, str), 'Mermaid graph should be a string'
        # graph TD が含まれていることを確認
        assert 'graph TD' in mermaid_graph, 'Mermaid graph should start with "graph TD"'
