#!/usr/bin/env bash
set -euo pipefail
cd /workspaces/ai
if [ ! -f /tmp/arabic-aligner.pid ] || ! kill -0 "$(cat /tmp/arabic-aligner.pid)" 2>/dev/null; then
  nohup python app.py > /tmp/arabic-aligner.log 2>&1 < /dev/null &
  echo $! > /tmp/arabic-aligner.pid
fi
