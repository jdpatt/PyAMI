from dataclasses import dataclass


@dataclass
class Pin:
    name: str = ""
    model: str = ""
    resistance: float = 0
    inductance: float = 0
    capacitance: float = 0
