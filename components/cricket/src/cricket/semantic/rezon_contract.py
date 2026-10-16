from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RezonSemanticDimension(str, Enum):
    PROPOSITION = "PROPOSITION"
    REFERENT = "REFERENT"
    SCOPE = "SCOPE"
    MODALITY = "MODALITY"
    TEMPORAL_SCOPE = "TEMPORAL_SCOPE"
    PROVENANCE = "PROVENANCE"
    AUTHORITY = "AUTHORITY"
    ADVERSARIAL_FIDELITY = "ADVERSARIAL_FIDELITY"


@dataclass(frozen=True)
class RezonSemanticContract:
    repository: str
    commit: str
    relationship: str
    runtime_required: bool
    package_import: str
    dimensions: tuple[RezonSemanticDimension, ...]
    source_paths: tuple[str, ...]


REZON_CONTRACT = RezonSemanticContract(
    repository="thebrazenbeard/rezon",
    commit="ec401810990337bf07a5d6473782ba13eba1bb3f",
    relationship="SEMANTIC_UPSTREAM",
    runtime_required=False,
    package_import="",
    dimensions=(
        RezonSemanticDimension.PROPOSITION,
        RezonSemanticDimension.REFERENT,
        RezonSemanticDimension.SCOPE,
        RezonSemanticDimension.MODALITY,
        RezonSemanticDimension.TEMPORAL_SCOPE,
        RezonSemanticDimension.PROVENANCE,
        RezonSemanticDimension.AUTHORITY,
        RezonSemanticDimension.ADVERSARIAL_FIDELITY,
    ),
    source_paths=(
        "docs/EXECUTABLE_FRAMEWORK_DIRECTION.md",
        "docs/ADVERSARIAL_COLLABORATION.md",
        "docs/SEMANTIC_PROVENANCE.md",
        "docs/EVALUATION_AND_FALSIFICATION.md",
        "src/rezon/envelopes.py",
        "src/rezon/hostile.py",
        "src/rezon/interop.py",
    ),
)
