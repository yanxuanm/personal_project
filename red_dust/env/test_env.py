#!/usr/bin/env python3
"""Test script for Mars environment simulation."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from red_dust.harness.rand_gen import DeterministicRandom
from red_dust.env.schema import GameState
from red_dust.env.mars import MarsEnvironment


def main():
    """Run a 10-tick simulation test."""
    print("=" * 60)
    print("Project Red Dust - Environment Simulation Test")
    print("=" * 60)

    # Create deterministic random generator with fixed seed for reproducibility
    rng = DeterministicRandom(seed=42)

    # Create initial game state with default crew
    state = GameState.create_initial_state()
    print(f"Initialized with {len(state.agents)} crew members")
    print(f"Initial resources: {state.resources}")
    print()

    # Create environment
    env = MarsEnvironment(state, rng)

    # Run simulation for up to 10 ticks
    max_ticks = 10
    game_over = False

    for tick in range(max_ticks):
        print(f"\n--- Tick {tick + 1} ---")

        # Execute one simulation step
        game_over = env.step()

        # Print status report
        print(env.get_status_report())

        # Check if game ended early
        if game_over:
            print("\n⚠️  Game over detected!")
            break

    # Simulation results
    print("\n" + "=" * 60)
    print("Simulation Results:")
    print("=" * 60)

    print(f"Final tick: {state.tick}")
    print(f"Game over: {game_over}")

    print("\nFinal resource levels:")
    for resource, amount in state.resources.items():
        print(f"  {resource.capitalize()}: {amount:.1f}")

    print("\nCrew status:")
    for name, agent in state.agents.items():
        status = "ALIVE" if agent.is_alive() else "DECEASED"
        print(
            f"  {name}: Health={agent.health:.1f}, Mental={agent.mental_state:.1f} ({status})"
        )

    print(f"\nTotal log entries: {len(state.logs)}")
    if state.logs:
        print("\nLast 5 log entries:")
        for log in state.logs[-5:]:
            print(f"  {log}")

    # Test deterministic replay
    print("\n" + "=" * 60)
    print("Testing Deterministic Replay...")
    print("=" * 60)

    # Reset and run simulation with same seed
    rng2 = DeterministicRandom(seed=42)
    state2 = GameState.create_initial_state()
    env2 = MarsEnvironment(state2, rng2)

    # Run same number of ticks
    for _ in range(state.tick):
        env2.step()

    # Compare final states (excluding logs timestamps which include tick numbers)
    # Compare resources
    match = True
    for resource in state.resources:
        if abs(state.resources[resource] - state2.resources[resource]) > 0.001:
            print(
                f"✗ Resource mismatch for {resource}: "
                f"{state.resources[resource]:.1f} vs {state2.resources[resource]:.1f}"
            )
            match = False

    # Compare agent health
    for name in state.agents:
        agent1 = state.agents[name]
        agent2 = state2.agents[name]
        if abs(agent1.health - agent2.health) > 0.001:
            print(
                f"✗ Health mismatch for {name}: "
                f"{agent1.health:.1f} vs {agent2.health:.1f}"
            )
            match = False

    if match:
        print("✓ Deterministic replay successful! Identical results with same seed.")
    else:
        print("✗ Deterministic replay failed!")

    return 0 if match else 1


if __name__ == "__main__":
    sys.exit(main())
