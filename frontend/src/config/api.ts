/**
 * API Configuration for XFactor Bot
 * 
 * Automatically patches fetch for Tauri desktop environment.
 */

// Check if we're running in Tauri (desktop)
const isTauri = typeof window !== 'undefined' && 
  ('__TAURI__' in window || '__TAURI_INTERNALS__' in window);

// Backend URL for desktop app
const DESKTOP_API_URL = 'http://localhost:9876';

// Store original fetch
const originalFetch = window.fetch.bind(window);

// Patched fetch that rewrites relative URLs for Tauri
const patchedFetch: typeof fetch = (input, init?) => {
  // Handle Request objects
  if (input instanceof Request) {
    const url = input.url;
    if (url.startsWith('/api')) {
      const newUrl = `${DESKTOP_API_URL}${url}`;
      return originalFetch(new Request(newUrl, input), init);
    }
    return originalFetch(input, init);
  }
  
  // Handle string URLs
  if (typeof input === 'string') {
    if (input.startsWith('/api')) {
      const newUrl = `${DESKTOP_API_URL}${input}`;
      return originalFetch(newUrl, init);
    }
    if (input.startsWith('/ws')) {
      const newUrl = `ws://localhost:9876${input}`;
      return originalFetch(newUrl, init);
    }
  }
  
  return originalFetch(input, init);
};

// Apply patch if running in Tauri
if (isTauri) {
  console.log('Running in Tauri desktop mode - patching fetch for localhost:9876');
  window.fetch = patchedFetch;
}

// Export utilities
export const getApiBaseUrl = (): string => {
  return isTauri ? DESKTOP_API_URL : '';
};

export const getWsBaseUrl = (): string => {
  if (isTauri) {
    return 'ws://localhost:9876';
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}`;
};

export const isDesktopApp = isTauri;
