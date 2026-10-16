from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .model import Interpretation, InterpretationRelation, Sign, Source


class RegistryError(ValueError):
    """Raised when registry data violates the explicit schema or references."""


RELATION_KINDS = frozenset(
    {"contrasts_with", "contradicts", "supports", "refines"}
)


class Registry:
    def __init__(
        self,
        signs: list[Sign],
        sources: list[Source],
        interpretations: list[Interpretation],
        relations: list[InterpretationRelation] | None = None,
    ) -> None:
        relations = list(relations or [])
        _validate_entities(signs, sources, interpretations, relations)
        self.signs = {item.id: item for item in signs}
        self.sources = {item.id: item for item in sources}
        self.interpretations = list(interpretations)
        self.relations = relations

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Registry":
        _reject_unknown_keys(
            data,
            {"signs", "sources", "interpretations", "relations"},
            "registry",
        )
        signs = [_parse_sign(item) for item in _list_field(data, "signs")]
        sources = [_parse_source(item) for item in _list_field(data, "sources")]
        interpretations = [
            _parse_interpretation(item) for item in _list_field(data, "interpretations")
        ]
        relations = [
            _parse_relation(item) for item in _optional_list_field(data, "relations")
        ]

        return cls(signs, sources, interpretations, relations)

    def query(
        self,
        sign_id: str,
        tags: set[str] | None = None,
        *,
        include_superseded: bool = False,
    ) -> list[dict[str, Any]]:
        tags = tags or set()
        if not all(isinstance(tag, str) and tag.strip() for tag in tags):
            raise RegistryError("context tags must be non-empty strings")
        if sign_id not in self.signs:
            raise RegistryError(f"unknown sign {sign_id!r}")

        superseded_ids = {
            item.supersedes_id
            for item in self.interpretations
            if item.supersedes_id is not None
        }
        matches = [
            item
            for item in self.interpretations
            if item.sign_id == sign_id
            and item.matches(tags)
            and (include_superseded or item.id not in superseded_ids)
        ]
        matches.sort(key=lambda item: (-item.specificity, item.id))

        result = []
        for item in matches:
            entry = {
                "interpretation": _interpretation_dict(item),
                "source": _source_dict(self.sources[item.source_id]),
            }
            relations = [
                _relation_dict(relation)
                for relation in self.relations
                if item.id in {relation.left_id, relation.right_id}
            ]
            if relations:
                entry["relations"] = sorted(relations, key=lambda relation: relation["id"])
            result.append(entry)
        return result

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "signs": [
                asdict(item)
                for item in sorted(self.signs.values(), key=lambda item: item.id)
            ],
            "sources": [
                _source_registry_dict(item)
                for item in sorted(self.sources.values(), key=lambda item: item.id)
            ],
            "interpretations": [
                _interpretation_dict(item)
                for item in sorted(self.interpretations, key=lambda item: item.id)
            ],
        }
        if self.relations:
            payload["relations"] = [
                _relation_dict(item)
                for item in sorted(self.relations, key=lambda item: item.id)
            ]
        return payload


def load_registry(path: str | Path) -> Registry:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RegistryError("registry root must be a JSON object")
    return Registry.from_dict(payload)


