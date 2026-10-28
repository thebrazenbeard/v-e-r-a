from pathlib import Path
import argparse
import os
import subprocess
import sys

PIN = "f622e564bf257b0ffc0b3c05130b62db1c201d3d"
ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--volition-root", type=Path, required=True)
    a = p.parse_args()
    v = a.volition_root.resolve()
    if not (v / "src" / "volition" / "__init__.py").is_file():
        p.error("Volition source package not found")
    head = subprocess.check_output(["git", "-C", str(v), "rev-parse", "HEAD"], text=True).strip()
    if head != PIN:
        p.error("Volition source is not the pinned revision")
    changed = subprocess.check_output(["git", "-C", str(v), "status", "--porcelain"], text=True)
    if changed.strip():
        p.error("Volition source checkout is dirty")
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(v / "src")])
    return subprocess.call([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd=ROOT, env=env)

if __name__ == "__main__":
    raise SystemExit(main())
