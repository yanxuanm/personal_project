#!/usr/bin/env python3
"""Test LLM integration with fallback to mock logic."""

import sys
sys.path.insert(0, '.')

from red_dust.simulation import SimulationController

print("Testing LLM integration...")
print("Initializing simulation with use_llm=True...")

# Initialize with LLM mode (but API key is placeholder)
controller = SimulationController(seed=42, use_llm=True)

print(f"Simulation initialized. Number of agents: {len(controller.agents)}")

# Check each agent's brain LLM status
for agent_info in controller.agents:
    brain = agent_info['brain']
    print(f"{agent_info['name']}: use_llm={brain.use_llm}, llm_client={brain.llm_client is not None}")

print("\nRunning one simulation step...")
game_over = controller.step()

print(f"Step completed. Game over: {game_over}")
print("Current tick:", controller.clock.tick)
print("Resources:", controller.env.state.resources)

print("\nTest completed successfully.")