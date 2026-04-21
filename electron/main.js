const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow = null;

const APP_CONFIG = {
  name: 'AUTOMATON',
  version: '2.2.0',
  width: 1400,
  height: 900,
  minWidth: 1024,
  minHeight: 700,
  backgroundColor: '#050505',
  webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    sandbox: true,
    preload: path.join(__dirname, 'preload.js'),
  },
};

const BACKEND_API_URL = 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';

/**
 * Wait for server to be available with polling
 * @param {string} url - URL to poll
 * @param {number} timeout - Timeout in ms (default 30000)
 * @returns {Promise<void>}
 */
async function waitForServer(url, timeout = 30000) {
  const start = Date.now();
  const interval = 500;
  
  while (Date.now() - start < timeout) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        console.log(`[MAIN] Server ready at ${url}`);
        return;
      }
    } catch (err) {
      // Server not ready yet, continue polling
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  throw new Error(`Server at ${url} did not respond within ${timeout}ms`);
}

async function createWindow() {
  console.log('[MAIN] Creating main window...');

  // Wait for frontend server to be ready
  try {
    console.log(`[MAIN] Waiting for server at ${FRONTEND_URL}...`);
    await waitForServer(FRONTEND_URL);
  } catch (err) {
    console.error('[MAIN] Server not available:', err.message);
    // Continue anyway - will show error page
  }

  mainWindow = new BrowserWindow({
    width: APP_CONFIG.width,
    height: APP_CONFIG.height,
    minWidth: APP_CONFIG.minWidth,
    minHeight: APP_CONFIG.minHeight,
    backgroundColor: APP_CONFIG.backgroundColor,
    title: APP_CONFIG.name,
    webPreferences: APP_CONFIG.webPreferences,
    show: false,
  });

  console.log('[MAIN] Loading URL:', FRONTEND_URL);

  mainWindow.loadURL(FRONTEND_URL).catch(err => {
    console.error('[MAIN] Failed to load URL:', err);
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    console.log('[MAIN] Window ready and shown');
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    console.log('[MAIN] Window closed');
  });
}

// IPC Handlers
ipcMain.handle('get-backend-url', () => {
  return BACKEND_API_URL;
});

ipcMain.handle('get-app-info', () => {
  return {
    name: APP_CONFIG.name,
    version: APP_CONFIG.version,
    platform: process.platform,
    arch: process.arch,
    electron: process.versions.electron,
    node: process.versions.node,
    chrome: process.versions.chrome,
  };
});

ipcMain.handle('window-minimize', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.handle('window-maximize', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.handle('window-close', () => {
  if (mainWindow) mainWindow.close();
});

// App lifecycle
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});