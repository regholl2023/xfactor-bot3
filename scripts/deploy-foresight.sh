#!/bin/bash
# XFactor Bot Deployment to foresight.nvidia.com
# Usage: SSH_PASS='yourpassword' ./scripts/deploy-foresight.sh

set -e

# Configuration
REMOTE_USER="cvanthin"
REMOTE_HOST="foresight.nvidia.com"
REMOTE_DIR="/home/cvanthin/trading"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_PORT=9876
FRONTEND_PORT=9877

# Check for password
if [ -z "$SSH_PASS" ]; then
    echo "❌ Error: SSH_PASS environment variable not set"
    echo ""
    echo "Usage: SSH_PASS='yourpassword' ./scripts/deploy-foresight.sh"
    echo ""
    exit 1
fi

SSH_CMD="sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no"
SCP_CMD="sshpass -p '$SSH_PASS' scp -o StrictHostKeyChecking=no"
RSYNC_CMD="sshpass -p '$SSH_PASS' rsync -e 'ssh -o StrictHostKeyChecking=no'"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     XFactor Bot Deployment to foresight.nvidia.com        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check disk space
echo "📊 Step 1: Checking remote disk space..."
eval $SSH_CMD $REMOTE_USER@$REMOTE_HOST "df -h /home && echo '' && du -sh /home/$REMOTE_USER 2>/dev/null || echo 'Home directory is new'"

echo ""
echo "Need approximately 500MB for deployment."
echo ""

# Step 2: Create directory
echo "📁 Step 2: Creating remote directory..."
eval $SSH_CMD $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_DIR"
echo "✅ Created $REMOTE_DIR"

# Step 3: Upload files
echo ""
echo "📤 Step 3: Uploading files (this may take a few minutes)..."
eval $RSYNC_CMD -avz --progress \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude 'node_modules' \
    --exclude '.DS_Store' \
    --exclude 'htmlcov' \
    --exclude '*.egg-info' \
    --exclude 'dist' \
    --exclude 'build' \
    --exclude '.cursor' \
    "'$LOCAL_DIR/'" "'$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/'"

echo "✅ Files uploaded"

# Step 4: Set up environment
echo ""
echo "🔧 Step 4: Setting up Python environment..."
eval $SSH_CMD $REMOTE_USER@$REMOTE_HOST "
cd $REMOTE_DIR

# Create venv if needed
if [ ! -d '.venv' ]; then
    echo 'Creating Python virtual environment...'
    python3 -m venv .venv
fi

# Install dependencies
source .venv/bin/activate
echo 'Installing Python dependencies...'
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo '✅ Python environment ready'
"

# Step 5: Set up frontend
echo ""
echo "🎨 Step 5: Setting up frontend..."
eval $SSH_CMD $REMOTE_USER@$REMOTE_HOST "
cd $REMOTE_DIR/frontend
if [ -f 'package.json' ]; then
    echo 'Installing npm dependencies...'
    npm install --silent 2>/dev/null || npm install
    echo '✅ Frontend dependencies installed'
fi
"

# Step 6: Create start/stop scripts
echo ""
echo "⚙️  Step 6: Creating service scripts..."
eval $SSH_CMD $REMOTE_USER@$REMOTE_HOST "
cat > $REMOTE_DIR/start.sh << 'SCRIPT'
#!/bin/bash
cd $REMOTE_DIR
source .venv/bin/activate

# Kill any existing processes
pkill -f 'uvicorn src.api.main:app' 2>/dev/null || true
pkill -f 'vite.*9877' 2>/dev/null || true
sleep 1

# Start API
echo 'Starting XFactor Bot API on port $APP_PORT...'
nohup uvicorn src.api.main:app --host 0.0.0.0 --port $APP_PORT > api.log 2>&1 &
echo \$! > api.pid

# Start frontend
cd frontend
echo 'Starting frontend on port $FRONTEND_PORT...'
nohup npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT > frontend.log 2>&1 &
echo \$! > frontend.pid
cd ..

sleep 2
echo ''
echo '╔════════════════════════════════════════════════════════════╗'
echo '║            🚀 XFactor Bot is running!                      ║'
echo '╠════════════════════════════════════════════════════════════╣'
echo '║  API:      http://foresight.nvidia.com:$APP_PORT           ║'
echo '║  Frontend: http://foresight.nvidia.com:$FRONTEND_PORT      ║'
echo '║  API Docs: http://foresight.nvidia.com:$APP_PORT/docs      ║'
echo '╚════════════════════════════════════════════════════════════╝'
SCRIPT
chmod +x $REMOTE_DIR/start.sh

cat > $REMOTE_DIR/stop.sh << 'SCRIPT'
#!/bin/bash
echo 'Stopping XFactor Bot...'
pkill -f 'uvicorn src.api.main:app' 2>/dev/null || true
pkill -f 'vite.*$FRONTEND_PORT' 2>/dev/null || true
[ -f $REMOTE_DIR/api.pid ] && kill \$(cat $REMOTE_DIR/api.pid) 2>/dev/null
[ -f $REMOTE_DIR/frontend.pid ] && kill \$(cat $REMOTE_DIR/frontend.pid) 2>/dev/null
rm -f $REMOTE_DIR/api.pid $REMOTE_DIR/frontend.pid
echo '✅ XFactor Bot stopped'
SCRIPT
chmod +x $REMOTE_DIR/stop.sh
"
echo "✅ Service scripts created"

# Step 7: Start the application
echo ""
echo "🚀 Step 7: Starting XFactor Bot..."
eval $SSH_CMD $REMOTE_USER@$REMOTE_HOST "$REMOTE_DIR/start.sh"

# Step 8: Verify
echo ""
echo "🔍 Step 8: Verifying deployment..."
sleep 3
eval $SSH_CMD $REMOTE_USER@$REMOTE_HOST "curl -s http://localhost:$APP_PORT/health || echo 'API not responding yet'"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           🎉 Deployment Complete!                          ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  🌐 API:      http://foresight.nvidia.com:$APP_PORT        ║"
echo "║  🖥️  Frontend: http://foresight.nvidia.com:$FRONTEND_PORT  ║"
echo "║  📚 API Docs: http://foresight.nvidia.com:$APP_PORT/docs   ║"
echo "║                                                            ║"
echo "║  Commands:                                                 ║"
echo "║  • Start: ssh $REMOTE_USER@$REMOTE_HOST '$REMOTE_DIR/start.sh' ║"
echo "║  • Stop:  ssh $REMOTE_USER@$REMOTE_HOST '$REMOTE_DIR/stop.sh'  ║"
echo "║  • Logs:  ssh $REMOTE_USER@$REMOTE_HOST 'tail -f $REMOTE_DIR/api.log' ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"

