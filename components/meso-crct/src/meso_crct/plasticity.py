"""Bounded plasticity proposals for persistent association learning.

Transient reward/salience state does not directly mutate permanent preference.
This module emits bounded, receipt-bound association-update candidates from an
explicit teaching signal.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .circuit import CircuitState
from .provenance import TransitionReceipt, state_fingerprint


def _unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(0.0, value))


def _signed_unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(-1.0, value))


@dataclass(frozen=True, slots=True)
class PlasticityPolicy:
    maximum_absolute_delta: float
    minimum_salience_gate: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "maximum_absolute_delta",
            _unit(self.maximum_absolute_delta, name="maximum_absolute_delta"),
        )
        object.__setattr__(
            self,
            "minimum_salience_gate",
            _unit(self.minimum_salience_gate, name="minimum_salience_gate"),
        )


class PlasticityReceiptMismatch(ValueError):
    pass


_PLASTICITY_CANDIDATE_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class PlasticityCandidate:
    association_id: str
    delta: float
    teaching_signal: float
    salience_gate: float
    gate_driver: str | None
    transition_receipt_id: str

    def __init__(
        self,
        association_id: str,
        delta: float,
        teaching_signal: float,
        salience_gate: float,
        gate_driver: str | None,
        transition_receipt_id: str,
        *,
        _token: object | None = None,
    ) -> None:
        if _token is not _PLASTICITY_CANDIDATE_TOKEN:
            raise TypeError(
                "PlasticityCandidate must be created by propose_plasticity"
            )
        if not association_id.strip():
            raise ValueError("association_id must be non-empty")
        if not transition_receipt_id.strip():
            raise ValueError("transition_receipt_id must be non-empty")
        object.__setattr__(self, "association_id", association_id)
        object.__setattr__(self, "delta", _signed_unit(delta, name="delta"))
        object.__setattr__(
            self,
            "teaching_signal",
            _signed_unit(teaching_signal, name="teaching_signal"),
        )
        object.__setattr__(
            self,
            "salience_gate",
            _unit(salience_gate, name="salience_gate"),
        )
        object.__setattr__(self, "gate_driver", gate_driver)
        object.__setattr__(
            self,
            "transition_receipt_id",
            transition_receipt_id,
        )


def propose_plasticity(
    *,
    state: CircuitState,
    association_id: str,
    receipt: TransitionReceipt,
    policy: PlasticityPolicy,
) -> PlasticityCandidate:
    """Create a bounded persistent-learning candidate from a matching receipt."""
    if receipt.after_fingerprint != state_fingerprint(state):
        raise PlasticityReceiptMismatch(
            "plasticity state does not match receipt after-state fingerprint"
        )

    gates = (
        ("semantic_relevance", state.salience.semantic_relevance),
        ("motivational_salience", state.salience.motivational_salience),
        ("incentive_salience", state.salience.incentive_salience),
        ("epistemic_value", state.salience.epistemic_value),
    )
    gate_driver, gate = max(gates, key=lambda item: item[1])
    teaching_signal = state.learning.prediction_error

    if gate < policy.minimum_salience_gate or teaching_signal == 0.0:
        delta = 0.0
        gate_driver_out: str | None = gate_driver if gate > 0.0 else None
    else:
        delta = teaching_signal * gate * policy.maximum_absolute_delta
        gate_driver_out = gate_driver

    return PlasticityCandidate(
        association_id=association_id,
        delta=delta,
        teaching_signal=teaching_signal,
        salience_gate=gate,
        gate_driver=gate_driver_out,
        transition_receipt_id=receipt.receipt_id,
        _token=_PLASTICITY_CANDIDATE_TOKEN,
    )


def preview_association_strength(
    current_strength: float,
    candidate: PlasticityCandidate,
) -> float:
    """Preview an association update without persisting it."""
    current = _signed_unit(current_strength, name="current_strength")
    return _signed_unit(current + candidate.delta, name="resulting_strength")
