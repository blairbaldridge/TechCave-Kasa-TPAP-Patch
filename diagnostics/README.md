# Optional read-only TPAP diagnostic

On a separate Linux system with git, Python 3.11+ and venv, run:

    cd diagnostics
    bash install.sh
    bash test.sh SWITCH_IP

Replace SWITCH_IP with the switch address on your own network. The probe prompts for account credentials and never saves them. It does not toggle the switch or change Home Assistant. Only the exception type is logged on failure. The exact upstream commit is pinned; do not substitute a moving branch.
