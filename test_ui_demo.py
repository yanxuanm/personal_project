#!/usr/bin/env python3
"""Test the new CRT-style UI by running a few simulation ticks."""

import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_ui_functionality():
    """Run a few ticks to demonstrate the UI."""
    print("=" * 60)
    print("PROJECT RED DUST - CRT TERMINAL UI DEMO")
    print("=" * 60)
    print(f"\nUI available at: http://localhost:8000/static/index.html")
    print("\nTesting UI functionality...")
    
    # First, check current state
    try:
        response = requests.get(f"{BASE_URL}/state")
        response.raise_for_status()
        state = response.json()
        print(f"✓ Initial state loaded (Tick {state['tick']})")
        print(f"  Resources: {state['resources']}")
        print(f"  Crew alive: {sum(1 for a in state['agents'].values() if a['is_alive'])}/5")
    except Exception as e:
        print(f"✗ Failed to get initial state: {e}")
        return
    
    # Run 3 ticks to show progression
    print("\nRunning 3 simulation ticks to demonstrate UI updates...")
    for i in range(3):
        try:
            print(f"\nTick {i+1}:")
            response = requests.post(f"{BASE_URL}/next")
            response.raise_for_status()
            new_state = response.json()
            
            print(f"  Tick: {new_state['tick']}")
            print(f"  Resources: {new_state['resources']}")
            
            # Show new logs
            if new_state['logs']:
                latest_log = new_state['logs'][-1] if new_state['logs'] else "No new logs"
                print(f"  Latest log: {latest_log}")
            
            time.sleep(0.5)  # Brief pause
            
        except Exception as e:
            print(f"✗ Error on tick {i+1}: {e}")
    
    # Test time travel
    print("\n\nTesting Time Travel functionality...")
    try:
        # Get history
        response = requests.get(f"{BASE_URL}/history")
        history = response.json()
        
        if history['max_tick'] >= 2:
            print(f"Rewinding to tick 2...")
            response = requests.post(f"{BASE_URL}/rewind/2")
            response.raise_for_status()
            
            # Check new state
            response = requests.get(f"{BASE_URL}/state")
            state = response.json()
            print(f"✓ Successfully rewound to tick {state['tick']}")
            print(f"  Resources after rewind: {state['resources']}")
        else:
            print("Not enough history for time travel demo")
            
    except Exception as e:
        print(f"✗ Time travel test failed: {e}")
    
    print("\n" + "=" * 60)
    print("UI DEMO COMPLETE")
    print("=" * 60)
    print("\nOpen your browser to: http://localhost:8000/static/index.html")
    print("\nUI Features to check:")
    print("1. CRT scanline overlay effect")
    print("2. Retro progress bars with character-based indicators")
    print("3. Crew cards with 'TERMINATED' stamp for deceased agents")
    print("4. Terminal-style event log with color coding")
    print("5. Blinking cursor and retro styling")
    print("6. Time travel slider with retro design")
    print("\nThe server continues running. Press Ctrl+C in the terminal to stop it.")

if __name__ == "__main__":
    test_ui_functionality()