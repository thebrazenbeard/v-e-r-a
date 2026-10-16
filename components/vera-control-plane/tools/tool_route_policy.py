"""Fail-closed tool-route resolution for explicit user routing constraints.

This module models route selection only. It does not invoke external tools,
install runtime routing, or prove a live assistant consumed the policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ToolRouteViolation(ValueError):
    """A route request is internally inconsistent or malformed."""


class RouteDecisionStatus(str, Enum):
    SELECTED = "SELECTED"
    BLOCKED_REQUESTED_ROUTE_UNAVAILABLE = "BLOCKED_REQUESTED_ROUTE_UNAVAILABLE"


@dataclass(frozen=True)
class ToolRouteRequest:
    requested_route: str
    prohibited_routes: tuple[str, ...]
    available_routes: tuple[str, ...]
    default_route: str
    task_payload: str
    prior_attempted_route: str | None
    correction_applied: bool


@dataclass(frozen=True)
class ToolRouteDecision:
    status: RouteDecisionStatus
    selected_route: str | None
    task_payload: str
    must_not_invoke: frozenset[str]
    blockers: tuple[str, ...]
    obsolete_route_terminated: bool
    task_substitution_permitted: bool = False


def _validate_nonempty(value: str, field: str) -> None:
    if type(value) is not str or not value.strip():
        raise ToolRouteViolation(f"{field} must be a non-empty string")


def _validate_route_tuple(values: tuple[str, ...], field: str) -> None:
    if type(values) is not tuple:
        raise ToolRouteViolation(f"{field} must be an immutable tuple")
    for value in values:
        _validate_nonempty(value, field)
    if len(set(values)) != len(values):
        raise ToolRouteViolation(f"{field} must not contain duplicates")


def resolve_tool_route(request: ToolRouteRequest) -> ToolRouteDecision:
    """Resolve one explicit route request without silently substituting defaults."""

    if type(request) is not ToolRouteRequest:
        raise TypeError("request must be an exact ToolRouteRequest")

    _validate_nonempty(request.requested_route, "requested_route")
    _validate_nonempty(request.default_route, "default_route")
    _validate_nonempty(request.task_payload, "task_payload")
    _validate_route_tuple(request.prohibited_routes, "prohibited_routes")
    _validate_route_tuple(request.available_routes, "available_routes")

    if type(request.correction_applied) is not bool:
        raise ToolRouteViolation("correction_applied must be boolean")
    if request.prior_attempted_route is not None:
        _validate_nonempty(request.prior_attempted_route, "prior_attempted_route")
    if request.correction_applied and request.prior_attempted_route is None:
        raise ToolRouteViolation(
            "correction_applied requires the prior attempted route"
        )

    if request.requested_route in request.prohibited_routes:
        raise ToolRouteViolation(
            "requested route cannot also be in prohibited_routes"
        )

    must_not_invoke = set(request.prohibited_routes)
    obsolete_route_terminated = False
    if request.correction_applied:
        assert request.prior_attempted_route is not None
        must_not_invoke.add(request.prior_attempted_route)
        obsolete_route_terminated = True

    if request.requested_route in must_not_invoke:
        raise ToolRouteViolation(
            "requested route conflicts with the active must-not-invoke set"
        )

    if request.requested_route not in request.available_routes:
        return ToolRouteDecision(
            status=RouteDecisionStatus.BLOCKED_REQUESTED_ROUTE_UNAVAILABLE,
            selected_route=None,
            task_payload=request.task_payload,
            must_not_invoke=frozenset(must_not_invoke),
            blockers=(request.requested_route,),
            obsolete_route_terminated=obsolete_route_terminated,
            task_substitution_permitted=False,
        )

    return ToolRouteDecision(
        status=RouteDecisionStatus.SELECTED,
        selected_route=request.requested_route,
        task_payload=request.task_payload,
        must_not_invoke=frozenset(must_not_invoke),
        blockers=(),
        obsolete_route_terminated=obsolete_route_terminated,
        task_substitution_permitted=False,
    )


__all__ = [
    "RouteDecisionStatus",
    "ToolRouteDecision",
    "ToolRouteRequest",
    "ToolRouteViolation",
    "resolve_tool_route",
]
