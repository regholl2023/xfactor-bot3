//! XFactor Bot Desktop Application
//! 
//! AI-Powered Automated Trading System with backtesting, ML optimization,
//! portfolio rebalancing, and multi-account support.

use std::sync::Mutex;
use std::process::{Child, Command, Stdio};
use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem, Submenu},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Emitter, Manager, Runtime,
};
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandChild;

/// Trading state shared across the app
#[derive(Default)]
pub struct TradingState {
    pub is_trading: bool,
    pub connected_accounts: u32,
    pub active_bots: u32,
}

/// Backend process state
pub struct BackendState {
    pub child: Mutex<Option<CommandChild>>,
}

/// Start the Python backend server
#[tauri::command]
async fn start_backend(app: tauri::AppHandle, state: tauri::State<'_, BackendState>) -> Result<String, String> {
    // Check if already running
    {
        let guard = state.child.lock().unwrap();
        if guard.is_some() {
            return Ok("Backend already running".to_string());
        }
    }
    
    // Spawn the sidecar backend
    let sidecar = app.shell()
        .sidecar("xfactor-backend")
        .map_err(|e| format!("Failed to create sidecar command: {}", e))?;
    
    let (mut _rx, child) = sidecar.spawn()
        .map_err(|e| format!("Failed to spawn backend: {}", e))?;
    
    // Store the child process
    {
        let mut guard = state.child.lock().unwrap();
        *guard = Some(child);
    }
    
    log::info!("Backend sidecar started");
    Ok("Backend started".to_string())
}

/// Stop the Python backend server
#[tauri::command]
async fn stop_backend(state: tauri::State<'_, BackendState>) -> Result<String, String> {
    let mut guard = state.child.lock().unwrap();
    if let Some(child) = guard.take() {
        child.kill().map_err(|e| format!("Failed to kill backend: {}", e))?;
        log::info!("Backend sidecar stopped");
        Ok("Backend stopped".to_string())
    } else {
        Ok("Backend was not running".to_string())
    }
}

/// Get system information
#[tauri::command]
fn get_system_info() -> serde_json::Value {
    serde_json::json!({
        "os": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "version": env!("CARGO_PKG_VERSION"),
    })
}

/// Check if backend is healthy
#[tauri::command]
async fn check_backend_health() -> Result<bool, String> {
    // The frontend will handle health checks via its own HTTP client
    // This is just a placeholder that returns true
    Ok(true)
}

/// Show a desktop notification (placeholder - notification plugin removed for now)
#[tauri::command]
async fn show_notification(
    _title: String,
    _body: String,
) -> Result<(), String> {
    // Notifications will be shown via the frontend
    Ok(())
}

