from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import copy
from enum import Enum


class Specialization(Enum):
    ENGINEER = "engineer"
    SCIENTIST = "scientist"
    EXPLORER = "explorer"
    MEDIC = "medic"
    PILOT = "pilot"
    COMMANDER = "commander"


class SecretObjectiveType(Enum):
    BETRAY_LOVER = "betray_lover"
    STEAL_RESOURCES = "steal_resources"
    SABOTAGE = "sabotage"
    BECOME_LEADER = "become_leader"
    SURVIVE_SILENTLY = "survive_silently"
    PROTECT_SOMEONE = "protect_someone"


class CrisisType(Enum):
    OXYGEN_CRISIS = "oxygen_crisis"
    WATER_CRISIS = "water_crisis"
    ENERGY_CRISIS = "energy_crisis"
    FOOD_CRISIS = "food_crisis"


CRISIS_THRESHOLDS = {
    CrisisType.OXYGEN_CRISIS: 100,
    CrisisType.WATER_CRISIS: 80,
    CrisisType.ENERGY_CRISIS: 50,
    CrisisType.FOOD_CRISIS: 60,
}


SECRET_OBJECTIVE_DESCRIPTIONS = {
    SecretObjectiveType.BETRAY_LOVER: "Betray your closest ally at a critical moment",
    SecretObjectiveType.STEAL_RESOURCES: "Secretly steal 100+ units of any resource",
    SecretObjectiveType.SABOTAGE: "Sabotage a key system without getting caught",
    SecretObjectiveType.BECOME_LEADER: "Become the colony leader through influence",
    SecretObjectiveType.SURVIVE_SILENTLY: "Survive without drawing attention to yourself",
    SecretObjectiveType.PROTECT_SOMEONE: "Ensure a specific agent survives to the end",
}


