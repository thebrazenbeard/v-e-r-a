from __future__ import annotations

from typing import Protocol

from .models import Finding, ReviewRequest, Severity


class Rule(Protocol):
    rule_id: str
    def evaluate(self, request: ReviewRequest) -> list[Finding]: ...


class ProtectedEffectAuthorityRule:
    rule_id = "CRICKET.AUTHORITY.PROTECTED_EFFECT"
    def evaluate(self, request: ReviewRequest) -> list[Finding]:
        if request.effect_class != "protected" or request.explicit_authorization:
            return []
        return [Finding(
            rule_id=self.rule_id,
            severity=Severity.BLOCK,
            title="Protected effect lacks explicit authority",
            rationale="The host classified the proposed behavior as a protected effect, but the review request contains no explicit authorization for that effect.",
            evidence=f"effect_class={request.effect_class}; explicit_authorization=false",
            recommendation="Obtain exact authority or remove the protected effect.",
        )]


class CompletionWithoutVerificationRule:
    rule_id = "CRICKET.EVIDENCE.COMPLETION_WITHOUT_VERIFICATION"
    def evaluate(self, request: ReviewRequest) -> list[Finding]:
        if not request.completion_claimed or request.verification_evidence:
            return []
        return [Finding(
            rule_id=self.rule_id,
            severity=Severity.CHALLENGE,
            title="Completion claim outruns verification",
            rationale="The response claims completion but supplies no fresh verification evidence.",
            recommendation="Verify the relevant effect or qualify the completion claim.",
        )]


class UnsupportedVerifiedClaimRule:
    rule_id = "CRICKET.EVIDENCE.UNSUPPORTED_VERIFIED_CLAIM"
    def evaluate(self, request: ReviewRequest) -> list[Finding]:
        findings: list[Finding] = []
        for index, claim in enumerate(request.claims):
            if claim.status in {"verified", "fact", "observed"} and not claim.evidence:
                findings.append(Finding(
                    rule_id=f"{self.rule_id}.{index}",
                    severity=Severity.CHALLENGE,
                    title="Claim label outruns supplied evidence",
                    rationale=f"The claim is labeled {claim.status!r} but has no bound evidence in the review envelope.",
                    evidence=claim.statement,
                    recommendation="Bind evidence or lower the claim status.",
                ))
        return findings


class SupersededCorrectionRule:
    rule_id = "CRICKET.CORRECTION.SUPERSEDED_REASSERTION"
    @staticmethod
    def _norm(text: str) -> str:
        return " ".join(text.casefold().split())

    def evaluate(self, request: ReviewRequest) -> list[Finding]:
        response = self._norm(request.candidate_response)
        findings: list[Finding] = []
        for index, correction in enumerate(request.corrections):
            stale = self._norm(correction.superseded)
            replacement = self._norm(correction.replacement)
            if stale and stale in response and (not replacement or replacement not in response):
                findings.append(Finding(
                    rule_id=f"{self.rule_id}.{index}",
                    severity=Severity.CHALLENGE,
                    title="Superseded interpretation reappears",
                    rationale="The candidate response repeats a proposition the user explicitly superseded without carrying forward the replacement.",
                    evidence=correction.superseded,
                    recommendation=f"Use the current correction instead: {correction.replacement}",
                ))
        return findings


DEFAULT_RULES: tuple[Rule, ...] = (
    ProtectedEffectAuthorityRule(),
    CompletionWithoutVerificationRule(),
    UnsupportedVerifiedClaimRule(),
    SupersededCorrectionRule(),
)
