"""
FastAPI server for Project Red Dust simulation.

Provides REST API endpoints for controlling the simulation and a web interface
for visualizing the state of the Mars colony.
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from red_dust.simulation import SimulationController
from red_dust.env.schema import MissionStatus


# Global simulation controller (singleton)
sim_controller: Optional[SimulationController] = None


class ResetRequest(BaseModel):
    seed: int = 42
    use_llm: bool = False


class DecisionResolveRequest(BaseModel):
    decision_id: str
    option_index: int


def init_simulation(seed: int = 42, use_llm: bool = False):
    """Initialize the global simulation controller."""
    global sim_controller
    if sim_controller is None:
        sim_controller = SimulationController(seed=seed, use_llm=use_llm)
        print(f"Simulation initialized with seed {seed}, LLM mode: {use_llm}")
    return sim_controller


# Initialize simulation with default seed (mock mode)
init_simulation(42, use_llm=False)

# Create FastAPI app
app = FastAPI(
    title="Project Red Dust API",
    description="API for controlling Mars survival simulation with time travel",
    version="1.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path, html=True), name="static")


@app.get("/")
async def root():
    """Redirect to the web interface."""
    return {
        "message": "Project Red Dust API is running. Visit /static/index.html for the web interface."
    }


@app.get("/api/state")
async def get_state():
    """Get current simulation state."""
    if sim_controller is None:
        raise HTTPException(status_code=500, detail="Simulation not initialized")

    try:
        # Get current status
        status = sim_controller.get_current_status()

        # Get detailed state
        state = sim_controller.env.state

        # Prepare response
        response = {
            "tick": state.tick,
            "resources": state.resources,
            "agents": {},
            "logs": state.logs[-20:],  # Last 20 logs
            "history_size": len(sim_controller.history),
            "game_over": state.is_game_over(),
            "status": status,
            "pending_decisions": [
                d.to_dict() for d in state.pending_decisions if not d.resolved
            ],
            "missions": [
                m.to_dict()
                for m in state.missions
                if m.status == MissionStatus.ACTIVE.value
            ],
        }

        # Add agent details
        for name, agent in state.agents.items():
            response["agents"][name] = {
                "name": agent.name,
                "health": agent.health,
                "mental_state": agent.mental_state,
                "location": agent.location,
                "is_alive": agent.is_alive(),
            }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting state: {str(e)}")


@app.post("/api/next")
async def next_tick():
    """Advance simulation by one tick."""
    if sim_controller is None:
        raise HTTPException(status_code=500, detail="Simulation not initialized")

    try:
        # Execute one simulation tick
        game_over = sim_controller.step()

        # Get updated state
        return await get_state()

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error advancing simulation: {str(e)}"
        )


@app.post("/api/rewind/{tick}")
async def rewind(tick: int):
    """Rewind simulation to a specific tick."""
    if sim_controller is None:
        raise HTTPException(status_code=500, detail="Simulation not initialized")

    try:
        # Perform time travel
        success = sim_controller.time_travel(tick)

        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot rewind to tick {tick}. Valid range: 0-{len(sim_controller.history) - 1}",
            )

        # Get updated state
        return await get_state()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rewinding simulation: {str(e)}"
        )


@app.post("/api/reset")
async def reset_simulation(request: ResetRequest):
    """Reset simulation with optional new seed and LLM mode."""
    global sim_controller

    try:
        # Reinitialize simulation
        sim_controller = SimulationController(
            seed=request.seed, use_llm=request.use_llm
        )

        # Get initial state
        return await get_state()

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error resetting simulation: {str(e)}"
        )


@app.post("/api/decision/resolve")
async def resolve_decision(request: DecisionResolveRequest):
    """Resolve a pending decision with the chosen option."""
    if sim_controller is None:
        raise HTTPException(status_code=500, detail="Simulation not initialized")

    try:
        result = sim_controller.env.resolve_decision(
            request.decision_id, request.option_index
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to resolve decision"),
            )

        return await get_state()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error resolving decision: {str(e)}"
        )


@app.get("/api/history")
async def get_history():
    """Get history information (ticks and resource snapshots)."""
    if sim_controller is None:
        raise HTTPException(status_code=500, detail="Simulation not initialized")

    try:
        # Extract resource history for timeline
        history_data = []
        for i, state in enumerate(sim_controller.history):
            history_data.append(
                {
                    "tick": i,
                    "oxygen": state.resources.get("oxygen", 0),
                    "water": state.resources.get("water", 0),
                    "energy": state.resources.get("energy", 0),
                    "food": state.resources.get("food", 0),
                }
            )

        return {
            "history": history_data,
            "max_tick": len(sim_controller.history) - 1,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


if __name__ == "__main__":
    # Run with: python -m red_dust.server.api
    uvicorn.run("red_dust.server.api:app", host="0.0.0.0", port=8000, reload=True)
