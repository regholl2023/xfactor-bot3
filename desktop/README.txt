XFactor Bot Desktop Application
===============================

A native desktop application for the XFactor Bot trading system,
built with Tauri (Rust) wrapping the React frontend.

PREREQUISITES
-------------
- Node.js 18+
- Rust 1.77+
- Python 3.11+ (for backend)

DEVELOPMENT
-----------
1. Start the Python backend (in a separate terminal):
   cd ..
   source .venv/bin/activate
   python3 -m uvicorn src.api.main:app --host 127.0.0.1 --port 9876 --reload

2. Start the desktop app in development mode:
   cd desktop
   npm run dev

This will:
- Start the Vite dev server for the React frontend
- Launch the Tauri desktop window
- Enable hot reload for both frontend and Rust code

BUILDING
--------
To create a production build:

   npm run build

Platform-specific builds:
   npm run build:mac     # macOS (.dmg, .app)
   npm run build:win     # Windows (.msi, .exe)
   npm run build:linux   # Linux (.deb, .AppImage)

Output will be in: src-tauri/target/release/bundle/

BUNDLING THE BACKEND
--------------------
To bundle the Python backend as a standalone executable:

   python3 scripts/bundle-backend.py

This uses PyInstaller to create a single executable that can be
distributed alongside the desktop app.

PROJECT STRUCTURE
-----------------
desktop/
  package.json          - Node.js dependencies and scripts
  src-tauri/
    Cargo.toml          - Rust dependencies
    tauri.conf.json     - Tauri configuration
    src/
      main.rs           - Application entry point
      lib.rs            - Main app logic, menus, tray
    capabilities/
      default.json      - Security permissions
    icons/              - App icons for all platforms
  scripts/
    start-backend.sh    - Start Python backend
    bundle-backend.py   - Bundle backend with PyInstaller

FEATURES
--------
- Native window with custom menu bar
- System tray with quick actions
- Desktop notifications for trade alerts
- Automatic updates (when configured)
- Single instance enforcement
- Auto-start on login (optional)
- Full keyboard shortcuts

KEYBOARD SHORTCUTS
------------------
Ctrl/Cmd + 1        Dashboard
Ctrl/Cmd + 2        Bot Manager
Ctrl/Cmd + 3        Backtesting
Ctrl/Cmd + 4        Portfolio
Ctrl/Cmd + Shift+S  Start All Bots
Ctrl/Cmd + Shift+X  Stop All Bots
Ctrl/Cmd + Shift+P  Pause Trading
Ctrl/Cmd + Shift+K  KILL SWITCH
F11                 Toggle Fullscreen
F12                 Toggle DevTools

