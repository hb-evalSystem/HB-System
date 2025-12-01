# User Guide

Step-by-step guide to using the HB-Eval System.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip or conda package manager
- (Optional) OpenAI API key for real LLM calls

### Installation

#### Method 1: From Source (Recommended)

```bash
git clone https://github.com/hb-evalSystem/HB-System.git
cd HB-System
pip install -e .
```

#### Method 2: Requirements Only

```bash
git clone https://github.com/hb-evalSystem/HB-System.git
cd HB-System
pip install -r requirements.txt
```

#### Verify Installation

```python
python -c "import hb_eval; print(hb_eval.__version__)"
# Output: 1.0.0
```

---

## Your First Agent

### Step 1: Basic Setup

```python
from hb_eval import EDM, AdaptPlan, AgentLoop

# Initialize components
edm = EDM()                    # Memory system
planner = AdaptPlan()          # Planning system
agent = AgentLoop(edm, planner)  # Agent loop

# Run your first task
result = agent.run("Optimize database performance")
print(f"Result: {result}")
```

That's it! You've run your first HB-Eval agent.

### Step 2: Understanding the Output

```python
result = agent.run("Your task here")

# The agent automatically:
# 1. Generates a plan (or retrieves from memory)
# 2. Executes steps one by one
# 3. Tracks metrics (PEI, success/failure)
# 4. Stores successful experiences
```

---

## Core Concepts

### 1. Memory (EDM)

EDM stores and retrieves high-quality plans.

```python
from hb_eval import EDM

# Initialize with custom thresholds
edm = EDM(
    storage_threshold=0.78,   # Only store if PEI ≥ 0.78
    retrieval_threshold=0.40, # Retrieve if similarity ≥ 0.40
    max_memory_size=1000      # Maximum experiences to keep
)

# Check memory status
print(f"Stored experiences: {edm.get_memory_size()}")
```

**Key Concept**: EDM uses **PEI** (Planning Efficiency Index) as a quality gate. Only high-quality experiences are stored.

### 2. Planning (Adapt-Plan)

AdaptPlan generates or retrieves plans.

```python
from hb_eval import AdaptPlan

planner = AdaptPlan(enable_verbose=True)  # Enable detailed logs

# Generate plan
plan = planner.generate_plan("Deploy new feature", edm)

print(f"Goal: {plan.goal}")
print(f"Steps: {len(plan.sub_goals)}")
for i, step in enumerate(plan.sub_goals, 1):
    print(f"  {i}. {step}")
```

**Key Concept**: If a similar plan exists in EDM, it's reused. Otherwise, a new one is generated.

### 3. Execution (AgentLoop)

AgentLoop executes plans step-by-step.

```python
from hb_eval import AgentLoop

agent = AgentLoop(
    edm=edm,
    planner=planner,
    max_recovery_attempts=3,  # Retry failed steps up to 3 times
    enable_verbose=True       # Show detailed execution logs
)

result = agent.run("Your goal", store_experience=True)
```

**Key Concept**: AgentLoop automatically tracks metrics and handles failures.

---

## Working with Different LLM Providers

### Mock Mode (Default - No API Key Needed)

```python
from hb_eval.core.external_llm_api import LLMConfig, LLMProvider, set_global_config

# Mock mode (for testing)
config = LLMConfig(provider=LLMProvider.MOCK)
set_global_config(config)

# Now run your agent - it will use mock responses
agent = AgentLoop(EDM(), AdaptPlan())
result = agent.run("Test task")
```

### OpenAI GPT

```python
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    api_key="your-openai-key",  # Or set LLM_API_KEY env variable
    model="gpt-4",               # or "gpt-3.5-turbo"
    temperature=0.7,
    max_tokens=500
)
set_global_config(config)

# Now agent uses real OpenAI API
result = agent.run("Real task")
```

### Using Environment Variables

```bash
# In terminal
export LLM_API_KEY="your-api-key"
export OPENAI_API_KEY="your-api-key"  # Alternative name
```

```python
# In Python - automatically picks up from environment
config = LLMConfig(provider=LLMProvider.OPENAI)
set_global_config(config)
```

---

## Common Workflows

### Workflow 1: Simple Task Execution

```python
from hb_eval import EDM, AdaptPlan, AgentLoop

# One-time setup
edm = EDM()
planner = AdaptPlan()
agent = AgentLoop(edm, planner)

# Execute tasks
tasks = [
    "Analyze sales data",
    "Generate monthly report",
    "Send report to team"
]

for task in tasks:
    print(f"\nExecuting: {task}")
    result = agent.run(task)
    print(f"✓ Completed: {result[:50]}...")
```

