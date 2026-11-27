# Advanced manual installation

Only for Core 2026.10.4. The app is preferred for Home Assistant OS; manual method requires Linux with Python 3.11+ and git to build, plus Python 3 on the machine/container that can access HA config.

From the repository root on Linux:

    python3 -m venv .venv
    .venv/bin/python tpap_patch/build_patch.py payload
    cp tpap_patch/manage_patch.py payload/
    tar -czf tpap-deploy.tar.gz payload

This builds locally from the pinned sources and does not change Home Assistant. Copy the archive to a temporary directory on the Home Assistant host and extract it. Verify the Core version in Settings → About, create a full backup, then run (from the extraction directory with Python 3 available):

    python3 payload/manage_patch.py install --payload payload --config /config --core-version 2026.10.4 --confirm-backup

For Container users, use the mounted host configuration path for --config; the Core container must see it at /config. For other layouts this release is not supported. Restart Core manually. To roll back:

    python3 payload/manage_patch.py rollback --config /config --confirm-backup

Restart Core. Rollback retains the wheel directory and disabled override. To reinstall, first inspect and move the retained techcave_tpap directory to a safe backup location after restarting with the official integration. Do not delete configuration entries or working devices.

## Troubleshooting
- Wrong Core version: stop, use only a separately validated build or native support.
- Existing custom tplink override: stop and inspect/back up the existing files. Never overwrite another integration.
- Dependency error or unavailable working devices: roll back, restart, inspect logs; restore full backup if needed.
- Unsupported TPAP despite successful installation: verify the hardware/firmware and check logs. Try the read-only diagnostic from another Linux machine.
- Build failures: check GitHub/PyPI connectivity, available space, and upstream commit availability. Do not substitute a moving branch or change the wheel version check.
