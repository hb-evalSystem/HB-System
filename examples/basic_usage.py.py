"""
Basic Usage Examples for HB-Eval System
Demonstrates common usage patterns and features.
"""

from hb_eval import EDM, AdaptPlan, AgentLoop, Experience, ExperienceMetrics, Plan
from hb_eval.core.external_llm_api import LLMConfig, LLMProvider, set_global_config


def example_1_basic_agent():
    """Example 1: Basic agent execution."""
    print("\n" + "="*60)
    print("Example 1: Basic Agent Execution")
    print("="*60)
    
    # Setup (mock mode for demonstration)
    set_global_config(LLMConfig(provider=LLMProvider.MOCK))
    
    # Initialize components
    edm = EDM()
    planner = AdaptPlan()
    agent = AgentLoop(edm, planner, enable_verbose=True)
    
    # Execute a simple goal
    result = agent.run("Analyze system performance")
    print(f"\nResult: {result}")


def example_2_with_memory():
    """Example 2: Using memory-based retrieval."""
    print("\n" + "="*60)
    print("Example 2: Memory-Based Retrieval")
    print("="*60)
    
    # Setup
    set_global_config(LLMConfig(provider=LLMProvider.MOCK))
    edm = EDM()
    planner = AdaptPlan()
    agent = AgentLoop(edm, planner, enable_verbose=False)
    
    # Store a high-quality experience
    plan = Plan(
        goal="Optimize Database Performance",
        sub_goals=[
            "Analyze query patterns",
            "Identify bottlenecks",
            "Apply optimizations",
            "Validate improvements"
        ]
    )
    exp = Experience(plan=plan, metrics=ExperienceMetrics(pei=0.92))
    edm.store(exp)
    print(f"✓ Stored experience: '{plan.goal}' (PEI: 0.92)")
    
    # Execute similar goal (should retrieve from memory)
    print("\nExecuting similar goal...")
    result = agent.run("Optimize Database", store_experience=False)
    print(f"Result: {result[:100]}...")


def example_3_custom_config():
    """Example 3: Custom configuration."""
    print("\n" + "="*60)
    print("Example 3: Custom Configuration")
    print("="*60)
    
    # Custom EDM configuration
    edm = EDM(
        storage_threshold=0.80,    # Higher quality threshold
        retrieval_threshold=0.50,   # Stricter similarity
        max_memory_size=500         # Limit memory size
    )
    
    # Custom planner
    planner = AdaptPlan(enable_verbose=True)
    
    # Custom agent with callback
    def step_callback(state, step, output):
        """Called after each step."""
        print(f"  Callback: Step {state.step_index} completed")
    
    agent = AgentLoop(
        edm, 
        planner,
        max_recovery_attempts=5,
        enable_verbose=True,
        step_callback=step_callback
    )
    
    print("\n✓ Configured custom components")
    print(f"  EDM: threshold={edm.storage_threshold}, max_size={edm.max_memory_size}")
    print(f"  Agent: max_retries={agent.max_recovery_attempts}")


def example_4_metrics_tracking():
    """Example 4: Tracking execution metrics."""
    print("\n" + "="*60)
    print("Example 4: Metrics Tracking")
    print("="*60)
    
    set_global_config(LLMConfig(provider=LLMProvider.MOCK))
    
    edm = EDM()
    planner = AdaptPlan()
    agent = AgentLoop(edm, planner, enable_verbose=False)
    
    # Execute and track
    print("\nExecuting goal...")
    result = agent.run("Complete complex task", store_experience=True)
    
    # Check stored experiences
    print(f"\nMemory Statistics:")
    print(f"  Total experiences: {edm.get_memory_size()}")
    
    if edm.get_memory_size() > 0:
        top_exp = edm.get_top_experiences(n=1)[0]
        print(f"  Top experience PEI: {top_exp.metrics.pei:.2f}")
        print(f"  Top experience goal: '{top_exp.plan.goal}'")


def example_5_real_llm_integration():
    """Example 5: Real LLM API integration (requires API key)."""
    print("\n" + "="*60)
    print("Example 5: Real LLM Integration")
    print("="*60)
    
    import os
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    
    if not api_key:
        print("\n⚠️  No API key found. This example requires:")
        print("   export OPENAI_API_KEY='your-key'")
        print("\nSkipping real API example (use mock mode instead)")
        return
    
    # Configure for real OpenAI API
    config = LLMConfig(
        provider=LLMProvider.OPENAI,
        api_key=api_key,
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=200
    )
    set_global_config(config)
    
    print("✓ Configured for OpenAI API")
    
    # Initialize and run
    edm = EDM()
    planner = AdaptPlan()
    agent = AgentLoop(edm, planner, enable_verbose=True)
    
    print("\nExecuting with real LLM...")
    result = agent.run("Summarize the benefits of automated testing")
    print(f"\nLLM Result: {result}")


def example_6_plan_management():
    """Example 6: Manual plan creation and management."""
    print("\n" + "="*60)
    print("Example 6: Plan Management")
    print("="*60)
    
    # Create a custom plan
    plan = Plan(
        goal="Deploy New Feature",
        sub_goals=[
            "Run tests",
            "Build package",
            "Deploy to staging",
            "Validate deployment",
            "Deploy to production"
        ],
        l_min=5,
        metadata={"priority": "high", "team": "backend"}
    )
    
    print(f"Created plan: '{plan.goal}'")
    print(f"  Steps: {len(plan.sub_goals)}")
    print(f"  Metadata: {plan.metadata}")
    
    # Simulate execution
    print("\nSimulating execution:")
    for i, step in enumerate(plan.sub_goals, 1):
        plan.add_step(step)
        print(f"  [{i}/{len(plan.sub_goals)}] {step} - Done")
        print(f"      Progress: {plan.get_progress()*100:.0f}%")
    
    print(f"\n✓ Plan completed: {plan.is_complete()}")


def main():
    """Run all examples."""
    examples = [
        ("Basic Agent", example_1_basic_agent),
        ("Memory Retrieval", example_2_with_memory),
        ("Custom Config", example_3_custom_config),
        ("Metrics Tracking", example_4_metrics_tracking),
        ("Real LLM", example_5_real_llm_integration),
        ("Plan Management", example_6_plan_management),
    ]
    
    print("\n" + "="*60)
    print("HB-Eval System - Usage Examples")
    print("="*60)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nChoose an example (1-6) or 'all' to run all:")
    choice = input("> ").strip()
    
    if choice.lower() == 'all':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("Invalid choice")
        except (ValueError, IndexError):
            print("Invalid input")


if __name__ == "__main__":
    main()