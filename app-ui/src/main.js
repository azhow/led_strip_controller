const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 800,
    webPreferences: {
      preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY,
    },
  });

  mainWindow.removeMenu()

  // and load the index.html of the app.
  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  spawnBackendProcess();

  var client = grpc_main(mainWindow);

  ipcMain.on('set-color', (event, color_rgb) => {
    return new Promise(() => {
      setColor(client, color_rgb);
    });
  });
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
function spawnBackendProcess() {
  let spawn = require("child_process").spawn;

  let bat = spawn(".\\..\\.venv\\Scripts\\python.exe", [ ".\\..\\Controller\\main.py" ]);
  
  bat.stdout.on("data", (data) => {
    // Handle data...
    console.log(`Data:\n${data}`);
  });
  
  bat.stderr.on("data", (err) => {
    // Handle error...
    console.log(`Error:\n${err}`);
  });
  
  bat.on("exit", (code) => {
    // Handle exit
    console.log(`Stdout:\n${code}`);
  });
}

function grpc_main(mainWindow) {
  var PROTO_PATH = __dirname + '/../../../protoc/test.proto';

  var grpc = require('@grpc/grpc-js');
  var protoLoader = require('@grpc/proto-loader');
  var packageDefinition = protoLoader.loadSync(
      PROTO_PATH,
      {keepCase: true,
       longs: String,
       enums: String,
       defaults: true,
       oneofs: true
      });
  
  var hello_proto = grpc.loadPackageDefinition(packageDefinition);
  
  var client = new hello_proto.Greeter('localhost:50051', grpc.credentials.createInsecure());

  client.waitForReady(Infinity, (err) => { server_ready(mainWindow, err); });

  return client;
}

function server_ready(mainWindow, err) {
  if (!err) {
    mainWindow.webContents.send('set-server-ready');
  }
}

function setColor(client, color_rgb) {
  client.setColor({rgb_color: [color_rgb.r, color_rgb.g, color_rgb.b]}, function(err, response) {
    if (err) console.log('Error:', err);
  });
}