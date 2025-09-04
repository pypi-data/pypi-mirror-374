const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // App information
    getEngineInfo: () => ipcRenderer.invoke('get-engine-info'),

    // File operations
    selectFile: (options) => ipcRenderer.invoke('select-file', options),
    saveFile: (options) => ipcRenderer.invoke('save-file', options),

    // Sudarshan Engine operations
    executeSudarshan: (command, args) => ipcRenderer.invoke('execute-sudarshan', command, args),

    // Menu actions
    onMenuAction: (callback) => ipcRenderer.on('menu-action', callback),

    // Remove all listeners when component unmounts
    removeAllListeners: (event) => ipcRenderer.removeAllListeners(event)
});

// Security: Only expose specific, safe APIs
// No direct access to Node.js APIs or file system