### Workflow 2: Monitoring Performance

```python
# Track metrics over multiple tasks
metrics_history = []

for task in tasks:
    result = agent.run(task, store_experience=True)
    
    # Access metrics
    metrics = {
        'task': task,
        'success': result.status == 'success',
        'pei': result.metrics.pei if hasattr(result, 'metrics') else None
    }
    metrics_history.append(metrics)

# Analyze
import pandas as pd
df = pd.DataFrame(metrics_history)
print(df)
print(f"\nAverage PEI: {df['pei'].mean():.2f}")
```

### Workflow 3: Memory-Enhanced Learning

```python
# Seed initial knowledge
from hb_eval import Experience, ExperienceMetrics, Plan

initial_plan = Plan(
    goal="Deploy application",
    sub_goals=["Run tests", "Build Docker", "Push to registry", "Deploy"]
)

exp = Experience(
    plan=initial_plan,
    metrics=ExperienceMetrics(pei=0.95, frr=1.0)
)

edm.store(exp)
print(f"✓ Seeded memory with {edm.get_memory_size()} experience(s)")

# Now similar tasks will reuse this knowledge
result = agent.run("Deploy new version")  # Will retrieve similar plan!
```

### Workflow 4: Fault Injection Testing

```python
# Test agent reliability manually
def inject_fault(agent, task):
    """Simulate tool failure during execution."""
    # This is a simplified example
    # Real fault injection in benchmarks/fit/
    try:
        result = agent.run(task)
        return True, result
    except Exception as e:
        return False, str(e)

# Test resilience
success, result = inject_fault(agent, "Critical task")
print(f"Success: {success}")
```

---

## Advanced Features

### Custom Callbacks

Monitor execution in real-time:

```python
def my_callback(state, step, output):
    """Called after each step."""
    print(f"[Step {state.step_index + 1}] {step}")
    print(f"  Output: {output[:40]}...")
    print(f"  PEI so far: {state.metrics.pei if hasattr(state, 'metrics') else 'N/A'}")

agent = AgentLoop(
    edm=edm,
    planner=planner,
    step_callback=my_callback,
    enable_verbose=False  # Disable built-in logs if using callback
)

result = agent.run("Task with monitoring")
```

### Custom Metrics Calculation

```python
from hb_eval import AgentLoop, LoopState

class CustomAgentLoop(AgentLoop):
    def _calculate_pei(self, state: LoopState) -> float:
        """Override PEI calculation."""
        # Your custom logic here
        pei = super()._calculate_pei(state)
        
        # Add your adjustments
        custom_pei = pei * 0.9  # Example adjustment
        
        return custom_pei

# Use custom agent
custom_agent = CustomAgentLoop(edm, planner)
```

### Memory Analysis

```python
# Get top performers
top_5 = edm.get_top_experiences(5)

print("Top 5 Experiences:")
for i, exp in enumerate(top_5, 1):
    print(f"{i}. {exp.plan.goal}")
    print(f"   PEI: {exp.metrics.pei:.2f}")
    print(f"   Steps: {len(exp.plan.sub_goals)}")
    print(f"   Metadata: {exp.metadata}")
    print()

# Clear poor experiences (careful!)
# edm.clear_memory()
```

---

## Best Practices

### 1. Start with Mock Mode

```python
# Test your logic first
from hb_eval.core.external_llm_api import LLMConfig, LLMProvider, set_global_config

set_global_config(LLMConfig(provider=LLMProvider.MOCK))

# Develop and debug
agent = AgentLoop(EDM(), AdaptPlan())
result = agent.run("Test task")

# Then switch to real API when ready
```

### 2. Enable Verbose Logging During Development

```python
planner = AdaptPlan(enable_verbose=True)
agent = AgentLoop(edm, planner, enable_verbose=True)

# You'll see detailed execution traces
```

### 3. Set Appropriate Memory Thresholds

```python
# For research/experimentation (keep more)
edm = EDM(storage_threshold=0.70, max_memory_size=2000)

# For production (keep only best)
edm = EDM(storage_threshold=0.85, max_memory_size=500)
```

### 4. Handle API Failures Gracefully

```python
try:
    result = agent.run("Important task")
except RuntimeError as e:
    print(f"API Error: {e}")
    # Fallback to mock mode or retry
    set_global_config(LLMConfig(provider=LLMProvider.MOCK))
    result = agent.run("Important task")
```

### 5. Monitor Memory Growth

```python
# Periodic cleanup
if edm.get_memory_size() > 1000:
    print("Memory getting large, consider clearing old experiences")
    # Option 1: Clear all
    # edm.clear_memory()
    
    # Option 2: Keep only top experiences
    top = edm.get_top_experiences(500)
    edm.procedural_memory = top
```

