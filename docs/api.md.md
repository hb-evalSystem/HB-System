# API Reference

Complete API documentation for HB-Eval System.

---

## Core Modules

### `hb_eval.core.edm_memory`

#### Classes

##### `ExperienceMetrics`

Performance metrics for a stored experience.

```python
@dataclass
class ExperienceMetrics:
    pei: float = 0.0   # Planning Efficiency Index (0.0-1.0)
    frr: float = 0.0   # Failure Recovery Rate (0.0-1.0)
    ti: float = 0.0    # Traceability Index (0.0-1.0)
```

**Methods**:
- `__post_init__()`: Validates metric ranges

**Raises**:
- `ValueError`: If any metric is outside valid range

**Example**:
```python
from hb_eval import ExperienceMetrics

metrics = ExperienceMetrics(pei=0.92, frr=1.0, ti=0.95)
```

---

##### `Experience`

Container for a procedural plan and its evaluation.

```python
@dataclass
class Experience:
    plan: Plan
    metrics: ExperienceMetrics
    timestamp: Optional[float] = None
    metadata: dict = field(default_factory=dict)
```

**Attributes**:
- `plan`: The procedural plan that was executed
- `metrics`: Performance metrics for this experience
- `timestamp`: Optional Unix timestamp
- `metadata`: Additional context (dict)

**Example**:
```python
from hb_eval import Experience, ExperienceMetrics, Plan

plan = Plan(goal="Task", sub_goals=["Step 1", "Step 2"])
metrics = ExperienceMetrics(pei=0.85)
exp = Experience(plan=plan, metrics=metrics)
```

---

##### `EDM`

Eval-Driven Memory - Core memory system.

```python
class EDM:
    def __init__(
        self, 
        storage_threshold: float = 0.75,
        retrieval_threshold: float = 0.40,
        max_memory_size: int = 1000
    )
```

**Parameters**:
- `storage_threshold`: Minimum PEI to store (default: 0.75)
- `retrieval_threshold`: Minimum similarity to retrieve (default: 0.40)
- `max_memory_size`: Maximum experiences to store (default: 1000)

**Attributes**:
- `procedural_memory`: List[Experience] - Stored experiences

**Methods**:

###### `calculate_similarity(goal_a: str, goal_b: str) -> float`

Calculate Jaccard similarity between two goals.

**Returns**: Similarity score (0.0-1.0)

**Example**:
```python
edm = EDM()
sim = edm.calculate_similarity("optimize system", "improve system")
print(f"Similarity: {sim:.2f}")  # e.g., 0.67
```

###### `retrieve_procedural_guide(goal: str) -> Optional[Experience]`

Retrieve most similar past experience.

**Returns**: Most similar experience or None

**Example**:
```python
retrieved = edm.retrieve_procedural_guide("Deploy feature")
if retrieved:
    print(f"Found: {retrieved.plan.goal}")
```

###### `store(exp: Experience) -> bool`

Store experience if quality threshold met.

**Returns**: True if stored, False if rejected

**Example**:
```python
stored = edm.store(exp)
if stored:
    print("Experience stored successfully")
```

###### `get_memory_size() -> int`

Get number of stored experiences.

###### `clear_memory() -> None`

Clear all stored experiences.

###### `get_top_experiences(n: int = 5) -> List[Experience]`

Get top N experiences by PEI.

**Example**:
```python
top_5 = edm.get_top_experiences(5)
for exp in top_5:
    print(f"{exp.plan.goal}: PEI={exp.metrics.pei:.2f}")
```

---

### `hb_eval.core.adapt_planner`

#### Classes

##### `Plan`

Hierarchical procedural plan.

```python
@dataclass
class Plan:
    goal: str
    sub_goals: List[str] = field(default_factory=list)
    l_min: int = 5
    steps_taken: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

**Methods**:

###### `add_step(step: str) -> None`

Record a step as taken.

###### `get_progress() -> float`

Calculate completion progress (0.0-1.0).

###### `is_complete() -> bool`

Check if all sub-goals executed.

**Example**:
```python
plan = Plan(goal="Deploy", sub_goals=["Test", "Build", "Deploy"])
plan.add_step("Test")
print(f"Progress: {plan.get_progress():.0%}")  # 33%
```

---

##### `AdaptPlan`

Adaptive planning system.

```python
class AdaptPlan:
    def __init__(self, enable_verbose: bool = False)
