from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import copy


@dataclass
class Agent:
    """Agent/crew member in the Mars colony."""
    
    name: str
    health: float = 100.0  # 0-100%
    mental_state: float = 80.0  # mental stability 0-100%
    location: str = "habitat"  # habitat, greenhouse, solar_farm, etc.
    
    def __post_init__(self):
        """Validate initial values."""
        self.health = max(0.0, min(100.0, self.health))
        self.mental_state = max(0.0, min(100.0, self.mental_state))
    
    def is_alive(self) -> bool:
        """Check if agent is alive."""
        return self.health > 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "health": self.health,
            "mental_state": self.mental_state,
            "location": self.location,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            health=data.get("health", 100.0),
            mental_state=data.get("mental_state", 80.0),
            location=data.get("location", "habitat"),
        )


@dataclass
class GameState:
    """Complete state of the Mars survival simulation."""
    
    tick: int = 0
    
    # Resource levels (units are abstract)
    resources: Dict[str, float] = field(
        default_factory=lambda: {
            "oxygen": 1000.0,
            "water": 800.0,
            "energy": 500.0,
            "food": 600.0,
        }
    )
    
    # Event log
    logs: List[str] = field(default_factory=list)
    
    # Crew members
    agents: Dict[str, Agent] = field(default_factory=dict)
    
    # Random number generator state for deterministic replay
    rng_state: Optional[Dict[str, Any]] = None
    
    def add_log(self, message: str) -> None:
        """Add a timestamped log entry."""
        self.logs.append(f"[T{self.tick:04d}] {message}")
    
    def get_resource(self, resource_name: str) -> float:
        """Get current level of a resource."""
        return self.resources.get(resource_name, 0.0)
    
    def modify_resource(self, resource_name: str, delta: float) -> None:
        """Modify a resource level with bounds checking."""
        if resource_name not in self.resources:
            self.resources[resource_name] = 0.0
        
        new_value = self.resources[resource_name] + delta
        self.resources[resource_name] = max(0.0, new_value)
        
        # Log critical resource depletion
        if new_value <= 0.0:
            self.add_log(f"CRITICAL: {resource_name} depleted!")
    
    def is_game_over(self) -> bool:
        """Check if game has ended due to critical resource depletion."""
        critical_resources = ["oxygen", "water", "energy", "food"]
        for resource in critical_resources:
            if self.get_resource(resource) <= 0.0:
                return True
        
        # Also check if all agents are dead
        alive_agents = [agent for agent in self.agents.values() if agent.is_alive()]
        if not alive_agents:
            return True
            
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "tick": self.tick,
            "resources": copy.deepcopy(self.resources),
            "logs": copy.deepcopy(self.logs),
            "agents": {name: agent.to_dict() for name, agent in self.agents.items()},
            "rng_state": copy.deepcopy(self.rng_state) if self.rng_state else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create state from dictionary."""
        state = cls(
            tick=data["tick"],
            resources=copy.deepcopy(data["resources"]),
            logs=copy.deepcopy(data["logs"]),
            rng_state=copy.deepcopy(data.get("rng_state")),
        )
        
        # Recreate agents
        for name, agent_data in data.get("agents", {}).items():
            state.agents[name] = Agent.from_dict(agent_data)
        
        return state
    
    @classmethod
    def create_initial_state(cls, crew_names: Optional[List[str]] = None) -> 'GameState':
        """Create initial game state with default crew."""
        if crew_names is None:
            crew_names = ["Commander Chen", "Dr. Rodriguez", "Engineer Tanaka", 
                         "Botanist Schmidt", "Pilot Okafor"]
        
        state = cls()
        
        # Initialize crew
        for name in crew_names:
            state.agents[name] = Agent(name=name)
        
        # Add initial log
        state.add_log("Mission 'Project Red Dust' initialized. Mars colony established.")
        
        return state