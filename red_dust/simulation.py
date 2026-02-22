import copy
from typing import List, Optional
from .harness.clock import VirtualClock
from .harness.rand_gen import DeterministicRandom
from .env.schema import GameState
from .env.mars import MarsEnvironment
from .agents.personas import create_all_personas
from .agents.brain import AgentBrain
from .agents.schema import AgentAction


class SimulationController:
    """Main simulation controller with time travel capabilities."""
    
    def __init__(self, seed: int = 42, use_llm: bool = False):
        """Initialize simulation with deterministic seed.
        
        Args:
            seed: Random seed for determinism
            use_llm: Whether agents should use LLM for decision making
        """
        self.seed = seed
        self.use_llm = use_llm
        self.clock = VirtualClock(initial_tick=0)
        
        # Create deterministic random generator
        self.rng = DeterministicRandom(seed=seed)
        
        # Create initial game state
        self.initial_state = GameState.create_initial_state()
        
        # Initialize environment
        self.env = MarsEnvironment(self.initial_state, self.rng)
        
        # Set initial RNG state in game state
        self.env.state.rng_state = self.rng.get_state()
        
        # Create agents with personas
        personas = create_all_personas()
        self.agents = []
        for persona in personas:
            brain = AgentBrain(persona, use_llm=self.use_llm)
            self.agents.append({
                'persona': persona,
                'brain': brain,
                'name': persona.name,
            })
        
        # History of game states (for time travel)
        self.history: List[GameState] = []
        
        # Save initial state to history
        self._save_state_to_history()
        
        print(f"Simulation initialized with seed {seed}")
        print(f"Loaded {len(self.agents)} agents")
        print(f"Initial resources: {self.env.state.resources}")
    
    def _save_state_to_history(self) -> None:
        """Save current game state to history (deep copy)."""
        state_copy = copy.deepcopy(self.env.state)
        self.history.append(state_copy)
    

    
    def step(self) -> bool:
        """Execute one simulation tick.
        
        Returns:
            True if game is over, False otherwise
        """
        print(f"\n=== Tick {self.clock.tick} ===")
        
        # Get actions from all agents
        actions: List[AgentAction] = []
        for agent_info in self.agents:
            brain = agent_info['brain']
            action = brain.think(self.env.state)
            actions.append(action)
            print(f"{agent_info['name']}: {action}")
        
        # Save current RNG state (before environment consumes random numbers)
        current_rng_state = self.rng.get_state()
        
        # Execute environment step with agent actions (resource consumption, random events, etc.)
        game_over = self.env.step(actions)
        
        # Advance clock
        self.clock.step()
        
        # Update tick in game state to match clock
        self.env.state.tick = self.clock.tick
        
        # RNG state already saved by environment at end of tick
        # This is the state after random consumptions, which becomes the start of next tick
        pass
        
        # Save state to history (includes tick-start RNG state but post-step resources)
        self._save_state_to_history()
        
        # Print status
        print(self.env.get_status_report())
        
        if game_over:
            print("\n⚠️  GAME OVER!")
        
        return game_over
    
    def time_travel(self, target_tick: int) -> bool:
        """Rewind simulation to a specific tick.
        
        Args:
            target_tick: Tick to rewind to
            
        Returns:
            True if successful, False if target tick not in history
        """
        if target_tick < 0 or target_tick >= len(self.history):
            print(f"Cannot rewind to tick {target_tick}. History size: {len(self.history)}")
            return False
        
        print(f"\n⏪ Time travel to tick {target_tick}")
        
        # Get the historical state
        historical_state = self.history[target_tick]
        
        # Restore game state
        self.env.state = copy.deepcopy(historical_state)
        
        # Restore clock
        self.clock = VirtualClock(initial_tick=target_tick)
        
        # Restore RNG state
        if historical_state.rng_state:
            print(f"Restoring RNG state: {historical_state.rng_state}")
            self.rng.set_state(historical_state.rng_state)
        else:
            # If no RNG state saved, reset with seed + tick
            print(f"WARNING: No RNG state saved for tick {target_tick}. Creating new RNG with seed {self.seed + target_tick}")
            self.rng = DeterministicRandom(seed=self.seed + target_tick)
        
        # Truncate history (create new timeline)
        self.history = self.history[:target_tick + 1]
        
        print(f"Successfully rewound to tick {target_tick}")
        print(f"Resources: {self.env.state.resources}")
        
        return True
    
    def get_current_status(self) -> dict:
        """Get current simulation status."""
        return {
            'tick': self.clock.tick,
            'resources': self.env.state.resources.copy(),
            'agents_alive': sum(1 for a in self.env.state.agents.values() if a.is_alive()),
            'total_agents': len(self.env.state.agents),
            'history_size': len(self.history),
            'game_over': self.env.state.is_game_over(),
        }
    
    def print_status(self) -> None:
        """Print current simulation status."""
        status = self.get_current_status()
        print(f"\nCurrent Tick: {status['tick']}")
        print(f"History Size: {status['history_size']} states")
        print(f"Agents Alive: {status['agents_alive']}/{status['total_agents']}")
        print(f"Game Over: {status['game_over']}")
        
        print("\nResources:")
        for resource, amount in status['resources'].items():
            print(f"  {resource.capitalize()}: {amount:.1f}")
        
        # Show recent logs
        if self.env.state.logs:
            print("\nRecent Logs:")
            for log in self.env.state.logs[-3:]:
                print(f"  {log}")


def run_interactive_simulation(seed: int = 42, use_llm: bool = False) -> None:
    """Run simulation with interactive CLI.
    
    Args:
        seed: Random seed for determinism
        use_llm: Whether agents should use LLM for decision making
    """
    print("=" * 60)
    print("Project Red Dust - Interactive Simulation")
    print("=" * 60)
    if use_llm:
        print("LLM MODE ENABLED - Agents will use DeepSeek API for decisions")
    else:
        print("Mock mode - Agents use deterministic mock logic")
    
    controller = SimulationController(seed=seed, use_llm=use_llm)
    
    while True:
        print("\n" + "=" * 40)
        print("Commands: n (next) | r [tick] (rewind) | s (status) | q (quit)")
        command = input("> ").strip().lower()
        
        if command == 'q':
            print("Exiting simulation. Goodbye!")
            break
        
        elif command == 'n':
            game_over = controller.step()
            if game_over:
                print("Game over reached. Simulation ended.")
                break
        
        elif command.startswith('r '):
            try:
                parts = command.split()
                if len(parts) == 2:
                    target_tick = int(parts[1])
                    controller.time_travel(target_tick)
                else:
                    print("Usage: r [tick_number]")
            except ValueError:
                print("Invalid tick number. Usage: r [tick_number]")
        
        elif command == 's':
            controller.print_status()
        
        elif command == '':
            continue
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: n, r [tick], s, q")