/// Create the application menu
fn create_menu<R: Runtime>(app: &tauri::AppHandle<R>) -> Result<Menu<R>, tauri::Error> {
    let file_menu = Submenu::with_items(
        app,
        "File",
        true,
        &[
            &MenuItem::with_id(app, "new-bot", "New Bot", true, None::<&str>)?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "import-config", "Import Configuration...", true, None::<&str>)?,
            &MenuItem::with_id(app, "export-config", "Export Configuration...", true, None::<&str>)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::quit(app, Some("Quit XFactor Bot"))?,
        ],
    )?;

    let edit_menu = Submenu::with_items(
        app,
        "Edit",
        true,
        &[
            &PredefinedMenuItem::undo(app, None)?,
            &PredefinedMenuItem::redo(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::cut(app, None)?,
            &PredefinedMenuItem::copy(app, None)?,
            &PredefinedMenuItem::paste(app, None)?,
            &PredefinedMenuItem::select_all(app, None)?,
        ],
    )?;

    let view_menu = Submenu::with_items(
        app,
        "View",
        true,
        &[
            &MenuItem::with_id(app, "dashboard", "Dashboard", true, Some("CmdOrCtrl+1"))?,
            &MenuItem::with_id(app, "bots", "Bot Manager", true, Some("CmdOrCtrl+2"))?,
            &MenuItem::with_id(app, "backtest", "Backtesting", true, Some("CmdOrCtrl+3"))?,
            &MenuItem::with_id(app, "portfolio", "Portfolio", true, Some("CmdOrCtrl+4"))?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "toggle-fullscreen", "Toggle Fullscreen", true, Some("F11"))?,
            &MenuItem::with_id(app, "toggle-devtools", "Toggle DevTools", true, Some("F12"))?,
        ],
    )?;

    let trading_menu = Submenu::with_items(
        app,
        "Trading",
        true,
        &[
            &MenuItem::with_id(app, "start-all", "Start All Bots", true, Some("CmdOrCtrl+Shift+S"))?,
            &MenuItem::with_id(app, "stop-all", "Stop All Bots", true, Some("CmdOrCtrl+Shift+X"))?,
            &MenuItem::with_id(app, "pause-all", "Pause Trading", true, Some("CmdOrCtrl+Shift+P"))?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "kill-switch", "🚨 KILL SWITCH", true, Some("CmdOrCtrl+Shift+K"))?,
        ],
    )?;

    let help_menu = Submenu::with_items(
        app,
        "Help",
        true,
        &[
            &MenuItem::with_id(app, "documentation", "Documentation", true, None::<&str>)?,
            &MenuItem::with_id(app, "release-notes", "Release Notes", true, None::<&str>)?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "check-updates", "Check for Updates...", true, None::<&str>)?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "about", "About XFactor Bot", true, None::<&str>)?,
        ],
    )?;

    Menu::with_items(
        app,
        &[&file_menu, &edit_menu, &view_menu, &trading_menu, &help_menu],
    )
}

