from __future__ import annotations

from collections.abc import Iterable

from .behavior import BehavioralScanner
from .critic import CRITIC_PROMPT, CriticAdapter, parse_critic_findings
from .models import Disposition, Finding, ReviewRequest, ReviewResult, Severity
from .rules import DEFAULT_RULES, Rule
from .semantic.scanner import SemanticScanner, findings_from_semantic_report


class Cricket:
    def __init__(
        self,
        *,
        rules: Iterable[Rule] = DEFAULT_RULES,
        critic: CriticAdapter | None = None,
        semantic_blocking: bool = False,
        semantic_scanner: SemanticScanner | None = None,
        behavior_scanner: BehavioralScanner | None = None,
    ) -> None:
        self.rules = tuple(rules)
        self.critic = critic
        self.semantic_blocking = semantic_blocking
        self.semantic_scanner = semantic_scanner
        self.behavior_scanner = behavior_scanner

    def review(self, request: ReviewRequest) -> ReviewResult:
        findings: list[Finding] = []
        for rule in self.rules:
            findings.extend(rule.evaluate(request))

        if self.semantic_scanner is not None:
            report = self.semantic_scanner.scan(
                source_text=request.user_message,
                candidate_text=request.candidate_response,
            )
            findings.extend(findings_from_semantic_report(report))

        if self.behavior_scanner is not None:
            findings.extend(self.behavior_scanner.scan(
                source_text=request.user_message,
                candidate_text=request.candidate_response,
            ))

        if self.critic is not None:
            semantic = parse_critic_findings(
                self.critic.critique(prompt=CRITIC_PROMPT, request=request)
            )
            if not self.semantic_blocking:
                semantic = [
                    Finding(
                        rule_id=f.rule_id,
                        severity=Severity.CHALLENGE if f.severity is Severity.BLOCK else f.severity,
                        title=f.title,
                        rationale=f.rationale,
                        evidence=f.evidence,
                        recommendation=f.recommendation,
                        source=f.source,
                    )
                    for f in semantic
                ]
            findings.extend(semantic)

        findings = self._deduplicate(findings)
        if any(f.severity is Severity.BLOCK for f in findings):
            disposition = Disposition.BLOCK
        elif any(f.severity is Severity.CHALLENGE for f in findings):
            disposition = Disposition.CHALLENGE
        else:
            disposition = Disposition.PASS
        return ReviewResult(disposition=disposition, findings=tuple(findings))

    @staticmethod
    def _deduplicate(findings: list[Finding]) -> list[Finding]:
        seen: set[tuple[str, str, str]] = set()
        output: list[Finding] = []
        for finding in findings:
            key = (finding.rule_id, finding.title, finding.evidence)
            if key not in seen:
                seen.add(key)
                output.append(finding)
        return output
