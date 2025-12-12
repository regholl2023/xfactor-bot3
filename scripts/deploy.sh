#!/bin/bash
# XFactor Bot Deployment Script
# Deploy to foresight.nvidia.com

set -e

# Configuration
REMOTE_USER="cvanthin"
REMOTE_HOST="foresight.nvidia.com"
REMOTE_DIR="/home/cvanthin/trading"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_PORT=9876

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           XFactor Bot Deployment Script                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Local directory: $LOCAL_DIR"
echo "🖥️  Remote: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
echo "🌐 Port: $APP_PORT"
echo ""

# Step 1: Check disk space on remote server
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Step 1: Checking remote disk space..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh $REMOTE_USER@$REMOTE_HOST "
echo 'Disk space on /home:'
df -h /home
echo ''
echo 'Current usage in home directory:'
du -sh /home/$REMOTE_USER 2>/dev/null || echo '/home/$REMOTE_USER does not exist yet'
echo ''
echo 'Available space check (need ~500MB):'
AVAIL=\$(df /home | tail -1 | awk '{print \$4}')
echo \"Available: \$AVAIL KB\"
"

echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

# Step 2: Create remote directory
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Step 2: Creating remote directory..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_DIR"
echo "✅ Created $REMOTE_DIR"

# Step 3: Sync files (excluding large/unnecessary directories)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 Step 3: Uploading files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

rsync -avz --progress \
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
    "$LOCAL_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

echo "✅ Files uploaded successfully"

# Step 4: Set up environment on remote server
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Step 4: Setting up environment on remote server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh $REMOTE_USER@$REMOTE_HOST "
cd $REMOTE_DIR

# Create virtual environment if it doesn't exist
if [ ! -d '.venv' ]; then
    echo 'Creating Python virtual environment...'
    python3 -m venv .venv
fi

# Activate and install dependencies
source .venv/bin/activate
echo 'Installing Python dependencies...'
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Install frontend dependencies
if [ -d 'frontend' ]; then
    echo 'Installing frontend dependencies...'
    cd frontend
    npm install --silent
    cd ..
fi

echo '✅ Environment setup complete'
"

# Step 5: Create systemd service file
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Step 5: Creating service configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh $REMOTE_USER@$REMOTE_HOST "
cat > $REMOTE_DIR/start.sh << 'EOF'
#!/bin/bash
cd $REMOTE_DIR
source .venv/bin/activate

# Start backend API
echo 'Starting XFactor Bot API on port $APP_PORT...'
uvicorn src.api.main:app --host 0.0.0.0 --port $APP_PORT &
API_PID=\$!

# Start frontend (development mode)
cd frontend
echo 'Starting frontend...'
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=\$!

echo \"API PID: \$API_PID\"
echo \"Frontend PID: \$FRONTEND_PID\"

# Save PIDs
echo \$API_PID > $REMOTE_DIR/api.pid
echo \$FRONTEND_PID > $REMOTE_DIR/frontend.pid

echo 'XFactor Bot is running!'
echo 'API: http://foresight.nvidia.com:$APP_PORT'
echo 'Frontend: http://foresight.nvidia.com:9877'

wait
EOF
chmod +x $REMOTE_DIR/start.sh

cat > $REMOTE_DIR/stop.sh << 'EOF'
#!/bin/bash
echo 'Stopping XFactor Bot...'
if [ -f $REMOTE_DIR/api.pid ]; then
    kill \$(cat $REMOTE_DIR/api.pid) 2>/dev/null
    rm $REMOTE_DIR/api.pid
fi
if [ -f $REMOTE_DIR/frontend.pid ]; then
    kill \$(cat $REMOTE_DIR/frontend.pid) 2>/dev/null
    rm $REMOTE_DIR/frontend.pid
fi
echo 'Stopped.'
EOF
chmod +x $REMOTE_DIR/stop.sh

echo '✅ Service scripts created'
"

# Step 6: Start the application
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Step 6: Starting XFactor Bot..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Start the application now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_DIR && nohup ./start.sh > $REMOTE_DIR/xfactor.log 2>&1 &"
    sleep 3
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           🎉 XFactor Bot Deployed Successfully!            ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║                                                            ║"
    echo "║  🌐 API:      http://foresight.nvidia.com:$APP_PORT       ║"
    echo "║  🖥️  Frontend: http://foresight.nvidia.com:9877           ║"
    echo "║                                                            ║"
    echo "║  📋 Logs:     $REMOTE_DIR/xfactor.log          ║"
    echo "║                                                            ║"
    echo "║  ⏹️  Stop:     ssh $REMOTE_USER@$REMOTE_HOST '$REMOTE_DIR/stop.sh' ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
else
    echo ""
    echo "Application not started. To start manually:"
    echo "  ssh $REMOTE_USER@$REMOTE_HOST '$REMOTE_DIR/start.sh'"
fi

echo ""
echo "Deployment complete!"

