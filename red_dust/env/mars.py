from typing import Optional, List, Dict, Any
from .schema import (
    GameState,
    Decision,
    Mission,
    DecisionType,
    MissionType,
    MissionStatus,
    Specialization,
    SPECIALIZATION_BONUSES,
)
from ..harness.rand_gen import DeterministicRandom
from ..agents.schema import AgentAction


DECISION_TEMPLATES = {
    DecisionType.METEOR_STRIKE: {
        "title": "陨石来袭！METEOR STRIKE IMMINENT!",
        "description": "雷达探测到大型陨石正在接近殖民地！需要立即做出决定。",
        "options": [
            {"text": "启动防御护盾 (消耗100能量)", "effects": {"energy": -100}},
            {"text": "疏散人员到避难所 (无消耗)", "effects": {}},
            {
                "text": "发射拦截导弹 (消耗50能量, 30水)",
                "effects": {"energy": -50, "water": -30},
            },
        ],
    },
    DecisionType.ENERGY_CRISIS: {
        "title": "能源危机！ENERGY CRISIS!",
        "description": "太阳能板故障，能源储备严重不足！",
        "options": [
            {"text": "关闭非必要系统 (保存50能量)", "effects": {"energy": 50}},
            {"text": "启动备用发电机 (消耗30食物)", "effects": {"food": -30}},
            {"text": "紧急抢修太阳能板 (无消耗, 成功率50%)", "effects": {}},
        ],
    },
    DecisionType.WATER_CONTAMINATION: {
        "title": "水源污染！WATER CONTAMINATION!",
        "description": "水循环系统检测到有害物质！",
        "options": [
            {"text": "丢弃所有受污染水源 (损失100水)", "effects": {"water": -100}},
            {"text": "启用净化系统 (消耗40能量)", "effects": {"energy": -40}},
            {"text": "使用紧急过滤装置 (消耗20食物)", "effects": {"food": -20}},
        ],
    },
    DecisionType.SOLAR_STORM: {
        "title": "太阳风暴！SOLAR STORM WARNING!",
        "description": "强烈的太阳风暴即将来袭，可能损坏电子设备！",
        "options": [
            {"text": "关闭所有电子设备 (无消耗)", "effects": {}},
            {"text": "增强防护罩 (消耗80能量)", "effects": {"energy": -80}},
            {"text": "疏散到地下掩体 (无消耗)", "effects": {}},
        ],
    },
    DecisionType.CREW_MUTINY: {
        "title": "船员叛变！CREW MUTINY!",
        "description": "船员对任务分配感到不满，可能发生叛变！",
        "options": [
            {"text": "增加食物配给 (消耗30食物)", "effects": {"food": -30}},
            {"text": "召开全体会议 (无消耗)", "effects": {}},
            {"text": "重新分配任务 (无消耗)", "effects": {}},
        ],
    },
    DecisionType.EQUIPMENT_FAILURE: {
        "title": "设备故障！EQUIPMENT FAILURE!",
        "description": "关键生命维持设备出现故障！",
        "options": [
            {"text": "紧急修复 (消耗50能量)", "effects": {"energy": -50}},
            {"text": "切换到备用设备 (消耗30水)", "effects": {"water": -30}},
            {"text": "让工程师手动维修 (无消耗)", "effects": {}},
        ],
    },
    DecisionType.SUPPLY_DROP: {
        "title": "补给空投！SUPPLY DROP AVAILABLE!",
        "description": "收到地面控制中心的紧急补给信号！",
        "options": [
            {
                "text": "接收所有补给 (增加资源)",
                "effects": {"oxygen": 50, "water": 50, "energy": 50, "food": 50},
            },
            {
                "text": "只接收关键物资 (增加30氧气, 30水)",
                "effects": {"oxygen": 30, "water": 30},
            },
            {"text": "拒绝接收 (保持现状)", "effects": {}},
        ],
    },
}