```

**Methods**:

###### `generate_plan(goal: str, edm: EDM, is_replan: bool = False, force_new: bool = False) -> Plan`

Generate adaptive plan for goal.

**Parameters**:
- `goal`: Goal to plan for
- `edm`: EDM instance for retrieval
- `is_replan`: Whether this is replanning
- `force_new`: Skip retrieval, generate new

**Returns**: Plan instance

**Example**:
```python
planner = AdaptPlan()
edm = EDM()
plan = planner.generate_plan("Optimize database", edm)
print(f"Steps: {len(plan.sub_goals)}")
```

###### `replan(original_plan: Plan, edm: EDM, failure_point: Optional[int] = None) -> Plan`

Generate recovery plan after failure.

**Example**:
```python
recovery = planner.replan(failed_plan, edm, failure_point=2)
```

---

### `hb_eval.core.agent_loop`

#### Classes

##### `ExecutionStatus`

Execution status enumeration.

```python
class ExecutionStatus(Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RECOVERING = "recovering"
```

---

##### `ExecutionMetrics`

Runtime execution metrics.

```python
@dataclass
class ExecutionMetrics:
    steps_completed: int = 0
    steps_failed: int = 0
    recovery_attempts: int = 0
    total_steps: int = 0
```

**Methods**:
- `get_completion_rate() -> float`
- `get_failure_rate() -> float`

---

##### `LoopState`

Runtime execution state.

```python
@dataclass
class LoopState:
    goal: str
    plan: Optional[Plan] = None
    step_index: int = 0
    status: ExecutionStatus = ExecutionStatus.RUNNING
    outputs: List[str] = field(default_factory=list)
    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    error_log: List[str] = field(default_factory=list)
```

**Methods**:
- `is_finished() -> bool`
- `get_last_output() -> str`

---

##### `AgentLoop`

Main agent execution loop.

```python
class AgentLoop:
    def __init__(
        self, 
        edm: EDM, 
        planner: AdaptPlan,
        max_recovery_attempts: int = 3,
        enable_verbose: bool = False,
        step_callback: Optional[Callable] = None
    )
```

**Parameters**:
- `edm`: EDM instance
- `planner`: AdaptPlan instance
- `max_recovery_attempts`: Max recovery tries (default: 3)
- `enable_verbose`: Enable detailed logging (default: False)
- `step_callback`: Optional callback after each step

**Methods**:

###### `run(goal: str, store_experience: bool = True) -> str`

Execute complete planning/execution cycle.

**Returns**: Final output/result

**Example**:
```python
agent = AgentLoop(EDM(), AdaptPlan())
result = agent.run("Complete task", store_experience=True)
print(result)
```

---

### `hb_eval.core.external_llm_api`

#### Classes

##### `LLMProvider`

Supported LLM providers.

```python
class LLMProvider(Enum):
    OPENAI = "openai"
    MOCK = "mock"
    CUSTOM = "custom"
```

---

##### `LLMConfig`

LLM API configuration.

```python
class LLMConfig:
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.MOCK,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        endpoint: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout: int = 30,
        max_retries: int = 3
    )
```

**Example**:
```python
from hb_eval.core.external_llm_api import LLMConfig, LLMProvider

config = LLMConfig(
    provider=LLMProvider.OPENAI,
    api_key="sk-...",
    model="gpt-4",
    temperature=0.7
)
```

---

#### Functions

##### `set_global_config(config: LLMConfig) -> None`

Set global LLM configuration.

##### `get_global_config() -> LLMConfig`

Get current global configuration.

##### `get_api_key() -> Optional[str]`

Get API key from config or environment.

##### `llm_call(prompt: str, config: Optional[LLMConfig] = None, system_message: Optional[str] = None) -> str`

Execute LLM API call.

**Parameters**:
- `prompt`: User prompt
- `config`: Optional custom config
- `system_message`: Optional system context

**Returns**: LLM response text

**Example**:
```python
from hb_eval.core.external_llm_api import llm_call, LLMConfig, LLMProvider, set_global_config

# Setup
set_global_config(LLMConfig(provider=LLMProvider.OPENAI, api_key="..."))

