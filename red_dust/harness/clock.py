import json
from typing import Dict, Any

class VirtualClock:
    """Virtual clock for simulation time tracking.
    
    Replaces real system time with discrete ticks for deterministic simulation.
    """
    
    def __init__(self, initial_tick: int = 0):
        """Initialize virtual clock.
        
        Args:
            initial_tick: Starting tick value
        """
        self._current_tick = initial_tick
        self._initial_tick = initial_tick
    
    def step(self, steps: int = 1) -> None:
        """Advance the clock by specified number of ticks.
        
        Args:
            steps: Number of ticks to advance (must be >= 0)
        """
        if steps < 0:
            raise ValueError("Steps must be non-negative")
        self._current_tick += steps
    
    def reset(self) -> None:
        """Reset clock to initial tick value."""
        self._current_tick = self._initial_tick
    
    @property
    def tick(self) -> int:
        """Get current tick value.
        
        Returns:
            Current tick
        """
        return self._current_tick
    
    def get_state(self) -> Dict[str, Any]:
        """Get current clock state for serialization.
        
        Returns:
            Dictionary containing state data
        """
        return {
            "current_tick": self._current_tick,
            "initial_tick": self._initial_tick
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore clock state from serialized data.
        
        Args:
            state: Dictionary containing state data
        """
        self._current_tick = state["current_tick"]
        self._initial_tick = state["initial_tick"]
    
    def to_json(self) -> str:
        """Serialize state to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.get_state())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'VirtualClock':
        """Create instance from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            VirtualClock instance
        """
        state = json.loads(json_str)
        instance = cls(initial_tick=state["initial_tick"])
        instance.set_state(state)
        return instance
    
    def __repr__(self) -> str:
        return f"VirtualClock(tick={self._current_tick}, initial={self._initial_tick})"