// === Imports ===

const { app, BrowserWindow } = require('electron');
const path = require('path');
const portscanner = require('portscanner');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) { // eslint-disable-line global-require
  app.quit();
}

// === Setup ===

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', start);

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  ////if (process.platform !== 'darwin') {
    app.quit();
  ////}
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.

// === Main ===

function start() {
  // === Port Selection ===
  
  var selected_port = null;
  var port_blacklist = [5000];

  function recursive_port_search(port) {
    var callback = (error, status) => {
      console.log('Port ' + port + ' current activity: ' + status);
      if(!port_blacklist.includes(port) && status === 'closed') {
        console.log('Openning connection on port: ' + port);
        selected_port = port;
        createWindow();
      } else if(!selected_port && port < 5100) {
        recursive_port_search(port + 1);
      }
    }
    portscanner.checkPortStatus(port, callback);
  }

  recursive_port_search(5000);
  
  // === Launch Window ===
  
  const createWindow = () => {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
      width: 1100,
      height: 600,
    });

    // and load the index.html of the app.
    //mainWindow.loadFile(path.join(__dirname, 'source/ui/index.html'));

    var url = 'http://127.0.0.1:'+selected_port+'/ui/index.html';
    mainWindow.loadURL(url);
    console.log('Opening Electron browser at: ' + url);
    
    // Open the DevTools.
    mainWindow.webContents.openDevTools();
  };
  
  app.on('activate', () => {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
}
