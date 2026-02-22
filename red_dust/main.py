#!/usr/bin/env python3
"""Main entry point for Project Red Dust simulation."""

import sys
from .simulation import run_interactive_simulation


def main():
    """Main CLI entry point."""
    print("=" * 60)
    print("PROJECT RED DUST - Mars Survival Simulation")
    print("=" * 60)
    print()
    print("A deterministic simulation of a Mars colony with time travel.")
    print("Features:")
    print("  • 5 unique crew members with personalities and secret goals")
    print("  • Resource management (oxygen, water, energy, food)")
    print("  • Random events and disasters")
    print("  • Time travel - rewind to any previous tick")
    print("  • Deterministic simulation - same seed = same results")
    print()
    
    # Get seed from user or use default
    seed_input = input("Enter seed number (press Enter for default 42): ").strip()
    if seed_input == "":
        seed = 42
    else:
        try:
            seed = int(seed_input)
        except ValueError:
            print("Invalid seed. Using default 42.")
            seed = 42
    
    # Ask about LLM mode
    llm_input = input("Enable LLM mode? (y/N): ").strip().lower()
    use_llm = llm_input in ('y', 'yes')
    
    if use_llm:
        print("Note: LLM mode requires a valid DEEPSEEK_API_KEY in .env file")
        print("If API key is missing or invalid, agents will fall back to mock logic.")
    
    print(f"\nStarting simulation with seed {seed}, LLM mode: {use_llm}...")
    print("=" * 60)
    
    # Run interactive simulation
    run_interactive_simulation(seed, use_llm=use_llm)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())