# Call
response = llm_call("What is 2+2?")
print(response)
```

##### `test_connection(config: Optional[LLMConfig] = None) -> bool`

Test LLM API connection.

**Returns**: True if successful

---

## Top-Level Exports

### `hb_eval` Package

```python
from hb_eval import (
    # Memory
    EDM,
    Experience,
    ExperienceMetrics,
    
    # Planning
    AdaptPlan,
    Plan,
    
    # Execution
    AgentLoop,
    LoopState,
)
```

---

## Usage Examples

### Basic Agent

```python
from hb_eval import EDM, AdaptPlan, AgentLoop

# Initialize
edm = EDM()
planner = AdaptPlan()
agent = AgentLoop(edm, planner)

# Run
result = agent.run("Your goal here")
```

### With Custom Configuration

```python
from hb_eval import EDM, AdaptPlan, AgentLoop
from hb_eval.core.external_llm_api import LLMConfig, LLMProvider, set_global_config

# Configure LLM
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    api_key="your-key",
    model="gpt-4",
    temperature=0.7
)
set_global_config(config)

# Custom EDM
edm = EDM(
    storage_threshold=0.80,
    retrieval_threshold=0.50,
    max_memory_size=500
)

# Initialize agent
planner = AdaptPlan(enable_verbose=True)
agent = AgentLoop(edm, planner, max_recovery_attempts=5)

# Run
result = agent.run("Complex task")
```

### With Callbacks

```python
def my_callback(state, step, output):
    print(f"Completed step {state.step_index}: {step}")
    print(f"Output: {output[:50]}...")

agent = AgentLoop(
    edm=edm,
    planner=planner,
    step_callback=my_callback
)

result = agent.run("Task with monitoring")
```

### Memory Management

```python
edm = EDM()

# Store experiences
for task_result in task_results:
    exp = Experience(
        plan=task_result.plan,
        metrics=ExperienceMetrics(pei=task_result.pei)
    )
    stored = edm.store(exp)
    print(f"Stored: {stored}")

# Query memory
print(f"Memory size: {edm.get_memory_size()}")

# Get top experiences
top = edm.get_top_experiences(5)
for i, exp in enumerate(top, 1):
    print(f"{i}. {exp.plan.goal} (PEI: {exp.metrics.pei:.2f})")

# Clear if needed
# edm.clear_memory()
```

---

## Type Hints

All classes and functions include comprehensive type hints:

```python
from typing import List, Optional, Callable

def process_experiences(
    experiences: List[Experience],
    threshold: float = 0.8
) -> Optional[Experience]:
    """Process and filter experiences."""
    filtered = [e for e in experiences if e.metrics.pei >= threshold]
    return max(filtered, key=lambda e: e.metrics.pei) if filtered else None
```

---

## Error Handling

### Common Exceptions

```python
# ValueError: Invalid metric ranges
try:
    metrics = ExperienceMetrics(pei=1.5)  # Invalid!
except ValueError as e:
    print(f"Error: {e}")

# RuntimeError: API failures
try:
    result = llm_call("prompt")
except RuntimeError as e:
    print(f"LLM API failed: {e}")
```

### Best Practices

```python
# Always wrap API calls in try-except
try:
    agent = AgentLoop(EDM(), AdaptPlan())
    result = agent.run("task")
except Exception as e:
    print(f"Execution failed: {e}")
    # Handle gracefully
```

---

## Performance Considerations

### Memory Usage

```python
# Limit memory size for long-running agents
edm = EDM(max_memory_size=100)  # Only keep 100 best experiences
```

### API Rate Limits

```python
# Configure retries and timeout
config = LLMConfig(
    max_retries=3,
    timeout=30  # seconds
)
set_global_config(config)
```

---

## Logging

Enable verbose mode for debugging:

```python
planner = AdaptPlan(enable_verbose=True)
agent = AgentLoop(edm, planner, enable_verbose=True)

# Will print detailed execution logs
result = agent.run("task")
```

---

## Version Compatibility

- **Python**: 3.8+
- **Dependencies**: See `requirements.txt`

```python
import sys
assert sys.version_info >= (3, 8), "Python 3.8+ required"
```

---

## See Also

- [Metrics Guide](metrics.md) - Detailed metrics documentation
- [User Guide](guide.md) - Step-by-step tutorials
- [Examples](../examples/) - Complete code examples
- [Research Papers](../RESEARCH.md) - Theoretical foundation

---

<p align="center">
  <i>For questions or clarifications, open an issue on GitHub</i>
</p>