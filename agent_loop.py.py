"""
Agent Execution Loop
Lightweight execution loop for Open-Core Agent with evaluation capabilities.

This module provides the main agent control loop that:
- Executes plans step-by-step
- Integrates with external LLM APIs
- Tracks execution metrics
- Handles failures and recovery
"""

from dataclasses import dataclass, field
from typing import Optional, List, Callable
from enum import Enum

from hb_eval.core.adapt_planner import AdaptPlan, Plan
from hb_eval.core.edm_memory import EDM, Experience, ExperienceMetrics
from hb_eval.core.external_llm_api import llm_call


class ExecutionStatus(Enum):
    """Execution status enumeration."""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RECOVERING = "recovering"


@dataclass
class ExecutionMetrics:
    """Runtime execution metrics."""
    steps_completed: int = 0
    steps_failed: int = 0
    recovery_attempts: int = 0
    total_steps: int = 0
    
    def get_completion_rate(self) -> float:
        """Calculate completion rate."""
        if self.total_steps == 0:
            return 0.0
        return self.steps_completed / self.total_steps
    
    def get_failure_rate(self) -> float:
        """Calculate failure rate."""
        total_attempts = self.steps_completed + self.steps_failed
        if total_attempts == 0:
            return 0.0
        return self.steps_failed / total_attempts


@dataclass
class LoopState:
    """
    Runtime execution state of the agent loop.
    
    Attributes:
        goal: The main goal being executed
        plan: Current active plan
        step_index: Current step position
        status: Current execution status
        outputs: List of outputs from each step
        metrics: Execution metrics
    """
    goal: str
    plan: Optional[Plan] = None
    step_index: int = 0
    status: ExecutionStatus = ExecutionStatus.RUNNING
    outputs: List[str] = field(default_factory=list)
    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    error_log: List[str] = field(default_factory=list)
    
    def is_finished(self) -> bool:
        """Check if execution is complete."""
        return self.status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED]
    
    def get_last_output(self) -> str:
        """Get the most recent output."""
        return self.outputs[-1] if self.outputs else ""


