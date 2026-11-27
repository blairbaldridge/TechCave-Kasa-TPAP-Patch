"""Install or roll back the pinned payload. Never edit HA storage or Core."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from urllib.request import Request, urlopen

VERSION = "2026.10.4"
SHA = "844ec73b08f5284626e40aa6f0f73e293502b0b3"
WHEEL = "python_kasa-0.12.0-py3-none-any.whl"
MARKER = "_techcave_tpap_patch.json"


def present(path):
    return path.exists() or path.is_symlink()


def recognized(path):
    if path.is_symlink() or not path.is_dir() or (path / MARKER).is_symlink():
        return False
    try:
        data = json.loads((path / MARKER).read_text())
        return (data.get("home_assistant_core") == VERSION
                and data.get("python_kasa_commit") == SHA
                and data.get("python_kasa_wheel") == WHEEL)
    except (OSError, ValueError, AttributeError):
        return False


def core_version():
    request = Request("http://supervisor/core/info", headers={
        "Authorization": "Bearer " + os.environ["SUPERVISOR_TOKEN"]
    })
    with urlopen(request, timeout=15) as response:
        result = json.load(response)
    if result.get("result") != "ok":
        raise RuntimeError("Supervisor did not return Core information.")
    return result["data"]["version"]


def apply(action, root, payload, version=None, confirmed=False):
    if not root.is_dir() or not (root / "configuration.yaml").is_file():
        raise RuntimeError("Home Assistant configuration not found.")
    components = root / "custom_components"
    target = components / "tplink"
    lib = root / "techcave_tpap"
    if components.is_symlink() or lib.is_symlink():
        raise RuntimeError("Refusing symlinked patch directories.")
    if action == "status":
        print("TechCave override installed." if recognized(target)
              else "Other override present; not managed." if present(target)
              else "No custom tplink override installed.")
        print("Wheel directory retained." if lib.exists() else "No wheel directory.")
        return
    if not confirmed:
        raise RuntimeError("Create a full backup and explicitly confirm it first.")
    if action == "rollback":
        if not present(target):
            print("No override to roll back.")
            return
        if not recognized(target):
            raise RuntimeError("Not a recognized TechCave override; refusing rollback.")
        lib.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        target.rename(lib / ("disabled_override_" + stamp))
        print("SUCCESS: override disabled. Restart Core manually; wheel retained.")
        return
    if action != "install":
        raise RuntimeError("Invalid action.")
    if version != VERSION:
        raise RuntimeError("This build requires exactly Core " + VERSION + ".")
    if present(target) or present(lib):
        raise RuntimeError("Existing override or wheel directory; refusing overwrite. Inspect and back up manually.")
    source = payload / "custom_components" / "tplink"
    src_lib = payload / "techcave_tpap"
    wheel = src_lib / "lib" / WHEEL
    if not recognized(source):
        raise RuntimeError("Payload marker missing or incorrect.")
    manifest = json.loads((source / "manifest.json").read_text())
    if manifest.get("requirements") != ["python-kasa[speedups] @ file:///config/techcave_tpap/lib/" + WHEEL]:
        raise RuntimeError("Unexpected payload requirement.")
    expected = (src_lib / "WHEEL_SHA256.txt").read_text().split()[0]
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != expected:
        raise RuntimeError("Wheel checksum mismatch.")
    components.mkdir(exist_ok=True)
    staged = components / ".tplink_tpap_stage"
    lib_stage = root / ".techcave_tpap_stage"
    if present(staged) or present(lib_stage):
        raise RuntimeError("Existing staging folder; inspect manually.")
    published_lib = False
    try:
        shutil.copytree(src_lib, lib_stage)
        shutil.copytree(source, staged)
        if present(target) or present(lib):
            raise RuntimeError("Destination changed during install.")
        lib_stage.rename(lib)
        published_lib = True
        staged.rename(target)
    except Exception:
        if staged.is_dir():
            shutil.rmtree(staged)
        if lib_stage.is_dir():
            shutil.rmtree(lib_stage)
        if published_lib and not present(target):
            shutil.rmtree(lib)
        raise
    print("SUCCESS: installed override. Restart Core manually and verify switches.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["app", "status", "install", "rollback"])
    parser.add_argument("--config", type=Path, default=Path("/config"))
    parser.add_argument("--payload", type=Path, default=Path(__file__).parent / "payload")
    parser.add_argument("--core-version")
    parser.add_argument("--confirm-backup", action="store_true")
    args = parser.parse_args()
    if args.action == "app":
        opts = json.loads(Path("/data/options.json").read_text())
        action = opts.get("action", "status")
        version = core_version() if action == "install" else None
        apply(action, Path("/ha_config"), Path("/payload"), version,
              opts.get("confirm_backup") is True)
    else:
        apply(args.action, args.config, args.payload, args.core_version, args.confirm_backup)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        raise SystemExit(1)
