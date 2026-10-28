#!/usr/bin/env bash
set -eu
cd -- "$(dirname -- "$0")"
if [ "$#" -eq 0 ]; then
  read -r -p 'Domain to cultivate (example.com): ' target
  exec python3 mailthorn_cultivator.py "$target"
fi
exec python3 mailthorn_cultivator.py "$@"
