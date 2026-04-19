const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),
  
  // Window controls
  minimize: () => ipcRenderer.invoke('window-minimize'),
  maximize: () => ipcRenderer.invoke('window-maximize'),
  close: () => ipcRenderer.invoke('window-close'),
  toggleFullscreen: () => ipcRenderer.invoke('window-toggle-fullscreen'),
  getWindowState: () => ipcRenderer.invoke('get-window-state'),
  
  // Theme
  getTheme: () => ipcRenderer.invoke('get-theme'),
  
  // Notifications
  showNotification: (title, body) => ipcRenderer.invoke('show-notification', { title, body }),
  
  // Platform info
  platform: process.platform,
  
  // Event listeners
  onWindowStateChange: (callback) => {
    ipcRenderer.on('window-state-changed', (event, state) => callback(state));
  },
  
  onThemeChange: (callback) => {
    ipcRenderer.on('theme-changed', (event, theme) => callback(theme));
  },
});