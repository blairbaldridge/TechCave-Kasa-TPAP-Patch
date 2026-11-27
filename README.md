# TechCave Kasa TPAP Patch

Unofficial, temporary workaround for Kasa KS205 switches (hardware 1.0, firmware 1.4.0, TPAP level 2) that fail to connect to Home Assistant with an unsupported encryption error.

**Compatibility: Home Assistant Core 2026.10.4 ONLY.** The original manually installed override restored four affected switches in the maintainer's setup. The new app installer is experimental and has not yet been tested on a live Home Assistant system. Do not install on newer Core releases without a separately validated build; check native support first.

## Install using Home Assistant OS (recommended after testing)

1. Create and download a full Home Assistant backup.
2. Open Settings → Apps (Add-ons) → App store → ⋮ → Repositories.
3. Add this repository: https://github.com/blairbaldridge/TechCave-Kasa-TPAP-Patch
4. Install **TechCave Kasa TPAP Patch**. The image builds the pinned dependency locally; this can take several minutes.
5. In the app's Configuration tab set action to `install` and confirm_backup to true, save, then click Start. Check the app log for SUCCESS. The app exits after its operation.
6. Restart Home Assistant Core manually. Check logs and test an affected switch and previously working devices. Do not delete any existing integration entries, devices or entities.

After each operation reset action to status and confirm_backup to false. Start on boot is disabled. The app does not run continuously, restart Core automatically or request Kasa credentials. It writes to the Home Assistant configuration directory. It refuses to overwrite an existing custom tplink override, including an older TechCave installation.

## Rollback / upgrading Core

Before upgrading Core, set action to `rollback` and confirm_backup to true, save and start the app. Check its log and restart Core. This moves only a recognized TechCave override to a backup directory outside custom_components; the wheel is retained. Uninstalling the app alone does NOT remove the override. If dependency conflicts remain, restore the full backup. Do not delete existing entities or integration entries.

## Manual installation (advanced)

See [manual installation](docs/MANUAL.md) and [diagnostic probe](diagnostics/README.md). No machine-specific configuration or default network address is provided.

## Risks and scope

The override replaces the entire built-in tplink domain and changes the shared python-kasa dependency. Other TP-Link devices or integrations may be affected. The original Core dependency is replaced by a local wheel built from the exact tested commit. All actions require explicit selection; the default is status only. The app checks the exact Core version for installation; rollback remains available on other versions. If a different override is present, stop and inspect it manually.

This is not an official Home Assistant, TP-Link or python-kasa product. Upstream projects retain their licenses; see [NOTICE.md](NOTICE.md). The TPAP protocol implementation is upstream work, not authored by TechCave.

## Upstream

- [python-kasa TPAP PR #1592](https://github.com/python-kasa/python-kasa/pull/1592)
- [Pinned python-kasa revision](https://github.com/python-kasa/python-kasa/commit/844ec73b08f5284626e40aa6f0f73e293502b0b3)
- [Home Assistant Core 2026.10.4](https://github.com/home-assistant/core/tree/2026.10.4/homeassistant/components/tplink)

Report problems via Issues; redact credentials, tokens, addresses, aliases, identifiers and logs before posting.
