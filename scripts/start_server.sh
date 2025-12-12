#!/bin/bash
cd /home/cvanthin/trading
source .venv/bin/activate
pkill -f "uvicorn src.api.main" 2>/dev/null
sleep 1
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 9876 > api.log 2>&1 &
echo $! > api.pid
sleep 2
curl -s http://localhost:9876/health