class AgentLoop:
    """
    Main agent execution loop with evaluation capabilities.
    
    Executes procedural plans step-by-step, integrates with LLM APIs,
    tracks performance metrics, and handles failures with recovery.
    """

    def __init__(
        self, 
        edm: EDM, 
        planner: AdaptPlan,
        max_recovery_attempts: int = 3,
        enable_verbose: bool = False,
        step_callback: Optional[Callable] = None
    ):
        """
        Initialize the agent loop.
        
        Args:
            edm: EDM instance for memory operations
            planner: AdaptPlan instance for plan generation
            max_recovery_attempts: Maximum number of recovery attempts
            enable_verbose: Enable detailed logging
            step_callback: Optional callback function called after each step
        """
        self.edm = edm
        self.planner = planner
        self.max_recovery_attempts = max_recovery_attempts
        self.enable_verbose = enable_verbose
        self.step_callback = step_callback

    def run(self, goal: str, store_experience: bool = True) -> str:
        """
        Execute a complete planning and execution cycle.
        
        Args:
            goal: The goal to achieve
            store_experience: Whether to store the experience in EDM
            
        Returns:
            The final output/result
        """
        # Initialize state
        state = LoopState(goal=goal)
        state.plan = self.planner.generate_plan(goal, self.edm)
        state.metrics.total_steps = len(state.plan.sub_goals)

        if self.enable_verbose:
            print(f"\n{'='*60}")
            print(f"[AgentLoop] Starting execution for: {goal}")
            print(f"[AgentLoop] Plan has {len(state.plan.sub_goals)} steps")
            print(f"{'='*60}\n")

        # Main execution loop
        while not state.is_finished():
            try:
                self._execute_step(state)
            except Exception as e:
                self._handle_failure(state, str(e))

        # Store experience if successful and enabled
        if state.status == ExecutionStatus.SUCCESS and store_experience:
            self._store_execution_experience(state)

        if self.enable_verbose:
            self._print_summary(state)

        return state.get_last_output()

    def _execute_step(self, state: LoopState):
        """Execute a single step of the plan."""
        # Check termination
        if state.plan is None or state.step_index >= len(state.plan.sub_goals):
            state.status = ExecutionStatus.SUCCESS
            return

        # Get current step
        step = state.plan.sub_goals[state.step_index]
        
        if self.enable_verbose:
            print(f"\n[Step {state.step_index + 1}/{len(state.plan.sub_goals)}]")
            print(f"Executing: {step}")

        # Build execution prompt
        prompt = self._build_step_prompt(state.goal, step, state.step_index)

        # Execute via LLM
        try:
            output = llm_call(prompt)
            
            if self.enable_verbose:
                print(f"Output: {output[:100]}..." if len(output) > 100 else f"Output: {output}")

            # Update state
            state.outputs.append(output)
            state.plan.add_step(step)
            state.metrics.steps_completed += 1
            state.step_index += 1

            # Callback
            if self.step_callback:
                self.step_callback(state, step, output)

        except Exception as e:
            raise RuntimeError(f"Step execution failed: {str(e)}")

    def _build_step_prompt(self, goal: str, step: str, step_index: int) -> str:
        """Build the prompt for LLM execution."""
        return (
            f"You are an AI agent executing a procedural plan.\n\n"
            f"Overall Goal: {goal}\n"
            f"Current Step ({step_index + 1}): {step}\n\n"
            f"Execute this step and provide the result.\n"
            f"Be concise and action-oriented."
        )

    def _handle_failure(self, state: LoopState, error: str):
        """Handle execution failure and attempt recovery."""
        state.metrics.steps_failed += 1
        state.error_log.append(f"Step {state.step_index}: {error}")

        if self.enable_verbose:
            print(f"\n[ERROR] Step {state.step_index + 1} failed: {error}")

        # Check if recovery is possible
        if state.metrics.recovery_attempts >= self.max_recovery_attempts:
            if self.enable_verbose:
                print("[AgentLoop] Max recovery attempts reached. Execution failed.")
            state.status = ExecutionStatus.FAILED
            return

        # Attempt recovery
        if self.enable_verbose:
            print(f"[AgentLoop] Attempting recovery ({state.metrics.recovery_attempts + 1}/{self.max_recovery_attempts})")

        state.status = ExecutionStatus.RECOVERING
        state.metrics.recovery_attempts += 1

        # Replan
        state.plan = self.planner.replan(state.plan, self.edm, state.step_index)
        state.step_index = 0  # Restart from beginning with new plan
        state.status = ExecutionStatus.RUNNING

    def _store_execution_experience(self, state: LoopState):
        """Store successful execution as an experience in EDM."""
        # Calculate PEI (simplified version)
        pei = self._calculate_pei(state)
        
        # Calculate FRR
        frr = 1.0 if state.metrics.recovery_attempts == 0 else 0.5
        
        # Create experience
        exp = Experience(
            plan=state.plan,
            metrics=ExperienceMetrics(pei=pei, frr=frr, ti=1.0)
        )
        
        # Store in EDM
        stored = self.edm.store(exp)
        
        if self.enable_verbose:
            if stored:
                print(f"\n[EDM] Experience stored (PEI: {pei:.2f})")
            else:
                print(f"\n[EDM] Experience not stored (PEI {pei:.2f} below threshold)")

    def _calculate_pei(self, state: LoopState) -> float:
        """
        Calculate Performance Efficiency Index.
        
        Simplified formula based on:
        - Completion rate
        - Failure rate
        - Recovery attempts
        """
        completion = state.metrics.get_completion_rate()
        failure_penalty = state.metrics.get_failure_rate() * 0.3
        recovery_penalty = (state.metrics.recovery_attempts / max(self.max_recovery_attempts, 1)) * 0.2
        
        pei = max(0.0, completion - failure_penalty - recovery_penalty)
        return min(1.0, pei)

    def _print_summary(self, state: LoopState):
        """Print execution summary."""
        print(f"\n{'='*60}")
        print(f"[AgentLoop] Execution Summary")
        print(f"{'='*60}")
        print(f"Status: {state.status.value.upper()}")
        print(f"Steps Completed: {state.metrics.steps_completed}/{state.metrics.total_steps}")
        print(f"Steps Failed: {state.metrics.steps_failed}")
        print(f"Recovery Attempts: {state.metrics.recovery_attempts}")
        print(f"PEI: {self._calculate_pei(state):.2f}")
        print(f"{'='*60}\n")