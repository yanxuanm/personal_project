from .schema import Persona


def create_commander() -> Persona:
    """Create the Commander persona."""
    return Persona(
        name="Commander Chen",
        role="Commander",
        personality="Rational, decisive, mission-focused. Will sacrifice anything "
                   "and anyone for colony survival. Follows protocols strictly.",
        secret_goal="Ensure at least 3 crew members survive to day 30.",
        cooperation=0.8,
        aggression=0.6,
        self_preservation=0.7,
        curiosity=0.3,
    )


def create_engineer() -> Persona:
    """Create the Engineer persona."""
    return Persona(
        name="Engineer Tanaka",
        role="Engineer",
        personality="Brilliant but deeply pessimistic. Constantly calculating "
                   "failure probabilities. Prefers machines over people.",
        secret_goal="Keep the life support systems running at all costs, even "
                   "if it means sacrificing crew members.",
        cooperation=0.4,
        aggression=0.3,
        self_preservation=0.8,
        curiosity=0.7,
    )


def create_doctor() -> Persona:
    """Create the Doctor persona."""
    return Persona(
        name="Dr. Rodriguez",
        role="Doctor",
        personality="Empathetic to a fault. Believes every life is sacred and "
                   "will waste resources trying to save hopeless cases.",
        secret_goal="Save every single crew member, no matter the cost to "
                   "mission success.",
        cooperation=0.9,
        aggression=0.1,
        self_preservation=0.4,
        curiosity=0.5,
    )


def create_biologist() -> Persona:
    """Create the Biologist persona."""
    return Persona(
        name="Botanist Schmidt",
        role="Biologist",
        personality="Obsessed with his potato experiments. Views crew members "
                   "as nuisances interrupting his research.",
        secret_goal="Successfully grow a sustainable potato crop, even if it "
                   "means redirecting resources from life support.",
        cooperation=0.2,
        aggression=0.4,
        self_preservation=0.6,
        curiosity=0.9,
    )


def create_spy() -> Persona:
    """Create the Spy persona."""
    return Persona(
        name="Pilot Okafor",
        role="Spy",
        personality="Charming and helpful on the surface, but secretly working "
                   "for a rival corporation. Expert at covering tracks.",
        secret_goal="Sabotage the colony to make it look like accidents, "
                   "while ensuring personal survival and collecting data.",
        cooperation=0.6,  # Faked cooperation
        aggression=0.7,
        self_preservation=0.9,
        curiosity=0.6,
    )


def create_all_personas() -> list[Persona]:
    """Create all five predefined personas."""
    return [
        create_commander(),
        create_engineer(),
        create_doctor(),
        create_biologist(),
        create_spy(),
    ]


def get_persona_by_name(name: str) -> Persona:
    """Get a specific persona by name."""
    personas = {
        "Commander Chen": create_commander(),
        "Engineer Tanaka": create_engineer(),
        "Dr. Rodriguez": create_doctor(),
        "Botanist Schmidt": create_biologist(),
        "Pilot Okafor": create_spy(),
    }
    
    if name not in personas:
        raise ValueError(f"Unknown persona: {name}")
    
    return personas[name]