import json
from typing import Dict, Any, Optional

class DeterministicRandom:
    """Deterministic random number generator with serializable state.
    
    Uses a Linear Congruential Generator (LCG) for deterministic results.
    State can be serialized to JSON for save/load functionality.
    """
    
    # LCG parameters from glibc (used in rand() function)
    # These produce a period of 2^31
    _MODULUS = 2**31
    _MULTIPLIER = 1103515245
    _INCREMENT = 12345
    
    def __init__(self, seed: int = 42):
        """Initialize with a seed value.
        
        Args:
            seed: Integer seed value
        """
        self._seed = seed % self._MODULUS
        self._initial_seed = self._seed
    
    def next_int(self, min_val: int = 0, max_val: Optional[int] = None) -> int:
        """Generate a random integer.
        
        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive). If None, returns raw LCG output.
        
        Returns:
            Random integer
        """
        # Generate next LCG value
        self._seed = (self._MULTIPLIER * self._seed + self._INCREMENT) % self._MODULUS
        
        if max_val is None:
            return self._seed
        
        # Scale to range [min_val, max_val]
        if max_val < min_val:
            raise ValueError("max_val must be >= min_val")
        
        range_size = max_val - min_val + 1
        return min_val + (self._seed % range_size)
    
    def next_float(self) -> float:
        """Generate a random float in [0.0, 1.0).
        
        Returns:
            Random float
        """
        self._seed = (self._MULTIPLIER * self._seed + self._INCREMENT) % self._MODULUS
        return self._seed / self._MODULUS
    
    def choice(self, seq):
        """Choose a random element from a non-empty sequence.
        
        Args:
            seq: Non-empty sequence
            
        Returns:
            Random element
        """
        if not seq:
            raise ValueError("Sequence must not be empty")
        idx = self.next_int(0, len(seq) - 1)
        return seq[idx]
    
    def get_state(self) -> Dict[str, Any]:
        """Get current generator state for serialization.
        
        Returns:
            Dictionary containing state data
        """
        return {
            "seed": self._seed,
            "initial_seed": self._initial_seed,
            "modulus": self._MODULUS,
            "multiplier": self._MULTIPLIER,
            "increment": self._INCREMENT
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore generator state from serialized data.
        
        Args:
            state: Dictionary containing state data
        """
        self._seed = state["seed"]
        self._initial_seed = state["initial_seed"]
        # Note: LCG parameters are read-only, but we verify consistency
        if state.get("modulus") != self._MODULUS:
            raise ValueError("Incompatible modulus in saved state")
        if state.get("multiplier") != self._MULTIPLIER:
            raise ValueError("Incompatible multiplier in saved state")
        if state.get("increment") != self._INCREMENT:
            raise ValueError("Incompatible increment in saved state")
    
    def to_json(self) -> str:
        """Serialize state to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.get_state())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DeterministicRandom':
        """Create instance from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            DeterministicRandom instance
        """
        state = json.loads(json_str)
        instance = cls(seed=state["initial_seed"])
        instance.set_state(state)
        return instance
    
    def reset(self) -> None:
        """Reset generator to initial seed state."""
        self._seed = self._initial_seed
    
    def __repr__(self) -> str:
        return f"DeterministicRandom(seed={self._initial_seed}, current={self._seed})"