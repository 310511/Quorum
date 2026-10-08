#!/usr/bin/env bash
# Quorum Demo UI — start server from repo root
# Usage (from anywhere in the repo):  bash ui/run.sh

set -e
cd "$(dirname "$0")/.."   # always run from repo root

# Activate venv if one exists
for venv in .venv venv env; do
  if [ -f "$venv/bin/activate" ]; then
    echo "Activating virtualenv: $venv"
    source "$venv/bin/activate"
    break
  fi
done

# Ensure Flask is available
python3 -c "import flask, flask_cors" 2>/dev/null || {
  echo "Installing flask + flask-cors..."
  python3 -m pip install flask flask-cors --break-system-packages --quiet
}

echo ""
echo "  ⚖️  Quorum Demo UI"
echo "  ─────────────────────────────────────────"
echo "  Open → http://localhost:5173"
echo "  Press Ctrl-C to stop."
echo ""

python3 ui/server.py
