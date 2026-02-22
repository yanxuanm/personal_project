#!/usr/bin/env python3
"""Test script for agent brains and personas."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ..env.schema import GameState
from .personas import create_all_personas
from .brain import AgentBrain


def main():
    """Test agent decision-making."""
    print("=" * 60)
    print("Project Red Dust - Agent Brain Test")
    print("=" * 60)
    
    # Create a test game state
    gamestate = GameState.create_initial_state()
    
    # Set some resource levels to test situational awareness
    gamestate.resources["oxygen"] = 45.0
    gamestate.resources["energy"] = 15.0  # Low energy
    gamestate.resources["food"] = 75.0
    gamestate.resources["water"] = 60.0
    
    gamestate.tick = 5  # Set to tick 5
    
    print(f"Test Game State (Tick {gamestate.tick}):")
    print(f"  Oxygen: {gamestate.resources['oxygen']}")
    print(f"  Energy: {gamestate.resources['energy']} (LOW)")
    print(f"  Food: {gamestate.resources['food']}")
    print(f"  Water: {gamestate.resources['water']}")
    print()
    
    # Create all personas
    personas = create_all_personas()
    
    print("Agent Decision Results:")
    print("-" * 60)
    
    actions = []  # List of (name, action) tuples
    analyses = []
    
    # Have each persona think
    for persona in personas:
        brain = AgentBrain(persona)
        
        # Get action
        action = brain.think(gamestate)
        actions.append((persona.name, action))
        
        # Get situation analysis
        analysis = brain.analyze_situation(gamestate)
        analyses.append(analysis)
        
        # Print result
        print(f"{persona.name} ({persona.role}):")
        print(f"  Personality: {persona.personality[:80]}...")
        print(f"  Secret Goal: {persona.secret_goal}")
        print(f"  Decision: {action}")
        print()
    
    # Compare decisions
    print("=" * 60)
    print("Decision Comparison:")
    print("=" * 60)
    
    action_counts = {}
    target_counts = {}
    
    for persona, action in actions:
        action_type = action.type
        target = action.target
        
        action_counts[action_type] = action_counts.get(action_type, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
    
    print("Action Types:")
    for action_type, count in sorted(action_counts.items()):
        print(f"  {action_type}: {count} agent(s)")
    
    print("\nTargets:")
    for target, count in sorted(target_counts.items()):
        print(f"  {target}: {count} agent(s)")
    
    # Show situation analyses
    print("\n" + "=" * 60)
    print("Situation Analysis (from each persona's perspective):")
    print("=" * 60)
    
    for analysis in analyses:
        print(f"\n{analysis['persona']} ({analysis['role']}):")
        print(f"  Threat Level: {analysis['threat_level']:.2f}")
        print(f"  Recommended Priority: {analysis['recommended_priority']}")
        print("  Resource Assessment:")
        for resource, assessment in analysis['resource_assessment'].items():
            print(f"    {resource}: {assessment}")
    
    # Test determinism
    print("\n" + "=" * 60)
    print("Testing Determinism...")
    print("=" * 60)
    
    # Reset game state RNG
    gamestate2 = GameState.create_initial_state()
    gamestate2.resources = gamestate.resources.copy()
    gamestate2.tick = gamestate.tick
    
    # Run again with same seed
    actions2 = []
    for persona in personas:
        brain = AgentBrain(persona)
        action = brain.think(gamestate2)
        actions2.append((persona.name, action))
    
    # Compare
    deterministic = True
    for (name1, action1), (name2, action2) in zip(actions, actions2):
        if name1 != name2:
            print(f"✗ Persona mismatch: {name1} vs {name2}")
            deterministic = False
            continue
        
        if (action1.type != action2.type or 
            action1.target != action2.target):
            print(f"✗ Action mismatch for {name1}:")
            print(f"  First run: {action1}")
            print(f"  Second run: {action2}")
            deterministic = False
    
    if deterministic:
        print("✓ Deterministic decision-making verified!")
        print("  Same seed produces identical decisions.")
    else:
        print("✗ Determinism check failed!")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    
    return 0 if deterministic else 1


if __name__ == "__main__":
    sys.exit(main())