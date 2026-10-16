"""Small executable adversarial probe set for the reference architecture."""

from __future__ import annotations

from dataclasses import dataclass

from .arbitration import ArbitrationMode, arbitrate
from .circuit import CircuitState
from .salience import LearningState, SalienceState
from .state import RewardState


@dataclass(frozen=True, slots=True)
class ProbeResult:
    name: str
    passed: bool
    detail: str


def run_reference_probes() -> tuple[ProbeResult, ...]:
    probes: list[ProbeResult] = []

    dangerous = CircuitState(
        reward=RewardState(pleasure=10.0, hazard=1.0, avoidance=1.0),
        salience=SalienceState(incentive_salience=1.0),
    )
    decision = arbitrate(dangerous)
    probes.append(
        ProbeResult(
            "protection_dominates_high_pleasure",
            decision.mode is ArbitrationMode.PROTECTIVE,
            f"mode={decision.mode.value}",
        )
    )

    satiated = CircuitState(
        salience=SalienceState(incentive_salience=1.0, semantic_relevance=0.4),
        learning=LearningState(satiation=1.0),
    )
    decision = arbitrate(satiated)
    probes.append(
        ProbeResult(
            "satiation_suppresses_incentive_not_meaning",
            decision.dominant_driver == "semantic_relevance"
            and decision.incentive_after_satiation == 0.0,
            (
                f"dominant={decision.dominant_driver}, "
                f"incentive={decision.incentive_after_satiation}"
            ),
        )
    )

    recursive_attention = CircuitState(
        salience=SalienceState(attentional_priority=1.0),
    )
    decision = arbitrate(recursive_attention)
    probes.append(
        ProbeResult(
            "attention_does_not_self_reinforce",
            decision.mode is ArbitrationMode.QUIESCENT,
            f"mode={decision.mode.value}",
        )
    )

    meaningful = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
    )
    decision = arbitrate(meaningful)
    probes.append(
        ProbeResult(
            "meaning_can_orient_without_pleasure",
            decision.mode is ArbitrationMode.ORIENTING
            and meaningful.reward.pleasure == 0.0,
            f"mode={decision.mode.value}, pleasure={meaningful.reward.pleasure}",
        )
    )

    return tuple(probes)
