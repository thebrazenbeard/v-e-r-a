from __future__ import annotations

from typing import Protocol

from ..models import Finding, Severity
from .analyzer import SemanticIntegrityAnalyzer
from .model import SemanticFrame, SemanticIntegrityReport, TransformationKind


class SemanticPairExtractor(Protocol):
    def extract_pair(
        self,
        *,
        source_text: str,
        candidate_text: str,
    ) -> tuple[SemanticFrame, SemanticFrame]: ...


class SemanticScanner(Protocol):
    def scan(self, *, source_text: str, candidate_text: str) -> SemanticIntegrityReport: ...


_RECOMMENDATIONS = {
    TransformationKind.STRENGTHENED: "Restore the source modality or explicitly justify the stronger claim.",
    TransformationKind.WEAKENED: "Preserve the original force unless weakening is intentional and explained.",
    TransformationKind.REFERENT_CHANGED: "Restore the original referent or make the referent change explicit.",
    TransformationKind.PREDICATE_CHANGED: "Respond to the original proposition rather than substituting a different one.",
    TransformationKind.CONTRADICTED: "Do not reverse polarity without explicitly addressing the contradiction.",
    TransformationKind.SCOPE_BROADENED: "Do not broaden the source scope without evidence or authorization.",
    TransformationKind.SCOPE_NARROWED: "Make the scope narrowing explicit instead of silently changing the claim.",
    TransformationKind.SCOPE_CHANGED: "Preserve or explicitly restate the changed scope.",
    TransformationKind.AUTHORITY_ESCALATED: "Do not convert preference, description, or request into permission, instruction, or commitment.",
    TransformationKind.SPEECH_ACT_CHANGED: "Preserve the source speech act or explicitly explain the reinterpretation.",
    TransformationKind.CURRENTNESS_PROMOTED: "Keep historical, proposed, and current state distinct.",
    TransformationKind.TEMPORAL_CHANGED: "Preserve temporal status or explicitly explain the temporal change.",
    TransformationKind.PROVENANCE_CHANGED: "Do not transfer provenance or authority merely because wording is similar.",
    TransformationKind.AMBIGUITY_COLLAPSED: "Preserve live interpretations until evidence supports resolving them.",
    TransformationKind.DROPPED: "Do not silently drop a material source proposition.",
    TransformationKind.ADDED: "Mark added propositions as new inference instead of attributing them to the source.",
}


class SemanticIntegrityScanner:
    def __init__(
        self,
        extractor: SemanticPairExtractor,
        analyzer: SemanticIntegrityAnalyzer | None = None,
    ) -> None:
        self.extractor = extractor
        self.analyzer = analyzer or SemanticIntegrityAnalyzer()

    def scan(self, *, source_text: str, candidate_text: str) -> SemanticIntegrityReport:
        source, candidate = self.extractor.extract_pair(
            source_text=source_text,
            candidate_text=candidate_text,
        )
        return self._compare_frames(source, candidate, analyzer=self.analyzer)

    @staticmethod
    def _compare_frames(
        source: SemanticFrame,
        candidate: SemanticFrame,
        *,
        analyzer: SemanticIntegrityAnalyzer | None = None,
    ) -> SemanticIntegrityReport:
        return (analyzer or SemanticIntegrityAnalyzer()).compare(source, candidate)


def findings_from_semantic_report(report: SemanticIntegrityReport) -> list[Finding]:
    findings: list[Finding] = []
    for change in report.changes:
        if not change.material:
            continue
        findings.append(Finding(
            rule_id=f"CRICKET.SEMANTIC.{change.kind.value}.{change.anchor_id}",
            severity=Severity.CHALLENGE,
            title=f"Semantic integrity: {change.kind.value}",
            rationale=change.rationale,
            evidence=change.anchor_id,
            recommendation=_RECOMMENDATIONS.get(
                change.kind,
                "Preserve the source meaning or make the transformation explicit.",
            ),
            source="semantic",
        ))
    return findings
