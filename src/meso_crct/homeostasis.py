"""Generic homeostatic modulation for MESO-CRCT.

Homeostatic state is represented as named need axes. A target may advertise a
bounded corrective affordance for one or more needs. The strongest matching
deficit can raise incentive salience without changing hedonic pleasure.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


def _unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(0.0, value))


@dataclass(frozen=True, slots=True)
class NeedAxis:
    need_id: str
    setpoint: float
    current_level: float
    sensitivity: float = 1.0

    def __post_init__(self) -> None:
        if not self.need_id.strip():
            raise ValueError("need_id must be non-empty")
        for name in ("setpoint", "current_level", "sensitivity"):
            object.__setattr__(self, name, _unit(getattr(self, name), name=name))

    @property
    def deficit(self) -> float:
        return max(0.0, self.setpoint - self.current_level) * self.sensitivity

    @property
    def surplus(self) -> float:
        return max(0.0, self.current_level - self.setpoint) * self.sensitivity


@dataclass(frozen=True, slots=True)
class HomeostaticState:
    axes: tuple[NeedAxis, ...] = ()

    def __post_init__(self) -> None:
        ids = [axis.need_id for axis in self.axes]
        if len(ids) != len(set(ids)):
            raise ValueError("homeostatic need_id values must be unique")

    def axis(self, need_id: str) -> NeedAxis | None:
        for axis in self.axes:
            if axis.need_id == need_id:
                return axis
        return None


@dataclass(frozen=True, slots=True)
class NeedAffordance:
    need_id: str
    corrective_strength: float

    def __post_init__(self) -> None:
        if not self.need_id.strip():
            raise ValueError("need_id must be non-empty")
        object.__setattr__(
            self,
            "corrective_strength",
            _unit(self.corrective_strength, name="corrective_strength"),
        )


@dataclass(frozen=True, slots=True)
class HomeostaticModulation:
    base_incentive: float
    effective_incentive: float
    boost: float
    dominant_need: str | None


def modulate_incentive_salience(
    *,
    base_incentive: float,
    homeostasis: HomeostaticState,
    affordances: Iterable[NeedAffordance],
) -> HomeostaticModulation:
    """Apply the strongest matching corrective need as a bounded incentive boost.

    Multiple weak needs are not summed into an artificial extreme. The boost
    uses the strongest matched deficit x corrective affordance.
    """
    base = _unit(base_incentive, name="base_incentive")
    candidates: list[tuple[str, float]] = []

    for affordance in affordances:
        axis = homeostasis.axis(affordance.need_id)
        if axis is None:
            continue
        candidates.append(
            (
                axis.need_id,
                axis.deficit * affordance.corrective_strength,
            )
        )

    if not candidates:
        return HomeostaticModulation(
            base_incentive=base,
            effective_incentive=base,
            boost=0.0,
            dominant_need=None,
        )

    dominant_need, boost = max(candidates, key=lambda item: item[1])
    effective = base + (1.0 - base) * boost
    return HomeostaticModulation(
        base_incentive=base,
        effective_incentive=effective,
        boost=boost,
        dominant_need=dominant_need if boost > 0.0 else None,
    )
