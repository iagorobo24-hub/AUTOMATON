const { app, BrowserWindow, ipcMain, Menu, Tray, globalShortcut, nativeTheme } = require('electron');
const path = require('path');

let mainWindow = null;
let tray = null;

// Configuracion de la aplicacion
const APP_CONFIG = {
  name: 'AUTOMATON',
  version: '1.0.0',
  width: 1400,
  height: 900,
  minWidth: 1024,
  minHeight: 700,
  backgroundColor: '#050505',
  webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    preload: path.join(__dirname, 'preload.js'),
    sandbox: false,
  },
};

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
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../frontend/build/index.html')}`;

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


  mainWindow.on('minimize', (event) => {

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
              message: 'AUTOMATON v' + APP_CONFIG.version,
              detail: 'Framework de Agentes Autoreplicantes para Trading Crypto',
            });
          },
        },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Crear icono en bandeja del sistema
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

// Registrar atajos de teclado
function registerShortcuts() {
  // Mostrar/ocultar ventana
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

  console.log('[MAIN] Global shortcuts registered');
}

// IPC Handlers
function setupIpcHandlers() {
  // Obtener info de la app
  ipcMain.handle('get-app-info', () => {
    return {
      name: APP_CONFIG.name,
      version: APP_CONFIG.version,
      platform: process.platform,
      arch: process.arch,
      electron: process.versions.electron,
      node: process.versions.node,
    };
  });

  // Obtener estado de la ventana
  ipcMain.handle('get-window-state', () => {
    if (!mainWindow) return null;
    return {
      isMinimized: mainWindow.isMinimized(),
      isMaximized: mainWindow.isMaximized(),
      isFullScreen: mainWindow.isFullScreen(),
      isVisible: mainWindow.isVisible(),
    };
  });

  // Control de ventana
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

  // Tema
  ipcMain.handle('get-theme', () => {
    return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
  });

  // Notificaciones
  ipcMain.handle('show-notification', (event, { title, body }) => {
    const { Notification } = require('electron');
    if (Notification.isSupported()) {
      new Notification({ title, body }).show();
    }
  });

  console.log('[MAIN] IPC handlers registered');
}

// Manejo de errores no capturados
process.on('uncaughtException', (error) => {
  console.error('[MAIN] Uncaught Exception:', error);
  // No salir en desarrollo para facilitar debug
  if (!isDev) {
    app.exit(1);
  }
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('[MAIN] Unhandled Rejection at:', promise, 'reason:', reason);
});

// App lifecycle
app.whenReady().then(() => {
  console.log('[MAIN] App ready, initializing...');
  
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