def dump_registry(registry: Registry, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(registry.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _source_dict(item: Source) -> dict[str, Any]:
    result = asdict(item)
    if item.citation is None:
        result.pop("citation")
    if item.published_year is None:
        result.pop("published_year")
    return result


def _source_registry_dict(item: Source) -> dict[str, Any]:
    result = asdict(item)
    return {key: value for key, value in result.items() if value is not None}


def _relation_dict(item: InterpretationRelation) -> dict[str, Any]:
    return asdict(item)


def _interpretation_dict(item: Interpretation) -> dict[str, Any]:
    result = {
        "id": item.id,
        "sign_id": item.sign_id,
        "meaning": item.meaning,
        "source_id": item.source_id,
        "required_tags": sorted(item.required_tags),
        "excluded_tags": sorted(item.excluded_tags),
    }
    if item.supersedes_id is not None:
        result["supersedes_id"] = item.supersedes_id
    return result


def _reject_unknown_keys(
    item: dict[str, Any], allowed: set[str], kind: str
) -> None:
    unknown = sorted(set(item) - allowed)
    if unknown:
        raise RegistryError(
            f"{kind} contains unknown fields: " + ", ".join(unknown)
        )


def _optional_list_field(data: dict[str, Any], name: str) -> list[dict[str, Any]]:
    if name not in data:
        return []
    return _list_field(data, name)


def _list_field(data: dict[str, Any], name: str) -> list[dict[str, Any]]:
    value = data.get(name)
    if not isinstance(value, list):
        raise RegistryError(f"{name!r} must be a list")
    if not all(isinstance(item, dict) for item in value):
        raise RegistryError(f"every item in {name!r} must be an object")
    return value


def _validate_entities(
    signs: list[Sign],
    sources: list[Source],
    interpretations: list[Interpretation],
    relations: list[InterpretationRelation],
) -> None:
    for item in signs:
        _validate_model_text(item.id, "sign id")
        _validate_model_text(item.form, "sign form")
        _validate_model_text(item.modality, "sign modality")

    for item in sources:
        _validate_model_text(item.id, "source id")
        _validate_model_text(item.description, "source description")
        _validate_optional_model_text(item.locator, "source locator")
        _validate_optional_model_text(item.citation, "source citation")
        if item.published_year is not None and (
            isinstance(item.published_year, bool)
            or not isinstance(item.published_year, int)
        ):
            raise RegistryError("source published_year must be an integer when present")

    for item in interpretations:
        _validate_model_text(item.id, "interpretation id")
        _validate_model_text(item.sign_id, "interpretation sign_id")
        _validate_model_text(item.meaning, "interpretation meaning")
        _validate_model_text(item.source_id, "interpretation source_id")
        _validate_optional_model_text(
            item.supersedes_id,
            "interpretation supersedes_id",
        )
        _validate_model_tags(item.required_tags, "required_tags")
        _validate_model_tags(item.excluded_tags, "excluded_tags")

    for item in relations:
        _validate_model_text(item.id, "relation id")
        _validate_model_text(item.left_id, "relation left_id")
        _validate_model_text(item.right_id, "relation right_id")
        _validate_model_text(item.kind, "relation kind")
        _validate_model_text(item.source_id, "relation source_id")

    _require_unique([item.id for item in signs], "sign")
    _require_unique([item.id for item in sources], "source")
    _require_unique([item.id for item in interpretations], "interpretation")
    _require_unique([item.id for item in relations], "relation")

    sign_ids = {item.id for item in signs}
    source_ids = {item.id for item in sources}
    for item in interpretations:
        if item.sign_id not in sign_ids:
            raise RegistryError(
                f"interpretation {item.id!r} references unknown sign {item.sign_id!r}"
            )
        if item.source_id not in source_ids:
            raise RegistryError(
                f"interpretation {item.id!r} references unknown source {item.source_id!r}"
            )
        overlap = item.required_tags & item.excluded_tags
        if overlap:
            raise RegistryError(
                f"interpretation {item.id!r} requires and excludes the same tags: "
                + ", ".join(sorted(overlap))
            )

    interpretation_by_id = {item.id: item for item in interpretations}
    for item in interpretations:
        if item.supersedes_id is None:
            continue
        prior = interpretation_by_id.get(item.supersedes_id)
        if prior is None:
            raise RegistryError(
                f"interpretation {item.id!r} supersedes unknown interpretation "
                f"{item.supersedes_id!r}"
            )
        if prior.sign_id != item.sign_id:
            raise RegistryError(
                f"interpretation {item.id!r} must supersede a reading of the same sign"
            )

    for item in interpretations:
        seen: set[str] = set()
        current = item
        while current.supersedes_id is not None:
            if current.id in seen:
                raise RegistryError("interpretation revision history contains a cycle")
            seen.add(current.id)
            current = interpretation_by_id[current.supersedes_id]

    for relation in relations:
        if relation.left_id == relation.right_id:
            raise RegistryError(
                f"relation {relation.id!r} must connect distinct interpretations"
            )
        for endpoint in (relation.left_id, relation.right_id):
            if endpoint not in interpretation_by_id:
                raise RegistryError(
                    f"relation {relation.id!r} references unknown interpretation "
                    f"{endpoint!r}"
                )
        if relation.source_id not in source_ids:
            raise RegistryError(
                f"relation {relation.id!r} references unknown source "
                f"{relation.source_id!r}"
            )
        if relation.kind not in RELATION_KINDS:
            raise RegistryError(f"relation kind {relation.kind!r} is not supported")


def _validate_model_text(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{label} must be a non-empty string")


def _validate_optional_model_text(value: Any, label: str) -> None:
    if value is not None:
        _validate_model_text(value, label)


def _validate_model_tags(value: Any, label: str) -> None:
    if not isinstance(value, (set, frozenset)) or not all(
        isinstance(tag, str) and tag.strip() for tag in value
    ):
        raise RegistryError(f"{label} must contain only non-empty strings")


def _require_unique(values: list[str], kind: str) -> None:
    seen: set[str] = set()
    for value in values:
        if value in seen:
            raise RegistryError(f"duplicate {kind} id {value!r}")
        seen.add(value)


def _required_text(item: dict[str, Any], name: str) -> str:
    value = item.get(name)
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{name!r} must be a non-empty string")
    return value


def _optional_text(item: dict[str, Any], name: str) -> str | None:
    value = item.get(name)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{name!r} must be a non-empty string when present")
    return value


def _optional_int(item: dict[str, Any], name: str) -> int | None:
    value = item.get(name)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise RegistryError(f"{name!r} must be an integer when present")
    return value


def _tag_set(item: dict[str, Any], name: str) -> frozenset[str]:
    value = item.get(name, [])
    if not isinstance(value, list) or not all(
        isinstance(tag, str) and tag.strip() for tag in value
    ):
        raise RegistryError(f"{name!r} must be a list of non-empty strings")
    if len(value) != len(set(value)):
        raise RegistryError(f"{name!r} must not contain duplicate tags")
    return frozenset(value)


def _parse_sign(item: dict[str, Any]) -> Sign:
    _reject_unknown_keys(item, {"id", "form", "modality"}, "sign")
    return Sign(
        id=_required_text(item, "id"),
        form=_required_text(item, "form"),
        modality=_required_text(item, "modality"),
    )


def _parse_source(item: dict[str, Any]) -> Source:
    _reject_unknown_keys(
        item,
        {"id", "description", "locator", "citation", "published_year"},
        "source",
    )
    return Source(
        id=_required_text(item, "id"),
        description=_required_text(item, "description"),
        locator=_optional_text(item, "locator"),
        citation=_optional_text(item, "citation"),
        published_year=_optional_int(item, "published_year"),
    )


def _parse_interpretation(item: dict[str, Any]) -> Interpretation:
    _reject_unknown_keys(
        item,
        {
            "id",
            "sign_id",
            "meaning",
            "source_id",
            "supersedes_id",
            "required_tags",
            "excluded_tags",
        },
        "interpretation",
    )
    return Interpretation(
        id=_required_text(item, "id"),
        sign_id=_required_text(item, "sign_id"),
        meaning=_required_text(item, "meaning"),
        source_id=_required_text(item, "source_id"),
        supersedes_id=_optional_text(item, "supersedes_id"),
        required_tags=_tag_set(item, "required_tags"),
        excluded_tags=_tag_set(item, "excluded_tags"),
    )

def _parse_relation(item: dict[str, Any]) -> InterpretationRelation:
    _reject_unknown_keys(
        item,
        {"id", "left_id", "right_id", "kind", "source_id"},
        "relation",
    )
    return InterpretationRelation(
        id=_required_text(item, "id"),
        left_id=_required_text(item, "left_id"),
        right_id=_required_text(item, "right_id"),
        kind=_required_text(item, "kind"),
        source_id=_required_text(item, "source_id"),
    )
