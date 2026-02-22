#!/usr/bin/env python3
"""Test simulation controller with time travel."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from red_dust.simulation import SimulationController


def test_basic_simulation():
    """Test basic simulation progression."""
    controller = SimulationController(seed=123)
    
    # Run 3 ticks
    for i in range(3):
        game_over = controller.step()
        assert not game_over, "Game over reached unexpectedly!"
    
    # Check history size
    status = controller.get_current_status()
    assert status['tick'] == 3, f"Expected tick 3, got {status['tick']}"
    assert len(controller.history) == 4, f"Expected 4 history states, got {len(controller.history)}"


def test_time_travel():
    """Test time travel functionality."""
    controller = SimulationController(seed=456)
    
    # Run 5 ticks and record resource levels at tick 2
    tick2_resources = None
    for i in range(5):
        controller.step()
        if i == 1:
            tick2_resources = controller.env.state.resources.copy()
    
    # Verify we're at tick 5
    assert controller.clock.tick == 5, f"Expected tick 5, got {controller.clock.tick}"
    
    # Time travel back to tick 2
    success = controller.time_travel(2)
    assert success, "Time travel should succeed"
    
    # Verify tick is 2
    assert controller.clock.tick == 2, f"Expected tick 2 after rewind, got {controller.clock.tick}"
    
    # Verify resources match what they were at tick 2
    current_resources = controller.env.state.resources
    for resource in tick2_resources:
        assert abs(current_resources[resource] - tick2_resources[resource]) < 0.01, \
            f"Resource {resource} mismatch after rewind"
    
    # Verify history was truncated
    assert len(controller.history) == 3, f"Expected 3 history states after rewind"


def test_determinism():
    """Test that simulation is deterministic."""
    # Run simulation A
    controller_a = SimulationController(seed=789)
    for _ in range(4):
        controller_a.step()
    
    # Run simulation B with same seed
    controller_b = SimulationController(seed=789)
    for _ in range(4):
        controller_b.step()
    
    # Compare final states
    state_a = controller_a.env.state
    state_b = controller_b.env.state
    
    # Compare resources
    for resource in state_a.resources:
        assert abs(state_a.resources[resource] - state_b.resources[resource]) < 0.01, \
            f"Resource {resource} mismatch"
    
    # Compare agent health
    for name in state_a.agents:
        agent_a = state_a.agents[name]
        agent_b = state_b.agents[name]
        assert abs(agent_a.health - agent_b.health) < 0.01, \
            f"Agent {name} health mismatch"


def main():
    """Run all tests."""
    print("=" * 60)
    print("Project Red Dust - Simulation Controller Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Simulation", test_basic_simulation),
        ("Time Travel", test_time_travel),
        ("Determinism", test_determinism),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())