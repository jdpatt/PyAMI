from dataclasses import dataclass


@dataclass
class Package:
    resistance: float = 0
    inductance: float = 0
    capacitance: float = 0
