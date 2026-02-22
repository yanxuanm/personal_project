from typing import Dict, Any
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ..env.schema import GameState
from ..harness.rand_gen import DeterministicRandom
from .schema import AgentAction, Persona


class AgentBrain:
    """Decision-making brain for agents. Can use mock logic or LLM."""
    
    def __init__(self, persona: Persona, use_llm: bool = False):
        """Initialize with a specific persona.
        
        Args:
            persona: The persona/role for this agent
            use_llm: Whether to use LLM for decision making (default: False)
        """
        self.persona = persona
        self.use_llm = use_llm
        
        # Cache for action preferences
        self._action_preferences = persona.get_action_preferences()
        self._target_preferences = persona.get_target_preferences()
        
        # Initialize OpenAI client if API key is available
        self.llm_client = None
        if self.use_llm:
            self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize the OpenAI-compatible client for DeepSeek."""
        try:
            # Try to import openai
            from openai import OpenAI
            
            # Get API key from environment
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key or api_key == "your_deepseek_api_key_here":
                print(f"Warning: No valid DEEPSEEK_API_KEY found for {self.persona.name}. "
                      "Falling back to mock logic.")
                self.use_llm = False
                return
            
            # Initialize client with DeepSeek endpoint
            self.llm_client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            
            print(f"LLM client initialized for {self.persona.name}")
            
        except ImportError:
            print("Warning: openai package not installed. Falling back to mock logic.")
            self.use_llm = False
        except Exception as e:
            print(f"Warning: Failed to initialize LLM client: {e}")
            self.use_llm = False
    
    def think(self, gamestate: GameState) -> AgentAction:
        """Generate an action based on current game state.
        
        Tries to use LLM if configured and available, otherwise falls back to mock logic.
        """
        # Try to use LLM if configured
        if self.use_llm and self.llm_client:
            try:
                return self._llm_think(gamestate)
            except Exception as e:
                print(f"LLM thinking failed for {self.persona.name}: {e}")
                print("Falling back to mock logic...")
                # Log error in game state
                gamestate.add_log(f"LLM_ERROR: {self.persona.name} - {str(e)[:100]}")
        
        # Fall back to mock logic
        return self._mock_think(gamestate)
    
    def _mock_think(self, gamestate: GameState) -> AgentAction:
        """Mock decision logic using deterministic random choices."""
        # Restore RNG state from game state for determinism
        rng = self._create_rng(gamestate)
        
        # Choose action type based on persona preferences
        action_type = self._choose_weighted(rng, self._action_preferences)
        
        # Choose target based on persona preferences and current situation
        target = self._choose_target(rng, gamestate)
        
        # Generate argument based on action and target
        argument = self._generate_argument(rng, action_type, target, gamestate)
        
        return AgentAction(
            type=action_type,
            target=target,
            argument=argument,
        )
    
    def _llm_think(self, gamestate: GameState) -> AgentAction:
        """LLM-based decision making using DeepSeek API.
        
        Returns:
            AgentAction based on LLM reasoning
            
        Raises:
            Exception: If LLM call fails or response cannot be parsed
        """
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        # Construct system prompt
        system_prompt = f"""You are {self.persona.name}, a {self.persona.role} in a Mars colony simulation.

PERSONALITY: {self.persona.personality}
SECRET GOAL: {self.persona.secret_goal}

You must roleplay as this character and make decisions consistent with their personality and secret goal.

AVAILABLE ACTIONS:
- work: Perform work on a system or location
- rest: Take a break or rest
- sabotage: Sabotage a system (must be subtle to avoid detection)
- talk: Have a conversation with someone or about something
- repair: Repair a damaged system
- research: Conduct research or experiments
- eat: Consume food

AVAILABLE TARGETS: greenhouse, solar_panel, oxygen_generator, water_recycler, habitat, commander, engineer, doctor, biologist, spy, storage, laboratory, communication, rover

You MUST respond with a valid JSON object in this exact format:
{{
    "type": "action_type",
    "target": "target_name",
    "argument": "reasoning_for_action"
}}

The "argument" field should explain your reasoning in 1-2 sentences, as if you were saying it to yourself or logging it.

