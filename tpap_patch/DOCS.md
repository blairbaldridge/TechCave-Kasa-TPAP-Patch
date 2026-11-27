# TechCave Kasa TPAP Patch

Experimental installer; only Core 2026.10.4 is supported. Take a full backup before any changes.

- **status**: show whether a recognized override exists (no writes).
- **install**: set confirm_backup to true, save, Start, and check Logs for SUCCESS. Restart Core manually.
- **rollback**: set confirm_backup to true, save, Start, and check Logs. Restart Core manually.

After each operation set action back to status and confirm_backup to false. Do not enable automatic start or watchdog. Uninstalling this app does not remove the override. Roll back before upgrading Core. The installer refuses existing overrides or retained wheel folders; inspect and back these up manually before reinstalling. See repository README for recovery. No credentials needed.
