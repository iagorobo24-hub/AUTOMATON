const { app, BrowserWindow, ipcMain, Menu, Tray, globalShortcut, nativeTheme } = require('electron');
const path = require('path');

let mainWindow = null;
let tray = null;

const isDev = !app.isPackaged;

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
    preload: path.join(__dirname, 'preload.js'),
    sandbox: true,
  },
};

const FRONTEND_DEV_URL = 'http://localhost:3001';
const BACKEND_API_URL = 'http://localhost:8001';

function createWindow() {
  console.log('[MAIN] Creating main window...');

  mainWindow = new BrowserWindow({
    width: APP_CONFIG.width,
    height: APP_CONFIG.height,
    minWidth: APP_CONFIG.minWidth,
    minHeight: APP_CONFIG.minHeight,
    backgroundColor: APP_CONFIG.backgroundColor,
    title: APP_CONFIG.name,
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: APP_CONFIG.webPreferences,
    show: false,
  });

  const startUrl = isDev
    ? FRONTEND_DEV_URL
    : `file://${path.join(__dirname, '../build/index.html')}`;

  console.log('[MAIN] Loading URL:', startUrl);
  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    console.log('[MAIN] Window ready and shown');
  });

  mainWindow.setMenuBarVisibility(false);

  mainWindow.on('closed', () => {
    mainWindow = null;
    console.log('[MAIN] Window closed');
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

function createAppMenu() {
  const template = [
    {
      label: 'Archivo',
      submenu: [
        {
          label: 'Nueva Ventana',
          accelerator: 'CmdOrCtrl+N',
          click: () => createWindow(),
        },
        { type: 'separator' },
        {
          label: 'Salir',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Alt+F4',
          click: () => app.quit(),
        },
      ],
    },
    {
      label: 'Ver',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Ventana',
      submenu: [
        { role: 'minimize' },
        { role: 'close' },
        { type: 'separator' },
        {
          label: 'Always on Top',
          type: 'checkbox',
          click: (menuItem) => {
            if (mainWindow) {
              mainWindow.setAlwaysOnTop(menuItem.checked);
            }
          },
        },
      ],
    },
    {
      label: 'Ayuda',
      submenu: [
        {
          label: 'Acerca de AUTOMATON',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'Acerca de AUTOMATON',
              message: `AUTOMATON v${APP_CONFIG.version}`,
              detail: 'Plataforma de Trading Automatizado con IA',
            });
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

function createTray() {
  try {
    const iconPath = path.join(__dirname, 'icon.ico');
    tray = new Tray(iconPath);

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Mostrar AUTOMATON',
        click: () => {
          if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
          }
        },
      },
      { type: 'separator' },
      {
        label: 'Estado del Sistema',
        enabled: false,
      },
      { type: 'separator' },
      {
        label: 'Salir',
        click: () => app.quit(),
      },
    ]);

    tray.setToolTip('AUTOMATON - Agentes de Trading');
    tray.setContextMenu(contextMenu);

    tray.on('double-click', () => {
      if (mainWindow) {
        mainWindow.show();
        mainWindow.focus();
      }
    });

    console.log('[MAIN] Tray created successfully');
  } catch (error) {
    console.log('[MAIN] Tray not created (icon may not exist):', error.message);
  }
}

function registerShortcuts() {
  globalShortcut.register('CommandOrControl+Shift+A', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });
}

function setupIpcHandlers() {
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

  ipcMain.handle('get-window-state', () => {
    if (!mainWindow) return null;
    return {
      isMinimized: mainWindow.isMinimized(),
      isMaximized: mainWindow.isMaximized(),
      isFullScreen: mainWindow.isFullScreen(),
      isVisible: mainWindow.isVisible(),
      isFocused: mainWindow.isFocused(),
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

  ipcMain.handle('window-toggle-fullscreen', () => {
    if (mainWindow) {
      mainWindow.setFullScreen(!mainWindow.isFullScreen());
    }
  });

  ipcMain.handle('get-theme', () => {
    return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
  });

  ipcMain.handle('show-notification', (event, { title, body }) => {
    const { Notification } = require('electron');
    if (Notification.isSupported()) {
      new Notification({ title, body }).show();
    }
  });

  ipcMain.handle('get-backend-url', () => {
    return BACKEND_API_URL;
  });

  ipcMain.handle('get-frontend-url', () => {
    return isDev ? FRONTEND_DEV_URL : null;
  });

  console.log('[MAIN] IPC handlers registered');
}

process.on('uncaughtException', (error) => {
  console.error('[MAIN] Uncaught Exception:', error);
  if (!isDev) {
    app.exit(1);
  }
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('[MAIN] Unhandled Rejection at:', promise, 'reason:', reason);
});

app.whenReady().then(() => {
  console.log('[MAIN] App ready, initializing...');
  console.log('[MAIN] Running in:', isDev ? 'development' : 'production');
  console.log('[MAIN] Frontend URL:', isDev ? FRONTEND_DEV_URL : 'build');
  console.log('[MAIN] Backend API:', BACKEND_API_URL);

  createAppMenu();
  setupIpcHandlers();
  createWindow();
  createTray();
  registerShortcuts();

  console.log('[MAIN] Initialization complete');
});

app.on('window-all-closed', () => {
  console.log('[MAIN] All windows closed');
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  console.log('[MAIN] App will quit');
});

app.on('before-quit', () => {
  console.log('[MAIN] Before quit event');
});