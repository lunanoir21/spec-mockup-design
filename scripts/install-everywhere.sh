#!/usr/bin/env bash
# Kept for compatibility: links the skill into every agent found on this machine.
# Use ../install.sh directly for the interactive picker and the other options.
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/install.sh" --detected --yes "$@"
