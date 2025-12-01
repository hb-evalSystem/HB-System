"""
HB-Eval System Demo
Interactive demonstration of the Open-Core system capabilities.

This script demonstrates:
1. Memory-based plan retrieval
2. New plan generation
3. Execution with metrics
4. Failure recovery (optional)
"""

from hb_eval.core.edm_memory import EDM, Experience, ExperienceMetrics
from hb_eval.core.adapt_planner import AdaptPlan, Plan
from hb_eval.core.agent_loop import AgentLoop
from hb_eval.core.external_llm_api import LLMConfig, LLMProvider, set_global_config


def setup_demo_environment():
    """Initialize demo environment with sample data."""
    print("\n" + "="*70)
    print("🧠 HB-Eval System™ — Open-Core Edition")
    print("   The Leading Behavioral Evaluation & Trustworthy Agentic AI Framework")
    print("="*70)
    
    # Configure LLM (mock mode for demo)
    print("\n[SETUP] Configuring LLM interface...")
    config = LLMConfig(provider=LLMProvider.MOCK)
    set_global_config(config)
    print("✓ LLM configured (MOCK mode for demo)")
    
    # Initialize components
    print("\n[SETUP] Initializing core components...")
    edm = EDM(storage_threshold=0.75, retrieval_threshold=0.40)
    planner = AdaptPlan(enable_verbose=True)
    agent = AgentLoop(edm, planner, enable_verbose=True)
    print("✓ EDM, AdaptPlan, and AgentLoop initialized")
    
    return edm, planner, agent


def seed_initial_experience(edm: EDM):
    """Seed EDM with an initial high-quality experience."""
    print("\n[SETUP] Seeding initial experience in EDM...")
    
    initial_plan = Plan(
        goal="Optimize General Operations",
        sub_goals=[
            "Analyze current operational metrics",
            "Identify optimization opportunities",
            "Execute optimization algorithms",
            "Validate improvements"
        ],
        l_min=4,
        metadata={"source": "seed", "quality": "high"}
    )
    
    seed_experience = Experience(
        plan=initial_plan,
        metrics=ExperienceMetrics(pei=0.95, frr=1.0, ti=1.0)
    )
    
    edm.store(seed_experience)
    print(f"✓ Seeded 1 high-quality experience (PEI: 0.95)")
    print(f"  Goal: '{initial_plan.goal}'")


def demo_1_retrieval(agent: AgentLoop):
    """Demo 1: Retrieve and execute a similar stored plan."""
    print("\n" + "="*70)
    print("📋 DEMO 1: Memory-Based Plan Retrieval")
    print("="*70)
    print("\nGoal: 'Optimize General Operations'")
    print("Expected: Should retrieve the stored 4-step plan from EDM\n")
    
    input("Press Enter to start Demo 1...")
    
    result = agent.run("Optimize General Operations", store_experience=True)
    
    print(f"\n✓ Demo 1 Complete")
    print(f"Final Output: {result[:100]}...")


def demo_2_generation(agent: AgentLoop):
    """Demo 2: Generate new plan for unseen goal."""
    print("\n" + "="*70)
    print("🆕 DEMO 2: New Plan Generation")
    print("="*70)
    print("\nGoal: 'Improve Inventory Management Efficiency'")
    print("Expected: Should generate a new 4-step plan (no matching memory)\n")
    
    input("Press Enter to start Demo 2...")
    
    result = agent.run("Improve Inventory Management Efficiency", store_experience=True)
    
    print(f"\n✓ Demo 2 Complete")
    print(f"Final Output: {result[:100]}...")


def demo_3_memory_stats(edm: EDM):
    """Demo 3: Show memory statistics."""
    print("\n" + "="*70)
    print("📊 DEMO 3: Memory Statistics")
    print("="*70)
    
    print(f"\nTotal Experiences Stored: {edm.get_memory_size()}")
    print(f"\nTop Experiences by PEI:")
    
    top_exp = edm.get_top_experiences(n=5)
    for i, exp in enumerate(top_exp, 1):
        print(f"  {i}. Goal: '{exp.plan.goal}'")
        print(f"     PEI: {exp.metrics.pei:.2f} | FRR: {exp.metrics.frr:.2f} | Steps: {len(exp.plan.sub_goals)}")


def interactive_mode(agent: AgentLoop, edm: EDM):
    """Interactive mode for custom goal testing."""
    print("\n" + "="*70)
    print("🎮 INTERACTIVE MODE")
    print("="*70)
    print("\nEnter your own goals to test the system!")
    print("Type 'quit' to exit, 'stats' to see memory statistics\n")
    
    while True:
        try:
            goal = input("\nEnter goal (or 'quit'/'stats'): ").strip()
            
            if goal.lower() == 'quit':
                print("\n👋 Exiting interactive mode...")
                break
            
            if goal.lower() == 'stats':
                demo_3_memory_stats(edm)
                continue
            
            if not goal:
                print("⚠️  Please enter a valid goal")
                continue
            
            print(f"\n{'─'*70}")
            result = agent.run(goal, store_experience=True)
            print(f"{'─'*70}")
            print(f"\n✓ Execution complete!")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def run_demo():
    """Main demo execution function."""
    try:
        # Setup
        edm, planner, agent = setup_demo_environment()
        seed_initial_experience(edm)
        
        # Run demos
        demo_1_retrieval(agent)
        demo_2_generation(agent)
        demo_3_memory_stats(edm)
        
        # Interactive mode
        print("\n" + "="*70)
        choice = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
        if choice == 'y':
            interactive_mode(agent, edm)
        
        # Final summary
        print("\n" + "="*70)
        print("🎉 Demo Complete!")
        print("="*70)
        print("\nWhat you've seen:")
        print("  ✓ Memory-based plan retrieval (EDM)")
        print("  ✓ Adaptive plan generation")
        print("  ✓ Step-by-step execution with metrics")
        print("  ✓ Experience storage and ranking")
        print("\nNext steps:")
        print("  • Read the documentation: README.md")
        print("  • Explore the research papers: papers/")
        print("  • Check out the API: import hb_eval")
        print("  • Configure real LLM: set LLM_API_KEY environment variable")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise


# CLI entry point
if __name__ == "__main__":
    run_demo()