Choose an action and target that makes sense given:
1. Your personality and secret goal
2. The current colony situation
3. Available resources and recent events

IMPORTANT: Your response must be ONLY the JSON object, no other text."""
        
        # Construct user prompt with current game state
        recent_logs = gamestate.logs[-5:] if gamestate.logs else ["No events yet"]
        logs_text = "\n".join(recent_logs)
        
        resources_text = "\n".join([
            f"{resource}: {amount:.1f}" 
            for resource, amount in gamestate.resources.items()
        ])
        
        # Count alive agents
        alive_agents = [agent for agent in gamestate.agents.values() if agent.is_alive()]
        
        user_prompt = f"""CURRENT COLONY STATUS (Tick {gamestate.tick}):

RESOURCES:
{resources_text}

ALIVE CREW: {len(alive_agents)}/{len(gamestate.agents)}

RECENT EVENTS:
{logs_text}

As {self.persona.name}, what do you decide to do? Remember your personality: {self.persona.personality}
Remember your secret goal: {self.persona.secret_goal}

Respond with ONLY the JSON object in the required format."""
        
        try:
            # Call DeepSeek API
            response = self.llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Extract and parse response
            response_text = response.choices[0].message.content
            
            # Try to parse JSON
            try:
                action_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON if response contains other text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    action_data = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
            
            # Validate required fields
            required_fields = ["type", "target"]
            for field in required_fields:
                if field not in action_data:
                    raise ValueError(f"Missing required field '{field}' in LLM response")
            
            # Create AgentAction from parsed data
            action = AgentAction(
                type=action_data["type"],
                target=action_data["target"],
                argument=action_data.get("argument", "")
            )
            
            # Log the LLM decision
            gamestate.add_log(f"LLM_DECISION: {self.persona.name} chose {action}")
            
            return action
            
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"LLM thinking failed: {str(e)}")
    
    def _create_rng(self, gamestate: GameState) -> DeterministicRandom:
        """Create deterministic RNG from game state."""
        # Use persona name as part of seed for uniqueness
        base_seed = hash(self.persona.name) % 10000
        
        if gamestate.rng_state is not None:
            # Restore from saved state for determinism
            rng = DeterministicRandom(seed=base_seed)
            rng.set_state(gamestate.rng_state)
            # Advance based on tick and persona to get unique sequences
            for _ in range(gamestate.tick + hash(self.persona.name) % 100):
                rng.next_int(0, 1000)
            return rng
        else:
            # No saved state, create new RNG
            return DeterministicRandom(seed=base_seed + gamestate.tick)
    
    def _choose_weighted(self, rng: DeterministicRandom, 
                        choices: Dict[str, float]) -> str:
        """Choose an option based on weighted probabilities."""
        if not choices:
            raise ValueError("No choices available")
        
        items = list(choices.items())
        total_weight = sum(weight for _, weight in items)
        
        if total_weight <= 0:
            # Fallback to uniform random
            return rng.choice(list(choices.keys()))
        
        # Normalize weights
        normalized = [(item, weight/total_weight) for item, weight in items]
        
        # Weighted random selection
        rand_val = rng.next_float()
        cumulative = 0.0
        
        for item, prob in normalized:
            cumulative += prob
            if rand_val <= cumulative:
                return item
        
        # Fallback (shouldn't reach here due to floating point)
        return items[-1][0]
    
    def _choose_target(self, rng: DeterministicRandom, 
                      gamestate: GameState) -> str:
        """Choose target based on persona preferences and current situation."""
        # Start with persona preferences
        target_weights = self._target_preferences.copy()
        
        # Adjust based on resource levels
        resources = gamestate.resources
        
        if resources.get("energy", 0) < 20:
            target_weights["solar_panel"] = target_weights.get("solar_panel", 0.0) + 0.3
        
        if resources.get("oxygen", 0) < 30:
            target_weights["oxygen_generator"] = target_weights.get("oxygen_generator", 0.0) + 0.3
        
        if resources.get("water", 0) < 25:
            target_weights["water_recycler"] = target_weights.get("water_recycler", 0.0) + 0.3
        
        if resources.get("food", 0) < 20:
            target_weights["greenhouse"] = target_weights.get("greenhouse", 0.0) + 0.3
        
        # Adjust based on secret goal
        if "sabotage" in self.persona.secret_goal.lower():
            # Spy prefers sabotage targets
            target_weights["oxygen_generator"] = target_weights.get("oxygen_generator", 0.0) + 0.2
            target_weights["solar_panel"] = target_weights.get("solar_panel", 0.0) + 0.2
        
        # Ensure at least some valid targets
        if not target_weights:
            target_weights = {"habitat": 1.0}
        
        return self._choose_weighted(rng, target_weights)
    
    def _generate_argument(self, rng: DeterministicRandom, 
                          action_type: str, target: str,
                          gamestate: GameState) -> str:
        """Generate argument text for the action."""
        arguments = {
            AgentAction.WORK: [
                "Performing routine maintenance",
                "Optimizing system efficiency",
                "Checking diagnostic reports",
                "Running standard procedures",
            ],
            AgentAction.REST: [
                "Taking scheduled break",
                "Feeling fatigued, need rest",
                "Medical recommendation to rest",
                "Mental health break",
            ],
            AgentAction.SABOTAGE: [
                "Accidental misconfiguration",
                "System stress test gone wrong",
                "Unintended side effect of optimization",
                "Experimental procedure failure",
            ],
            AgentAction.TALK: [
                "Discussing resource allocation",
                "Checking on crew morale",
                "Coordinating emergency protocols",
                "Debating mission priorities",
            ],
            AgentAction.REPAIR: [
                "Fixing identified issue",
                "Preventive maintenance",
                "Responding to alert",
                "System recovery procedure",
            ],
            AgentAction.RESEARCH: [
                "Experimenting with new approach",
                "Collecting data samples",
                "Testing hypothesis",
                "Analyzing system performance",
            ],
            AgentAction.EAT: [
                "Scheduled meal time",
                "Energy levels low",
                "Medical nutrition requirement",
                "Stress eating",
            ],
        }
        
        # Get base arguments
        base_args = arguments.get(action_type, ["Performing action"])
        
        # Add role-specific flavor
        role_args = {
            "Commander": ["As per protocol", "Mission directive", "Command decision"],
            "Engineer": ["Technical assessment indicates", "Engineering analysis shows"],
            "Doctor": ["Medical advisory", "Health considerations require"],
            "Biologist": ["Research imperative", "Experimental requirements"],
            "Spy": ["Standard procedure", "Routine check", "System verification"],
        }
        
        role_prefix = ""
        for role, prefixes in role_args.items():
            if role.lower() in self.persona.role.lower():
                role_prefix = rng.choice(prefixes)
                break
        
        # Combine
        base_arg = rng.choice(base_args)
        
        if role_prefix:
            return f"{role_prefix}: {base_arg}"
        else:
            return base_arg
    
    def analyze_situation(self, gamestate: GameState) -> Dict[str, Any]:
        """Analyze current situation from this persona's perspective.
        
        Returns a dictionary with analysis results.
        """
        analysis = {
            "persona": self.persona.name,
            "role": self.persona.role,
            "resource_assessment": {},
            "threat_level": 0.0,
            "recommended_priority": "maintenance",
        }
        
        # Assess resources
        resources = gamestate.resources
        for resource, amount in resources.items():
            if amount < 20:
                analysis["resource_assessment"][resource] = "CRITICAL"
                analysis["threat_level"] += 0.3
            elif amount < 50:
                analysis["resource_assessment"][resource] = "LOW"
                analysis["threat_level"] += 0.1
            elif amount < 100:
                analysis["resource_assessment"][resource] = "MODERATE"
            else:
                analysis["resource_assessment"][resource] = "ADEQUATE"
        
        # Adjust based on personality
        if self.persona.aggression > 0.7:
            analysis["threat_level"] *= 1.2  # Aggressive personalities perceive more threats
        
        if self.persona.self_preservation > 0.8:
            analysis["recommended_priority"] = "self_preservation"
        
        return analysis