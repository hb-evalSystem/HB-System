"""
HB-Eval System: Semantic EDM (Episodic-Dense Memory)
=====================================================

Open-Core implementation with lightweight semantic similarity.
Premium features (hierarchical memory, custom embeddings, vector DB) available separately.

Strategic Design:
- Open-Core: GOOD quality (proves the concept works)
- Premium: GREAT quality (optimized for production scale)

Author: HB-Eval System Team
Version: 2.0.0 (Open-Core with Semantic)
License: Apache 2.0
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import warnings
import json
from pathlib import Path

# Graceful import with fallback
try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    warnings.warn(
        "sentence-transformers not installed. Install with: "
        "pip install sentence-transformers\n"
        "Falling back to Jaccard similarity (keyword mode).",
        ImportWarning
    )

try:
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    warnings.warn("scikit-learn not installed. Some features may be limited.", ImportWarning)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ExperienceMetrics:
    """
    Metrics associated with an experience (0-100 scale).
    """
    pei_score: float
    frr_score: float = 0.0
    ti_score: float = 0.0
    success: bool = True
    execution_time: float = 0.0
    
    def __post_init__(self):
        """Validate metrics are in valid ranges"""
        if not 0 <= self.pei_score <= 100:
            raise ValueError(f"PEI score must be 0-100, got {self.pei_score}")
        if not 0 <= self.frr_score <= 100:
            raise ValueError(f"FRR score must be 0-100, got {self.frr_score}")
        if not 0 <= self.ti_score <= 100:
            raise ValueError(f"TI score must be 0-100, got {self.ti_score}")


@dataclass
class Experience:
    """
    A stored experience in EDM.
    """
    task: str
    plan: List[Dict[str, Any]]
    result: str
    metrics: ExperienceMetrics
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    embedding: Optional[np.ndarray] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "task": self.task,
            "plan": self.plan,
            "result": self.result,
            "metrics": {
                "pei_score": self.metrics.pei_score,
                "frr_score": self.metrics.frr_score,
                "ti_score": self.metrics.ti_score,
                "success": self.metrics.success,
                "execution_time": self.metrics.execution_time
            },
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


# =============================================================================
# Semantic EDM Implementation (Open-Core)
# =============================================================================

class EDMMemory:
    """
    Episodic-Dense Memory with Performance-Weighted Retrieval.
    
    Open-Core Features:
    - ✅ Semantic similarity (all-MiniLM-L6-v2, 80MB model)
    - ✅ PEI-guided selective storage
    - ✅ Performance-weighted retrieval
    - ✅ Local file storage (JSON)
    - ✅ Up to 10k episodes
    
    Premium Features (Not included):
    - ⭐ Custom fine-tuned embeddings (domain-specific)
    - ⭐ Hierarchical memory (multi-level abstraction)
    - ⭐ Vector database integration (Pinecone, Weaviate)
    - ⭐ Sub-10ms retrieval for 100k+ episodes
    - ⭐ Automatic bias mitigation dashboards
    - ⭐ Enterprise support & SLA
    
    Learn more: https://hbeval.org/premium
    """
    
    def __init__(
        self,
        use_semantic: bool = True,
        model_name: str = "all-MiniLM-L6-v2",
        cache_embeddings: bool = True,
        max_episodes: int = 10000,
        storage_threshold: float = 80.0,
        device: str = "cpu"
    ):
        """
        Initialize EDM Memory System.
        
        Args:
            use_semantic: Use semantic similarity (True) or Jaccard (False)
            model_name: Sentence-Transformer model (default: lightweight 80MB)
            cache_embeddings: Cache computed embeddings for speed
            max_episodes: Maximum episodes to store (0 = unlimited, but not recommended)
            storage_threshold: Minimum PEI score to store (0-100)
            device: 'cpu' or 'cuda' for GPU acceleration
        
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If semantic model fails to load
        """
        if max_episodes < 0:
            raise ValueError(f"max_episodes must be >= 0, got {max_episodes}")
        if not 0 <= storage_threshold <= 100:
            raise ValueError(f"storage_threshold must be 0-100, got {storage_threshold}")
        
        self.episodes: List[Experience] = []
        self.use_semantic = use_semantic and SEMANTIC_AVAILABLE
        self.model = None
        self.cache_embeddings = cache_embeddings
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.max_episodes = max_episodes
        self.storage_threshold = storage_threshold
        
        # Initialize semantic model if requested and available
        if self.use_semantic:
            try:
                print(f"🔄 Loading semantic model: {model_name}...")
                self.model = SentenceTransformer(model_name, device=device)
                print(f"✅ Semantic mode enabled (device: {device})")
            except Exception as e:
                warnings.warn(
                    f"Failed to load semantic model: {e}\n"
                    f"Falling back to Jaccard similarity (keyword mode).",
                    RuntimeWarning
                )
                self.use_semantic = False
        
        if not self.use_semantic:
            print(f"⚠️  Running in Keyword Mode (Jaccard similarity)")
            print(f"   For semantic understanding, install: pip install sentence-transformers")
        
        print(f"📊 Storage PEI Threshold: {self.storage_threshold:.1f}%")
        print(f"💾 Max Episodes: {self.max_episodes if self.max_episodes > 0 else 'Unlimited'}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get or compute embedding for text.
        
        Args:
            text: Input text to embed
        
        Returns:
            Embedding vector (normalized)
        
        Note:
            If semantic mode is disabled, returns None
        """
        if not self.use_semantic:
            return None
        
        # Check cache first
        if self.cache_embeddings and text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # Compute embedding
        try:
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            # Cache if enabled
            if self.cache_embeddings:
                # Simple cache size management
                if len(self.embedding_cache) >= 1000:
                    # Remove oldest (first inserted)
                    self.embedding_cache.pop(next(iter(self.embedding_cache)))
                self.embedding_cache[text] = embedding
            
            return embedding
        
        except Exception as e:
            warnings.warn(f"Failed to compute embedding: {e}", RuntimeWarning)
            return None
    
    def calculate_similarity(
        self,
        text_a: str,
        text_b: str,
        method: str = "auto"
    ) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text_a: First text
            text_b: Second text
            method: 'auto' (semantic if available, else Jaccard),
                   'semantic' (force semantic, error if unavailable),
                   'keyword' (force Jaccard)
        
        Returns:
            Similarity score [0.0-1.0]
        
        Examples:
            >>> edm = EDMMemory(use_semantic=True)
            >>> # Semantic mode handles paraphrases
            >>> edm.calculate_similarity(
            ...     "navigate to kitchen",
            ...     "go to cooking area"
            ... )
            0.847
            
            >>> # Keyword mode (Jaccard) only matches words
            >>> edm_keyword = EDMMemory(use_semantic=False)
            >>> edm_keyword.calculate_similarity(
            ...     "navigate to kitchen",
            ...     "go to cooking area"
            ... )
            0.0  # No shared words
        """
        # Determine actual method
        if method == "auto":
            actual_method = "semantic" if self.use_semantic else "keyword"
        elif method == "semantic" and not self.use_semantic:
            raise RuntimeError(
                "Semantic similarity requested but not available. "
                "Install sentence-transformers or use method='keyword'"
            )
        else:
            actual_method = method
        
        # Semantic similarity
        if actual_method == "semantic":
            emb_a = self._get_embedding(text_a)
            emb_b = self._get_embedding(text_b)
            
            if emb_a is None or emb_b is None:
                warnings.warn("Embedding failed, falling back to Jaccard", RuntimeWarning)
                actual_method = "keyword"
            else:
                # Cosine similarity (already normalized, so dot product)
                similarity = float(np.dot(emb_a, emb_b))
                return max(0.0, min(1.0, similarity))
        
        # Jaccard similarity (keyword matching)
        if actual_method == "keyword":
            words_a = set(text_a.lower().split())
            words_b = set(text_b.lower().split())
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'is', 'of', 'in', 'and', 'for', 'to', 'with'}
            words_a = words_a - stop_words
            words_b = words_b - stop_words
            
            if not words_a or not words_b:
                return 0.0
            
            intersection = len(words_a.intersection(words_b))
            union = len(words_a | words_b)
            
            return intersection / union if union > 0 else 0.0
        
        raise ValueError(f"Invalid method: {method}")
    
    def store_episode(
        self,
        task: str,
        plan: List[Dict[str, Any]],
        result: str,
        metrics: ExperienceMetrics,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        compute_embedding: bool = True
    ) -> Optional[Experience]:
        """
        Store a new experience in memory (Selective Storage based on PEI).
        
        This implements the 'Meta-Learning Filter' - only high-quality
        experiences (PEI >= storage_threshold) are stored.
        
        Args:
            task: Task description
            plan: Executed plan (list of actions)
            result: Outcome description
            metrics: Performance metrics (must include pei_score)
            context: Additional contextual information
            tags: Tags for categorization
            compute_embedding: Whether to compute embedding (if semantic mode enabled)
        
        Returns:
            Stored Experience object, or None if rejected (below threshold)
        
        Example:
            >>> edm = EDMMemory(storage_threshold=80.0)
            >>> exp = edm.store_episode(
            ...     task="Optimize database query",
            ...     plan=[{"step": 1, "action": "add_index"}],
            ...     result="Success: 50% speedup",
            ...     metrics=ExperienceMetrics(pei_score=92.0, success=True)
            ... )
            📚 Stored: 'Optimize database query' ✅ (PEI: 92.0%)
        """
        # Check Selective Storage Threshold
        if metrics.pei_score < self.storage_threshold:
            print(f"🗑️  Rejected: PEI {metrics.pei_score:.1f}% < threshold {self.storage_threshold:.1f}%")
            return None
        
        # Compute embedding if semantic mode enabled
        embedding = None
        if self.use_semantic and compute_embedding:
            embedding = self._get_embedding(task)
        
        # Create experience
        experience = Experience(
            task=task,
            plan=plan,
            result=result,
            metrics=metrics,
            context=context or {},
            tags=tags or [],
            timestamp=datetime.now(),
            embedding=embedding
        )
        
        # Add to episodes
        self.episodes.append(experience)
        
        # Evict oldest if max exceeded
        if self.max_episodes > 0 and len(self.episodes) > self.max_episodes:
            removed = self.episodes.pop(0)
            print(f"⚠️  Max episodes ({self.max_episodes}) exceeded. "
                  f"Removed oldest: '{removed.task[:50]}...'")
        
        # Log storage
        pei = metrics.pei_score
        success_icon = "✅" if metrics.success else "❌"
        print(f"📚 Stored: '{task[:60]}...' {success_icon} (PEI: {pei:.1f}%)")
        
        return experience
    
    def retrieve_similar(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.3,
        min_pei: float = 0.0,
        context_filter: Optional[Dict[str, Any]] = None,
        tags_filter: Optional[List[str]] = None,
        max_age_days: Optional[int] = None,
        similarity_method: str = "auto"
    ) -> List[Tuple[Experience, float, float, float]]:
        """
        Retrieve similar experiences (Performance-Weighted Retrieval).
        
        Ranking formula: combined_score = similarity * (pei_score / 100)
        This prioritizes both relevance AND quality.
        
        Args:
            query: Query text to match against stored tasks
            top_k: Maximum number of results to return
            min_similarity: Minimum similarity score [0.0-1.0]
            min_pei: Minimum PEI score [0-100]
            context_filter: Filter by context values (e.g., {"environment": "AlfWorld"})
            tags_filter: Filter by tags (any match)
            max_age_days: Filter by age (e.g., only experiences from last 30 days)
            similarity_method: 'auto', 'semantic', or 'keyword'
        
        Returns:
            List of tuples: (experience, similarity, pei_normalized, combined_score)
            Sorted by combined_score (descending)
        
        Example:
            >>> results = edm.retrieve_similar(
            ...     "database performance",
            ...     top_k=3,
            ...     min_pei=80.0
            ... )
            🔍 Found 2 experiences (Semantic mode)
            >>> for exp, sim, pei, score in results:
            ...     print(f"{exp.task[:40]}... sim={sim:.2f} pei={pei:.2f}")
        """
        # Validation
        if top_k <= 0:
            raise ValueError(f"top_k must be > 0, got {top_k}")
        if not 0 <= min_similarity <= 1:
            raise ValueError(f"min_similarity must be 0-1, got {min_similarity}")
        if not 0 <= min_pei <= 100:
            raise ValueError(f"min_pei must be 0-100, got {min_pei}")
        
        if not self.episodes:
            return []
        
        scored_episodes = []
        now = datetime.now()
        
        for episode in self.episodes:
            # Apply filters
            is_valid = True
            
            # Context filter
            if context_filter:
                is_valid = all(
                    episode.context.get(k) == v
                    for k, v in context_filter.items()
                )
            if not is_valid:
                continue
            
            # Tags filter
            if tags_filter and not any(tag in episode.tags for tag in tags_filter):
                continue
            
            # Age filter
            if max_age_days is not None:
                age_days = (now - episode.timestamp).days
                if age_days > max_age_days:
                    continue
            
            # PEI filter
            if episode.metrics.pei_score < min_pei:
                continue
            
            # Calculate similarity
            similarity = self.calculate_similarity(
                query,
                episode.task,
                method=similarity_method
            )
            
            # Similarity threshold
            if similarity < min_similarity:
                continue
            
            # Calculate combined score (relevance * quality)
            normalized_pei = episode.metrics.pei_score / 100.0
            combined_score = similarity * normalized_pei
            
            scored_episodes.append((episode, similarity, normalized_pei, combined_score))
        
        # Sort by combined score
        scored_episodes.sort(key=lambda x: x[3], reverse=True)
        results = scored_episodes[:top_k]
        
        # Log retrieval
        if results:
            mode = "Semantic" if self.use_semantic else "Keyword"
            print(f"🔍 Found {len(results)} experiences (Mode: {mode})")
        
        return results
    
    def save(self, filepath: str) -> None:
        """
        Save memory to disk (JSON format).
        
        Note: Embeddings are NOT saved (recomputed on load if needed)
        """
        filepath = Path(filepath)
        data = {
            "version": "2.0.0-opencore",
            "use_semantic": self.use_semantic,
            "storage_threshold": self.storage_threshold,
            "max_episodes": self.max_episodes,
            "episodes": [exp.to_dict() for exp in self.episodes]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved {len(self.episodes)} episodes to {filepath}")
    
    def load(self, filepath: str, recompute_embeddings: bool = True) -> None:
        """
        Load memory from disk.
        
        Args:
            filepath: Path to saved memory file
            recompute_embeddings: Whether to recompute embeddings (if semantic mode enabled)
        """
        filepath = Path(filepath)
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.episodes = []
        for exp_data in data["episodes"]:
            metrics = ExperienceMetrics(**exp_data["metrics"])
            exp = Experience(
                task=exp_data["task"],
                plan=exp_data["plan"],
                result=exp_data["result"],
                metrics=metrics,
                context=exp_data["context"],
                timestamp=datetime.fromisoformat(exp_data["timestamp"]),
                tags=exp_data["tags"]
            )
            
            # Recompute embedding if semantic mode enabled
            if self.use_semantic and recompute_embeddings:
                exp.embedding = self._get_embedding(exp.task)
            
            self.episodes.append(exp)
        
        print(f"📂 Loaded {len(self.episodes)} episodes from {filepath}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with statistics about stored episodes
        """
        if not self.episodes:
            return {
                "total_episodes": 0,
                "avg_pei": 0.0,
                "success_rate": 0.0,
                "semantic_mode": self.use_semantic
            }
        
        pei_scores = [exp.metrics.pei_score for exp in self.episodes]
        successes = sum(1 for exp in self.episodes if exp.metrics.success)
        
        return {
            "total_episodes": len(self.episodes),
            "avg_pei": float(np.mean(pei_scores)),
            "min_pei": float(np.min(pei_scores)),
            "max_pei": float(np.max(pei_scores)),
            "std_pei": float(np.std(pei_scores)),
            "success_rate": successes / len(self.episodes),
            "oldest_episode": min(exp.timestamp for exp in self.episodes),
            "newest_episode": max(exp.timestamp for exp in self.episodes),
            "semantic_mode": self.use_semantic,
            "cache_size": len(self.embedding_cache) if self.use_semantic else 0
        }
    
    def clear(self) -> None:
        """Clear all stored episodes and cache"""
        self.episodes = []
        self.embedding_cache = {}
        print("🗑️  Memory cleared")


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("HB-Eval EDM Memory - Open-Core Demo")
    print("="*70 + "\n")
    
    # Initialize (will use semantic if available, else Jaccard)
    memory = EDMMemory(use_semantic=True, storage_threshold=80.0)
    
    # Store high-quality experience (PEI >= 80.0)
    exp1 = memory.store_episode(
        task="Optimize database query speed",
        plan=[{"step": 1, "action": "analyze_queries"}, {"step": 2, "action": "add_index"}],
        result="Success: 50% speedup achieved",
        metrics=ExperienceMetrics(pei_score=92.0, success=True, execution_time=120.5),
        tags=["performance", "database"]
    )
    
    # Store another high-quality experience
    exp2 = memory.store_episode(
        task="Improve database performance with caching",
        plan=[{"step": 1, "action": "implement_redis"}],
        result="Success: 70% speedup",
        metrics=ExperienceMetrics(pei_score=95.0, success=True, execution_time=90.0),
        tags=["performance", "caching"]
    )
    
    # Try to store low-quality experience (will be rejected)
    exp3 = memory.store_episode(
        task="Optimize database query speed",
        plan=[{"step": 1, "action": "just_wait"}],
        result="Failure: 10% slowdown",
        metrics=ExperienceMetrics(pei_score=75.0, success=False),
        tags=["failure"]
    )
    
    print("\n" + "-"*70)
    
    # Retrieval (performance-weighted)
    similar = memory.retrieve_similar(
        "Database optimization speedup techniques",
        top_k=3,
        min_pei=90.0
    )
    
    print("\n📋 Retrieved Experiences:")
    for i, (exp, sim, pei, score) in enumerate(similar, 1):
        print(f"\n{i}. Task: {exp.task}")
        print(f"   Similarity: {sim:.3f}")
        print(f"   PEI: {pei*100:.1f}%")
        print(f"   Combined Score: {score:.3f}")
        print(f"   Result: {exp.result}")
    
    # Statistics
    print("\n" + "="*70)
    print("📊 Memory Statistics:")
    stats = memory.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n" + "="*70)
    print("✅ Demo completed!")
    print("="*70 + "\n")