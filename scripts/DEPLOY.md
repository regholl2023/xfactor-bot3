# XFactor Bot Deployment Guide

## Target Server
- **Host:** foresight.nvidia.com
- **Port:** 9876
- **User:** cvanthin
- **Directory:** /home/cvanthin/trading

## Disk Space Requirements

| Component | Size |
|-----------|------|
| Source code (src/) | ~2 MB |
| Frontend (without node_modules) | ~5 MB |
| Docker configs | ~20 KB |
| Tests | ~500 KB |
| Data | ~200 KB |
| **Total (excluding deps)** | **~10 MB** |
| Python dependencies | ~200 MB |
| Node modules | ~150 MB |
| **Total with dependencies** | **~360 MB** |

**Recommended minimum:** 500 MB free space

---

## Quick Deploy (Manual Steps)

### Step 1: Check Disk Space on Remote Server

```bash
# SSH to server
ssh cvanthin@foresight.nvidia.com

# Check disk space
df -h /home

# Check your home directory
du -sh /home/cvanthin 2>/dev/null
```

### Step 2: Create Directory

```bash
# On remote server
mkdir -p /home/cvanthin/trading
```

### Step 3: Upload Files

```bash
# From your local machine
rsync -avz --progress \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude 'node_modules' \
    --exclude '.pytest_cache' \
    --exclude '.DS_Store' \
    /Users/cvanthin/code/trading/000_trading/ \
    cvanthin@foresight.nvidia.com:/home/cvanthin/trading/
```

### Step 4: Set Up Environment (on remote server)

```bash
# SSH to server
ssh cvanthin@foresight.nvidia.com
cd /home/cvanthin/trading

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 5: Configure Environment

```bash
# Copy and edit .env file
cp env.example .env
nano .env

# Key settings:
# - Set OPENAI_API_KEY (or use Ollama)
# - Configure broker credentials
# - Set appropriate ports
```

### Step 6: Start the Application

```bash
# Option A: Run in foreground (for testing)
cd /home/cvanthin/trading
source .venv/bin/activate

# Start API
uvicorn src.api.main:app --host 0.0.0.0 --port 9876

# In another terminal, start frontend
cd /home/cvanthin/trading/frontend
npm run dev -- --host 0.0.0.0 --port 9877
```

```bash
# Option B: Run in background with nohup
cd /home/cvanthin/trading
source .venv/bin/activate

# Start API in background
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 9876 > api.log 2>&1 &
echo $! > api.pid

# Start frontend in background
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 9877 > frontend.log 2>&1 &
echo $! > frontend.pid
```

```bash
# Option C: Use tmux (recommended for persistent sessions)
tmux new -s xfactor

# Pane 1: API
cd /home/cvanthin/trading
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 9876

# Ctrl+B, % to split pane

# Pane 2: Frontend
cd /home/cvanthin/trading/frontend
npm run dev -- --host 0.0.0.0 --port 9877

# Ctrl+B, D to detach (keeps running)
# tmux attach -t xfactor to reattach
```

---

## Access Points

| Service | URL |
|---------|-----|
| **API** | http://foresight.nvidia.com:9876 |
| **Frontend** | http://foresight.nvidia.com:9877 |
| **API Docs** | http://foresight.nvidia.com:9876/docs |
| **Health Check** | http://foresight.nvidia.com:9876/health |

---

## Stop the Application

```bash
# If using PID files
kill $(cat /home/cvanthin/trading/api.pid)
kill $(cat /home/cvanthin/trading/frontend.pid)

# Or find and kill by port
lsof -ti:9876 | xargs kill
lsof -ti:9877 | xargs kill
```

---

## Docker Deployment (Alternative)

```bash
# On remote server
cd /home/cvanthin/trading/docker

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Automated Deploy Script

```bash
# Make deploy script executable
chmod +x /Users/cvanthin/code/trading/000_trading/scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

---

## Troubleshooting

### Port already in use
```bash
lsof -i :9876
kill -9 <PID>
```

### Permission denied on .env
```bash
chmod 600 .env
```

### Module not found
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend not accessible
```bash
# Check if running
curl http://localhost:9877

# Check firewall
sudo firewall-cmd --add-port=9877/tcp
```

---

## Verify Deployment

```bash
# Test API
curl http://foresight.nvidia.com:9876/health

# Expected response:
# {"status":"healthy"}

# Test API info
curl http://foresight.nvidia.com:9876/

# Expected response:
# {"status":"ok","name":"XFactor Bot","version":"0.1.0",...}
```

