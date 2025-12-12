#!/bin/bash
# Start the XFactor Bot Python backend for desktop app

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "Starting XFactor Bot backend..."
echo "Project root: $PROJECT_ROOT"

# Check if virtual environment exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Start the FastAPI server
cd "$PROJECT_ROOT"
python3 -m uvicorn src.api.main:app --host 127.0.0.1 --port 9876 --reload

