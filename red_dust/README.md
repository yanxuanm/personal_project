# Project Red Dust

A deterministic Mars survival simulation with time travel capabilities, built as a demonstration of long-running agent harness architecture.

## Overview

Project Red Dust simulates a Mars colony with 5 unique crew members, each with distinct personalities, secret goals, and decision-making abilities. The simulation features:

- **Deterministic simulation**: Same seed = identical results every time
- **Time travel**: Rewind to any previous tick and create new timeline branches
- **Resource management**: Oxygen, water, energy, and food systems
- **Agent personalities**: 5 crew members with hidden agendas and behavioral patterns
- **Random events**: Solar panel failures, system malfunctions, mental breakdowns
- **Web interface**: Real-time visualization and control panel

## Architecture

The project implements the "Effective Harnesses for Long-running Agents" principles from Anthropic's research:

- **DeterministicRandom**: Serializable random number generator for reproducible simulations
- **VirtualClock**: Time abstraction for discrete tick-based simulation
- **GameState**: Complete state serialization for time travel
- **AgentBrain**: Decision-making with persona-based preferences (mock + LLM placeholder)
- **SimulationController**: Main loop with history tracking and time travel
- **Web Dashboard**: God's-eye view of the simulation with real-time controls

## Project Structure

```
red_dust/
├── __init__.py
├── main.py                    # CLI entry point
├── simulation.py              # Main simulation controller
├── test_simulation.py         # Integration tests
│
├── harness/                   # Deterministic core
│   ├── clock.py              # VirtualClock for time abstraction
│   ├── rand_gen.py           # DeterministicRandom with serialization
│   └── test_harness.py       # Harness component tests
│
├── env/                       # Mars environment
│   ├── schema.py             # GameState and Agent data classes
│   ├── mars.py               # MarsEnvironment with resource systems
│   └── test_env.py           # Environment tests
│
├── agents/                    # Crew member AI
│   ├── schema.py             # AgentAction and Persona definitions
│   ├── personas.py           # 5 predefined crew personas
│   ├── brain.py              # AgentBrain (mock + LLM placeholder)
│   └── test_agents.py        # Agent decision tests
│
├── server/                    # Web interface
│   ├── api.py                # FastAPI REST API
│   └── static/
│       └── index.html        # Vue.js dashboard
│
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
# Install required packages for core simulation and web interface
pip install fastapi uvicorn

# For LLM integration (optional)
pip install openai python-dotenv

# For development and testing
pip install pytest httpx  # For testing
```

The core simulation works with only Python standard library plus FastAPI/Uvicorn. LLM integration requires additional packages as shown above.

## Quick Start

### 1. Run the CLI Simulation

```bash
cd red_dust
python main.py
```

Follow the interactive prompts to control the simulation.

### 2. Run the Web Interface

```bash
# From the red_dust directory
python -m red_dust.server.api
```

Or using uvicorn directly:

```bash
uvicorn red_dust.server.api:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser to: http://localhost:8000/static/index.html

### 3. Run Tests

```bash
# Test harness components
python harness/test_harness.py

# Test environment
python env/test_env.py

# Test agents
python agents/test_agents.py

# Test full simulation
python test_simulation.py
```

## Usage

### CLI Interface

The command-line interface supports:

- `n` - Advance one tick
- `r [tick]` - Rewind to specified tick
- `s` - Show current status
- `q` - Quit

### Web Dashboard

The web interface provides:

1. **Resource Dashboard**: Real-time gauges for oxygen, water, energy, and food
2. **Crew Status**: Health and mental state of all 5 agents
3. **Event Log**: Timeline of simulation events
4. **Time Travel Slider**: Drag to any tick and rewind
5. **Auto-refresh**: Updates every second

### API Endpoints

- `GET /api/state` - Get current simulation state
- `POST /api/next` - Advance simulation by one tick
- `POST /api/rewind/{tick}` - Rewind to specific tick
- `POST /api/reset` - Reset simulation (optional seed parameter)
- `GET /api/history` - Get timeline data

## Crew Members

1. **Commander Chen** - Rational leader, will sacrifice anything for survival
2. **Engineer Tanaka** - Brilliant but pessimistic, prioritizes systems over people
3. **Dr. Rodriguez** - Empathetic to a fault, will waste resources to save anyone
4. **Botanist Schmidt** - Obsessed with potato experiments, indifferent to crew
5. **Pilot Okafor** - Hidden spy, sabotages systems while ensuring personal survival

## Deterministic Time Travel

The simulation implements true time travel:

1. **State Serialization**: Complete GameState saved every tick
2. **RNG State Tracking**: Random number generator state preserved
3. **Branching Timelines**: Rewinding discards "future" history
4. **Deterministic Replay**: Same seed produces identical timeline

## Extending the Project

### Adding New Agent Actions

1. Edit `agents/schema.py` to define new action types
2. Update `env/mars.py` `_process_actions()` method to handle new actions
3. Modify `agents/brain.py` to include new actions in decision-making

### Integrating Real LLMs (DeepSeek API)

The `AgentBrain` class now includes full LLM integration using DeepSeek API. To enable:

1. **Get a DeepSeek API key** from [platform.deepseek.com](https://platform.deepseek.com)
2. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```
3. **Edit the `.env` file** and replace `your_deepseek_api_key_here` with your actual API key.
3. **Install LLM dependencies**:
   ```bash
   pip install openai python-dotenv
   ```
4. **Enable LLM mode**:
   - **CLI**: When starting the simulation, answer "y" to "Enable LLM mode?"
   - **Web interface**: Use the reset endpoint with `use_llm=true` parameter
   - **Programmatic**: Initialize `SimulationController(use_llm=True)`

The integration includes:
- **Persona-aware prompts**: Each agent's personality and secret goal included in system prompt
- **Structured JSON output**: LLM returns actions in strict JSON format
- **Graceful fallback**: If API key is missing or LLM fails, agents automatically use mock logic
- **Determinism preserved**: LLM decisions are not deterministic; use only for exploration, not time travel scenarios

**Note**: LLM mode consumes API credits and may be slower than mock logic. For deterministic time travel, keep LLM disabled.

### Customizing Resource Systems

Edit `env/mars.py` to:
- Adjust consumption/production rates
- Add new resource types
- Create more complex disaster scenarios

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Make sure you're in the right directory
cd red_dust

# Or run as module
python -m red_dust.main
```

### Web Interface Not Loading

- Ensure FastAPI server is running (`uvicorn red_dust.server.api:app --reload`)
- Check browser console for JavaScript errors
- Verify CORS settings in `server/api.py` if accessing from different origin

### Simulation Determinism Issues

- Verify `DeterministicRandom` state is being properly serialized in `GameState.rng_state`
- Check that `time_travel()` method correctly restores RNG state
- Ensure no external randomness sources are used

## Future Enhancements

Potential improvements:

1. **Multi-agent Collaboration**: Agents working together on complex tasks
2. **Research Tree**: Technology progression for colony development
3. **External Events**: Mars storms, supply drops, communication blackouts
4. **Save/Load System**: Persistent simulation states across sessions
5. **LLM Integration**: Already implemented with DeepSeek API (see above)
6. **Multiplayer**: Human players taking on crew roles

## Credits

This project implements concepts from Anthropic's research on "Effective Harnesses for Long-running Agents" (https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

Built as an educational demonstration of deterministic simulation, agent-based modeling, and time travel architectures.

## License

Educational Use - See project documentation for details.