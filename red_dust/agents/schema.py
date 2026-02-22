from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import copy


@dataclass
class AgentAction:
    """Action that an agent can take in the simulation."""
    
    # Action types
    WORK = "work"
    REST = "rest"
    SABOTAGE = "sabotage"
    TALK = "talk"
    REPAIR = "repair"
    RESEARCH = "research"
    EAT = "eat"
    
    # Valid targets
    VALID_TARGETS = {
        "greenhouse", "solar_panel", "oxygen_generator", "water_recycler",
        "habitat", "commander", "engineer", "doctor", "biologist", "spy",
        "storage", "laboratory", "communication", "rover"
    }
    
    type: str
    target: str
    argument: str = ""
    
    def __post_init__(self):
        """Validate action."""
        valid_types = {self.WORK, self.REST, self.SABOTAGE, self.TALK, 
                      self.REPAIR, self.RESEARCH, self.EAT}
        if self.type not in valid_types:
            raise ValueError(f"Invalid action type: {self.type}")
        
        if self.target not in self.VALID_TARGETS:
            # Allow custom targets but warn
            print(f"Warning: Unusual target '{self.target}' for action {self.type}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "target": self.target,
            "argument": self.argument,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentAction':
        """Create from dictionary."""
        return cls(
            type=data["type"],
            target=data["target"],
            argument=data.get("argument", ""),
        )
    
    def __str__(self) -> str:
        if self.argument:
            return f"{self.type} on {self.target}: {self.argument}"
        return f"{self.type} on {self.target}"


@dataclass
class Persona:
    """Personality and role definition for an agent."""
    
    name: str
    role: str
    personality: str  # Personality description
    secret_goal: str  # Hidden objective
    
    # Behavioral tendencies (0.0-1.0)
    cooperation: float = 0.5
    aggression: float = 0.5
    self_preservation: float = 0.5
    curiosity: float = 0.5
    
    # Role-specific capabilities
    skills: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default skills based on role."""
        if not self.skills:
            # Default skills based on role
            role_skills = {
                "Commander": {"leadership": 0.9, "engineering": 0.4, "medical": 0.3},
                "Engineer": {"engineering": 0.9, "maintenance": 0.8, "problem_solving": 0.7},
                "Doctor": {"medical": 0.9, "empathy": 0.8, "psychology": 0.6},
                "Biologist": {"botany": 0.9, "research": 0.7, "chemistry": 0.6},
                "Spy": {"stealth": 0.9, "sabotage": 0.8, "persuasion": 0.7},
            }
            
            for role_pattern, default_skills in role_skills.items():
                if role_pattern.lower() in self.role.lower():
                    self.skills = default_skills.copy()
                    break
            
            # If no match, use generic skills
            if not self.skills:
                self.skills = {"generic": 0.5}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "personality": self.personality,
            "secret_goal": self.secret_goal,
            "cooperation": self.cooperation,
            "aggression": self.aggression,
            "self_preservation": self.self_preservation,
            "curiosity": self.curiosity,
            "skills": copy.deepcopy(self.skills),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Persona':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            role=data["role"],
            personality=data["personality"],
            secret_goal=data["secret_goal"],
            cooperation=data.get("cooperation", 0.5),
            aggression=data.get("aggression", 0.5),
            self_preservation=data.get("self_preservation", 0.5),
            curiosity=data.get("curiosity", 0.5),
            skills=data.get("skills", {}),
        )
    
    def get_action_preferences(self) -> Dict[str, float]:
        """Get preferred action types based on personality."""
        preferences = {}
        
        # Base preferences
        preferences[AgentAction.WORK] = 0.3 + (self.cooperation * 0.2)
        preferences[AgentAction.REST] = 0.2 + ((1.0 - self.aggression) * 0.1)
        preferences[AgentAction.SABOTAGE] = 0.05 + (self.aggression * 0.1)
        preferences[AgentAction.TALK] = 0.2 + (self.cooperation * 0.15)
        preferences[AgentAction.REPAIR] = 0.1 + (self.cooperation * 0.1)
        preferences[AgentAction.RESEARCH] = 0.1 + (self.curiosity * 0.15)
        preferences[AgentAction.EAT] = 0.05 + (self.self_preservation * 0.1)
        
        return preferences
    
    def get_target_preferences(self) -> Dict[str, float]:
        """Get preferred targets based on role and personality."""
        preferences = {}
        
        # Role-based preferences
        if "Commander" in self.role:
            preferences["commander"] = 0.3
            preferences["habitat"] = 0.2
            preferences["communication"] = 0.2
        elif "Engineer" in self.role:
            preferences["solar_panel"] = 0.3
            preferences["oxygen_generator"] = 0.2
            preferences["water_recycler"] = 0.2
        elif "Doctor" in self.role:
            preferences["habitat"] = 0.3
            preferences["storage"] = 0.2
        elif "Biologist" in self.role:
            preferences["greenhouse"] = 0.5
            preferences["laboratory"] = 0.3
        elif "Spy" in self.role:
            preferences["oxygen_generator"] = 0.3
            preferences["solar_panel"] = 0.2
            preferences["water_recycler"] = 0.2
        
        # Personality adjustments
        if self.aggression > 0.7:
            preferences["commander"] = preferences.get("commander", 0.0) + 0.1
        
        # Add some generic targets
        preferences["habitat"] = preferences.get("habitat", 0.1)
        preferences["storage"] = preferences.get("storage", 0.05)
        
        return preferences