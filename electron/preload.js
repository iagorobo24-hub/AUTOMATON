const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer via 'api' namespace
contextBridge.exposeInMainWorld('api', {
  // Backend URL
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  
  // App info
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),
  
  // Window controls
  minimize: () => ipcRenderer.invoke('window-minimize'),
  maximize: () => ipcRenderer.invoke('window-maximize'),
  close: () => ipcRenderer.invoke('window-close'),
});