# ================================================================
#  open_core/demo.py
#  Main execution demo for Open-Core Agent System
# ================================================================

from edm_memory import EDM, Experience, ExperienceMetrics
from adapt_planner import AdaptPlan, Plan
from agent_loop import AgentLoop


# ================================================================
# 1. Seed an initial experience for retrieval tests
# ================================================================

initial_plan = Plan(
    goal="Optimize General Operations",
    sub_goals=[
        "S_1: Data Collection",
        "S_2: Algorithm Run"
    ],
    l_min=5
)

# Experience with high PEI score (stored in EDM)
seed_experience = Experience(
    plan=initial_plan,
    metrics=ExperienceMetrics(pei=0.95)
)

# Initialize EDM memory and store the experience
edm = EDM()
edm.store(seed_experience)

# Initialize planning and agent loop system
planner = AdaptPlan()
agent = AgentLoop(edm, planner)


# ================================================================
# 2. Demo 1 — Retrieve stored plan
# ================================================================

print(">>> Running Demo 1: Goal Similar to Stored Experience")

# Should retrieve the stored 2-step plan
demo1_result = agent.run("Optimize General Operations")
# print(f"Final Result 1: {demo1_result}")


print("\n" + "=" * 50 + "\n")


# ================================================================
# 3. Demo 2 — Generate new plan (no matching experience)
# ================================================================

print(">>> Running Demo 2: Goal Requires New Plan")

agent2 = AgentLoop(edm, planner)

# Should generate a new 3-step procedural template plan
demo2_result = agent2.run("Improve Inventory Management Efficiency")
# print(f"Final Result 2: {demo2_result}")
