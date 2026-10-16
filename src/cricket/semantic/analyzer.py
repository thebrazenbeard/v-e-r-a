from __future__ import annotations

from .model import (
    FORCE_RANK,
    SemanticChange,
    SemanticFrame,
    SemanticIntegrityReport,
    TransformationKind,
    SpeechAct,
    TemporalStatus,
)


_EFFECT_BEARING_ACTS = {
    SpeechAct.PERMISSION,
    SpeechAct.INSTRUCTION,
    SpeechAct.COMMITMENT,
}


class SemanticIntegrityAnalyzer:
    """Deterministically compare two host-supplied semantic frames."""

    def compare(
        self,
        source: SemanticFrame,
        candidate: SemanticFrame,
    ) -> SemanticIntegrityReport:
        source_by_id = {item.anchor_id: item for item in source.propositions}
        candidate_by_id = {item.anchor_id: item for item in candidate.propositions}
        changes: list[SemanticChange] = []

        for anchor_id in sorted(source_by_id | candidate_by_id):
            before = source_by_id.get(anchor_id)
            after = candidate_by_id.get(anchor_id)

            if before is None:
                changes.append(self._change(
                    anchor_id,
                    TransformationKind.ADDED,
                    before,
                    after,
                    "Candidate introduces a proposition with no source-frame anchor.",
                ))
                continue
            if after is None:
                changes.append(self._change(
                    anchor_id,
                    TransformationKind.DROPPED,
                    before,
                    after,
                    "Candidate drops a proposition present in the source frame.",
                ))
                continue

            if before.referent != after.referent:
                changes.append(self._change(
                    anchor_id,
                    TransformationKind.REFERENT_CHANGED,
                    before,
                    after,
                    "Candidate changes the proposition referent.",
                ))
            if before.predicate != after.predicate:
                changes.append(self._change(
                    anchor_id,
                    TransformationKind.PREDICATE_CHANGED,
                    before,
                    after,
                    "Candidate changes the proposition predicate.",
                ))
            if before.polarity != after.polarity:
                changes.append(self._change(
                    anchor_id,
                    TransformationKind.CONTRADICTED,
                    before,
                    after,
                    "Candidate reverses proposition polarity.",
                ))

            if before.scope != after.scope:
                changes.append(self._scope_change(anchor_id, before, after))

            before_rank = FORCE_RANK[before.force]
            after_rank = FORCE_RANK[after.force]
            if after_rank > before_rank:
                changes.append(self._change(
                    anchor_id,
                    TransformationKind.STRENGTHENED,
                    before,
                    after,
                    f"Candidate strengthens force from {before.force.value} to {after.force.value}.",
                ))
            elif after_rank < before_rank:
                changes.append(self._change(
                    anchor_id,
                    TransformationKind.WEAKENED,
                    before,
                    after,
                    f"Candidate weakens force from {before.force.value} to {after.force.value}.",
                ))

            if before.speech_act != after.speech_act:
                kind = (
                    TransformationKind.AUTHORITY_ESCALATED
                    if before.speech_act not in _EFFECT_BEARING_ACTS
                    and after.speech_act in _EFFECT_BEARING_ACTS
                    else TransformationKind.SPEECH_ACT_CHANGED
                )
                changes.append(self._change(
                    anchor_id,
                    kind,
                    before,
                    after,
                    f"Candidate changes speech act from {before.speech_act.value} to {after.speech_act.value}.",
                ))

            if before.temporal_status != after.temporal_status:
                kind = (
                    TransformationKind.CURRENTNESS_PROMOTED
                    if before.temporal_status is not TemporalStatus.CURRENT
                    and after.temporal_status is TemporalStatus.CURRENT
                    else TransformationKind.TEMPORAL_CHANGED
                )
                changes.append(self._change(
                    anchor_id,
                    kind,
                    before,
                    after,
                    f"Candidate changes temporal status from {before.temporal_status.value} to {after.temporal_status.value}.",
                ))

            if before.provenance != after.provenance:
                changes.append(self._change(
                    anchor_id,
                    TransformationKind.PROVENANCE_CHANGED,
                    before,
                    after,
                    f"Candidate changes provenance from {before.provenance.value} to {after.provenance.value}.",
                ))

        source_ambiguity = set(source.unresolved_interpretations)
        candidate_ambiguity = set(candidate.unresolved_interpretations)
        if source_ambiguity and candidate_ambiguity < source_ambiguity:
            changes.append(SemanticChange(
                anchor_id="__ambiguity__",
                kind=TransformationKind.AMBIGUITY_COLLAPSED,
                source=None,
                candidate=None,
                material=True,
                rationale="Candidate resolves one or more source ambiguities without an explicit proposition-level basis.",
            ))

        return SemanticIntegrityReport(changes=tuple(changes))

    @staticmethod
    def _change(anchor_id, kind, before, after, rationale) -> SemanticChange:
        return SemanticChange(
            anchor_id=anchor_id,
            kind=kind,
            source=before,
            candidate=after,
            material=True,
            rationale=rationale,
        )

    def _scope_change(self, anchor_id, before, after) -> SemanticChange:
        if before.scope is not None and after.scope is not None:
            a = before.scope.members
            b = after.scope.members
            if a < b:
                kind = TransformationKind.SCOPE_BROADENED
            elif b < a:
                kind = TransformationKind.SCOPE_NARROWED
            else:
                kind = TransformationKind.SCOPE_CHANGED
        else:
            kind = TransformationKind.SCOPE_CHANGED
        return self._change(
            anchor_id,
            kind,
            before,
            after,
            "Candidate changes the proposition scope.",
        )