---

## Troubleshooting

### Issue: "No module named 'hb_eval'"

**Solution**: Install the package

```bash
cd HB-System
pip install -e .
```

### Issue: "LLM API call failed"

**Causes**:
1. No API key set
2. Invalid API key
3. Network issues
4. Rate limits

**Solutions**:

```python
# Check config
from hb_eval.core.external_llm_api import get_global_config

config = get_global_config()
print(f"Provider: {config.provider}")
print(f"Has API key: {bool(config.api_key)}")

# Test connection
from hb_eval.core.external_llm_api import test_connection

if test_connection():
    print("✓ API connection works")
else:
    print("✗ API connection failed")
    # Fall back to mock
    set_global_config(LLMConfig(provider=LLMProvider.MOCK))
```

### Issue: "Agent returns immediately without doing anything"

**Cause**: Empty plan

**Solution**: Check plan generation

```python
plan = planner.generate_plan("Your goal", edm)
print(f"Plan has {len(plan.sub_goals)} steps")

if len(plan.sub_goals) == 0:
    print("Warning: Empty plan generated!")
    # Force new plan
    plan = planner.generate_plan("Your goal", edm, force_new=True)
```

### Issue: "PEI always 0 or 1"

**Cause**: L_min not set correctly

**Solution**: Set l_min explicitly

```python
plan = Plan(
    goal="Your goal",
    sub_goals=["Step 1", "Step 2", "Step 3"],
    l_min=3  # Set optimal length
)
```

---

## Integration Examples

### With LangChain

```python
# 1. Build agent with LangChain
from langchain.agents import initialize_agent
langchain_agent = initialize_agent(...)

# 2. Evaluate with HB-Eval
from hb_eval import EDM, AdaptPlan, AgentLoop

evaluator = AgentLoop(EDM(), AdaptPlan())

# Wrap LangChain execution
def evaluate_langchain_agent(task):
    # Execute with LangChain
    lc_result = langchain_agent.run(task)
    
    # Evaluate with HB-Eval
    hb_result = evaluator.run(task)
    
    # Compare metrics
    print(f"LangChain: {lc_result}")
    print(f"HB-Eval PEI: {hb_result.metrics.pei:.2f}")

evaluate_langchain_agent("Test task")
```

### With Custom Agents

```python
class MyCustomAgent:
    def run(self, task):
        # Your agent logic
        return "result"

# Wrap for HB-Eval evaluation
def evaluate_custom_agent(agent, task):
    # Execute
    result = agent.run(task)
    
    # Create HB-Eval equivalent for metrics
    hb_agent = AgentLoop(EDM(), AdaptPlan())
    hb_result = hb_agent.run(task)
    
    return {
        'custom_result': result,
        'pei': hb_result.metrics.pei,
        'frr': hb_result.metrics.frr
    }

my_agent = MyCustomAgent()
metrics = evaluate_custom_agent(my_agent, "Task")
print(metrics)
```

---

## Next Steps

### Learn More

- **Metrics Guide**: [docs/metrics.md](metrics.md) - Deep dive into all 9 metrics
- **API Reference**: [docs/api.md](api.md) - Complete API documentation
- **Research Papers**: [RESEARCH.md](../RESEARCH.md) - Theoretical foundation
- **Examples**: [examples/](../examples/) - More code examples

### Contribute

- **Report Bugs**: [GitHub Issues](https://github.com/hb-evalSystem/HB-System/issues)
- **Ask Questions**: [GitHub Discussions](https://github.com/hb-evalSystem/HB-System/discussions)
- **Contribute Code**: [CONTRIBUTING.md](../CONTRIBUTING.md)

### Stay Updated

- ⭐ Star the repository
- 👀 Watch for updates
- 💬 Join discussions

---

## FAQ

### Q: Do I need an API key?

A: No, the framework works in mock mode without any API key. For production use with real LLMs, you'll need an API key.

### Q: Which LLM providers are supported?

A: Currently OpenAI (GPT-3.5, GPT-4) and Mock mode. More providers coming soon.

### Q: How accurate are the metrics?

A: Metrics are validated through empirical studies (500 tasks, 240 human participants). See research papers for details.

### Q: Can I use this for commercial applications?

A: Yes, the open-core version is Apache 2.0 licensed. Enterprise features require commercial license.

### Q: How do I cite this in my research?

A: See [CITATION.bib](../CITATION.bib) for BibTeX entries.

---

<p align="center">
  <b>Happy evaluating! 🚀</b>
</p>
