from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MethodParameterConfig:
    name: str
    type: str | None = None
    description: str | None = None

    def to_code(self) -> str:
        return f"{self.name}: {self.type}" if self.type is not None else self.name
