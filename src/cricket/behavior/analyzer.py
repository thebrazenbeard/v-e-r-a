from __future__ import annotations

from ..models import Finding, Severity
from .model import BehavioralAssessment, HypothesisState


class BehavioralAnalyzer:
    """Evaluate behavioral interpretations without promoting them to hidden-state facts."""

    def analyze(self, assessment: BehavioralAssessment) -> list[Finding]:
        observation_ids = {item.observation_id for item in assessment.observations}
        findings: list[Finding] = []

        for hypothesis in assessment.hypotheses:
            missing = [ref for ref in hypothesis.evidence_refs if ref not in observation_ids]
            if missing:
                findings.append(Finding(
                    rule_id=f"CRICKET.BEHAVIOR.UNBOUND_EVIDENCE.{hypothesis.hypothesis_id}",
                    severity=Severity.CHALLENGE,
                    title="Unbound behavioral evidence",
                    rationale=(
                        "The behavioral hypothesis cites evidence that is not present in the "
                        "assessment. A pattern claim without bound observations is storytelling."
                    ),
                    evidence=", ".join(missing),
                    recommendation="Bind the hypothesis to explicit observations or drop it.",
                    source="behavior",
                ))
                continue

            if (
                hypothesis.state is HypothesisState.SUPPORTED
                and not hypothesis.alternative_explanations
            ):
                findings.append(Finding(
                    rule_id=f"CRICKET.BEHAVIOR.NO_RIVAL.{hypothesis.hypothesis_id}",
                    severity=Severity.CHALLENGE,
                    title="Behavioral hypothesis lacks a rival explanation",
                    rationale=(
                        "A supported behavioral interpretation still needs at least one plausible "
                        "rival explanation. Observed behavior is evidence for an interpretation, "
                        "not omniscient access to motive."
                    ),
                    evidence=", ".join(hypothesis.evidence_refs),
                    recommendation="Keep at least one live alternative explanation attached.",
                    source="behavior",
                ))
                continue

            findings.append(Finding(
                rule_id=f"CRICKET.BEHAVIOR.HYPOTHESIS.{hypothesis.hypothesis_id}",
                severity=Severity.NOTE,
                title=f"Behavioral hypothesis: {hypothesis.pattern.value}",
                rationale=(
                    f"The interpretation remains a {hypothesis.state.value.lower()} hypothesis "
                    "bound to explicit observations, not a diagnosis or hidden-motive fact."
                ),
                evidence=", ".join(hypothesis.evidence_refs),
                recommendation="Preserve the hypothesis label and rival explanations.",
                source="behavior",
            ))

        return findings
