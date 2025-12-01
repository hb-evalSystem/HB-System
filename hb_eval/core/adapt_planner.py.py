"""
Adaptive Planner Module
Generates and adapts procedural plans for agent execution.

This module provides the AdaptPlan system that creates executable plans
by either retrieving similar past experiences or generating new plans.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from hb_eval.core.edm_memory import EDM


@dataclass
class Plan:
    """
    Represents a hierarchical procedural plan.
    
    Attributes:
        goal: The main goal this plan aims to achieve
        sub_goals: List of sequential sub-goals/steps
        l_min: Minimum expected execution length
        steps_taken: History of executed steps (populated at runtime)
        metadata: Optional additional plan metadata
    """
    goal: str
    sub_goals: List[str] = field(default_factory=list)
    l_min: int = 5
    steps_taken: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def add_step(self, step: str):
        """Record a step as taken."""
        self.steps_taken.append(step)
    
    def get_progress(self) -> float:
        """Calculate plan completion progress (0.0 to 1.0)."""
        if not self.sub_goals:
            return 0.0
        return len(self.steps_taken) / len(self.sub_goals)
    
    def is_complete(self) -> bool:
        """Check if all sub-goals have been executed."""
        return len(self.steps_taken) >= len(self.sub_goals)


class AdaptPlan:
    """
    Adaptive Planning System.
    
    Generates procedural plans by:
    1. Attempting retrieval from EDM memory
    2. Adapting retrieved plans if available
    3. Generating new plans from templates if needed
    
    This is a rule-based deterministic planner suitable for
    research and benchmarking scenarios.
    """

    def __init__(self, enable_verbose: bool = False):
        """
        Initialize the adaptive planner.
        
        Args:
            enable_verbose: Enable detailed logging of planning decisions
        """
        self.enable_verbose = enable_verbose
        self._plan_templates = self._initialize_templates()

    def _initialize_templates(self) -> dict:
        """
        Initialize default plan templates for common goal types.
        
        Returns:
            Dictionary mapping goal keywords to template structures
        """
        return {
            "optimize": {
                "sub_goals": [
                    "Analyze current state and identify bottlenecks",
                    "Design optimization strategy",
                    "Execute optimization procedure",
                    "Validate and measure improvements"
                ],
                "l_min": 4
            },
            "improve": {
                "sub_goals": [
                    "Assess baseline performance",
                    "Identify improvement opportunities",
                    "Implement enhancements",
                    "Verify improvements"
                ],
                "l_min": 4
            },
            "default": {
                "sub_goals": [
                    "Analyze goal requirements",
                    "Execute primary task",
                    "Validate result"
                ],
                "l_min": 3
            }
        }

    def _select_template(self, goal: str) -> dict:
        """
        Select appropriate template based on goal keywords.
        
        Args:
            goal: The goal string
            
        Returns:
            Template dictionary with sub_goals and l_min
        """
        goal_lower = goal.lower()
        
        for keyword, template in self._plan_templates.items():
            if keyword in goal_lower:
                return template
        
        return self._plan_templates["default"]

    def generate_plan(
        self, 
        goal: str, 
        edm: EDM, 
        is_replan: bool = False,
        force_new: bool = False
    ) -> Plan:
        """
        Generate an adaptive plan for the given goal.
        
        Strategy:
        1. If not replanning and not forced: Try retrieval from EDM
        2. If retrieved: Adapt the retrieved plan
        3. Otherwise: Generate from template
        
        Args:
            goal: The goal to plan for
            edm: EDM instance for memory retrieval
            is_replan: Whether this is a replanning attempt
            force_new: Force generation of new plan (skip retrieval)
            
        Returns:
            A Plan instance ready for execution
        """
        if self.enable_verbose:
            print(f"[AdaptPlan] Generating plan for: {goal}")
            print(f"[AdaptPlan] Replan: {is_replan}, Force New: {force_new}")

        # --------------------------------------------------------
        # Step 1: Attempt retrieval from EDM
        # --------------------------------------------------------
        retrieved = None
        if not is_replan and not force_new:
            retrieved = edm.retrieve_procedural_guide(goal)

        if retrieved:
            if self.enable_verbose:
                print(f"[AdaptPlan] Retrieved similar plan from memory")
                print(f"[AdaptPlan] Original goal: {retrieved.plan.goal}")
            
            # Adapt retrieved plan for new goal
            adapted_plan = Plan(
                goal=goal,
                sub_goals=list(retrieved.plan.sub_goals),  # Copy sub-goals
                l_min=retrieved.plan.l_min,
                metadata={
                    "source": "retrieved",
                    "original_goal": retrieved.plan.goal,
                    "pei": retrieved.metrics.pei
                }
            )
            return adapted_plan

        # --------------------------------------------------------
        # Step 2: Generate new plan from template
        # --------------------------------------------------------
        if self.enable_verbose:
            print(f"[AdaptPlan] No suitable memory found, generating new plan")

        template = self._select_template(goal)
        
        # Contextualize template sub-goals with the actual goal
        contextualized_sub_goals = [
            sub_goal.replace("goal", goal).replace("task", goal)
            for sub_goal in template["sub_goals"]
        ]
        
        new_plan = Plan(
            goal=goal,
            sub_goals=contextualized_sub_goals,
            l_min=template["l_min"],
            metadata={"source": "generated", "template_used": self._get_template_name(goal)}
        )
        
        if self.enable_verbose:
            print(f"[AdaptPlan] Generated {len(new_plan.sub_goals)}-step plan")
        
        return new_plan

    def _get_template_name(self, goal: str) -> str:
        """Get the name of the template that would be used for this goal."""
        goal_lower = goal.lower()
        for keyword in self._plan_templates.keys():
            if keyword in goal_lower:
                return keyword
        return "default"

    def replan(self, original_plan: Plan, edm: EDM, failure_point: Optional[int] = None) -> Plan:
        """
        Generate a recovery plan after failure.
        
        Args:
            original_plan: The plan that failed
            edm: EDM instance
            failure_point: Index where failure occurred (if known)
            
        Returns:
            A new recovery plan
        """
        if self.enable_verbose:
            print(f"[AdaptPlan] Replanning after failure at step {failure_point}")
        
        # For now, generate a fresh plan
        # Future: Could implement more sophisticated recovery strategies
        return self.generate_plan(original_plan.goal, edm, is_replan=True)