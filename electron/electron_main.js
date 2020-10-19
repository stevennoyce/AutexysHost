// === Imports ===

const { app, BrowserWindow } = require('electron');
const path = require('path');
const portscanner = require('portscanner');
const contextMenu = require('electron-context-menu');



// === Constants ===

const PORT_NUMBER_START = 5050;



// === Globals ===

var server_process = undefined;
var mainWindow = undefined;



// === Setup ===

contextMenu({
  showLookUpSelection: false,
  showSearchWithGoogle: false,
  showSaveImage: true,
  showSaveImageAs: true,
});

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) { // eslint-disable-line global-require
  app.quit();
}

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
    process.kill(-server_process.pid);
  }
});





// === Main ===

function start() {
  // === More Setup ===
  
  app.on('activate', () => {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
  
  // === Port Selection ===
  
  var selected_port = null;
  var port_blacklist = [5000];

  function recursive_port_search(port) {
    var callback = (error, status) => {
      console.log('[ELECTRON] Port ' + port + ' current activity: ' + status);
      if(!port_blacklist.includes(port) && status === 'closed') {
        console.log('[ELECTRON] Launching local server on port: ' + port);
        selected_port = port;
        createWindow();
        startPython();
        looping_wait_on_port(selected_port);
      } else if(!selected_port && port < 5999) {
        recursive_port_search(port + 1);
      }
    }
    portscanner.checkPortStatus(port, callback);
  }
  
  function looping_wait_on_port(port) {
  	var callback = (error, status) => {
  	  console.log('[ELECTRON] Any activity on port ' + port + ' yet? ' + (status==='open'? 'yes':'no'));
  	  if(status === 'open'){
  	  	showMainWindow();
  	  } else {
  	  	setTimeout(() => {
  	  		looping_wait_on_port(port);
  	  	}, 1000);
  	  }
  	}
  	portscanner.checkPortStatus(port, callback);
  }
  
  // === Launch Python Server ===
  
  const startPython = () => {
    const PY_DIST_FOLDER = 'dist';
    const PY_MODULE = 'AutexysPyinstalled';
    
    const executablePath = () => {
      if(process.platform === 'win32') {
        return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE, PY_MODULE + '.exe');
      }
      return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE, PY_MODULE);
    }
    
    var executable = executablePath();
    
    console.log('[ELECTRON] Launching python server at: ' + executable);
    
    server_process = require('child_process').spawn(executable, [selected_port], {detached: true, stdio: 'inherit'});
        
  }
  
  // === Manage Application Windows ===
  
  const createWindow = () => {
    mainWindow = new BrowserWindow({
      show: false,
      width: 800,
      height: 600,
      title: '',
      titleBarStyle: 'hidden', //'hiddenInset',
      webPreferences: {
        preload: path.join(__dirname, 'electron_preload.js'),
      },
    });
    
    // Wait until the window has resized before immediately showing it
    mainWindow.maximize();
    mainWindow.show();
    
    // Display a splash screen 
    mainWindow.loadFile(path.join(__dirname, 'splash_screen/splash_screen.html'));
    
    // Open the DevTools.
    //mainWindow.webContents.openDevTools();
  };
  
  const showMainWindow = () => {
   
    // Give it the URL that is being served up by our Python server (already running in the background)
  	var url = 'http://127.0.0.1:'+selected_port+'/ui/index.html';
  	mainWindow.loadURL(url);
    console.log('[ELECTRON]: Opening Electron browser at: ' + url);
  
    
  	mainWindow.webContents.on('did-finish-load', () => {
      // Inject CSS (makes the window draggable by the system bar)
		  mainWindow.webContents.insertCSS('.v-system-bar {-webkit-user-select: none;-webkit-app-region: drag;}');
      
      // Inject Javascript (call addEventListener on every document element of the class '.onClickFolderBrowser' and call a function defined)
      mainWindow.webContents.executeJavaScript(`
        document.querySelectorAll('.onClickFolderBrowser').forEach((elem) => {
          console.log('Injecting an Electron folder dialog event listener.');
          elem.addEventListener('click', (event) => {
            window.openFolderDialog().then((result) => {
              if(!result.canceled){
                console.log(result.filePaths[0]);
                window.app.$data.workspaceDataFolderPath = result.filePaths[0];
              }
            });
          });
        });
      `);
    });
  
  	// Open the DevTools.
  	//mainWindow.webContents.openDevTools();
  };
  
  
  
  // === Ready to Begin ===
  
  // This starts off the chain reaction that will launch the app
  recursive_port_search(PORT_NUMBER_START);
  
}
