"""Build the original version-specific override without touching a running HA."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

CORE_VERSION = "2026.10.4"
KASA_SHA = "844ec73b08f5284626e40aa6f0f73e293502b0b3"
WHEEL = "python_kasa-0.12.0-py3-none-any.whl"


def run(*args):
    subprocess.run(args, check=True)


def checkout(url, ref, dest, sparse=None):
    run("git", "init", str(dest))
    if sparse:
        run("git", "-C", str(dest), "sparse-checkout", "init", "--cone")
        run("git", "-C", str(dest), "sparse-checkout", "set", sparse)
    run("git", "-C", str(dest), "fetch", "--depth=1", url, ref)
    run("git", "-C", str(dest), "checkout", "--detach", "FETCH_HEAD")
    return subprocess.check_output(
        ["git", "-C", str(dest), "rev-parse", "HEAD"], text=True
    ).strip()


def build(out):
    if out.exists():
        raise RuntimeError("Output already exists; choose a new directory.")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        kasa = root / "kasa"
        core = root / "core"
        stage = root / "payload"
        lib = stage / "techcave_tpap" / "lib"
        lib.mkdir(parents=True)
        if checkout("https://github.com/python-kasa/python-kasa.git", KASA_SHA, kasa) != KASA_SHA:
            raise RuntimeError("Unexpected python-kasa revision.")
        run(sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(lib), str(kasa))
        if sorted(p.name for p in lib.iterdir()) != [WHEEL]:
            raise RuntimeError("Unexpected wheel name or platform.")
        core_sha = checkout("https://github.com/home-assistant/core.git",
                            "refs/tags/" + CORE_VERSION, core,
                            "homeassistant/components/tplink")
        integration = stage / "custom_components" / "tplink"
        shutil.copytree(core / "homeassistant/components/tplink", integration)
        manifest = integration / "manifest.json"
        data = json.loads(manifest.read_text())
        if data.get("domain") != "tplink" or data.get("requirements") != ["python-kasa[speedups]==0.11.0.1"]:
            raise RuntimeError("Unexpected upstream manifest; review required.")
        data["version"] = CORE_VERSION
        data["requirements"] = ["python-kasa[speedups] @ file:///config/techcave_tpap/lib/" + WHEEL]
        manifest.write_text(json.dumps(data, indent=2) + "\n")
        marker = {
            "purpose": "Experimental TPAP / KS205 custom integration override",
            "home_assistant_core": CORE_VERSION,
            "home_assistant_core_commit": core_sha,
            "python_kasa_commit": KASA_SHA,
            "python_kasa_wheel": WHEEL,
            "validated_on_ha": False,
        }
        (integration / "_techcave_tpap_patch.json").write_text(json.dumps(marker, indent=2) + "\n")
        digest = hashlib.sha256((lib / WHEEL).read_bytes()).hexdigest()
        (lib.parent / "WHEEL_SHA256.txt").write_text(digest + "  techcave_tpap/lib/" + WHEEL + "\n")
        shutil.copy2(core / "LICENSE.md", integration / "UPSTREAM_LICENSE.txt")
        shutil.copy2(kasa / "LICENSE", lib.parent / "UPSTREAM_LICENSE.txt")
        (integration / "TECHCAVE_CHANGES.txt").write_text(
            "Upstream HA Core " + CORE_VERSION + " (" + core_sha + ").\n"
            "TechCave changes manifest version and dependency only.\n"
            "python-kasa source: https://github.com/python-kasa/python-kasa/tree/" + KASA_SHA + "\n"
        )
        # Preserve upstream notice if present.
        for name in ("NOTICE", "NOTICE.md", "NOTICE.txt"):
            if (core / name).is_file():
                shutil.copy2(core / name, integration / name)
        shutil.copytree(stage, out)
    print("SUCCESS: built pinned deployment payload")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: build_patch.py OUTPUT_DIRECTORY")
    build(Path(sys.argv[1]).resolve())