/// Setup the system tray
fn setup_tray<R: Runtime>(app: &tauri::AppHandle<R>) -> Result<(), tauri::Error> {
    let menu = Menu::with_items(
        app,
        &[
            &MenuItem::with_id(app, "show", "Show XFactor Bot", true, None::<&str>)?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "tray-start-all", "▶ Start All", true, None::<&str>)?,
            &MenuItem::with_id(app, "tray-stop-all", "⏹ Stop All", true, None::<&str>)?,
            &MenuItem::with_id(app, "tray-pause-all", "⏸ Pause All", true, None::<&str>)?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "tray-quit", "Quit", true, None::<&str>)?,
        ],
    )?;

    let _tray = TrayIconBuilder::with_id("main-tray")
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .on_menu_event(|app, event| match event.id.as_ref() {
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            "tray-quit" => {
                app.exit(0);
            }
            _ => {}
        })
        .build(app)?;

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let mut builder = tauri::Builder::default()
        .plugin(tauri_plugin_log::Builder::default().build())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_store::Builder::new().build());

    // Desktop-only plugins
    #[cfg(desktop)]
    {
        builder = builder
            .plugin(tauri_plugin_single_instance::init(|app, argv, _cwd| {
                // Focus the main window when attempting to open a second instance
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
                log::info!("Single instance triggered with args: {:?}", argv);
            }))
            .plugin(tauri_plugin_autostart::init(
                tauri_plugin_autostart::MacosLauncher::LaunchAgent,
                None,
            ));
    }

    builder
        .manage(BackendState {
            child: Mutex::new(None),
        })
        .setup(|app| {
            // Create menu
            let menu = create_menu(app.handle())?;
            app.set_menu(menu)?;

            // Setup system tray
            setup_tray(app.handle())?;

            // Start backend automatically
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                log::info!("Starting backend...");
                
                // Give the app a moment to initialize
                tokio::time::sleep(std::time::Duration::from_millis(500)).await;
                
                // Get the resource directory (MacOS folder in bundled app)
                let backend_path = if let Ok(resource_dir) = handle.path().resource_dir() {
                    // In bundled app, look in the MacOS folder (parent of Resources)
                    let macos_dir = resource_dir.parent().unwrap_or(&resource_dir).join("MacOS");
                    
                    // Try different binary names
                    let candidates = [
                        macos_dir.join("xfactor-backend"),
                        macos_dir.join("xfactor-backend-aarch64-apple-darwin"),
                        macos_dir.join("xfactor-backend-x86_64-apple-darwin"),
                    ];
                    
                    candidates.into_iter().find(|p| p.exists())
                } else {
                    None
                };
                
                if let Some(backend) = backend_path {
                    log::info!("Found backend at: {:?}", backend);
                    
                    match Command::new(&backend)
                        .stdout(Stdio::piped())
                        .stderr(Stdio::piped())
                        .spawn()
                    {
                        Ok(child) => {
                            log::info!("Backend started successfully (PID: {})", child.id());
                            // Note: We're using std::process::Child here, not storing in BackendState
                            // The child will be killed when dropped or when the app exits
                        }
                        Err(e) => {
                            log::error!("Failed to spawn backend: {}", e);
                        }
                    }
                } else {
                    // Try the sidecar mechanism as fallback (for dev mode)
                    match handle.shell().sidecar("xfactor-backend") {
                        Ok(sidecar) => {
                            match sidecar.spawn() {
                                Ok((mut rx, child)) => {
                                    log::info!("Backend sidecar started successfully");
                                    
                                    if let Some(state) = handle.try_state::<BackendState>() {
                                        let mut guard = state.child.lock().unwrap();
                                        *guard = Some(child);
                                    }
                                    
                                    tauri::async_runtime::spawn(async move {
                                        use tauri_plugin_shell::process::CommandEvent;
                                        while let Some(event) = rx.recv().await {
                                            match event {
                                                CommandEvent::Stdout(line) => {
                                                    log::info!("[Backend] {}", String::from_utf8_lossy(&line));
                                                }
                                                CommandEvent::Stderr(line) => {
                                                    log::warn!("[Backend] {}", String::from_utf8_lossy(&line));
                                                }
                                                CommandEvent::Terminated(status) => {
                                                    log::info!("[Backend] Process terminated: {:?}", status);
                                                    break;
                                                }
                                                _ => {}
                                            }
                                        }
                                    });
                                }
                                Err(e) => {
                                    log::error!("Failed to spawn backend sidecar: {}", e);
                                }
                            }
                        }
                        Err(e) => {
                            log::warn!("Backend not found (dev mode?): {}", e);
                        }
                    }
                }
            });

            // Handle menu events
            app.on_menu_event(|app, event| {
                match event.id.as_ref() {
                    "toggle-devtools" => {
                        // DevTools toggle - handled via webview in Tauri 2.0
                        // Users can use browser shortcuts (F12 or Cmd+Option+I)
                        log::info!("Toggle DevTools requested");
                    }
                    "toggle-fullscreen" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let is_fullscreen = window.is_fullscreen().unwrap_or(false);
                            let _ = window.set_fullscreen(!is_fullscreen);
                        }
                    }
                    "kill-switch" => {
                        log::warn!("KILL SWITCH activated from menu!");
                        // Emit event to frontend
                        let _ = app.emit("kill-switch", ());
                    }
                    _ => {}
                }
            });

            log::info!("XFactor Bot Desktop v{} started", env!("CARGO_PKG_VERSION"));
            Ok(())
        })
        .on_window_event(|window, event| {
            // Stop backend when app closes
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                log::info!("Window closing, stopping backend...");
                if let Some(state) = window.app_handle().try_state::<BackendState>() {
                    let mut guard = state.child.lock().unwrap();
                    if let Some(child) = guard.take() {
                        let _ = child.kill();
                        log::info!("Backend stopped on window close");
                    }
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            start_backend,
            stop_backend,
            get_system_info,
            show_notification,
            check_backend_health,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
