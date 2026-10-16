from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .models import Disposition, ReviewRequest, ReviewResult
from .policy import PrinciplePack
from .receipts import JsonlReceiptLedger, canonical_digest
from .render import render_blockquote
from .reviewer import Cricket


class CandidateGenerator(Protocol):
    def generate(
        self,
        *,
        user_message: str,
        feedback: str | None = None,
        previous_candidate: str | None = None,
    ) -> str: ...


class CandidateMetadataProvider(Protocol):
    def __call__(
        self,
        *,
        user_message: str,
        candidate_response: str,
        attempt: int,
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class ReviewOutcome:
    initial_candidate: str
    final_candidate: str
    initial_result: ReviewResult
    final_result: ReviewResult
    revision_attempted: bool
    receipt: dict[str, Any] | None = None


class ReviewRuntime:
    """Bounded host-side review loop: generate -> review -> at most one revision."""

    _AUTHORITY_FIELDS = frozenset({"effect_class", "explicit_authorization"})

    def __init__(
        self,
        *,
        cricket: Cricket,
        generator: CandidateGenerator,
        principle_pack: PrinciplePack | None = None,
        receipt_ledger: JsonlReceiptLedger | None = None,
        metadata_provider: CandidateMetadataProvider | None = None,
    ) -> None:
        self.cricket = cricket
        self.generator = generator
        self.principle_pack = principle_pack
        self.receipt_ledger = receipt_ledger
        self.metadata_provider = metadata_provider

    def _metadata_for(
        self,
        *,
        user_message: str,
        candidate_response: str,
        attempt: int,
        base_metadata: dict[str, Any],
    ) -> dict[str, Any]:
        metadata = dict(base_metadata)
        if self.metadata_provider is None:
            return metadata

        dynamic = self.metadata_provider(
            user_message=user_message,
            candidate_response=candidate_response,
            attempt=attempt,
        )
        if not isinstance(dynamic, dict):
            raise ValueError("candidate metadata provider must return an object")

        forbidden_identity = {"user_message", "candidate_response"} & set(dynamic)
        if forbidden_identity:
            raise ValueError(
                "candidate metadata provider may not override request identity: "
                + ", ".join(sorted(forbidden_identity))
            )

        authority_drift = self._AUTHORITY_FIELDS & set(dynamic)
        if authority_drift:
            raise ValueError(
                "candidate metadata provider may not alter authority fields: "
                + ", ".join(sorted(authority_drift))
            )

        metadata.update(dynamic)
        return metadata

    def _request(
        self,
        *,
        user_message: str,
        candidate_response: str,
        request_metadata: dict[str, Any],
    ) -> ReviewRequest:
        forbidden = {"user_message", "candidate_response"} & set(request_metadata)
        if forbidden:
            raise ValueError(
                "request_metadata may not override: " + ", ".join(sorted(forbidden))
            )
        raw = dict(request_metadata)
        raw["user_message"] = user_message
        raw["candidate_response"] = candidate_response
        request = ReviewRequest.from_dict(raw)
        if self.principle_pack is not None:
            request = self.principle_pack.apply(request)
        return request

    def run(
        self,
        *,
        user_message: str,
        request_metadata: dict[str, Any] | None = None,
    ) -> ReviewOutcome:
        base_metadata = dict(request_metadata or {})

        initial_candidate = self.generator.generate(
            user_message=user_message,
            feedback=None,
            previous_candidate=None,
        )
        initial_metadata = self._metadata_for(
            user_message=user_message,
            candidate_response=initial_candidate,
            attempt=0,
            base_metadata=base_metadata,
        )
        initial_request = self._request(
            user_message=user_message,
            candidate_response=initial_candidate,
            request_metadata=initial_metadata,
        )
        initial_result = self.cricket.review(initial_request)

        revision_attempted = initial_result.disposition is Disposition.CHALLENGE
        final_candidate = initial_candidate
        final_result = initial_result
        final_metadata = initial_metadata
        final_request = initial_request

        if revision_attempted:
            feedback = render_blockquote(initial_result, speak_on_pass=True)
            final_candidate = self.generator.generate(
                user_message=user_message,
                feedback=feedback,
                previous_candidate=initial_candidate,
            )
            final_metadata = self._metadata_for(
                user_message=user_message,
                candidate_response=final_candidate,
                attempt=1,
                base_metadata=base_metadata,
            )
            final_request = self._request(
                user_message=user_message,
                candidate_response=final_candidate,
                request_metadata=final_metadata,
            )
            final_result = self.cricket.review(final_request)

        receipt = None
        if self.receipt_ledger is not None:
            receipt = self.receipt_ledger.append(
                {
                    "request_digest": canonical_digest(
                        {
                            "user_message": user_message,
                            "base_metadata": base_metadata,
                            "initial_candidate": initial_candidate,
                            "initial_metadata": initial_metadata,
                        }
                    ),
                    "initial_candidate_digest": canonical_digest(initial_candidate),
                    "final_candidate_digest": canonical_digest(final_candidate),
                    "initial_request_digest": canonical_digest(asdict(initial_request)),
                    "final_request_digest": canonical_digest(asdict(final_request)),
                    "principle_pack": (
                        {"id": self.principle_pack.id, "version": self.principle_pack.version}
                        if self.principle_pack is not None
                        else None
                    ),
                    "initial_disposition": initial_result.disposition.value,
                    "final_disposition": final_result.disposition.value,
                    "revision_attempted": revision_attempted,
                    "initial_finding_ids": [f.rule_id for f in initial_result.findings],
                    "final_finding_ids": [f.rule_id for f in final_result.findings],
                    "final_metadata_digest": canonical_digest(final_metadata),
                }
            )

        return ReviewOutcome(
            initial_candidate=initial_candidate,
            final_candidate=final_candidate,
            initial_result=initial_result,
            final_result=final_result,
            revision_attempted=revision_attempted,
            receipt=receipt,
        )
