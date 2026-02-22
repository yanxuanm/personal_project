from typing import Optional, List
from .schema import GameState
from ..harness.rand_gen import DeterministicRandom
from ..agents.schema import AgentAction


class MarsEnvironment:
    """Mars survival simulation environment."""

    # Resource consumption per agent per tick
    OXYGEN_PER_AGENT = 2.0
    FOOD_PER_AGENT = 0.5
    WATER_PER_AGENT = 1.0
    ENERGY_BASE_CONSUMPTION = 5.0  # Base energy consumption per tick

    # Resource production per tick (solar panels, water recyclers, etc.)
    ENERGY_PRODUCTION = 8.0
    WATER_RECYCLING = 0.8  # 80% of water is recycled

    # Random event probabilities
    SOLAR_PANEL_FAILURE_PROB = 0.05  # 5% chance per tick
    LIFE_SUPPORT_FAILURE_PROB = 0.03  # 3% chance when energy is low

    def __init__(self, state: GameState, rng: DeterministicRandom):
        """Initialize environment with game state and random generator.

        Args:
            state: Current game state
            rng: Deterministic random generator
        """
        self.state = state
        self.rng = rng

        # Store initial RNG state in game state if not present
        if self.state.rng_state is None:
            self.state.rng_state = self.rng.get_state()

    def step(self, actions: Optional[List[AgentAction]] = None) -> bool:
        """Execute one simulation tick.

        Args:
            actions: List of agent actions to process this tick

        Returns:
            True if game is over, False otherwise
        """
        if actions is None:
            actions = []

        # Increment tick counter
        self.state.tick += 1

        # Count alive agents
        alive_agents = [
            agent for agent in self.state.agents.values() if agent.is_alive()
        ]
        num_alive = len(alive_agents)

        # Resource consumption
        self._consume_resources(num_alive)

        # Process agent actions
        self._process_actions(actions)

        # Resource production
        self._produce_resources()

        # Check for disaster conditions
        self._check_disasters()

        # Random events
        self._random_events()

        # Update agent states
        self._update_agents(alive_agents)

        # Check game over
        if self.state.is_game_over():
            self.state.add_log("GAME OVER: Colony has failed.")
            return True

        # Save RNG state for deterministic replay
        self.state.rng_state = self.rng.get_state()

        return False

    def _consume_resources(self, num_alive: int) -> None:
        """Consume resources based on number of alive agents."""
        if num_alive == 0:
            return

        # Calculate oxygen consumption (doubled if energy is low)
        oxygen_consumption = num_alive * self.OXYGEN_PER_AGENT
        if self.state.get_resource("energy") < 10.0:
            oxygen_consumption *= 2.0
            self.state.add_log("WARNING: Low energy! Oxygen consumption doubled.")

        # Apply consumption
        self.state.modify_resource("oxygen", -oxygen_consumption)
        self.state.modify_resource("food", -num_alive * self.FOOD_PER_AGENT)

        # Water consumption with recycling
        water_consumed = num_alive * self.WATER_PER_AGENT
        water_recycled = water_consumed * self.WATER_RECYCLING
        water_net_loss = water_consumed - water_recycled
        self.state.modify_resource("water", -water_net_loss)

        # Energy consumption
        energy_consumed = self.ENERGY_BASE_CONSUMPTION + (num_alive * 0.5)
        self.state.modify_resource("energy", -energy_consumed)

        # Log if any resource is critically low
        for resource, amount in self.state.resources.items():
            if amount < 20.0:
                self.state.add_log(
                    f"WARNING: {resource} critically low ({amount:.1f} units)"
                )

    def _process_actions(self, actions: List[AgentAction]) -> None:
        """Process agent actions and apply their effects to the game state.

        Args:
            actions: List of agent actions to process
        """
        # Log all actions
        for action in actions:
            self.state.add_log(
                f"{action.type.upper()}: {action.target} - {action.argument}"
            )

        # Apply action effects
        for action in actions:
            if action.type == AgentAction.WORK:
                # Working increases energy production slightly
                self.state.modify_resource("energy", 2.0)
            elif action.type == AgentAction.REPAIR:
                # Repairing consumes energy but improves systems
                self.state.modify_resource("energy", -5.0)
                # Random chance to fix something
                if self.rng.next_float() < 0.3:
                    resource_gain = self.rng.next_int(5, 15)
                    if action.target == "solar_panel":
                        self.state.modify_resource("energy", resource_gain)
                    elif action.target == "oxygen_generator":
                        self.state.modify_resource("oxygen", resource_gain)
                    elif action.target == "water_recycler":
                        self.state.modify_resource("water", resource_gain)
            elif action.type == AgentAction.SABOTAGE:
                # Sabotage consumes resources
                if action.target == "solar_panel":
                    self.state.modify_resource("energy", -self.rng.next_int(10, 30))
                elif action.target == "oxygen_generator":
                    self.state.modify_resource("oxygen", -self.rng.next_int(5, 20))
                elif action.target == "water_recycler":
                    self.state.modify_resource("water", -self.rng.next_int(5, 15))
                elif action.target == "greenhouse":
                    self.state.modify_resource("food", -self.rng.next_int(5, 25))
            elif action.type == AgentAction.EAT:
                # Eating consumes food but improves health
                food_consumed = self.rng.next_int(1, 3)
                self.state.modify_resource("food", -food_consumed)
                # Find the agent who ate and improve their health
                for agent in self.state.agents.values():
                    if agent.name.lower() in action.argument.lower():
                        agent.health = min(100.0, agent.health + 5.0)
            elif action.type == AgentAction.REST:
                # Resting improves mental state
                for agent in self.state.agents.values():
                    if agent.name.lower() in action.argument.lower():
                        agent.mental_state = min(100.0, agent.mental_state + 3.0)
            elif action.type == AgentAction.TALK:
                # Talking improves cooperation (mental state)
                participants = 0
                for agent in self.state.agents.values():
                    if agent.name.lower() in action.argument.lower():
                        agent.mental_state = min(100.0, agent.mental_state + 2.0)
                        participants += 1
                if participants >= 2:
                    # Group talk has additional benefits
                    self.state.modify_resource("energy", 1.0)

    def _produce_resources(self) -> None:
        """Produce resources through colony systems."""
        # Energy production from solar panels
        self.state.modify_resource("energy", self.ENERGY_PRODUCTION)

        # Note: Food production would be handled separately in greenhouse module
        # For now, no automatic food production

    def _check_disasters(self) -> None:
        """Check for and handle disaster conditions."""
        # Life support failure when energy is critically low
        if self.state.get_resource("energy") < 5.0:
            if self.rng.next_float() < self.LIFE_SUPPORT_FAILURE_PROB:
                self.state.modify_resource("oxygen", -10.0)
                self.state.add_log(
                    "DISASTER: Life support system failure! Oxygen leak."
                )

        # Starvation effects
        if self.state.get_resource("food") < 10.0:
            for agent in self.state.agents.values():
                if agent.is_alive():
                    agent.health -= 5.0
            self.state.add_log(
                "WARNING: Crew experiencing starvation. Health declining."
            )

    def _random_events(self) -> None:
        """Handle random events."""
        # Solar panel failure
        if self.rng.next_float() < self.SOLAR_PANEL_FAILURE_PROB:
            energy_loss = self.rng.next_int(5, 15)
            self.state.modify_resource("energy", -energy_loss)
            self.state.add_log(
                f"RANDOM EVENT: Solar panel malfunction! Lost {energy_loss} energy."
            )

        # Water recycling system failure (less common)
        if self.rng.next_float() < 0.02:  # 2% chance
            water_loss = self.rng.next_int(10, 30)
            self.state.modify_resource("water", -water_loss)
            self.state.add_log(
                f"RANDOM EVENT: Water recycler failure! Lost {water_loss} water."
            )

        # Mental breakdown (rare)
        if self.rng.next_float() < 0.01:  # 1% chance
            agents = [a for a in self.state.agents.values() if a.is_alive()]
            if agents:
                agent = self.rng.choice(agents)
                agent.mental_state -= 20.0
                self.state.add_log(
                    f"RANDOM EVENT: {agent.name} experienced mental breakdown!"
                )

    def _update_agents(self, alive_agents: list) -> None:
        """Update agent states each tick."""
        for agent in alive_agents:
            # Gradual health recovery if conditions are good
            if (
                self.state.get_resource("food") > 30.0
                and self.state.get_resource("oxygen") > 50.0
            ):
                agent.health = min(100.0, agent.health + 0.1)

            # Mental state affected by resource levels
            if self.state.get_resource("food") < 20.0:
                agent.mental_state -= 0.5
            if self.state.get_resource("oxygen") < 30.0:
                agent.mental_state -= 0.3

            # Prevent negative mental state
            agent.mental_state = max(0.0, agent.mental_state)

            # Agent death from health depletion
            if agent.health <= 0.0:
                agent.health = 0.0
                self.state.add_log(f"TRAGEDY: {agent.name} has died.")

    def get_status_report(self) -> str:
        """Generate a human-readable status report."""
        alive_count = sum(1 for agent in self.state.agents.values() if agent.is_alive())

        report = []
        report.append(f"=== Mars Colony Status (Tick {self.state.tick}) ===")
        report.append(f"Crew: {alive_count}/{len(self.state.agents)} alive")

        for resource, amount in self.state.resources.items():
            report.append(f"{resource.capitalize()}: {amount:.1f}")

        if self.state.logs:
            recent_logs = self.state.logs[-3:]  # Last 3 logs
            report.append("Recent events:")
            for log in recent_logs:
                report.append(f"  {log}")

        return "\n".join(report)
