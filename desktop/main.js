const { app, BrowserWindow } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    backgroundColor: '#050505',
    title: "AUTOMATON // NEXUS-9",
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    icon: path.join(__dirname, 'icon.ico') // Opcional si tienes icono
  });

  // En desarrollo, carga el servidor de React
  // En producción, cargará el archivo build/index.html
  const startUrl = isDev 
    ? 'http://localhost:3000' 
    : `file://${path.join(__dirname, '../frontend/build/index.html')}`;

  win.loadURL(startUrl);

  // Quitar la barra de menú superior para estética Cyberpunk
  win.setMenuBarVisibility(false);
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
