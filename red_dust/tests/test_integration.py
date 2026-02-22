#!/usr/bin/env python3
"""
Integration tests for Project Red Dust simulation.
Tests deterministic behavior and time travel functionality via API.
"""

import sys
import os
from typing import Dict, Any
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app
from red_dust.server.api import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


def test_time_travel_consistency(client: TestClient):
    """
    Test that time travel correctly restores state and simulation continues.

    Test flow:
    1. Reset simulator
    2. Phase 1: Run 5 ticks, record state at tick 5 (State_A)
    3. Continue to tick 10
    4. Phase 2: Rewind to tick 5, get state (State_B)
    5. Assert State_A == State_B
    6. Phase 3: Advance 1 tick to tick 6, get state (State_C)
    7. Verify State_C differs from State_A (simulation continues)
    """

    # Helper function to get current state
    def get_state() -> Dict[str, Any]:
        response = client.get("/api/state")
        assert response.status_code == 200, f"Failed to get state: {response.text}"
        return response.json()

    # Helper function to advance simulation
    def advance_ticks(num_ticks: int):
        for _ in range(num_ticks):
            response = client.post("/api/next")
            assert response.status_code == 200, (
                f"Failed to advance tick: {response.text}"
            )

    # Helper function to rewind to tick
    def rewind_to(tick: int):
        response = client.post(f"/api/rewind/{tick}")
        assert response.status_code == 200, (
            f"Failed to rewind to tick {tick}: {response.text}"
        )

    # Setup: Reset simulator with known seed and LLM disabled
    reset_response = client.post("/api/reset", json={"seed": 42, "use_llm": False})
    assert reset_response.status_code == 200, (
        f"Failed to reset simulator: {reset_response.text}"
    )

    # Phase 1: Run 5 ticks
    print("\nPhase 1: Running 5 ticks...")
    advance_ticks(5)

    # Get state at tick 5 (State_A)
    state_a = get_state()
    assert state_a["tick"] == 5, f"Expected tick 5, got {state_a['tick']}"
    print(f"State_A recorded at tick {state_a['tick']}")

    # Continue to tick 10
    print("Continuing to tick 10...")
    advance_ticks(5)  # 5 more ticks to reach tick 10

    state_at_10 = get_state()
    assert state_at_10["tick"] == 10, f"Expected tick 10, got {state_at_10['tick']}"
    print(f"Reached tick {state_at_10['tick']}")

    # Phase 2: Rewind to tick 5
    print("\nPhase 2: Rewinding to tick 5...")
    rewind_to(5)

    # Get state at tick 5 after rewind (State_B)
    state_b = get_state()
    assert state_b["tick"] == 5, f"Expected tick 5 after rewind, got {state_b['tick']}"
    print(f"State_B recorded at tick {state_b['tick']}")

    # Assert State_A == State_B
    print("\nAsserting State_A == State_B...")

    # Compare critical fields
    fields_to_compare = ["tick", "resources", "agents", "game_over", "history_size"]

    for field in fields_to_compare:
        assert field in state_a, f"Field {field} missing in State_A"
        assert field in state_b, f"Field {field} missing in State_B"

        if field == "resources":
            # Compare resource dictionaries
            for resource in state_a["resources"]:
                a_val = state_a["resources"][resource]
                b_val = state_b["resources"][resource]
                assert abs(a_val - b_val) < 0.01, (
                    f"Resource {resource} mismatch: {a_val} vs {b_val}"
                )
        elif field == "agents":
            # Compare agent states
            for agent_name in state_a["agents"]:
                assert agent_name in state_b["agents"], (
                    f"Agent {agent_name} missing in State_B"
                )

                agent_a = state_a["agents"][agent_name]
                agent_b = state_b["agents"][agent_name]

                # Compare agent attributes
                for attr in ["name", "health", "mental_state", "location", "is_alive"]:
                    if attr in agent_a and attr in agent_b:
                        if attr in ["health", "mental_state"]:
                            # Float comparison with tolerance
                            assert abs(agent_a[attr] - agent_b[attr]) < 0.01, (
                                f"Agent {agent_name} {attr} mismatch: {agent_a[attr]} vs {agent_b[attr]}"
                            )
                        else:
                            assert agent_a[attr] == agent_b[attr], (
                                f"Agent {agent_name} {attr} mismatch: {agent_a[attr]} vs {agent_b[attr]}"
                            )
        else:
            # Direct comparison for other fields
            assert state_a[field] == state_b[field], (
                f"Field {field} mismatch: {state_a[field]} vs {state_b[field]}"
            )

    # Verify logs consistency (last few logs should match)
    if state_a.get("logs") and state_b.get("logs"):
        # Compare last 5 logs
        logs_a = state_a["logs"][-5:]
        logs_b = state_b["logs"][-5:]
        assert logs_a == logs_b, f"Recent logs mismatch. A: {logs_a}, B: {logs_b}"

    print("✓ State_A and State_B are identical")

    # Phase 3: Advance 1 tick from tick 5 to tick 6
    print("\nPhase 3: Advancing 1 tick from tick 5...")
    advance_ticks(1)

    # Get state at tick 6 (State_C)
    state_c = get_state()
    assert state_c["tick"] == 6, f"Expected tick 6, got {state_c['tick']}"
    print(f"State_C recorded at tick {state_c['tick']}")

    # Verify State_C differs from State_A (simulation continues)
    print("\nVerifying simulation continues after rewind...")

    # Check that something changed between tick 5 and tick 6
    changes_detected = False

    # 1. Check resources changed (some consumption/production should occur)
    for resource in state_a["resources"]:
        if resource in state_c["resources"]:
            diff = abs(state_a["resources"][resource] - state_c["resources"][resource])
            if diff > 0.01:
                changes_detected = True
                print(
                    f"  Resource {resource} changed: {state_a['resources'][resource]:.2f} -> {state_c['resources'][resource]:.2f}"
                )
                break

    # 2. Check logs have new entries
    if not changes_detected and state_c.get("logs"):
        # Check if new logs were added
        if len(state_c["logs"]) > len(state_a.get("logs", [])):
            changes_detected = True
            print(
                f"  New logs added: {len(state_c['logs']) - len(state_a.get('logs', []))} new entries"
            )

    # 3. Check agent states changed (health, location, etc.)
    if not changes_detected and state_a.get("agents") and state_c.get("agents"):
        for agent_name in state_a["agents"]:
            if agent_name in state_c["agents"]:
                agent_a = state_a["agents"][agent_name]
                agent_c = state_c["agents"][agent_name]

                # Check health change
                if "health" in agent_a and "health" in agent_c:
                    if abs(agent_a["health"] - agent_c["health"]) > 0.01:
                        changes_detected = True
                        print(
                            f"  Agent {agent_name} health changed: {agent_a['health']:.2f} -> {agent_c['health']:.2f}"
                        )
                        break

                # Check location change
                if "location" in agent_a and "location" in agent_c:
                    if agent_a["location"] != agent_c["location"]:
                        changes_detected = True
                        print(
                            f"  Agent {agent_name} location changed: {agent_a['location']} -> {agent_c['location']}"
                        )
                        break

    assert changes_detected, (
        "No changes detected after advancing 1 tick. Simulation may be stuck."
    )

    print("✓ Simulation continues after rewind (changes detected)")

    # Phase 4: Verify deterministic continuation after rewind
    print("\nPhase 4: Verifying deterministic continuation after rewind...")

    # Rewind back to tick 5 again to start fresh
    print("Rewinding back to tick 5...")
    rewind_to(5)

    # Run 5 ticks from tick 5 to reach tick 10 again
    print("Running 5 ticks from tick 5...")
    advance_ticks(5)

    # Get state at tick 10 after rewind (State_D)
    state_d = get_state()
    assert state_d["tick"] == 10, f"Expected tick 10, got {state_d['tick']}"
    print(f"State_D recorded at tick {state_d['tick']}")

    # Compare State_D with state_at_10 (recorded in Phase 1)
    print("Comparing State_D with original tick 10 state...")

    # They should be identical due to deterministic RNG restoration
    for field in ["tick", "resources", "agents", "game_over"]:
        if field == "resources":
            for resource in state_at_10["resources"]:
                assert resource in state_d["resources"]
                diff = abs(
                    state_at_10["resources"][resource] - state_d["resources"][resource]
                )
                assert diff < 0.01, (
                    f"Resource {resource} mismatch after rewind continuation: {state_at_10['resources'][resource]} vs {state_d['resources'][resource]}"
                )
        elif field == "agents":
            for agent_name in state_at_10["agents"]:
                assert agent_name in state_d["agents"]
                agent_original = state_at_10["agents"][agent_name]
                agent_rewind = state_d["agents"][agent_name]

                # Compare health
                if "health" in agent_original and "health" in agent_rewind:
                    diff = abs(agent_original["health"] - agent_rewind["health"])
                    assert diff < 0.01, (
                        f"Agent {agent_name} health mismatch after rewind continuation: {agent_original['health']} vs {agent_rewind['health']}"
                    )
        else:
            assert state_at_10[field] == state_d[field], (
                f"Field {field} mismatch after rewind continuation: {state_at_10[field]} vs {state_d[field]}"
            )

    print(
        "✓ Deterministic continuation verified: Same timeline reproduced after rewind"
    )
    print("✓ Time travel consistency test passed!")


