"""Verify read-only V-E-R-A safe source-export trees.

An exact tree match does not qualify code safety, runtime installation or source freshness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

SCHEMA = "V_E_R_A_SAFE_COMPONENT_EXPORTS_V1"
SHA = re.compile(r"^[0-9a-f]{40}$")
AUTOMATION_DIRS = {".vscode", ".husky", ".devcontainer", ".idea"}
FONT_EXTENSIONS = {".woff", ".woff2", ".ttf", ".otf", ".eot"}
ACTIVE_CI_FILES = {".gitlab-ci.yml", "azure-pipelines.yml", "jenkinsfile"}

def omission_reason(path: str, mode: str = "100644") -> str | None:
    parts = path.lower().replace("\\", "/").split("/")
    if mode == "160000":
        return "GITLINK_UNQUALIFIED"
    if mode == "120000":
        return "SYMLINK_UNQUALIFIED"
    if any(p in AUTOMATION_DIRS for p in parts):
        return "ACTIVE_WORKSPACE_CONFIGURATION"
    if ".github" in parts and "workflows" in parts:
        return "CI_WORKFLOW_CONFIGURATION"
    if parts[-1] in ACTIVE_CI_FILES or parts[-1].endswith(".code-workspace"):
        return "AUTOMATIC_EXECUTION_CONFIGURATION"
    if Path(parts[-1]).suffix in FONT_EXTENSIONS:
        return "UNREVIEWED_EMBEDDED_FONT_BINARY"
    return None

def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True, encoding="utf-8", timeout=90)
    if p.returncode != 0:
        raise ValueError("git failed: " + p.stderr[-220:])
    return p.stdout.strip()

def tree_entries(repo: Path, subject: str) -> dict[str, tuple[str, str]]:
    proc = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "-z", subject],
                          capture_output=True, timeout=90)
    if proc.returncode:
        raise ValueError("source tree unavailable: " + proc.stderr[-150:].decode("utf8", "replace"))
    rows = {}
    for record in proc.stdout.split(b"\0"):
        if not record:
            continue
        meta, path = record.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split()
        rows[path.decode("utf8")] = (mode, oid)
    return rows

def inspect(repo: Path, tree: str = "HEAD", verify_source_objects: bool = False) -> dict:
    entries = json.loads(git(repo, "show", f"{tree}:components.json"))
    manifest = json.loads(git(repo, "show", f"{tree}:component-exports.json"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError("wrong export manifest schema")
    registry = entries.get("components")
    exports = manifest.get("components")
    if not isinstance(registry, list) or not isinstance(exports, list) or len(registry) != 44 or len(exports) != 44:
        raise ValueError("expected 44 component entries")
    b = {x["name"]: x for x in exports}
    if len(b) != 44 or len({x["name"] for x in registry}) != 44:
        raise ValueError("duplicate/missing component")
    omissions = 0
    safe_files = 0
    for r in registry:
        name = r["name"]
        x = b.get(name)
        if x is None or x["mirror_commit"] != r["mirror_commit"] or x["source_state"] != r["state"]:
            raise ValueError("name/source pin/state mismatch for " + name)
        if not all(isinstance(x.get(k), str) and SHA.fullmatch(x[k]) for k in ("source_tree", "export_tree")):
            raise ValueError("invalid tree hash " + name)
        actual = git(repo, "rev-parse", f"{tree}:components/{name}")
        if actual != x["export_tree"]:
            raise ValueError("tracked component tree mismatch " + name)
        exported_entries = tree_entries(repo, f"{tree}:components/{name}")
        paths = list(exported_entries)
        for path, (mode, oid) in exported_entries.items():
            if omission_reason(path, mode) is not None:
                raise ValueError("unsafe class retained: " + name + "/" + path)
        claimed = x.get("omitted_paths")
        if not isinstance(claimed, list) or len(claimed) != len({z["path"] for z in claimed}):
            raise ValueError("malformed omissions " + name)
        for item in claimed:
            if (not isinstance(item, dict) or
                omission_reason(item["path"], item["mode"]) != item["reason"] or
                item["path"] in paths):
                raise ValueError("unjustified omission " + name)
        if (x.get("retained_count") != len(paths) or
            x.get("omitted_count") != len(claimed) or
            x.get("source_file_count") != len(paths) + len(claimed)):
            raise ValueError("count mismatch " + name)
        if verify_source_objects:
            source_tree = git(repo, "rev-parse", x["mirror_commit"] + "^{tree}")
            if source_tree != x["source_tree"]:
                raise ValueError("pinned source tree mismatch " + name)
            origin_entries = tree_entries(repo, x["mirror_commit"])
            required_omissions = []
            retained_origin = {}
            for path, (mode, oid) in origin_entries.items():
                reason = omission_reason(path, mode)
                if reason:
                    required_omissions.append({
                        "path": path, "mode": mode, "blob_oid": oid, "reason": reason
                    })
                else:
                    retained_origin[path] = (mode, oid)
            if (required_omissions != claimed or
                    retained_origin != exported_entries):
                raise ValueError("source blob/omission provenance mismatch " + name)
        safe_files += len(paths)
        omissions += len(claimed)
    return {
        "status": "SOURCE_EXPORT_TREE_MATCH",
        "components": len(exports), "files_retained": safe_files,
        "explicit_omissions": omissions, "malware_free_proven": False,
        "upstream_freshness_proven": False,
        "source_blob_identity_verified": verify_source_objects,
        "veraos_installed": False,
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--tree", default="HEAD")
    ap.add_argument("--verify-source-objects", action="store_true")
    args = ap.parse_args()
    try:
        print(json.dumps(inspect(args.repo.resolve(), args.tree, args.verify_source_objects), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as e:
        ap.exit(2, "EXPORT_HELD: " + str(e) + "\n")

if __name__ == "__main__":
    main()
