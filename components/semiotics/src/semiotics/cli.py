from __future__ import annotations

import argparse
import json
import sys

from .engine import RegistryError, load_registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="semiotics",
        description="Query an explicit semiotic registry using exact context tags.",
    )
    parser.add_argument("registry", help="Path to a registry JSON file.")
    parser.add_argument("sign_id", help="Registered sign identifier.")
    parser.add_argument(
        "--tag",
        dest="tags",
        action="append",
        default=[],
        help="Context tag. Repeat for multiple tags.",
    )
    parser.add_argument(
        "--include-superseded",
        action="store_true",
        help="Include historical interpretations superseded by newer readings.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        registry = load_registry(args.registry)
        result = registry.query(
            args.sign_id,
            set(args.tags),
            include_superseded=args.include_superseded,
        )
    except (OSError, json.JSONDecodeError, RegistryError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
