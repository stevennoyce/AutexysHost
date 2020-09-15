// === Imports ===

const { app, BrowserWindow } = require('electron');
const path = require('path');
const portscanner = require('portscanner');
var server_process = undefined;

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

app.on('quit', () => {
  if(server_process) {
    server_process.kill();
  }
});

// === Main ===

function start() {
  // === Port Selection ===
  
  var selected_port = null;
  var port_blacklist = [5000];

  function recursive_port_search(port) {
    var callback = (error, status) => {
      console.log('Port ' + port + ' current activity: ' + status);
      if(!port_blacklist.includes(port) && status === 'closed') {
        console.log('Launching local server on port: ' + port);
        selected_port = port;
        startPython();
        looping_wait_on_port(selected_port);
      } else if(!selected_port && port < 5100) {
        recursive_port_search(port + 1);
      }
    }
    portscanner.checkPortStatus(port, callback);
  }
  
  function looping_wait_on_port(port) {
  	var callback = (error, status) => {
  	  console.log('Any activity on port ' + port + ' yet? ' + (status==='open'? 'yes':'no'));
  	  if(status === 'open'){
  	  	createWindow();
  	  } else {
  	  	setTimeout(() => {
  	  		looping_wait_on_port(port);
  	  	}, 1000);
  	  }
  	}
  	portscanner.checkPortStatus(port, callback);
  }

  recursive_port_search(5000);
  
  // === Launch Python Server ===
  
  const startPython = () => {
    const PY_DIST_FOLDER = 'dist';
    const PY_MODULE = 'AutexysPyinstalled';
    
    const executablePath = () => {
      if(process.platform === 'win32') {
        return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE + '.exe');
      }
      return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE);
    }
    
    var executable = executablePath();
    
    console.log('Launching python server at: ' + executable);
    
    server_process = require('child_process').execFile(executable, [selected_port], (error, stdout, stderr) => {
      console.log('Python executable has ended.');
      if(error) {
        console.log(error);
      } 
      console.log(stdout);
    });
    
    server_process.stdout.on('data', (data) => {
      console.log('[PYTHON]: ' + data);
    });
    server_process.stderr.on('data', (data) => {
      console.log('[PYTHON]: ' + data);
    });
    
    
  }
  
  // === Launch Window ===
  
  const createWindow = () => {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
      width: 1100,
      height: 600,
      title: '',
      titleBarStyle:'hiddenInset',
    });

    // Give it the URL that is being served up by our Python server (already running in the background)
  	var url = 'http://127.0.0.1:'+selected_port+'/ui/index.html';
  	mainWindow.loadURL(url);
    console.log('Opening Electron browser at: ' + url);
  
  	mainWindow.webContents.on('did-finish-load', () => {
		mainWindow.webContents.insertCSS('.v-app-bar {-webkit-user-select: none;-webkit-app-region: drag;}');
    });
  
  	// Open the DevTools.
  	//mainWindow.webContents.openDevTools();
  };
  
  app.on('activate', () => {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
}
