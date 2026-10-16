"""Compatibility namespace for Cricket Persona V1.

Canonical implementation lives in cricket.persona and cricket.persona_voice.
"""

from ..persona import CricketPersona, DEFAULT_CRICKET_PERSONA
from ..persona_voice import persona_line_for_finding

__all__ = [
    "CricketPersona",
    "DEFAULT_CRICKET_PERSONA",
    "persona_line_for_finding",
]
