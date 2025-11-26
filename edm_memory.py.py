# ================================================================
#  open_core/edm_memory.py
#  Minimal Experience-Driven Memory (EDM) for Open-Core RAG Planning
# ================================================================

from dataclasses import dataclass, field
from typing import List, Optional


# ================================================================
# 1. Data Structures
# ================================================================

@dataclass
class ExperienceMetrics:
    """Performance metrics for stored experience."""
    pei: float = 0.0


@dataclass
class Experience:
    """Container for a stored procedural plan and its evaluation."""
    plan: 'Plan'
    metrics: ExperienceMetrics


# ================================================================
# 2. EDM Core
# ================================================================

class EDM:
    """
    Open-source minimal EDM for procedural retrieval in RAG-planning.
    Stores and retrieves past plans based on similarity.
    """

    def __init__(self, storage_threshold: float = 0.75):
        self.storage_threshold = storage_threshold
        self.procedural_memory: List[Experience] = []

    # ------------------------------------------------------------
    # Similarity Function
    # ------------------------------------------------------------
    def calculate_similarity(self, a: str, b: str) -> float:
        """
        Simple bag-of-words Jaccard similarity.
        Used to compare new goal with stored experiences.
        """
        tokens_a = set(a.lower().split())
        tokens_b = set(b.lower().split())

        common = len(tokens_a.intersection(tokens_b))
        total = len(tokens_a.union(tokens_b))

        return common / total if total else 0.0

    # ------------------------------------------------------------
    # Retrieval Function
    # ------------------------------------------------------------
    def retrieve_procedural_guide(self, goal: str) -> Optional[Experience]:
        """
        Return the most similar past experience if similarity >= 0.40.
        Lower threshold increases retrieval likelihood in simulation.
        """
        candidates = []

        for exp in self.procedural_memory:
            sim = self.calculate_similarity(goal, exp.plan.goal)

            # Lowered retrieval threshold for more flexible matching
            if sim >= 0.40:
                candidates.append((exp, sim))

        if not candidates:
            return None

        # Return experience with highest similarity score
        return max(candidates, key=lambda x: x[1])[0]

    # ------------------------------------------------------------
    # Storage Function
    # ------------------------------------------------------------
    def store(self, exp: Experience):
        """
        Store experience only if PEI score meets threshold.
        """
        if exp.metrics.pei >= self.storage_threshold:
            self.procedural_memory.append(exp)
