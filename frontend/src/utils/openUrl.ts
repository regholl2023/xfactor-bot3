/**
 * Utility for opening external URLs in both browser and Tauri desktop app
 */

// Check if running in Tauri desktop app
export const isTauri = typeof window !== 'undefined' && 
  ('__TAURI__' in window || '__TAURI_INTERNALS__' in window)

/**
 * Open an external URL using the appropriate method
 * - In Tauri: Uses shell.open() to open in default browser
 * - In browser: Uses window.open()
 */
export const openExternalUrl = async (url: string): Promise<void> => {
  if (!url) {
    console.warn('No URL provided to openExternalUrl')
    return
  }
  
  try {
    if (isTauri) {
      // Use Tauri's shell.open for desktop app
      const { open } = await import('@tauri-apps/plugin-shell')
      await open(url)
      console.log('Opened URL via Tauri shell:', url)
    } else {
      // Use window.open for browser
      window.open(url, '_blank', 'noopener,noreferrer')
    }
  } catch (e) {
    console.error('Failed to open URL via Tauri, falling back to window.open:', e)
    // Fallback to window.open
    window.open(url, '_blank', 'noopener,noreferrer')
  }
}

/**
 * Open OAuth popup window
 * Note: In Tauri, this will open in the default browser, not a popup
 */
export const openOAuthPopup = async (url: string, name: string = 'oauth'): Promise<Window | null> => {
  if (!url) {
    console.warn('No URL provided to openOAuthPopup')
    return null
  }
  
  try {
    if (isTauri) {
      // In Tauri, open in default browser
      // OAuth callback will need to be handled differently (deep linking)
      const { open } = await import('@tauri-apps/plugin-shell')
      await open(url)
      return null
    } else {
      // In browser, open as popup
      return window.open(url, name, 'width=600,height=700')
    }
  } catch (e) {
    console.error('Failed to open OAuth popup:', e)
    return window.open(url, name, 'width=600,height=700')
  }
}

