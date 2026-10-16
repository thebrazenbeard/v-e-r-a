from __future__ import annotations

from typing import Protocol

from ..models import Finding
from .analyzer import BehavioralAnalyzer
from .model import BehavioralAssessment


class BehavioralExtractor(Protocol):
    def extract(
        self,
        *,
        source_text: str,
        candidate_text: str,
    ) -> BehavioralAssessment: ...


class BehavioralScanner:
    def __init__(
        self,
        extractor: BehavioralExtractor,
        analyzer: BehavioralAnalyzer | None = None,
    ) -> None:
        self.extractor = extractor
        self.analyzer = analyzer or BehavioralAnalyzer()

    def scan(self, *, source_text: str, candidate_text: str) -> list[Finding]:
        assessment = self.extractor.extract(
            source_text=source_text,
            candidate_text=candidate_text,
        )
        return self.analyzer.analyze(assessment)