def test_deterministic_simulation(client: TestClient):
    """
    Test that simulation with same seed produces identical results.
    """
    print("\nTesting deterministic simulation...")

    # Helper function to get state
    def get_state() -> Dict[str, Any]:
        response = client.get("/api/state")
        assert response.status_code == 200
        return response.json()

    # Helper function to advance ticks
    def advance_ticks(num_ticks: int):
        for _ in range(num_ticks):
            response = client.post("/api/next")
            assert response.status_code == 200

    # First run: reset with seed 100, run 7 ticks
    print("First run: seed 100, 7 ticks")
    reset1 = client.post("/api/reset", json={"seed": 100, "use_llm": False})
    assert reset1.status_code == 200

    advance_ticks(7)
    state1 = get_state()

    # Record some key metrics
    resources1 = state1["resources"].copy()
    agents1 = {name: agent.copy() for name, agent in state1["agents"].items()}

    # Second run: reset with same seed 100, run 7 ticks
    print("Second run: same seed 100, 7 ticks")
    reset2 = client.post("/api/reset", json={"seed": 100, "use_llm": False})
    assert reset2.status_code == 200

    advance_ticks(7)
    state2 = get_state()

    # Compare results
    print("Comparing results...")

    # Compare resources
    for resource in resources1:
        assert resource in state2["resources"]
        diff = abs(resources1[resource] - state2["resources"][resource])
        assert diff < 0.01, (
            f"Resource {resource} mismatch: {resources1[resource]} vs {state2['resources'][resource]}"
        )

    # Compare agent health
    for agent_name in agents1:
        assert agent_name in state2["agents"]
        health1 = agents1[agent_name]["health"]
        health2 = state2["agents"][agent_name]["health"]
        diff = abs(health1 - health2)
        assert diff < 0.01, (
            f"Agent {agent_name} health mismatch: {health1} vs {health2}"
        )

    print("✓ Deterministic simulation verified")
    print(f"  Tick: {state1['tick']} == {state2['tick']}")
    print(f"  Resources match: {state1['resources']}")


if __name__ == "__main__":
    # Run tests directly if script is executed
    pytest.main([__file__, "-v"])
