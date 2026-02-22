#!/usr/bin/env python3
"""Test harness for deterministic random generator and virtual clock."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rand_gen import DeterministicRandom
from clock import VirtualClock

def test_deterministic_random_serialization():
    """Test that random generator state can be saved and restored."""
    print("Testing DeterministicRandom serialization...")
    
    # Create generator with known seed
    rng = DeterministicRandom(seed=12345)
    
    # Save initial state
    initial_state_json = rng.to_json()
    
    # Generate a few numbers
    results1 = []
    for _ in range(5):
        results1.append(rng.next_int(1, 100))
    
    # Restore to initial state
    rng_restored = DeterministicRandom.from_json(initial_state_json)
    
    # Generate same sequence again
    results2 = []
    for _ in range(5):
        results2.append(rng_restored.next_int(1, 100))
    
    # Verify sequences match
    assert results1 == results2, f"Mismatch: {results1} != {results2}"
    print(f"✓ Sequences match: {results1}")
    
    # Test float generation consistency
    rng2 = DeterministicRandom(seed=67890)
    # Save state before generating floats
    float_state = rng2.get_state()
    floats1 = [rng2.next_float() for _ in range(5)]
    
    # Restore state and generate same floats
    rng2.set_state(float_state)
    floats2 = [rng2.next_float() for _ in range(5)]
    
    assert floats1 == floats2, f"Float mismatch: {floats1} != {floats2}"
    print(f"✓ Float sequences match: {floats1[:3]}...")
    
    # Test that state can be saved mid-sequence and restored
    rng3 = DeterministicRandom(seed=999)
    mid_seq = []
    mid_state = None
    for i in range(10):
        if i == 5:
            mid_state = rng3.get_state()
        mid_seq.append(rng3.next_int(0, 10000))
    
    # Restore to mid point
    assert mid_state is not None
    rng3.set_state(mid_state)
    for i in range(5, 10):
        val = rng3.next_int(0, 10000)
        assert val == mid_seq[i], f"Mid-sequence restore failed at position {i}"
    
    print("✓ Mid-sequence restoration works")
    
    print("✓ All deterministic random tests passed\n")

def test_virtual_clock_serialization():
    """Test that virtual clock state can be saved and restored."""
    print("Testing VirtualClock serialization...")
    
    clock = VirtualClock(initial_tick=10)
    clock.step(5)
    clock.step(3)
    
    # Save state
    state_json = clock.to_json()
    
    # Modify clock
    clock.step(20)
    assert clock.tick == 38  # 10 + 5 + 3 + 20
    
    # Restore state
    clock_restored = VirtualClock.from_json(state_json)
    assert clock_restored.tick == 18  # 10 + 5 + 3
    
    # Test step after restoration
    clock_restored.step(2)
    assert clock_restored.tick == 20
    
    print(f"✓ Clock serialization works: tick={clock_restored.tick}")
    print("✓ All virtual clock tests passed\n")

def test_determinism_across_instances():
    """Test that different instances with same seed produce same results."""
    print("Testing determinism across instances...")
    
    seed = 42
    rng1 = DeterministicRandom(seed)
    rng2 = DeterministicRandom(seed)
    
    seq1 = [rng1.next_int(0, 1000) for _ in range(10)]
    seq2 = [rng2.next_int(0, 1000) for _ in range(10)]
    
    assert seq1 == seq2, f"Different sequences from same seed: {seq1} != {seq2}"
    print(f"✓ Determinism verified: first 5 values {seq1[:5]}...")
    
    # Test that choice() is also deterministic
    items = ["apple", "banana", "cherry", "date", "elderberry"]
    choices1 = [rng1.choice(items) for _ in range(5)]
    choices2 = [rng2.choice(items) for _ in range(5)]
    
    assert choices1 == choices2, f"Choice mismatch: {choices1} != {choices2}"
    print(f"✓ Choice determinism verified: {choices1}")
    
    print("✓ All determinism tests passed\n")

def test_clock_reset():
    """Test clock reset functionality."""
    print("Testing clock reset...")
    
    clock = VirtualClock(initial_tick=100)
    clock.step(50)
    assert clock.tick == 150
    
    clock.reset()
    assert clock.tick == 100
    
    print("✓ Clock reset works")
    print("✓ All reset tests passed\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Project Red Dust Harness Components")
    print("=" * 60)
    
    try:
        test_deterministic_random_serialization()
        test_virtual_clock_serialization()
        test_determinism_across_instances()
        test_clock_reset()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())