class SecretObjective:
    def __init__(
        self, objective_type: SecretObjectiveType, target_agent: Optional[str] = None
    ):
        self.type = objective_type
        self.target_agent = target_agent
        self.completed = False
        self.failed = False
        self.description = SECRET_OBJECTIVE_DESCRIPTIONS.get(objective_type, "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "description": self.description,
            "target_agent": self.target_agent,
            "completed": self.completed,
            "failed": self.failed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecretObjective":
        obj = cls(
            objective_type=SecretObjectiveType(data["type"]),
            target_agent=data.get("target_agent"),
        )
        obj.completed = data.get("completed", False)
        obj.failed = data.get("failed", False)
        return obj


SPECIALIZATION_BONUSES = {
    Specialization.ENGINEER: {
        "repair_bonus": 0.30,
        "energy_bonus": 0.20,
    },
    Specialization.SCIENTIST: {
        "research_bonus": 0.40,
        "food_bonus": 0.20,
    },
    Specialization.EXPLORER: {
        "discovery_bonus": 0.50,
        "range_bonus": 0.30,
    },
    Specialization.MEDIC: {
        "health_bonus": 0.30,
        "mental_bonus": 0.40,
    },
    Specialization.PILOT: {
        "emergency_bonus": 0.30,
        "failure_reduction": 0.20,
    },
    Specialization.COMMANDER: {
        "team_efficiency": 0.15,
        "mutiny_reduction": 0.10,
    },
}


class DecisionType(Enum):
    METEOR_STRIKE = "meteor_strike"
    OXYGEN_CRISIS = "oxygen_crisis"
    WATER_CRISIS = "water_crisis"
    ENERGY_CRISIS = "energy_crisis"
    FOOD_CRISIS = "food_crisis"
    WATER_CONTAMINATION = "water_contamination"
    SOLAR_STORM = "solar_storm"
    CREW_MUTINY = "crew_mutiny"
    EQUIPMENT_FAILURE = "equipment_failure"
    SUPPLY_DROP = "supply_drop"


class MissionType(Enum):
    PRODUCE_RESOURCES = "produce_resources"
    MAINTAIN_SYSTEMS = "maintain_systems"
    EXPLORE = "explore"
    RESEARCH = "research"


class MissionStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Decision:
    """Emergency decision that pops up randomly."""

    id: str
    type: str
    title: str
    description: str
    options: List[Dict[str, Any]]
    tick_created: int
    resolved: bool = False
    chosen_option: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "options": self.options,
            "tick_created": self.tick_created,
            "resolved": self.resolved,
            "chosen_option": self.chosen_option,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Decision":
        return cls(
            id=data["id"],
            type=data["type"],
            title=data["title"],
            description=data["description"],
            options=data["options"],
            tick_created=data["tick_created"],
            resolved=data.get("resolved", False),
            chosen_option=data.get("chosen_option"),
        )


@dataclass
class Mission:
    """Daily mission assigned to crew."""

    id: str
    type: str
    title: str
    description: str
    target_value: float
    current_value: float = 0.0
    reward: Dict[str, float] = field(default_factory=dict)
    status: str = "active"
    tick_created: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "reward": self.reward,
            "status": self.status,
            "tick_created": self.tick_created,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Mission":
        return cls(
            id=data["id"],
            type=data["type"],
            title=data["title"],
            description=data["description"],
            target_value=data["target_value"],
            current_value=data.get("current_value", 0.0),
            reward=data.get("reward", {}),
            status=data.get("status", "active"),
            tick_created=data.get("tick_created", 0),
        )


@dataclass
class Agent:
    """Agent/crew member in the Mars colony."""

    name: str
    health: float = 100.0  # 0-100%
    mental_state: float = 80.0  # mental stability 0-100%
    location: str = "habitat"  # habitat, greenhouse, solar_farm, etc.
    specialization: Optional[str] = None  # Agent specialization type
    secret_objective: Optional[SecretObjective] = None  # Hidden secret objective

    def __post_init__(self):
        """Validate initial values."""
        self.health = max(0.0, min(100.0, self.health))
        self.mental_state = max(0.0, min(100.0, self.mental_state))

    def is_alive(self) -> bool:
        """Check if agent is alive."""
        return self.health > 0.0

    def get_specialization_enum(self) -> Optional[Specialization]:
        """Get specialization as enum."""
        if self.specialization:
            try:
                return Specialization(self.specialization)
            except ValueError:
                return None
        return None

    def get_bonuses(self) -> Dict[str, float]:
        """Get bonuses for this agent's specialization."""
        spec = self.get_specialization_enum()
        if spec and spec in SPECIALIZATION_BONUSES:
            return SPECIALIZATION_BONUSES[spec].copy()
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "health": self.health,
            "mental_state": self.mental_state,
            "location": self.location,
            "specialization": self.specialization,
            "secret_objective": self.secret_objective.to_dict()
            if self.secret_objective
            else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create from dictionary."""
        agent = cls(
            name=data["name"],
            health=data.get("health", 100.0),
            mental_state=data.get("mental_state", 80.0),
            location=data.get("location", "habitat"),
            specialization=data.get("specialization"),
        )
        if data.get("secret_objective"):
            agent.secret_objective = SecretObjective.from_dict(data["secret_objective"])
        return agent


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

    # Pending decisions
    pending_decisions: List[Decision] = field(default_factory=list)

    # Active missions
    missions: List[Mission] = field(default_factory=list)

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
            "pending_decisions": [d.to_dict() for d in self.pending_decisions],
            "missions": [m.to_dict() for m in self.missions],
            "rng_state": copy.deepcopy(self.rng_state) if self.rng_state else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
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

        # Recreate decisions
        for decision_data in data.get("pending_decisions", []):
            state.pending_decisions.append(Decision.from_dict(decision_data))

        # Recreate missions
        for mission_data in data.get("missions", []):
            state.missions.append(Mission.from_dict(mission_data))

        return state

    @classmethod
    def create_initial_state(
        cls, crew_names: Optional[List[str]] = None
    ) -> "GameState":
        """Create initial game state with default crew."""
        if crew_names is None:
            crew_names = [
                "Commander Chen",
                "Dr. Rodriguez",
                "Engineer Tanaka",
                "Botanist Schmidt",
                "Pilot Okafor",
            ]

        specialization_map = {
            "Commander Chen": Specialization.COMMANDER,
            "Dr. Rodriguez": Specialization.MEDIC,
            "Engineer Tanaka": Specialization.ENGINEER,
            "Botanist Schmidt": Specialization.SCIENTIST,
            "Pilot Okafor": Specialization.PILOT,
        }

        state = cls()

        # Initialize crew with specializations
        for name in crew_names:
            spec = specialization_map.get(name, Specialization.EXPLORER)
            state.agents[name] = Agent(name=name, specialization=spec.value)

        # Add initial log
        state.add_log(
            "Mission 'Project Red Dust' initialized. Mars colony established."
        )

        return state

    def assign_secret_objectives(self, rng) -> None:
        """Assign random secret objectives to all agents."""
        objective_types = list(SecretObjectiveType)
        agent_names = list(self.agents.keys())

        for name in agent_names:
            if len(agent_names) > 1:
                target_options = [n for n in agent_names if n != name]
                target = rng.choice(target_options) if target_options else None
            else:
                target = None

            obj_type = rng.choice(objective_types)
            self.agents[name].secret_objective = SecretObjective(
                objective_type=obj_type,
                target_agent=target,
            )
