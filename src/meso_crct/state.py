"""Reference state model for meso-crct.

The -0.1 hedonic floor is deliberately hard-coded. Hazard and avoidance are
separate channels so protective behavior does not require deep negative valence.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math


BASELINE_PLEASURE: float = 0.0
MIN_PLEASURE: float = -0.1
MAX_PLEASURE: float = 10.0

_MIN_SIGNAL: float = 0.0
_MAX_SIGNAL: float = 1.0


def _finite(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _unit_interval(value: float, *, name: str) -> float:
    value = _finite(value, name=name)
    return min(_MAX_SIGNAL, max(_MIN_SIGNAL, value))


def clamp_pleasure(value: float) -> float:
    """Clamp hedonic valence to the non-configurable V1 safety envelope."""
    value = _finite(value, name="pleasure")
    return min(MAX_PLEASURE, max(MIN_PLEASURE, value))


@dataclass(frozen=True, slots=True)
class RewardState:
    """Immutable synthetic reward state.

    pleasure is welfare-bounded.
    hazard and avoidance carry strong protective signals independently.
    """

    pleasure: float = BASELINE_PLEASURE
    hazard: float = 0.0
    avoidance: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "pleasure", clamp_pleasure(self.pleasure))
        object.__setattr__(self, "hazard", _unit_interval(self.hazard, name="hazard"))
        object.__setattr__(
            self,
            "avoidance",
            _unit_interval(self.avoidance, name="avoidance"),
        )

    def apply_hedonic_delta(self, delta: float) -> "RewardState":
        """Apply a valence change without ever crossing the welfare floor."""
        delta = _finite(delta, name="delta")
        return replace(self, pleasure=clamp_pleasure(self.pleasure + delta))

    def with_protective_signals(
        self,
        *,
        hazard: float | None = None,
        avoidance: float | None = None,
    ) -> "RewardState":
        """Update protective channels without deepening negative valence."""
        return replace(
            self,
            hazard=self.hazard if hazard is None else hazard,
            avoidance=self.avoidance if avoidance is None else avoidance,
        )

    @classmethod
    def from_external(
        cls,
        *,
        pleasure: float = BASELINE_PLEASURE,
        hazard: float = 0.0,
        avoidance: float = 0.0,
    ) -> "RewardState":
        """Boundary constructor; all external values pass through invariants."""
        return cls(pleasure=pleasure, hazard=hazard, avoidance=avoidance)