MISSION_TEMPLATES = {
    MissionType.PRODUCE_RESOURCES: [
        {
            "title": "增加氧气产量",
            "description": "生产50单位氧气",
            "target": 50,
            "resource": "oxygen",
            "reward": {"energy": 10},
        },
        {
            "title": "收集水资源",
            "description": "收集40单位水",
            "target": 40,
            "resource": "water",
            "reward": {"energy": 10},
        },
        {
            "title": "发电任务",
            "description": "产生60单位能量",
            "target": 60,
            "resource": "energy",
            "reward": {"oxygen": 10},
        },
        {
            "title": "食品生产",
            "description": "生产30单位食物",
            "target": 30,
            "resource": "food",
            "reward": {"water": 10},
        },
    ],
    MissionType.MAINTAIN_SYSTEMS: [
        {
            "title": "系统维护",
            "description": "修复关键设备",
            "target": 1,
            "resource": "repair",
            "reward": {"energy": 20},
        },
        {
            "title": "清洁太阳能板",
            "description": "清洁太阳能板提高效率",
            "target": 1,
            "resource": "clean",
            "reward": {"energy": 15},
        },
        {
            "title": "检查生命维持",
            "description": "全面检查生命维持系统",
            "target": 1,
            "resource": "check",
            "reward": {"oxygen": 15},
        },
    ],
    MissionType.EXPLORE: [
        {
            "title": "探索新区域",
            "description": "探索周边地区",
            "target": 1,
            "resource": "explore",
            "reward": {"energy": 30},
        },
        {
            "title": "采集样本",
            "description": "采集岩石样本",
            "target": 1,
            "resource": "sample",
            "reward": {"food": 20},
        },
    ],
    MissionType.RESEARCH: [
        {
            "title": "研究新算法",
            "description": "优化资源利用",
            "target": 1,
            "resource": "research",
            "reward": {"energy": 25},
        },
        {
            "title": "分析数据",
            "description": "分析气象数据",
            "target": 1,
            "resource": "analyze",
            "reward": {"water": 20},
        },
    ],
}


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

    # Decision and mission probabilities
    DECISION_PROB = 0.08  # 8% chance to trigger a decision per tick
    MISSION_PROB = 0.10  # 10% chance to generate a new mission per tick
    MAX_PENDING_DECISIONS = 3
    MAX_MISSIONS = 5

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

    def _get_agent_bonuses(self, agent_name: str) -> Dict[str, float]:
        """Get specialization bonuses for an agent."""
        agent = self.state.agents.get(agent_name)
        if agent:
            return agent.get_bonuses()
        return {}

    def _has_specialization(self, agent_name: str, spec: Specialization) -> bool:
        """Check if agent has a specific specialization."""
        agent = self.state.agents.get(agent_name)
        if agent and agent.specialization:
            return agent.specialization == spec.value
        return False

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

        # Generate new decisions (if conditions allow)
        self._generate_decision()

        # Generate new missions (if conditions allow)
        self._generate_mission()

        # Update missions progress
        self._update_missions(actions)

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
            # Find the agent who performed this action
            agent_name = action.argument if action.argument else None
            bonuses = self._get_agent_bonuses(agent_name) if agent_name else {}

            if action.type == AgentAction.WORK:
                # Working increases energy production slightly
                energy_gain = 2.0
                # SCIENTIST: food bonus when working on greenhouse
                if agent_name and self._has_specialization(
                    agent_name, Specialization.SCIENTIST
                ):
                    food_bonus = bonuses.get("food_bonus", 0.20)
                    self.state.modify_resource("food", 5.0 * (1 + food_bonus))
                # EXPLORER: discovery bonus - small resource find chance
                if agent_name and self._has_specialization(
                    agent_name, Specialization.EXPLORER
                ):
                    if self.rng.next_float() < bonuses.get("discovery_bonus", 0.50):
                        found_resource = self.rng.choice(
                            ["oxygen", "water", "energy", "food"]
                        )
                        amount = self.rng.next_int(3, 8)
                        self.state.modify_resource(found_resource, amount)
                        self.state.add_log(
                            f"EXPLORER DISCOVERY: {agent_name} found {amount} {found_resource}!"
                        )
                # PILOT: emergency bonus affects work efficiency
                if agent_name and self._has_specialization(
                    agent_name, Specialization.PILOT
                ):
                    energy_gain *= 1 + bonuses.get("emergency_bonus", 0.30)
                self.state.modify_resource("energy", energy_gain)

            elif action.type == AgentAction.REPAIR:
                # Repairing consumes energy but improves systems
                self.state.modify_resource("energy", -5.0)
                # Random chance to fix something
                repair_chance = 0.3
                # ENGINEER: repair bonus
                if agent_name and self._has_specialization(
                    agent_name, Specialization.ENGINEER
                ):
                    repair_bonus = bonuses.get("repair_bonus", 0.30)
                    repair_chance *= 1 + repair_bonus
                if self.rng.next_float() < repair_chance:
                    resource_gain = self.rng.next_int(5, 15)
                    # ENGINEER: repair bonus - extra resource gain
                    if agent_name and self._has_specialization(
                        agent_name, Specialization.ENGINEER
                    ):
                        repair_bonus = bonuses.get("repair_bonus", 0.30)
                        resource_gain = int(resource_gain * (1 + repair_bonus))
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
                        health_boost = 5.0
                        # MEDIC: health bonus
                        if self._has_specialization(agent.name, Specialization.MEDIC):
                            health_bonus = bonuses.get("health_bonus", 0.30)
                            health_boost *= 1 + health_bonus
                        agent.health = min(100.0, agent.health + health_boost)

            elif action.type == AgentAction.REST:
                # Resting improves mental state
                for agent in self.state.agents.values():
                    if agent.name.lower() in action.argument.lower():
                        mental_boost = 3.0
                        # MEDIC: mental bonus
                        if self._has_specialization(agent.name, Specialization.MEDIC):
                            mental_bonus = bonuses.get("mental_bonus", 0.40)
                            mental_boost *= 1 + mental_bonus
                        agent.mental_state = min(
                            100.0, agent.mental_state + mental_boost
                        )

            elif action.type == AgentAction.TALK:
                # Talking improves cooperation (mental state)
                participants = 0
                for agent in self.state.agents.values():
                    if agent.name.lower() in action.argument.lower():
                        mental_boost = 2.0
                        # MEDIC: mental bonus
                        if self._has_specialization(agent.name, Specialization.MEDIC):
                            mental_bonus = bonuses.get("mental_bonus", 0.40)
                            mental_boost *= 1 + mental_bonus
                        agent.mental_state = min(
                            100.0, agent.mental_state + mental_boost
                        )
                        participants += 1
                if participants >= 2:
                    # Group talk has additional benefits
                    # COMMANDER: team efficiency bonus
                    has_commander = any(
                        self._has_specialization(a.name, Specialization.COMMANDER)
                        for a in self.state.agents.values()
                    )
                    energy_bonus = 1.0
                    if has_commander:
                        for agent in self.state.agents.values():
                            if self._has_specialization(
                                agent.name, Specialization.COMMANDER
                            ):
                                team_eff = agent.get_bonuses().get(
                                    "team_efficiency", 0.15
                                )
                                energy_bonus *= 1 + team_eff
                                break
                    self.state.modify_resource("energy", energy_bonus)

    def _produce_resources(self) -> None:
        """Produce resources through colony systems."""
        # Energy production from solar panels
        # ENGINEER: energy bonus
        energy_gain = self.ENERGY_PRODUCTION
        for agent in self.state.agents.values():
            if self._has_specialization(agent.name, Specialization.ENGINEER):
                energy_bonus = agent.get_bonuses().get("energy_bonus", 0.20)
                energy_gain *= 1 + energy_bonus
                self.state.add_log(
                    f"ENGINEER BONUS: {agent.name} boosted energy production by {energy_bonus * 100:.0f}%"
                )
                break
        self.state.modify_resource("energy", energy_gain)

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
        # PILOT: failure reduction bonus
        failure_reduction = 0.0
        for agent in self.state.agents.values():
            if self._has_specialization(agent.name, Specialization.PILOT):
                failure_reduction = agent.get_bonuses().get("failure_reduction", 0.20)
                break

        # Solar panel failure - reduced by PILOT
        solar_failure_prob = self.SOLAR_PANEL_FAILURE_PROB * (1 - failure_reduction)
        if self.rng.next_float() < solar_failure_prob:
            energy_loss = self.rng.next_int(5, 15)
            self.state.modify_resource("energy", -energy_loss)
            self.state.add_log(
                f"RANDOM EVENT: Solar panel malfunction! Lost {energy_loss} energy."
            )

        # Water recycling system failure (less common) - reduced by PILOT
        water_failure_prob = 0.02 * (1 - failure_reduction)
        if self.rng.next_float() < water_failure_prob:
            water_loss = self.rng.next_int(10, 30)
            self.state.modify_resource("water", -water_loss)
            self.state.add_log(
                f"RANDOM EVENT: Water recycler failure! Lost {water_loss} water."
            )

        # Mental breakdown (rare) - reduced by PILOT
        mental_break_prob = 0.01 * (1 - failure_reduction)
        if self.rng.next_float() < mental_break_prob:
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
                health_recovery = 0.1
                # MEDIC: health bonus
                if self._has_specialization(agent.name, Specialization.MEDIC):
                    health_bonus = agent.get_bonuses().get("health_bonus", 0.30)
                    health_recovery *= 1 + health_bonus
                agent.health = min(100.0, agent.health + health_recovery)

            # Mental state affected by resource levels - reduced by MEDIC mental bonus
            mental_damage = 0.0
            if self.state.get_resource("food") < 20.0:
                mental_damage += 0.5
            if self.state.get_resource("oxygen") < 30.0:
                mental_damage += 0.3

            # MEDIC: mental bonus reduces mental damage
            if self._has_specialization(agent.name, Specialization.MEDIC):
                mental_bonus = agent.get_bonuses().get("mental_bonus", 0.40)
                mental_damage *= 1 - mental_bonus

            agent.mental_state -= mental_damage

            # Prevent negative mental state
            agent.mental_state = max(0.0, agent.mental_state)

            # Agent death from health depletion
            if agent.health <= 0.0:
                agent.health = 0.0
                self.state.add_log(f"TRAGEDY: {agent.name} has died.")

    def _generate_decision(self) -> None:
        """Generate a random decision if conditions allow."""
        if len(self.state.pending_decisions) >= self.MAX_PENDING_DECISIONS:
            return

        if self.rng.next_float() > self.DECISION_PROB:
            return

        decision_types = list(DecisionType)
        decision_type = self.rng.choice(decision_types)
        template = DECISION_TEMPLATES[decision_type]

        decision_id = f"decision_{self.state.tick}_{self.rng.next_int(1000, 9999)}"
        decision = Decision(
            id=decision_id,
            type=decision_type.value,
            title=template["title"],
            description=template["description"],
            options=template["options"],
            tick_created=self.state.tick,
            resolved=False,
            chosen_option=None,
        )

        self.state.pending_decisions.append(decision)
        self.state.add_log(f"EMERGENCY: {decision.title}")

    def _generate_mission(self) -> None:
        """Generate a random mission if conditions allow."""
        if len(self.state.missions) >= self.MAX_MISSIONS:
            return

        active_missions = [
            m for m in self.state.missions if m.status == MissionStatus.ACTIVE.value
        ]
        if active_missions:
            return

        if self.rng.next_float() > self.MISSION_PROB:
            return

        mission_types = list(MissionType)
        mission_type = self.rng.choice(mission_types)
        templates = MISSION_TEMPLATES[mission_type]
        template = self.rng.choice(templates)

        mission_id = f"mission_{self.state.tick}_{self.rng.next_int(1000, 9999)}"
        reward = template.get("reward", {})

        mission = Mission(
            id=mission_id,
            type=mission_type.value,
            title=template["title"],
            description=template["description"],
            target_value=template["target"],
            current_value=0.0,
            reward=reward,
            status=MissionStatus.ACTIVE.value,
            tick_created=self.state.tick,
        )

        self.state.missions.append(mission)
        self.state.add_log(f"MISSION ASSIGNED: {mission.title}")

    def _update_missions(self, actions: List[AgentAction]) -> None:
        """Update mission progress based on actions and resources."""
        for mission in self.state.missions:
            if mission.status != MissionStatus.ACTIVE.value:
                continue

            if mission.type == MissionType.PRODUCE_RESOURCES.value:
                resource_name = mission.to_dict().get("resource", "")
                if resource_name in ["oxygen", "water", "energy", "food"]:
                    mission.current_value += 2.0

            elif mission.type == MissionType.MAINTAIN_SYSTEMS.value:
                for action in actions:
                    if action.type == AgentAction.REPAIR:
                        mission.current_value += 1.0

            elif mission.type == MissionType.EXPLORE.value:
                for action in actions:
                    if action.type == AgentAction.WORK:
                        mission.current_value += 0.5

            elif mission.type == MissionType.RESEARCH.value:
                for action in actions:
                    if action.type == AgentAction.TALK:
                        mission.current_value += 0.5

            if mission.current_value >= mission.target_value:
                mission.status = MissionStatus.COMPLETED.value
                for resource, amount in mission.reward.items():
                    self.state.modify_resource(resource, amount)
                self.state.add_log(
                    f"MISSION COMPLETE: {mission.title} - Rewards: {mission.reward}"
                )

    def resolve_decision(self, decision_id: str, option_index: int) -> Dict[str, Any]:
        """Resolve a pending decision with the chosen option."""
        for decision in self.state.pending_decisions:
            if decision.id == decision_id:
                if option_index < 0 or option_index >= len(decision.options):
                    return {"success": False, "error": "Invalid option index"}

                decision.resolved = True
                decision.chosen_option = option_index
                option = decision.options[option_index]
                effects = option.get("effects", {})

                for resource, amount in effects.items():
                    self.state.modify_resource(resource, amount)

                self.state.add_log(
                    f"DECISION RESOLVED: {decision.title} - {option['text']}"
                )
                return {"success": True, "effects": effects}

        return {"success": False, "error": "Decision not found"}

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
