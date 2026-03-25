from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DiamondInputSchema:
    carat: float
    cut: str
    color: str
    clarity: str
    depth: float
    table: float
    x: float
    y: float
    z: float

    def to_dict(self) -> dict:
        return {
            "carat": float(self.carat),
            "cut": str(self.cut),
            "color": str(self.color),
            "clarity": str(self.clarity),
            "depth": float(self.depth),
            "table": float(self.table),
            "x": float(self.x),
            "y": float(self.y),
            "z": float(self.z),
        }