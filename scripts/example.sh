#!/usr/bin/env bash
# Example script that reads env vars when using `dotenv`-style shells or exported variables.
# For Python projects, prefer python-dotenv inside the app.
set -euo pipefail
echo "This script would run tasks using env vars like $ACCOUNT_KEY (do not echo real secrets in practice)."
