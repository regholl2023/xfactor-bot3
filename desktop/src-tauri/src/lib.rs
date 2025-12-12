//! XFactor Bot Desktop Application
//! 
//! AI-Powered Automated Trading System with backtesting, ML optimization,
//! portfolio rebalancing, and multi-account support.

use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem, Submenu},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Emitter, Manager, Runtime,
};

/// Trading state shared across the app
#[derive(Default)]
pub struct TradingState {
    pub is_trading: bool,
    pub connected_accounts: u32,
    pub active_bots: u32,
}

/// Start the Python backend server
#[tauri::command]
async fn start_backend() -> Result<String, String> {
    // In development, backend runs separately
    // In production, we'd spawn the bundled Python server
    Ok("Backend started".to_string())
}

/// Stop the Python backend server
#[tauri::command]
async fn stop_backend() -> Result<String, String> {
    Ok("Backend stopped".to_string())
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
        .setup(|app| {
            // Create menu
            let menu = create_menu(app.handle())?;
            app.set_menu(menu)?;

            // Setup system tray
            setup_tray(app.handle())?;

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
        .invoke_handler(tauri::generate_handler![
            start_backend,
            stop_backend,
            get_system_info,
            show_notification,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
