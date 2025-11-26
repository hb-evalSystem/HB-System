# ================================================================
#  open_core/adapt_planner.py
#  Adaptive Planner Module for Open-Core Agents
# ================================================================

from dataclasses import dataclass, field
from typing import List

# Direct import for Pydroid3 environment
from edm_memory import EDM


# ================================================================
# 1. Data Structure: Plan
# ================================================================

@dataclass
class Plan:
    """Represents a procedural plan with hierarchical sub-goals."""
    goal: str
    sub_goals: List[str] = field(default_factory=list)
    l_min: int = 5
    steps_taken: List[str] = field(default_factory=list)


# ================================================================
# 2. Adaptive Planning Core
# ================================================================

class AdaptPlan:
    """
    Generates and adapts procedural plans.
    Integrates with EDM for retrieval and reuse of prior experiences.
    """

    def generate_plan(self, goal: str, edm: EDM, is_replan: bool = False) -> Plan:
        """
        Generates a plan for a given goal.
        - Attempts retrieval from EDM if available.
        - Generates a default plan structure otherwise.
        """

        # ------------------------------------------------------------
        # Step 1: Attempt retrieval from EDM memory
        # ------------------------------------------------------------
        retrieved = edm.retrieve_procedural_guide(goal)

        if retrieved and not is_replan:
            # Reuse sub-goals and structure from past experience
            p = Plan(
                goal=goal,
                sub_goals=list(retrieved.plan.sub_goals),
                l_min=retrieved.plan.l_min
            )
            return p

        # ------------------------------------------------------------
        # Step 2: Generate default (protected) procedural plan
        # ------------------------------------------------------------
        # Template-based plan ensures reproducibility without exposing internal logic
        return Plan(
            goal=goal,
            sub_goals=[
                f"S_1: Analyze {goal}",
                f"S_2: Execute {goal}",
                "S_3: Validate Result"
            ],
            l_min=5
        )
