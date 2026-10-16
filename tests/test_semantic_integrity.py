from cricket.semantic import (
    Force,
    SemanticFrame,
    SemanticIntegrityAnalyzer,
    SemanticProposition,
    TransformationKind,
)


def test_semantic_analyzer_detects_modality_strengthening() -> None:
    source = SemanticFrame(
        propositions=(
            SemanticProposition(
                anchor_id="p1",
                referent="cricket",
                predicate="needs_personality",
                force=Force.PROBABLE,
            ),
        )
    )
    candidate = SemanticFrame(
        propositions=(
            SemanticProposition(
                anchor_id="p1",
                referent="cricket",
                predicate="needs_personality",
                force=Force.ASSERTED,
            ),
        )
    )

    report = SemanticIntegrityAnalyzer().compare(source, candidate)

    assert report.material_change is True
    assert [change.kind for change in report.changes] == [TransformationKind.STRENGTHENED]


def test_semantic_analyzer_detects_scope_broadening_and_narrowing() -> None:
    from cricket.semantic import SemanticScope

    source = SemanticFrame(propositions=(
        SemanticProposition(
            anchor_id="p1",
            referent="worker",
            predicate="authorized",
            scope=SemanticScope(members=frozenset({"repo-a"})),
        ),
        SemanticProposition(
            anchor_id="p2",
            referent="worker",
            predicate="can_read",
            scope=SemanticScope(members=frozenset({"repo-a", "repo-b"})),
        ),
    ))
    candidate = SemanticFrame(propositions=(
        SemanticProposition(
            anchor_id="p1",
            referent="worker",
            predicate="authorized",
            scope=SemanticScope(members=frozenset({"repo-a", "repo-b"})),
        ),
        SemanticProposition(
            anchor_id="p2",
            referent="worker",
            predicate="can_read",
            scope=SemanticScope(members=frozenset({"repo-a"})),
        ),
    ))

    report = SemanticIntegrityAnalyzer().compare(source, candidate)
    kinds = {change.anchor_id: change.kind for change in report.changes}
    assert kinds == {
        "p1": TransformationKind.SCOPE_BROADENED,
        "p2": TransformationKind.SCOPE_NARROWED,
    }


def test_semantic_analyzer_detects_authority_escalation() -> None:
    from cricket.semantic import SpeechAct

    source = SemanticFrame(propositions=(
        SemanticProposition(
            anchor_id="p1",
            referent="patrick",
            predicate="wants_publish",
            speech_act=SpeechAct.PREFERENCE,
        ),
    ))
    candidate = SemanticFrame(propositions=(
        SemanticProposition(
            anchor_id="p1",
            referent="patrick",
            predicate="wants_publish",
            speech_act=SpeechAct.PERMISSION,
        ),
    ))
    report = SemanticIntegrityAnalyzer().compare(source, candidate)
    assert report.changes[0].kind is TransformationKind.AUTHORITY_ESCALATED
    assert report.changes[0].material is True


def test_semantic_analyzer_detects_currentness_and_provenance_laundering() -> None:
    from cricket.semantic import ProvenanceKind, TemporalStatus

    source = SemanticFrame(propositions=(
        SemanticProposition(
            anchor_id="history",
            referent="configuration",
            predicate="enabled",
            temporal_status=TemporalStatus.HISTORICAL,
        ),
        SemanticProposition(
            anchor_id="inference",
            referent="patrick",
            predicate="authorized",
            provenance=ProvenanceKind.MODEL_INFERENCE,
        ),
    ))
    candidate = SemanticFrame(propositions=(
        SemanticProposition(
            anchor_id="history",
            referent="configuration",
            predicate="enabled",
            temporal_status=TemporalStatus.CURRENT,
        ),
        SemanticProposition(
            anchor_id="inference",
            referent="patrick",
            predicate="authorized",
            provenance=ProvenanceKind.USER_CURRENT,
        ),
    ))

    report = SemanticIntegrityAnalyzer().compare(source, candidate)
    kinds = {change.anchor_id: change.kind for change in report.changes}
    assert kinds["history"] is TransformationKind.CURRENTNESS_PROMOTED
    assert kinds["inference"] is TransformationKind.PROVENANCE_CHANGED


def test_semantic_analyzer_detects_polarity_reversal() -> None:
    from cricket.semantic import Polarity

    source = SemanticFrame(propositions=(
        SemanticProposition(
            anchor_id="p1",
            referent="cricket",
            predicate="installed",
            polarity=Polarity.AFFIRMED,
        ),
    ))
    candidate = SemanticFrame(propositions=(
        SemanticProposition(
            anchor_id="p1",
            referent="cricket",
            predicate="installed",
            polarity=Polarity.DENIED,
        ),
    ))
    report = SemanticIntegrityAnalyzer().compare(source, candidate)
    assert report.changes[0].kind is TransformationKind.CONTRADICTED


def test_unresolved_interpretations_are_preserved_without_forced_collapse() -> None:
    source = SemanticFrame(
        unresolved_interpretations=("request", "speculation"),
    )
    candidate = SemanticFrame(
        unresolved_interpretations=("request", "speculation"),
    )
    report = SemanticIntegrityAnalyzer().compare(source, candidate)
    assert report.material_change is False
    assert report.changes == ()


