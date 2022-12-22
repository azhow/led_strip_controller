// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
    onSetServerReady: (callback) => ipcRenderer.on('set-server-ready', callback),
    setColor: (color_rgb) => ipcRenderer.send('set-color', color_rgb)
});