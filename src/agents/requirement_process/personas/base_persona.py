"""ペルソナエージェントの基底クラス"""

import abc
from typing import Any, Dict, List

from agents.biz_requirement.schemas import ProjectBusinessRequirement
from agents.requirement_process.schemas import PersonaOutput, PersonaRole


class BasePersonaAgent(abc.ABC):
    """ペルソナエージェントの抽象基底クラス"""

    def __init__(self, persona_role: PersonaRole):
        self.persona_role = persona_role

    @abc.abstractmethod
    def execute(self, business_requirement: ProjectBusinessRequirement, previous_outputs: List[PersonaOutput] = None) -> PersonaOutput:
        """ペルソナエージェントのメイン実行メソッド

        Args:
            business_requirement: ビジネス要件定義
            previous_outputs: 前段階のペルソナエージェントの出力

        Returns:
            PersonaOutput: このペルソナエージェントの成果物
        """
        pass

    def _extract_relevant_info(self, previous_outputs: List[PersonaOutput], target_role: PersonaRole) -> Dict[str, Any]:
        """前段階の特定ペルソナの出力から関連情報を抽出"""
        if not previous_outputs:
            return {}

        for output in previous_outputs:
            if output.persona_role == target_role:
                return output.deliverables

        return {}

    def _create_output(
        self, deliverables: Dict[str, Any], recommendations: List[str] = None, concerns: List[str] = None
    ) -> PersonaOutput:
        """PersonaOutputを作成するヘルパーメソッド"""
        return PersonaOutput(
            persona_role=self.persona_role, deliverables=deliverables, recommendations=recommendations or [], concerns=concerns or []
        )
